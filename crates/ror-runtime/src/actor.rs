//! M6 actor runtime — isolation, mailbox FIFO, spawn/send/receive, FIFO scheduler.
//!
//! **Authority:** R-ACTOR-01…10, R-BUDGET-16, R-MARSHAL-01, R-CORE-07, GI-SEC-07.
//! **U-27 OPEN:** minimal `ActorStatus` set (runnable/blocked/pending/terminal).
//! **U-30 OPEN:** mailbox stores checked machine-data values (no Cap/Fn), not 15A bytes.
//! **U-03 OPEN:** thin spawn budget (integer units) without full BudgetAllocationSpec algebra.
//! **U-34 OPEN:** GlobalState / RunnableQueue shapes provisional.
//!
//! **Hard hinge:** no Actor/Scheduler/Mailbox path to `HostExecutor`. Effects only via
//! existing M5 `run_effect_pipeline` / CEK Request (not duplicated here).

use std::collections::{BTreeMap, BTreeSet, VecDeque};

use ror_core::capability::{CapabilityContext, Constraint, LogicalTime};
use ror_core::machine::{DelegatedCapability, Environment, Expr, Fault, Value};
use ror_core::types::{ActorId, ActorIdAlloc, CapRef};
use ror_kernel::CapabilityKernel;

/// Minimum ActorStatus set for R-ACTOR-04 eligibility (U-27 provisional).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum ActorStatus {
    /// Eligible for FIFO runnable selection.
    Runnable,
    /// Blocked on empty mailbox receive (R-ACTOR-06). Not scheduled.
    Blocked,
    /// Waiting on issued effect (R-CORE-14 step 15). Not scheduled. Survives Deadlock.
    Pending,
    /// Terminal — never scheduled (U-27 provisional label).
    Terminal,
}

impl ActorStatus {
    /// R-ACTOR-04 / SCHED-BLOCKED-NOT-SCHEDULED.
    pub fn is_schedulable(self) -> bool {
        matches!(self, ActorStatus::Runnable)
    }
}

/// Per-actor FIFO mailbox (R-ACTOR-06). Checked payloads only (R-MARSHAL-01).
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Mailbox {
    messages: VecDeque<Value>,
    /// Recipient reserved capacity slots (R-ACTOR-10 thin M).
    capacity: u64,
}

impl Mailbox {
    pub fn new(capacity: u64) -> Self {
        Self {
            messages: VecDeque::new(),
            capacity,
        }
    }

    pub fn len(&self) -> usize {
        self.messages.len()
    }

    pub fn is_empty(&self) -> bool {
        self.messages.is_empty()
    }

    pub fn capacity(&self) -> u64 {
        self.capacity
    }

    pub fn remaining_capacity(&self) -> u64 {
        self.capacity.saturating_sub(self.messages.len() as u64)
    }

    /// FIFO snapshot for differential observations.
    pub fn as_slice_order(&self) -> Vec<Value> {
        self.messages.iter().cloned().collect()
    }

    pub fn try_enqueue(&mut self, msg: Value) -> Result<(), Fault> {
        if self.messages.len() as u64 >= self.capacity {
            return Err(Fault::ReservedCapacityExceeded);
        }
        self.messages.push_back(msg);
        Ok(())
    }

    pub fn dequeue(&mut self) -> Option<Value> {
        self.messages.pop_front()
    }
}

/// Isolated actor state (R-ACTOR-01).
#[derive(Clone, Debug)]
pub struct ActorState {
    pub id: ActorId,
    pub status: ActorStatus,
    pub env: Environment,
    /// Current control expression (thin single-expr body for M6).
    pub expr: Expr,
    pub mailbox: Mailbox,
    pub caps: CapabilityContext,
    /// Thin consumable budget units (U-03 provisional).
    pub budget_units: u64,
    /// Parent link for spawn lineage tests (optional).
    pub parent: Option<ActorId>,
}

impl ActorState {
    pub fn new(
        id: ActorId,
        expr: Expr,
        caps: CapabilityContext,
        budget_units: u64,
        mailbox_capacity: u64,
        parent: Option<ActorId>,
    ) -> Self {
        Self {
            id,
            status: ActorStatus::Runnable,
            env: Environment::empty(),
            expr,
            mailbox: Mailbox::new(mailbox_capacity),
            caps,
            budget_units,
            parent,
        }
    }
}

/// FIFO runnable queue with at-most-once membership (R-ACTOR-04; M012).
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct RunnableQueue {
    order: VecDeque<ActorId>,
    members: BTreeSet<ActorId>,
}

impl RunnableQueue {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn len(&self) -> usize {
        self.order.len()
    }

    pub fn is_empty(&self) -> bool {
        self.order.is_empty()
    }

    pub fn contains(&self, id: ActorId) -> bool {
        self.members.contains(&id)
    }

    /// Enqueue at back if not already a member. Returns false if duplicate.
    pub fn enqueue_back(&mut self, id: ActorId) -> bool {
        if self.members.contains(&id) {
            return false;
        }
        self.members.insert(id);
        self.order.push_back(id);
        true
    }

    /// Pop front; removes membership.
    pub fn dequeue_front(&mut self) -> Option<ActorId> {
        let id = self.order.pop_front()?;
        self.members.remove(&id);
        Some(id)
    }

    /// Remove id from queue if present (status change).
    pub fn remove(&mut self, id: ActorId) {
        if self.members.remove(&id) {
            self.order.retain(|x| *x != id);
        }
    }

    pub fn as_order(&self) -> Vec<ActorId> {
        self.order.iter().copied().collect()
    }
}

/// Machine event log (U-28 thin minimum).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum MachineEvent {
    ActorSpawned {
        parent: Option<ActorId>,
        child: ActorId,
    },
    MessageSent {
        from: ActorId,
        to: ActorId,
    },
    ActorSelected {
        id: ActorId,
    },
    QuiescenceReconcile {
        pending: Vec<ActorId>,
    },
    EffectIndeterminate {
        actor: ActorId,
    },
    /// Delegation envelope constructed (R-MARSHAL-05).
    DelegationIssued {
        from: ActorId,
        to: ActorId,
        child: CapRef,
    },
    /// Delegation admitted into recipient context after revalidation.
    DelegationAdmitted {
        to: ActorId,
        child: CapRef,
    },
}

/// Global scheduler outcome for one driver step.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum GlobalStep {
    /// One actor transition completed.
    Turn { actor: ActorId },
    /// No runnable actors; no Pending.
    Deadlock,
    /// Deadlock ∧ ∃Pending → QuiescenceReconcile (R-BUDGET-16).
    QuiescenceReconciled { pending: Vec<ActorId> },
}

/// Thin spawn budget request (U-03 provisional).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SpawnBudgetSpec {
    /// Units transferred to child (escrowed from parent).
    pub child_units: u64,
    /// Mailbox capacity for child.
    pub mailbox_capacity: u64,
}

