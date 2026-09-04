//! Independent reference actor/concurrency model (M6).
//!
//! Separately authored mirror of production actor semantics (R-REF-02).
//! Does **not** import `ror-runtime` or `ror-kernel`. Uses `ror-core` types and
//! [`crate::cap_algebra::RefCapabilityStore`] for spawn-time derive only.
//! Effect handoff observations are structural (status Pending) — no production
//! `run_effect_pipeline` call.

use std::collections::{BTreeMap, BTreeSet, VecDeque};

use ror_core::capability::{CapabilityContext, Constraint, LogicalTime};
use ror_core::machine::{DelegatedCapability, Environment, Expr, Fault, Value};
use ror_core::types::{ActorId, ActorIdAlloc, CapRef};

use crate::cap_algebra::RefCapabilityStore;
use crate::pure_cek::{step, RefOutcome, RefState};

/// Reference actor status (U-27 provisional mirror).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum RefActorStatus {
    Runnable,
    Blocked,
    Pending,
    Terminal,
}

impl RefActorStatus {
    pub fn is_schedulable(self) -> bool {
        matches!(self, RefActorStatus::Runnable)
    }
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct RefMailbox {
    messages: VecDeque<Value>,
    capacity: u64,
}

impl RefMailbox {
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

    pub fn remaining_capacity(&self) -> u64 {
        self.capacity.saturating_sub(self.messages.len() as u64)
    }

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

#[derive(Clone, Debug)]
pub struct RefActor {
    pub id: ActorId,
    pub status: RefActorStatus,
    pub env: Environment,
    pub expr: Expr,
    pub mailbox: RefMailbox,
    pub caps: CapabilityContext,
    pub budget_units: u64,
    pub parent: Option<ActorId>,
}

impl RefActor {
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
            status: RefActorStatus::Runnable,
            env: Environment::empty(),
            expr,
            mailbox: RefMailbox::new(mailbox_capacity),
            caps,
            budget_units,
            parent,
        }
    }
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct RefRunnable {
    order: VecDeque<ActorId>,
    members: BTreeSet<ActorId>,
}

impl RefRunnable {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn is_empty(&self) -> bool {
        self.order.is_empty()
    }

    pub fn contains(&self, id: ActorId) -> bool {
        self.members.contains(&id)
    }

    pub fn enqueue_back(&mut self, id: ActorId) -> bool {
        if self.members.contains(&id) {
            return false;
        }
        self.members.insert(id);
        self.order.push_back(id);
        true
    }

    pub fn dequeue_front(&mut self) -> Option<ActorId> {
        let id = self.order.pop_front()?;
        self.members.remove(&id);
        Some(id)
    }

    pub fn remove(&mut self, id: ActorId) {
        if self.members.remove(&id) {
            self.order.retain(|x| *x != id);
        }
    }