impl SpawnBudgetSpec {
    pub fn new(child_units: u64, mailbox_capacity: u64) -> Self {
        Self {
            child_units,
            mailbox_capacity,
        }
    }
}

/// Global machine state (R-ACTOR-02).
pub struct GlobalState {
    pub actors: BTreeMap<ActorId, ActorState>,
    pub runnable: RunnableQueue,
    pub ids: ActorIdAlloc,
    pub logical_time: LogicalTime,
    pub events: Vec<MachineEvent>,
    /// Default mailbox capacity for root actors.
    pub default_mailbox_capacity: u64,
}

impl Default for GlobalState {
    fn default() -> Self {
        Self::new()
    }
}

impl GlobalState {
    pub fn new() -> Self {
        Self {
            actors: BTreeMap::new(),
            runnable: RunnableQueue::new(),
            ids: ActorIdAlloc::new(),
            logical_time: LogicalTime::ZERO,
            events: Vec::new(),
            default_mailbox_capacity: 64,
        }
    }

    pub fn actor_count(&self) -> usize {
        self.actors.len()
    }

    pub fn has_pending(&self) -> bool {
        self.actors
            .values()
            .any(|a| a.status == ActorStatus::Pending)
    }

    pub fn pending_ids(&self) -> Vec<ActorId> {
        self.actors
            .iter()
            .filter(|(_, a)| a.status == ActorStatus::Pending)
            .map(|(id, _)| *id)
            .collect()
    }

    /// Insert root actor with empty caps (isolated). Enqueues runnable.
    pub fn spawn_root(&mut self, expr: Expr, budget_units: u64) -> ActorId {
        let id = self.ids.allocate();
        let state = ActorState::new(
            id,
            expr,
            CapabilityContext::empty(),
            budget_units,
            self.default_mailbox_capacity,
            None,
        );
        self.actors.insert(id, state);
        self.runnable.enqueue_back(id);
        self.events.push(MachineEvent::ActorSpawned {
            parent: None,
            child: id,
        });
        id
    }

    /// Mark actor Pending (effect wait). Removes from runnable.
    pub fn set_pending(&mut self, id: ActorId) -> Result<(), Fault> {
        let a = self.actors.get_mut(&id).ok_or(Fault::ActorNotFound)?;
        a.status = ActorStatus::Pending;
        self.runnable.remove(id);
        Ok(())
    }

    /// Resume Pending → Runnable after effect receipt (caller supplies).
    pub fn clear_pending_to_runnable(&mut self, id: ActorId) -> Result<(), Fault> {
        let a = self.actors.get_mut(&id).ok_or(Fault::ActorNotFound)?;
        if a.status != ActorStatus::Pending {
            return Ok(());
        }
        a.status = ActorStatus::Runnable;
        self.runnable.enqueue_back(id);
        Ok(())
    }

    pub fn terminate(&mut self, id: ActorId) -> Result<(), Fault> {
        let a = self.actors.get_mut(&id).ok_or(Fault::ActorNotFound)?;
        a.status = ActorStatus::Terminal;
        self.runnable.remove(id);
        Ok(())
    }
}

/// Free function wrappers matching public re-exports.
pub fn spawn_root_in(g: &mut GlobalState, expr: Expr, budget_units: u64) -> ActorId {
    g.spawn_root(expr, budget_units)
}

pub fn set_pending(g: &mut GlobalState, id: ActorId) -> Result<(), Fault> {
    g.set_pending(id)
}

pub fn clear_pending_to_runnable(g: &mut GlobalState, id: ActorId) -> Result<(), Fault> {
    g.clear_pending_to_runnable(id)
}

pub fn finish_empty_runnable_pub(g: &mut GlobalState) -> GlobalStep {
    finish_empty_runnable(g)
}

// --- Marshal (R-MARSHAL-01 / R-CORE-07) ---------------------------------------

/// Recursive capability / closure rejection for ordinary messages.
pub fn machine_contains_capability(v: &Value) -> bool {
    match v {
        Value::Capability(_) | Value::DelegatedCapability(_) => true,
        Value::Function(_) => true, // M6 safety: reject closures in messages
        Value::Constraint(_) => false,
        Value::List(xs) | Value::Tuple(xs) => xs.iter().any(machine_contains_capability),
        Value::Unit
        | Value::Bool(_)
        | Value::Integer(_)
        | Value::Bytes(_)
        | Value::Symbol(_)
        | Value::String(_) => false,
    }
}

/// Ordinary message admission (R-MARSHAL-01).
pub fn marshal_message(v: &Value) -> Result<Value, Fault> {
    if machine_contains_capability(v) {
        return Err(Fault::MarshalCapabilityRejected);
    }
    Ok(v.clone())
}

// --- Spawn (R-ACTOR-05 / R-ACTOR-09) ------------------------------------------

/// Transactional spawn. Default child caps **empty** unless `manifest` provided.
///
/// Manifest entries: `(parent_cap, constraint)` derived via kernel — no wholesale clone.
pub fn spawn_child(
    g: &mut GlobalState,
    kernel: &mut CapabilityKernel,
    parent: ActorId,
    body: Expr,
    budget: SpawnBudgetSpec,
    manifest: &[(CapRef, Constraint)],
) -> Result<ActorId, Fault> {
    let parent_state = g.actors.get(&parent).ok_or(Fault::ActorNotFound)?;
    if parent_state.status == ActorStatus::Terminal {
        return Err(Fault::ActorNotFound);
    }
    // R-ACTOR-09 bounds (U-03 thin): child share ≤ parent residual.
    if budget.child_units > parent_state.budget_units {
        return Err(Fault::BudgetExhausted);
    }
    if budget.mailbox_capacity == 0 {
        return Err(Fault::EffectError {
            reason: "mailbox_capacity_zero",
        });
    }

    let t = g.logical_time;
    let mut child_caps = CapabilityContext::empty();
    let mut derived: Vec<CapRef> = Vec::new();
    for (cap, constraint) in manifest {
        if !parent_state.caps.contains(*cap) {
            for d in &derived {
                let _ = kernel.revoke(*d);
            }
            return Err(Fault::Unauthorized);
        }
        match kernel.derive(*cap, constraint, t) {
            Ok(child_cap) => {
                child_caps.insert(child_cap);
                derived.push(child_cap);
            }
            Err(_) => {
                for d in &derived {
                    let _ = kernel.revoke(*d);
                }
                return Err(Fault::InvalidConstraint);
            }
        }
    }

    // Commit parent budget escrow then allocate (journal-free thin M6).
    let parent_state = g.actors.get_mut(&parent).ok_or(Fault::ActorNotFound)?;
    parent_state.budget_units = parent_state.budget_units.saturating_sub(budget.child_units);

    let child_id = g.ids.allocate();
    let child = ActorState::new(
        child_id,
        body,
        child_caps,
        budget.child_units,
        budget.mailbox_capacity,
        Some(parent),
    );
    g.actors.insert(child_id, child);
    g.runnable.enqueue_back(child_id);
    g.events.push(MachineEvent::ActorSpawned {
        parent: Some(parent),
        child: child_id,
    });
    // δ_t(spawn)=0 — no logical time advance (R-BUDGET-16).
    Ok(child_id)
}

// --- Delegation (R-MARSHAL-05) ------------------------------------------------

/// Construct a kernel-derived delegation envelope for `to`.
///
/// Does **not** insert into recipient context — that requires
/// [`admit_delegation`] with revalidation. Ordinary Send still rejects the
/// envelope via marshal (DelegatedCapability is capability-bearing).
pub fn issue_delegation(
    g: &mut GlobalState,
    kernel: &mut CapabilityKernel,
    from: ActorId,
    to: ActorId,
    parent_cap: CapRef,
    constraint: &Constraint,
) -> Result<DelegatedCapability, Fault> {
    let parent_state = g.actors.get(&from).ok_or(Fault::ActorNotFound)?;
    if parent_state.status == ActorStatus::Terminal {
        return Err(Fault::ActorNotFound);
    }
    if !parent_state.caps.contains(parent_cap) {
        return Err(Fault::Unauthorized);
    }
    if !g.actors.contains_key(&to) {
        return Err(Fault::ActorNotFound);
    }
    let child = kernel
        .derive(parent_cap, constraint, g.logical_time)
        .map_err(|_| Fault::InvalidConstraint)?;
    let envelope = DelegatedCapability::from_derived(child, to.0);
    g.events
        .push(MachineEvent::DelegationIssued { from, to, child });
    Ok(envelope)
}

/// Receive-side admission: revalidate envelope then insert child into recipient.
///
/// On any fault the recipient CapabilityContext is left byte-identical
/// (R-MARSHAL-05).
pub fn admit_delegation(
    g: &mut GlobalState,
    kernel: &mut CapabilityKernel,
    recipient: ActorId,
    envelope: &DelegatedCapability,
) -> Result<(), Fault> {
    let before_slots = g
        .actors
        .get(&recipient)
        .ok_or(Fault::ActorNotFound)?
        .caps
        .slots()
        .to_vec();

    let fail = |g: &mut GlobalState, before: Vec<CapRef>| -> Result<(), Fault> {
        // Restore byte-identical context on fault.
        if let Some(a) = g.actors.get_mut(&recipient) {
            a.caps = CapabilityContext::empty();
            for c in before {
                a.caps.insert(c);
            }
        }
        Err(Fault::Unauthorized)
    };

    if envelope.target_actor() != recipient.0 {
        return fail(g, before_slots);
    }
    let child = envelope.child_cap();
    if !kernel.valid(child, g.logical_time) {
        return fail(g, before_slots);
    }
    // Lineage: parent of child must exist (derived).
    if kernel.parent_of(child).is_none() {
        return fail(g, before_slots);
    }

    let a = g.actors.get_mut(&recipient).ok_or(Fault::ActorNotFound)?;
    a.caps.insert(child);
    g.events.push(MachineEvent::DelegationAdmitted {
        to: recipient,
        child,
    });
    Ok(())
}

/// Deliver a delegation envelope to a target actor's mailbox as a dedicated
/// path (not ordinary marshal). On receive, the scheduler admits via
/// [`admit_delegation`].
///
/// Thin M6: store as `Value::DelegatedCapability` in mailbox **only** through
/// this API (bypasses ordinary marshal reject). Receive transition detects it
/// and runs admission instead of treating it as data.
pub fn send_delegation(
    g: &mut GlobalState,
    from: ActorId,
    to: ActorId,
    envelope: DelegatedCapability,
) -> Result<(), Fault> {
    if !g.actors.contains_key(&from) {
        return Err(Fault::ActorNotFound);
    }
    {
        let target = g.actors.get(&to).ok_or(Fault::ActorNotFound)?;
        if target.status == ActorStatus::Terminal {
            return Err(Fault::ActorNotFound);
        }
        if target.mailbox.remaining_capacity() == 0 {
            return Err(Fault::ReservedCapacityExceeded);
        }
        if envelope.target_actor() != to.0 {
            return Err(Fault::Unauthorized);
        }
    }
    let target = g.actors.get_mut(&to).ok_or(Fault::ActorNotFound)?;
    let was_blocked = target.status == ActorStatus::Blocked;
    // Dedicated path: enqueue DelegatedCapability without ordinary marshal.
    target
        .mailbox
        .try_enqueue(Value::DelegatedCapability(envelope))?;
    if was_blocked {
        target.status = ActorStatus::Runnable;
        g.runnable.enqueue_back(to);
    }
    g.events.push(MachineEvent::MessageSent { from, to });
    Ok(())
}

// --- Send / Receive (R-ACTOR-06 / R-ACTOR-10) ---------------------------------

/// Asynchronous send: marshal → admit → enqueue → wake blocked target once.
pub fn send_async(
    g: &mut GlobalState,
    from: ActorId,
    to: ActorId,
    message: Value,
) -> Result<(), Fault> {
    if !g.actors.contains_key(&from) {
        return Err(Fault::ActorNotFound);
    }
    let marshalled = marshal_message(&message)?;
    {
        let target = g.actors.get(&to).ok_or(Fault::ActorNotFound)?;
        if target.status == ActorStatus::Terminal {
            return Err(Fault::ActorNotFound);
        }
        if target.mailbox.remaining_capacity() == 0 {
            return Err(Fault::ReservedCapacityExceeded);
        }
    }
    let target = g.actors.get_mut(&to).ok_or(Fault::ActorNotFound)?;
    let was_blocked = target.status == ActorStatus::Blocked;
    target.mailbox.try_enqueue(marshalled)?;
    if was_blocked {
        target.status = ActorStatus::Runnable;
        // Wake exactly once at back (deterministic).
        g.runnable.enqueue_back(to);
    }
    g.events.push(MachineEvent::MessageSent { from, to });
    // δ_t(send)=0
    Ok(())
}

/// Blocking receive: dequeue or Block without fuel.
pub fn receive_or_block(g: &mut GlobalState, id: ActorId) -> Result<Option<Value>, Fault> {
    let actor = g.actors.get_mut(&id).ok_or(Fault::ActorNotFound)?;
    if let Some(msg) = actor.mailbox.dequeue() {
        return Ok(Some(msg));
    }
    // Empty → Blocked; remove from runnable; no fuel (R-ACTOR-06).
    actor.status = ActorStatus::Blocked;
    g.runnable.remove(id);
    Ok(None)
}

// --- Scheduler (R-ACTOR-04) ---------------------------------------------------