    pub fn as_order(&self) -> Vec<ActorId> {
        self.order.iter().copied().collect()
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RefMachineEvent {
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
    DelegationIssued {
        from: ActorId,
        to: ActorId,
        child: CapRef,
    },
    DelegationAdmitted {
        to: ActorId,
        child: CapRef,
    },
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RefGlobalStep {
    Turn { actor: ActorId },
    Deadlock,
    QuiescenceReconciled { pending: Vec<ActorId> },
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct RefSpawnBudget {
    pub child_units: u64,
    pub mailbox_capacity: u64,
}

impl RefSpawnBudget {
    pub fn new(child_units: u64, mailbox_capacity: u64) -> Self {
        Self {
            child_units,
            mailbox_capacity,
        }
    }
}

/// Reference global machine (independent of production GlobalState).
pub struct RefGlobal {
    pub actors: BTreeMap<ActorId, RefActor>,
    pub runnable: RefRunnable,
    pub ids: ActorIdAlloc,
    pub logical_time: LogicalTime,
    pub events: Vec<RefMachineEvent>,
    pub default_mailbox_capacity: u64,
}

impl Default for RefGlobal {
    fn default() -> Self {
        Self::new()
    }
}

impl RefGlobal {
    pub fn new() -> Self {
        Self {
            actors: BTreeMap::new(),
            runnable: RefRunnable::new(),
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
            .any(|a| a.status == RefActorStatus::Pending)
    }

    pub fn pending_ids(&self) -> Vec<ActorId> {
        self.actors
            .iter()
            .filter(|(_, a)| a.status == RefActorStatus::Pending)
            .map(|(id, _)| *id)
            .collect()
    }

    pub fn spawn_root(&mut self, expr: Expr, budget_units: u64) -> ActorId {
        let id = self.ids.allocate();
        let state = RefActor::new(
            id,
            expr,
            CapabilityContext::empty(),
            budget_units,
            self.default_mailbox_capacity,
            None,
        );
        self.actors.insert(id, state);
        self.runnable.enqueue_back(id);
        self.events.push(RefMachineEvent::ActorSpawned {
            parent: None,
            child: id,
        });
        id
    }

    pub fn set_pending(&mut self, id: ActorId) -> Result<(), Fault> {
        let a = self.actors.get_mut(&id).ok_or(Fault::ActorNotFound)?;
        a.status = RefActorStatus::Pending;
        self.runnable.remove(id);
        Ok(())
    }

    pub fn clear_pending_to_runnable(&mut self, id: ActorId) -> Result<(), Fault> {
        let a = self.actors.get_mut(&id).ok_or(Fault::ActorNotFound)?;
        if a.status != RefActorStatus::Pending {
            return Ok(());
        }
        a.status = RefActorStatus::Runnable;
        self.runnable.enqueue_back(id);
        Ok(())
    }

    pub fn terminate(&mut self, id: ActorId) -> Result<(), Fault> {
        let a = self.actors.get_mut(&id).ok_or(Fault::ActorNotFound)?;
        a.status = RefActorStatus::Terminal;
        self.runnable.remove(id);
        Ok(())
    }
}

// --- Marshal (independent recursive walk) ------------------------------------

pub fn ref_contains_capability(v: &Value) -> bool {
    match v {
        Value::Capability(_) | Value::DelegatedCapability(_) | Value::Function(_) => true,
        Value::Constraint(_) => false,
        Value::List(xs) | Value::Tuple(xs) => xs.iter().any(ref_contains_capability),
        Value::Unit
        | Value::Bool(_)
        | Value::Integer(_)
        | Value::Bytes(_)
        | Value::Symbol(_)
        | Value::String(_) => false,
    }
}

pub fn ref_marshal(v: &Value) -> Result<Value, Fault> {
    if ref_contains_capability(v) {
        Err(Fault::MarshalCapabilityRejected)
    } else {
        Ok(v.clone())
    }
}

// --- Spawn -------------------------------------------------------------------

pub fn ref_spawn_child(
    g: &mut RefGlobal,
    store: &mut RefCapabilityStore,
    parent: ActorId,
    body: Expr,
    budget: RefSpawnBudget,
    manifest: &[(CapRef, Constraint)],
) -> Result<ActorId, Fault> {
    let parent_state = g.actors.get(&parent).ok_or(Fault::ActorNotFound)?;
    if parent_state.status == RefActorStatus::Terminal {
        return Err(Fault::ActorNotFound);
    }
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
                let _ = store.revoke(*d);
            }
            return Err(Fault::Unauthorized);
        }
        match store.derive(*cap, constraint, t) {
            Ok(child_cap) => {
                child_caps.insert(child_cap);
                derived.push(child_cap);
            }
            Err(f) => {
                for d in &derived {
                    let _ = store.revoke(*d);
                }
                return Err(f);
            }
        }
    }

    let parent_state = g.actors.get_mut(&parent).ok_or(Fault::ActorNotFound)?;
    parent_state.budget_units = parent_state.budget_units.saturating_sub(budget.child_units);

    let child_id = g.ids.allocate();
    let child = RefActor::new(
        child_id,
        body,
        child_caps,
        budget.child_units,
        budget.mailbox_capacity,
        Some(parent),
    );
    g.actors.insert(child_id, child);
    g.runnable.enqueue_back(child_id);
    g.events.push(RefMachineEvent::ActorSpawned {
        parent: Some(parent),
        child: child_id,
    });
    Ok(child_id)
}

// --- Delegation (R-MARSHAL-05 independent) -----------------------------------

pub fn ref_issue_delegation(
    g: &mut RefGlobal,
    store: &mut RefCapabilityStore,
    from: ActorId,
    to: ActorId,
    parent_cap: CapRef,
    constraint: &Constraint,
) -> Result<DelegatedCapability, Fault> {
    let parent_state = g.actors.get(&from).ok_or(Fault::ActorNotFound)?;
    if parent_state.status == RefActorStatus::Terminal {
        return Err(Fault::ActorNotFound);
    }
    if !parent_state.caps.contains(parent_cap) {
        return Err(Fault::Unauthorized);
    }
    if !g.actors.contains_key(&to) {
        return Err(Fault::ActorNotFound);
    }
    let child = store.derive(parent_cap, constraint, g.logical_time)?;
    let envelope = DelegatedCapability::from_derived(child, to.0);
    g.events
        .push(RefMachineEvent::DelegationIssued { from, to, child });
    Ok(envelope)
}

pub fn ref_admit_delegation(
    g: &mut RefGlobal,
    store: &mut RefCapabilityStore,
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

    let restore = |g: &mut RefGlobal, before: Vec<CapRef>| {
        if let Some(a) = g.actors.get_mut(&recipient) {
            a.caps = CapabilityContext::empty();
            for c in before {
                a.caps.insert(c);
            }
        }
    };

    if envelope.target_actor() != recipient.0 {
        restore(g, before_slots);
        return Err(Fault::Unauthorized);
    }
    let child = envelope.child_cap();
    if !store.valid(child, g.logical_time) {
        restore(g, before_slots);
        return Err(Fault::Unauthorized);
    }
    if store.parent_of(child).is_none() {
        restore(g, before_slots);
        return Err(Fault::Unauthorized);
    }
    let a = g.actors.get_mut(&recipient).ok_or(Fault::ActorNotFound)?;
    a.caps.insert(child);
    g.events.push(RefMachineEvent::DelegationAdmitted {
        to: recipient,
        child,
    });
    Ok(())
}

pub fn ref_send_delegation(
    g: &mut RefGlobal,
    from: ActorId,
    to: ActorId,
    envelope: DelegatedCapability,
) -> Result<(), Fault> {
    if !g.actors.contains_key(&from) {
        return Err(Fault::ActorNotFound);
    }
    {
        let target = g.actors.get(&to).ok_or(Fault::ActorNotFound)?;
        if target.status == RefActorStatus::Terminal {
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
    let was_blocked = target.status == RefActorStatus::Blocked;
    target
        .mailbox
        .try_enqueue(Value::DelegatedCapability(envelope))?;
    if was_blocked {
        target.status = RefActorStatus::Runnable;
        g.runnable.enqueue_back(to);
    }
    g.events.push(RefMachineEvent::MessageSent { from, to });
    Ok(())
}

// --- Send / Receive ----------------------------------------------------------

pub fn ref_send(
    g: &mut RefGlobal,
    from: ActorId,
    to: ActorId,
    message: Value,
) -> Result<(), Fault> {
    if !g.actors.contains_key(&from) {
        return Err(Fault::ActorNotFound);
    }
    let marshalled = ref_marshal(&message)?;
    {
        let target = g.actors.get(&to).ok_or(Fault::ActorNotFound)?;
        if target.status == RefActorStatus::Terminal {
            return Err(Fault::ActorNotFound);
        }
        if target.mailbox.remaining_capacity() == 0 {
            return Err(Fault::ReservedCapacityExceeded);
        }
    }
    let target = g.actors.get_mut(&to).ok_or(Fault::ActorNotFound)?;
    let was_blocked = target.status == RefActorStatus::Blocked;
    target.mailbox.try_enqueue(marshalled)?;
    if was_blocked {
        target.status = RefActorStatus::Runnable;
        g.runnable.enqueue_back(to);
    }
    g.events.push(RefMachineEvent::MessageSent { from, to });
    Ok(())
}

pub fn ref_receive_or_block(g: &mut RefGlobal, id: ActorId) -> Result<Option<Value>, Fault> {
    let actor = g.actors.get_mut(&id).ok_or(Fault::ActorNotFound)?;
    if let Some(msg) = actor.mailbox.dequeue() {
        return Ok(Some(msg));
    }
    actor.status = RefActorStatus::Blocked;
    g.runnable.remove(id);
    Ok(None)
}

// --- Scheduler ---------------------------------------------------------------

pub fn ref_scheduler_turn(
    g: &mut RefGlobal,
    store: &mut RefCapabilityStore,
) -> Result<RefGlobalStep, Fault> {
    loop {
        let Some(id) = g.runnable.dequeue_front() else {
            return Ok(ref_finish_empty(g));
        };
        let status = g
            .actors
            .get(&id)
            .map(|a| a.status)
            .ok_or(Fault::ActorNotFound)?;
        if !status.is_schedulable() {
            continue;
        }
        g.events.push(RefMachineEvent::ActorSelected { id });
        ref_run_one(g, store, id)?;
        return Ok(RefGlobalStep::Turn { actor: id });
    }
}

fn ref_finish_empty(g: &mut RefGlobal) -> RefGlobalStep {
    if g.has_pending() {
        let pending = g.pending_ids();
        for id in &pending {
            g.events
                .push(RefMachineEvent::EffectIndeterminate { actor: *id });
        }
        g.events.push(RefMachineEvent::QuiescenceReconcile {
            pending: pending.clone(),
        });
        RefGlobalStep::QuiescenceReconciled { pending }
    } else {
        RefGlobalStep::Deadlock
    }
}

fn ref_run_one(
    g: &mut RefGlobal,
    store: &mut RefCapabilityStore,
    id: ActorId,
) -> Result<(), Fault> {
    let expr = g.actors.get(&id).ok_or(Fault::ActorNotFound)?.expr.clone();
    match expr {
        Expr::Receive => match ref_receive_or_block(g, id)? {
            Some(Value::DelegatedCapability(env)) => {
                ref_admit_delegation(g, store, id, &env)?;
                if let Some(a) = g.actors.get_mut(&id) {
                    a.expr = Expr::Value(Value::Unit);
                    if a.status == RefActorStatus::Runnable {
                        g.runnable.enqueue_back(id);
                    }
                }
            }
            Some(_msg) => {
                if let Some(a) = g.actors.get_mut(&id) {
                    a.expr = Expr::Value(Value::Unit);
                    if a.status == RefActorStatus::Runnable {
                        g.runnable.enqueue_back(id);
                    }
                }
            }
            None => {}
        },
        Expr::Delegate {
            capability,
            constraint,
            target,
        } => {
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
            let to = ref_eval_actor_id(&target)?;
            let envelope = ref_issue_delegation(g, store, id, to, parent_cap, &c)?;
            ref_send_delegation(g, id, to, envelope)?;
            if let Some(a) = g.actors.get_mut(&id) {
                a.expr = Expr::Value(Value::Unit);
                if a.status == RefActorStatus::Runnable {
                    g.runnable.enqueue_back(id);
                }
            }
        }
        Expr::Value(_) => {
            g.terminate(id)?;
        }
        Expr::Spawn {
            expr: child_body,
            initial_budget,
            capabilities: _,
        } => {
            let units = match *initial_budget {
                Expr::Value(Value::Integer(n)) if n >= 0 => n as u64,
                _ => {
                    return Err(Fault::TypeError {
                        expected: "Integer(budget)",
                        actual: "other",
                    })
                }
            };
            let cap = g.actors.get(&id).map(|a| a.mailbox.capacity).unwrap_or(64);
            let spec = RefSpawnBudget::new(units, cap);
            ref_spawn_child(g, store, id, *child_body, spec, &[])?;
            if let Some(a) = g.actors.get_mut(&id) {
                a.expr = Expr::Value(Value::Unit);
                if a.status == RefActorStatus::Runnable {
                    g.runnable.enqueue_back(id);
                }
            }
        }
        Expr::Send { target, message } => {
            let to = ref_eval_actor_id(&target)?;
            let msg = ref_eval_value(&message)?;
            ref_send(g, id, to, msg)?;
            if let Some(a) = g.actors.get_mut(&id) {
                a.expr = Expr::Value(Value::Unit);
                if a.status == RefActorStatus::Runnable {
                    g.runnable.enqueue_back(id);
                }
            }
        }
        other => {
            let mut state = RefState::new(other).at_time(g.logical_time);
            if let Some(a) = g.actors.get(&id) {
                state.env = a.env.clone();
            }
            step(&mut state, store);
            match state.outcome {
                RefOutcome::Running => {
                    if let Some(a) = g.actors.get_mut(&id) {
                        a.expr = state.expr;
                        a.env = state.env;
                        if a.status == RefActorStatus::Runnable {
                            g.runnable.enqueue_back(id);
                        }
                    }
                }
                RefOutcome::Halted(v) => {
                    if let Some(a) = g.actors.get_mut(&id) {
                        a.expr = Expr::Value(v);
                        a.env = state.env;
                        if a.status == RefActorStatus::Runnable {
                            g.runnable.enqueue_back(id);
                        }
                    }
                }
                RefOutcome::Fault(f) => {
                    g.terminate(id)?;
                    return Err(f);
                }
            }
        }
    }
    Ok(())
}

fn ref_eval_actor_id(e: &Expr) -> Result<ActorId, Fault> {
    match e {
        Expr::Value(Value::Integer(n)) if *n >= 0 => Ok(ActorId(*n as u64)),
        _ => Err(Fault::TypeError {
            expected: "Integer(ActorId)",
            actual: "other",
        }),
    }
}

fn ref_eval_value(e: &Expr) -> Result<Value, Fault> {
    match e {
        Expr::Value(v) => Ok(v.clone()),
        _ => Err(Fault::TypeError {
            expected: "Value",
            actual: "expr",
        }),
    }
}

pub fn ref_run_until_quiescent(
    g: &mut RefGlobal,
    store: &mut RefCapabilityStore,
    max_turns: u64,
) -> Result<RefGlobalStep, Fault> {
    let mut last = RefGlobalStep::Deadlock;
    for _ in 0..max_turns {
        last = ref_scheduler_turn(g, store)?;
        match &last {
            RefGlobalStep::Deadlock | RefGlobalStep::QuiescenceReconciled { .. } => {
                return Ok(last)
            }
            RefGlobalStep::Turn { .. } => continue,
        }
    }
    Ok(last)
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::machine::sugar::{receive, unit};

    #[test]
    fn ref_fifo_and_block() {
        let mut g = RefGlobal::new();
        let mut s = RefCapabilityStore::new();
        let a = g.spawn_root(unit(), 1);
        let b = g.spawn_root(unit(), 1);
        assert_eq!(
            ref_scheduler_turn(&mut g, &mut s).unwrap(),
            RefGlobalStep::Turn { actor: a }
        );
        assert_eq!(
            ref_scheduler_turn(&mut g, &mut s).unwrap(),
            RefGlobalStep::Turn { actor: b }
        );
        assert_eq!(
            ref_scheduler_turn(&mut g, &mut s).unwrap(),
            RefGlobalStep::Deadlock
        );
    }

    #[test]
    fn ref_receive_blocks() {
        let mut g = RefGlobal::new();
        let mut s = RefCapabilityStore::new();
        let a = g.spawn_root(receive(), 1);
        let _ = ref_scheduler_turn(&mut g, &mut s).unwrap();
        assert_eq!(g.actors.get(&a).unwrap().status, RefActorStatus::Blocked);
        assert_eq!(
            ref_scheduler_turn(&mut g, &mut s).unwrap(),
            RefGlobalStep::Deadlock
        );
    }

    #[test]
    fn ref_pending_quiescence() {
        let mut g = RefGlobal::new();
        let mut s = RefCapabilityStore::new();
        let a = g.spawn_root(unit(), 5);
        g.set_pending(a).unwrap();
        match ref_scheduler_turn(&mut g, &mut s).unwrap() {
            RefGlobalStep::QuiescenceReconciled { pending } => assert_eq!(pending, vec![a]),
            other => panic!("{other:?}"),
        }
        assert_eq!(g.actors.get(&a).unwrap().budget_units, 5);
        assert_eq!(g.actors.get(&a).unwrap().status, RefActorStatus::Pending);
    }

    #[test]
    fn ref_marshal_rejects_cap() {
        assert_eq!(
            ref_marshal(&Value::Capability(CapRef::from_kernel_parts(0, 0))),
            Err(Fault::MarshalCapabilityRejected)
        );
    }
}