/// One scheduler turn: select FIFO head if schedulable; run one transition.
pub fn scheduler_turn(
    g: &mut GlobalState,
    kernel: &mut CapabilityKernel,
) -> Result<GlobalStep, Fault> {
    // Skip non-schedulable heads (defensive; enqueue discipline should prevent).
    loop {
        let Some(id) = g.runnable.dequeue_front() else {
            return Ok(finish_empty_runnable(g));
        };
        let status = g
            .actors
            .get(&id)
            .map(|a| a.status)
            .ok_or(Fault::ActorNotFound)?;
        if !status.is_schedulable() {
            // Drop stale queue entry (should not happen under discipline).
            continue;
        }
        g.events.push(MachineEvent::ActorSelected { id });
        run_one_transition(g, kernel, id)?;
        // δ_t carried by transition: pure/spawn/send/receive/blocked = 0.
        return Ok(GlobalStep::Turn { actor: id });
    }
}

fn finish_empty_runnable(g: &mut GlobalState) -> GlobalStep {
    if g.has_pending() {
        // QuiescenceReconcile: δ_t=0, ΔD=0, no budget mutation.
        let pending = g.pending_ids();
        for id in &pending {
            // Record Indeterminate binding (thin R-RECOV-08); keep Pending status
            // (do not cancel / NotExecuted).
            g.events
                .push(MachineEvent::EffectIndeterminate { actor: *id });
        }
        g.events.push(MachineEvent::QuiescenceReconcile {
            pending: pending.clone(),
        });
        GlobalStep::QuiescenceReconciled { pending }
    } else {
        GlobalStep::Deadlock
    }
}

fn run_one_transition(
    g: &mut GlobalState,
    kernel: &mut CapabilityKernel,
    id: ActorId,
) -> Result<(), Fault> {
    let expr = g.actors.get(&id).ok_or(Fault::ActorNotFound)?.expr.clone();
    match expr {
        Expr::Receive => {
            match receive_or_block(g, id)? {
                Some(Value::DelegatedCapability(env)) => {
                    // Dedicated admission path (R-MARSHAL-05).
                    admit_delegation(g, kernel, id, &env)?;
                    if let Some(a) = g.actors.get_mut(&id) {
                        a.expr = Expr::Value(Value::Unit);
                        if a.status == ActorStatus::Runnable {
                            g.runnable.enqueue_back(id);
                        }
                    }
                }
                Some(_msg) => {
                    // Ordinary data message: leave Runnable; body becomes Unit (thin).
                    if let Some(a) = g.actors.get_mut(&id) {
                        a.expr = Expr::Value(Value::Unit);
                        if a.status == ActorStatus::Runnable {
                            g.runnable.enqueue_back(id);
                        }
                    }
                }
                None => {
                    // Now Blocked — not re-enqueued.
                }
            }
        }
        Expr::Delegate {
            capability,
            constraint,
            target,
        } => {
            // Thin: capability/constraint/target as already-evaluated Values in expr
            // positions (or Value literals). Full CEK eval of subexprs is deferred;
            // actor-turn form expects Value leaves.
            let parent_cap = match *capability {
                Expr::Value(Value::Capability(c)) => c,
                _ => {
                    return Err(Fault::TypeError {
                        expected: "Capability",
                        actual: "other",
                    })
                }
            };
            let c = match *constraint {
                Expr::Value(Value::Constraint(c)) => c,
                _ => {
                    return Err(Fault::TypeError {
                        expected: "Constraint",
                        actual: "other",
                    })
                }
            };
            let to = eval_actor_id_expr(&target)?;
            let envelope = issue_delegation(g, kernel, id, to, parent_cap, &c)?;
            send_delegation(g, id, to, envelope)?;
            if let Some(a) = g.actors.get_mut(&id) {
                a.expr = Expr::Value(Value::Unit);
                if a.status == ActorStatus::Runnable {
                    g.runnable.enqueue_back(id);
                }
            }
        }
        Expr::Value(_) => {
            // Halt-like: terminal after observing value (thin Halt support).
            g.terminate(id)?;
        }
        Expr::Spawn {
            expr: child_body,
            initial_budget,
            capabilities: _,
        } => {
            // Thin: initial_budget as Integer units; empty manifest (default empty caps).
            let units = match *initial_budget {
                Expr::Value(Value::Integer(n)) if n >= 0 => n as u64,
                _ => {
                    return Err(Fault::TypeError {
                        expected: "Integer(budget)",
                        actual: "other",
                    })
                }
            };
            let cap = g
                .actors
                .get(&id)
                .map(|a| a.mailbox.capacity())
                .unwrap_or(64);
            let spec = SpawnBudgetSpec::new(units, cap);
            spawn_child(g, kernel, id, *child_body, spec, &[])?;
            if let Some(a) = g.actors.get_mut(&id) {
                a.expr = Expr::Value(Value::Unit);
                if a.status == ActorStatus::Runnable {
                    g.runnable.enqueue_back(id);
                }
            }
        }
        Expr::Send { target, message } => {
            let to = eval_actor_id_expr(&target)?;
            let msg = eval_value_expr(&message)?;
            send_async(g, id, to, msg)?;
            if let Some(a) = g.actors.get_mut(&id) {
                a.expr = Expr::Value(Value::Unit);
                if a.status == ActorStatus::Runnable {
                    g.runnable.enqueue_back(id);
                }
            }
        }
        other => {
            // One pure CEK step for non-actor forms (Let/Seq/…).
            let mut state = crate::cek::EvalState::with_env(
                other,
                g.actors.get(&id).map(|a| a.env.clone()).unwrap_or_default(),
            )
            .at_time(g.logical_time);
            match crate::cek::step(&mut state, kernel) {
                crate::cek::StepResult::Continue => {
                    if let Some(a) = g.actors.get_mut(&id) {
                        a.expr = state.expr;
                        a.env = state.env;
                        if a.status == ActorStatus::Runnable {
                            g.runnable.enqueue_back(id);
                        }
                    }
                }
                crate::cek::StepResult::Halted(v) => {
                    if let Some(a) = g.actors.get_mut(&id) {
                        a.expr = Expr::Value(v);
                        a.env = state.env;
                        if a.status == ActorStatus::Runnable {
                            g.runnable.enqueue_back(id);
                        }
                    }
                }
                crate::cek::StepResult::Fault(f) => {
                    g.terminate(id)?;
                    return Err(f);
                }
            }
        }
    }
    Ok(())
}

fn eval_actor_id_expr(e: &Expr) -> Result<ActorId, Fault> {
    match e {
        Expr::Value(Value::Integer(n)) if *n >= 0 => Ok(ActorId(*n as u64)),
        _ => Err(Fault::TypeError {
            expected: "Integer(ActorId)",
            actual: "other",
        }),
    }
}

fn eval_value_expr(e: &Expr) -> Result<Value, Fault> {
    match e {
        Expr::Value(v) => Ok(v.clone()),
        _ => Err(Fault::TypeError {
            expected: "Value",
            actual: "expr",
        }),
    }
}

/// Drive until Deadlock or QuiescenceReconcile or step limit.
pub fn run_until_quiescent(
    g: &mut GlobalState,
    kernel: &mut CapabilityKernel,
    max_turns: u64,
) -> Result<GlobalStep, Fault> {
    let mut last = GlobalStep::Deadlock;
    for _ in 0..max_turns {
        last = scheduler_turn(g, kernel)?;
        match &last {
            GlobalStep::Deadlock | GlobalStep::QuiescenceReconciled { .. } => return Ok(last),
            GlobalStep::Turn { .. } => continue,
        }
    }
    Ok(last)
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::capability::{Lifetime, Op};
    use ror_core::machine::sugar::{int, receive, unit};
    use ror_core::machine::FunctionValue;
    use ror_kernel::{single_op_authority, single_op_constraint, CapabilityKernel};

    #[test]
    fn actor_id_monotonic_no_reuse() {
        let mut a = ActorIdAlloc::new();
        assert_eq!(a.allocate(), ActorId(0));
        assert_eq!(a.allocate(), ActorId(1));
        assert_eq!(a.allocate(), ActorId(2));
        assert_eq!(a.peek_next(), 3);
    }

    #[test]
    fn mailbox_fifo() {
        let mut m = Mailbox::new(8);
        m.try_enqueue(Value::Integer(1)).unwrap();
        m.try_enqueue(Value::Integer(2)).unwrap();
        m.try_enqueue(Value::Integer(3)).unwrap();
        assert_eq!(m.dequeue(), Some(Value::Integer(1)));
        assert_eq!(m.dequeue(), Some(Value::Integer(2)));
        assert_eq!(m.dequeue(), Some(Value::Integer(3)));
        assert!(m.dequeue().is_none());
    }

    #[test]
    fn mailbox_capacity_sender_pays() {
        let mut m = Mailbox::new(1);
        m.try_enqueue(Value::Unit).unwrap();
        assert_eq!(
            m.try_enqueue(Value::Unit),
            Err(Fault::ReservedCapacityExceeded)
        );
    }

    #[test]
    fn marshal_rejects_capability() {
        let cap = Value::Capability(CapRef::from_kernel_parts(0, 0));
        assert_eq!(marshal_message(&cap), Err(Fault::MarshalCapabilityRejected));
        let nested = Value::List(vec![Value::Integer(1), cap]);
        assert_eq!(
            marshal_message(&nested),
            Err(Fault::MarshalCapabilityRejected)
        );
        assert!(marshal_message(&Value::Integer(7)).is_ok());
    }

    #[test]
    fn marshal_rejects_function() {
        let f = Value::Function(FunctionValue {
            params: vec![],
            body: Box::new(unit()),
            env: Environment::empty(),
        });
        assert_eq!(marshal_message(&f), Err(Fault::MarshalCapabilityRejected));
    }

    #[test]
    fn runnable_at_most_once() {
        let mut q = RunnableQueue::new();
        assert!(q.enqueue_back(ActorId(1)));
        assert!(!q.enqueue_back(ActorId(1)));
        assert_eq!(q.len(), 1);
        assert_eq!(q.dequeue_front(), Some(ActorId(1)));
        assert!(q.is_empty());
    }

    #[test]
    fn scheduler_fifo_order() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let a = g.spawn_root(unit(), 10);
        let b = g.spawn_root(unit(), 10);
        let c = g.spawn_root(unit(), 10);
        assert_eq!(a, ActorId(0));
        assert_eq!(b, ActorId(1));
        assert_eq!(c, ActorId(2));
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Turn { actor: a }
        );
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Turn { actor: b }
        );
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Turn { actor: c }
        );
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Deadlock
        );
    }

    #[test]
    fn blocked_not_scheduled() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let a = g.spawn_root(receive(), 10);
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Turn { actor: a }
        );
        assert_eq!(g.actors.get(&a).unwrap().status, ActorStatus::Blocked);
        assert!(g.runnable.is_empty());
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Deadlock
        );
    }

    #[test]
    fn pending_not_scheduled_and_survives_deadlock_observation() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let a = g.spawn_root(unit(), 10);
        g.set_pending(a).unwrap();
        assert!(!g.runnable.contains(a));
        let step = scheduler_turn(&mut g, &mut k).unwrap();
        match step {
            GlobalStep::QuiescenceReconciled { pending } => {
                assert_eq!(pending, vec![a]);
            }
            other => panic!("expected quiescence, got {other:?}"),
        }
        assert_eq!(g.actors.get(&a).unwrap().status, ActorStatus::Pending);
        assert_eq!(g.actors.get(&a).unwrap().budget_units, 10);
    }

    #[test]
    fn send_wakes_blocked_receiver_once() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let recv = g.spawn_root(receive(), 10);
        let _ = scheduler_turn(&mut g, &mut k).unwrap();
        assert_eq!(g.actors.get(&recv).unwrap().status, ActorStatus::Blocked);
        let sender = g.spawn_root(unit(), 10);
        send_async(&mut g, sender, recv, Value::Integer(42)).unwrap();
        assert_eq!(g.actors.get(&recv).unwrap().status, ActorStatus::Runnable);
        assert!(g.runnable.contains(recv));
        send_async(&mut g, sender, recv, Value::Integer(43)).unwrap();
        assert_eq!(
            g.runnable.as_order().iter().filter(|&&x| x == recv).count(),
            1
        );
    }

    #[test]
    fn send_rejects_capability() {
        let mut g = GlobalState::new();
        let a = g.spawn_root(unit(), 10);
        let b = g.spawn_root(receive(), 10);
        let err = send_async(
            &mut g,
            a,
            b,
            Value::Capability(CapRef::from_kernel_parts(0, 0)),
        );
        assert_eq!(err, Err(Fault::MarshalCapabilityRejected));
        assert!(g.actors.get(&b).unwrap().mailbox.is_empty());
    }

    #[test]
    fn spawn_transactional_empty_default_caps() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let p = g.spawn_root(unit(), 100);
        let child =
            spawn_child(&mut g, &mut k, p, unit(), SpawnBudgetSpec::new(10, 8), &[]).unwrap();
        assert_eq!(child, ActorId(1));
        assert!(g.actors.get(&child).unwrap().caps.slots().is_empty());
        assert_eq!(g.actors.get(&p).unwrap().budget_units, 90);
        assert_eq!(g.actors.get(&child).unwrap().budget_units, 10);
    }

    #[test]
    fn spawn_budget_fail_no_partial() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let p = g.spawn_root(unit(), 5);
        let before = g.actor_count();
        let err = spawn_child(&mut g, &mut k, p, unit(), SpawnBudgetSpec::new(10, 8), &[]);
        assert_eq!(err, Err(Fault::BudgetExhausted));
        assert_eq!(g.actor_count(), before);
        assert_eq!(g.ids.peek_next(), 1);
    }

    #[test]
    fn spawn_with_manifest_attenuates() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let auth = single_op_authority(Op::FileRead, vec![1, 2, 3], 100, Lifetime::always());
        let parent_cap = k.grant_root_always(auth);
        let mut caps = CapabilityContext::empty();
        caps.insert(parent_cap);
        let p = g.ids.allocate();
        g.actors
            .insert(p, ActorState::new(p, unit(), caps, 100, 16, None));
        g.runnable.enqueue_back(p);
        let c = single_op_constraint(Op::FileRead, vec![1], 10, Lifetime::always());
        let child = spawn_child(
            &mut g,
            &mut k,
            p,
            unit(),
            SpawnBudgetSpec::new(5, 8),
            &[(parent_cap, c)],
        )
        .unwrap();
        let child_state = g.actors.get(&child).unwrap();
        assert!(!child_state.caps.slots().is_empty());
        let child_cap = child_state.caps.slots()[0];
        assert_ne!(child_cap, parent_cap);
        assert!(k.valid(child_cap, LogicalTime::ZERO));
        let ca = k.authority_snapshot(child_cap).unwrap();
        let pa = k.authority_snapshot(parent_cap).unwrap();
        assert!(ca.leq(&pa));
    }

    #[test]
    fn terminal_not_scheduled() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let a = g.spawn_root(unit(), 1);
        g.terminate(a).unwrap();
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Deadlock
        );
    }

    #[test]
    fn determinism_repeated_schedule() {
        fn run() -> Vec<ActorId> {
            let mut g = GlobalState::new();
            let mut k = CapabilityKernel::new();
            g.spawn_root(unit(), 1);
            g.spawn_root(unit(), 1);
            g.spawn_root(unit(), 1);
            let mut order = Vec::new();
            for _ in 0..3 {
                if let GlobalStep::Turn { actor } = scheduler_turn(&mut g, &mut k).unwrap() {
                    order.push(actor);
                }
            }
            order
        }
        assert_eq!(run(), run());
        assert_eq!(run(), vec![ActorId(0), ActorId(1), ActorId(2)]);
    }

    #[test]
    fn mutation_intent_fifo_order() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let a = g.spawn_root(unit(), 1);
        let b = g.spawn_root(unit(), 1);
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Turn { actor: a }
        );
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Turn { actor: b }
        );
    }

    #[test]
    fn mutation_intent_no_schedule_blocked() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let a = g.spawn_root(receive(), 1);
        let _ = scheduler_turn(&mut g, &mut k).unwrap();
        assert_eq!(g.actors.get(&a).unwrap().status, ActorStatus::Blocked);
        g.runnable.enqueue_back(a);
        let step = scheduler_turn(&mut g, &mut k).unwrap();
        assert_eq!(step, GlobalStep::Deadlock);
    }

    #[test]
    fn mutation_intent_duplicate_runnable_killed() {
        let mut q = RunnableQueue::new();
        assert!(q.enqueue_back(ActorId(0)));
        assert!(!q.enqueue_back(ActorId(0)));
        assert_eq!(q.len(), 1);
    }

    #[test]
    fn mutation_intent_cap_message_killed() {
        let mut g = GlobalState::new();
        let a = g.spawn_root(unit(), 1);
        let b = g.spawn_root(unit(), 1);
        assert!(send_async(
            &mut g,
            a,
            b,
            Value::Capability(CapRef::from_kernel_parts(1, 0))
        )
        .is_err());
    }

    #[test]
    fn mutation_intent_no_host_from_actor_module() {
        let mut g = GlobalState::new();
        let a = g.spawn_root(unit(), 1);
        let b = g.spawn_root(receive(), 1);
        send_async(&mut g, a, b, Value::Integer(1)).unwrap();
        assert_eq!(
            g.events
                .iter()
                .filter(|e| matches!(e, MachineEvent::MessageSent { .. }))
                .count(),
            1
        );
    }

    #[test]
    fn mutation_intent_quiescence_no_budget_mutation() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let a = g.spawn_root(unit(), 42);
        g.set_pending(a).unwrap();
        let before = g.actors.get(&a).unwrap().budget_units;
        let _ = scheduler_turn(&mut g, &mut k).unwrap();
        assert_eq!(g.actors.get(&a).unwrap().budget_units, before);
        assert_eq!(g.actors.get(&a).unwrap().status, ActorStatus::Pending);
    }

    #[test]
    fn receive_then_message_dequeues_fifo() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let r = g.spawn_root(receive(), 10);
        // First turn: r blocks on empty mailbox.
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Turn { actor: r }
        );
        assert_eq!(g.actors.get(&r).unwrap().status, ActorStatus::Blocked);
        // Sender is not on the runnable queue (spawned only for identity).
        let s = {
            let id = g.ids.allocate();
            g.actors.insert(
                id,
                ActorState::new(id, unit(), CapabilityContext::empty(), 10, 64, None),
            );
            // Terminal immediately — not enqueued.
            g.actors.get_mut(&id).unwrap().status = ActorStatus::Terminal;
            id
        };
        send_async(&mut g, s, r, Value::Integer(1)).unwrap();
        send_async(&mut g, s, r, Value::Integer(2)).unwrap();
        // r woken once; next turn is r and dequeues first message.
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Turn { actor: r }
        );
        assert_eq!(
            g.actors.get(&r).unwrap().mailbox.as_slice_order(),
            vec![Value::Integer(2)]
        );
    }

    #[test]
    fn spawn_expr_via_turn() {
        use ror_core::machine::sugar::spawn;
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let body = spawn(unit(), int(5), vec![]);
        let p = g.spawn_root(body, 20);
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Turn { actor: p }
        );
        assert_eq!(g.actor_count(), 2);
        assert_eq!(g.actors.get(&p).unwrap().budget_units, 15);
    }

    #[test]
    fn mutation_intent_spawn_no_cap_clone() {
        // Empty manifest → empty child caps even if parent holds caps.
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let auth = single_op_authority(Op::FileRead, vec![1], 10, Lifetime::always());
        let parent_cap = k.grant_root_always(auth);
        let mut caps = CapabilityContext::empty();
        caps.insert(parent_cap);
        let p = g.ids.allocate();
        g.actors
            .insert(p, ActorState::new(p, unit(), caps, 100, 16, None));
        let child =
            spawn_child(&mut g, &mut k, p, unit(), SpawnBudgetSpec::new(1, 4), &[]).unwrap();
        assert!(g.actors.get(&child).unwrap().caps.slots().is_empty());
    }

    #[test]
    fn delegation_issue_and_admit() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let auth = single_op_authority(Op::FileRead, vec![1, 2], 50, Lifetime::always());
        let parent_cap = k.grant_root_always(auth);
        let mut caps = CapabilityContext::empty();
        caps.insert(parent_cap);
        let from = g.ids.allocate();
        g.actors
            .insert(from, ActorState::new(from, unit(), caps, 10, 16, None));
        let to = g.spawn_root(receive(), 10);
        let c = single_op_constraint(Op::FileRead, vec![1], 5, Lifetime::always());
        let env = issue_delegation(&mut g, &mut k, from, to, parent_cap, &c).unwrap();
        // Ordinary send rejects envelope.
        assert_eq!(
            send_async(&mut g, from, to, Value::DelegatedCapability(env.clone())),
            Err(Fault::MarshalCapabilityRejected)
        );
        // Dedicated path delivers.
        send_delegation(&mut g, from, to, env).unwrap();
        // Receiver was not blocked yet (still runnable with receive); turn admits.
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Turn { actor: to }
        );
        assert!(!g.actors.get(&to).unwrap().caps.slots().is_empty());
        let child = g.actors.get(&to).unwrap().caps.slots()[0];
        assert!(k.valid(child, LogicalTime::ZERO));
        assert!(k
            .authority_snapshot(child)
            .unwrap()
            .leq(&k.authority_snapshot(parent_cap).unwrap()));
    }

    #[test]
    fn delegation_wrong_target_leaves_ctx_identical() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let auth = single_op_authority(Op::FileRead, vec![1], 10, Lifetime::always());
        let parent_cap = k.grant_root_always(auth);
        let mut caps = CapabilityContext::empty();
        caps.insert(parent_cap);
        let from = g.ids.allocate();
        g.actors
            .insert(from, ActorState::new(from, unit(), caps, 10, 16, None));
        let to = g.spawn_root(unit(), 10);
        let c = single_op_constraint(Op::FileRead, vec![1], 5, Lifetime::always());
        let env = issue_delegation(&mut g, &mut k, from, to, parent_cap, &c).unwrap();
        // Admit against wrong recipient.
        let other = g.spawn_root(unit(), 10);
        let before = g.actors.get(&other).unwrap().caps.slots().to_vec();
        assert!(admit_delegation(&mut g, &mut k, other, &env).is_err());
        assert_eq!(g.actors.get(&other).unwrap().caps.slots(), &before[..]);
    }

    #[test]
    fn ordinary_send_still_rejects_delegated_cap_value() {
        let mut g = GlobalState::new();
        let a = g.spawn_root(unit(), 1);
        let b = g.spawn_root(unit(), 1);
        let env = DelegatedCapability::provisional(0, 0);
        assert_eq!(
            send_async(&mut g, a, b, Value::DelegatedCapability(env)),
            Err(Fault::MarshalCapabilityRejected)
        );
    }

    // --- Addendum matrix coverage (M6-C) ------------------------------------

    /// T01/T02/T03 property: uniqueness + monotonic + no reuse across many allocs.
    #[test]
    fn property_actor_id_unique_monotonic_no_reuse() {
        let mut a = ActorIdAlloc::new();
        let mut seen = BTreeSet::new();
        let mut prev = None;
        for _ in 0..256 {
            let id = a.allocate();
            assert!(seen.insert(id), "reuse {id:?}");
            if let Some(p) = prev {
                assert!(id.0 > p, "non-monotonic {p} -> {}", id.0);
            }
            prev = Some(id.0);
        }
        // No recycling API: peek continues past last.
        assert_eq!(a.peek_next(), 256);
    }

    /// T04: actor creation isolates env and starts Runnable on queue.
    #[test]
    fn actor_creation_isolated_runnable() {
        let mut g = GlobalState::new();
        let a = g.spawn_root(unit(), 3);
        let st = g.actors.get(&a).unwrap();
        assert_eq!(st.status, ActorStatus::Runnable);
        assert!(st.env.is_empty());
        assert!(st.caps.slots().is_empty());
        assert!(st.mailbox.is_empty());
        assert!(g.runnable.contains(a));
        assert_eq!(st.parent, None);
    }

    /// T09: multiple senders preserve per-mailbox FIFO (not global total order).
    #[test]
    fn multiple_senders_mailbox_fifo() {
        let mut g = GlobalState::new();
        let r = g.spawn_root(receive(), 10);
        let s1 = {
            let id = g.ids.allocate();
            g.actors.insert(
                id,
                ActorState::new(id, unit(), CapabilityContext::empty(), 1, 64, None),
            );
            g.actors.get_mut(&id).unwrap().status = ActorStatus::Terminal;
            id
        };
        let s2 = {
            let id = g.ids.allocate();
            g.actors.insert(
                id,
                ActorState::new(id, unit(), CapabilityContext::empty(), 1, 64, None),
            );
            g.actors.get_mut(&id).unwrap().status = ActorStatus::Terminal;
            id
        };
        send_async(&mut g, s1, r, Value::Integer(1)).unwrap();
        send_async(&mut g, s2, r, Value::Integer(2)).unwrap();
        send_async(&mut g, s1, r, Value::Integer(3)).unwrap();
        assert_eq!(
            g.actors.get(&r).unwrap().mailbox.as_slice_order(),
            vec![Value::Integer(1), Value::Integer(2), Value::Integer(3)]
        );
    }

    /// T18: one transition per scheduler turn (selection event count == turns).
    #[test]
    fn one_transition_per_turn() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        g.spawn_root(unit(), 1);
        g.spawn_root(unit(), 1);
        let before = g
            .events
            .iter()
            .filter(|e| matches!(e, MachineEvent::ActorSelected { .. }))
            .count();
        let _ = scheduler_turn(&mut g, &mut k).unwrap();
        let mid = g
            .events
            .iter()
            .filter(|e| matches!(e, MachineEvent::ActorSelected { .. }))
            .count();
        assert_eq!(mid, before + 1);
        let _ = scheduler_turn(&mut g, &mut k).unwrap();
        let after = g
            .events
            .iter()
            .filter(|e| matches!(e, MachineEvent::ActorSelected { .. }))
            .count();
        assert_eq!(after, mid + 1);
    }

    /// T23/T24: GlobalStep Deadlock without Pending is pure Deadlock.
    #[test]
    fn deadlock_without_pending() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Deadlock
        );
        // With only terminal actors:
        let a = g.spawn_root(unit(), 1);
        g.terminate(a).unwrap();
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Deadlock
        );
        assert!(!g.events.iter().any(|e| matches!(
            e,
            MachineEvent::QuiescenceReconcile { .. } | MachineEvent::EffectIndeterminate { .. }
        )));
    }

    /// T25–T31: Deadlock∧Pending → Quiescence; Indeterminate; δ_t=0; no budget mut; Pending survives.
    #[test]
    fn quiescence_indeterminate_no_time_or_budget_mut() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let a = g.spawn_root(unit(), 99);
        g.set_pending(a).unwrap();
        let t_before = g.logical_time;
        let b_before = g.actors.get(&a).unwrap().budget_units;
        let step = scheduler_turn(&mut g, &mut k).unwrap();
        match step {
            GlobalStep::QuiescenceReconciled { pending } => assert_eq!(pending, vec![a]),
            other => panic!("{other:?}"),
        }
        assert_eq!(g.logical_time, t_before); // δ_t = 0
        assert_eq!(g.actors.get(&a).unwrap().budget_units, b_before); // ΔD/budget = 0
        assert_eq!(g.actors.get(&a).unwrap().status, ActorStatus::Pending); // survives
        assert!(g.events.iter().any(|e| matches!(
            e,
            MachineEvent::EffectIndeterminate { actor } if *actor == a
        )));
        // Deadlock alone does not mutate actor status (already Pending).
        assert!(!matches!(
            g.actors.get(&a).unwrap().status,
            ActorStatus::Terminal | ActorStatus::Runnable | ActorStatus::Blocked
        ));
    }

    /// T20 mutation: select pending killed (defensive skip → Quiescence/Deadlock path).
    #[test]
    fn mutation_intent_no_schedule_pending() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let a = g.spawn_root(unit(), 1);
        g.set_pending(a).unwrap();
        // Illegal enqueue of pending.
        g.runnable.enqueue_back(a);
        let step = scheduler_turn(&mut g, &mut k).unwrap();
        // Stale head dropped; empty → QuiescenceReconciled (still has Pending).
        assert!(matches!(step, GlobalStep::QuiescenceReconciled { .. }));
        assert_eq!(g.actors.get(&a).unwrap().status, ActorStatus::Pending);
    }

    /// T21 mutation: select terminal killed.
    #[test]
    fn mutation_intent_no_schedule_terminal() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let a = g.spawn_root(unit(), 1);
        g.terminate(a).unwrap();
        g.runnable.enqueue_back(a);
        assert_eq!(
            scheduler_turn(&mut g, &mut k).unwrap(),
            GlobalStep::Deadlock
        );
    }

    /// MUT-09: ActorId reuse not available — allocator never returns prior id.
    #[test]
    fn mutation_intent_actor_id_reuse_impossible() {
        let mut a = ActorIdAlloc::new();
        let first = a.allocate();
        let _ = a.allocate();
        // No free/recycle API on ActorIdAlloc.
        assert_ne!(a.allocate(), first);
        assert!(a.peek_next() > first.0);
    }

    /// MUT-12/15: Deadlock observation does not cancel Pending → NotExecuted.
    #[test]
    fn mutation_intent_pending_not_cancelled_on_deadlock() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let a = g.spawn_root(unit(), 5);
        g.set_pending(a).unwrap();
        let _ = scheduler_turn(&mut g, &mut k).unwrap();
        // Still Pending (not Terminal, not dropped).
        assert_eq!(g.actors.get(&a).unwrap().status, ActorStatus::Pending);
        assert!(g.actors.contains_key(&a));
    }

    /// MUT-13: logical time not advanced by QuiescenceReconcile.
    #[test]
    fn mutation_intent_no_time_advance_on_quiescence() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        g.logical_time = LogicalTime::new(7);
        let a = g.spawn_root(unit(), 1);
        g.set_pending(a).unwrap();
        let _ = scheduler_turn(&mut g, &mut k).unwrap();
        assert_eq!(g.logical_time, LogicalTime::new(7));
    }

    /// T15: nested capability in tuple rejected.
    #[test]
    fn nested_capability_in_tuple_rejected() {
        let nested = Value::Tuple(vec![
            Value::Integer(1),
            Value::List(vec![Value::Capability(CapRef::from_kernel_parts(0, 0))]),
        ]);
        assert_eq!(
            marshal_message(&nested),
            Err(Fault::MarshalCapabilityRejected)
        );
    }

    /// T10: async send does not block sender; receiver may still be blocked until wake.
    #[test]
    fn async_send_nonblocking_sender() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        let r = g.spawn_root(receive(), 10);
        let _ = scheduler_turn(&mut g, &mut k).unwrap(); // r blocked
        let s = g.spawn_root(unit(), 10);
        // Send succeeds while r is blocked; s remains runnable until its turn.
        send_async(&mut g, s, r, Value::Integer(9)).unwrap();
        assert_eq!(g.actors.get(&s).unwrap().status, ActorStatus::Runnable);
        assert_eq!(g.actors.get(&r).unwrap().status, ActorStatus::Runnable); // woken
    }

    /// Spawn δ_t = 0 (R-BUDGET-16).
    #[test]
    fn spawn_does_not_advance_logical_time() {
        let mut g = GlobalState::new();
        let mut k = CapabilityKernel::new();
        g.logical_time = LogicalTime::new(3);
        let p = g.spawn_root(unit(), 50);
        spawn_child(&mut g, &mut k, p, unit(), SpawnBudgetSpec::new(5, 8), &[]).unwrap();
        assert_eq!(g.logical_time, LogicalTime::new(3));
    }

    /// State machine: only Runnable is schedulable (RQ-01…04).
    #[test]
    fn state_machine_schedulability() {
        assert!(ActorStatus::Runnable.is_schedulable());
        assert!(!ActorStatus::Blocked.is_schedulable());
        assert!(!ActorStatus::Pending.is_schedulable());
        assert!(!ActorStatus::Terminal.is_schedulable());
    }

    /// Isolation: two actors do not share env/mailbox (R-ACTOR-01).
    #[test]
    fn actor_isolation_disjoint_mailbox_env() {
        let mut g = GlobalState::new();
        let a = g.spawn_root(unit(), 1);
        let b = g.spawn_root(unit(), 1);
        let sa = g.actors.get_mut(&a).unwrap();
        sa.env = Environment::empty().extend(ror_core::Symbol(1), Value::Integer(1));
        sa.mailbox.try_enqueue(Value::Integer(7)).unwrap();
        let sb = g.actors.get(&b).unwrap();
        assert!(sb.env.is_empty());
        assert!(sb.mailbox.is_empty());
        assert_ne!(
            g.actors.get(&a).unwrap().mailbox.as_slice_order(),
            sb.mailbox.as_slice_order()
        );
    }

    /// Clear pending resumes to runnable (canonical completion path).
    #[test]
    fn pending_clear_resumes_runnable() {
        let mut g = GlobalState::new();
        let a = g.spawn_root(unit(), 1);
        g.set_pending(a).unwrap();
        g.clear_pending_to_runnable(a).unwrap();
        assert_eq!(g.actors.get(&a).unwrap().status, ActorStatus::Runnable);
        assert!(g.runnable.contains(a));
    }
}
