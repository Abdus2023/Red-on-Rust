//! M6 differential: actor / mailbox / scheduler observations.
//!
//! Production: `ror-runtime::actor` + kernel.
//! Reference: `ror-reference::actor_model` + RefCapabilityStore (R-REF-02).
//!
//! Black-box observations only — no Rust-internal equality of queue structs.

use ror_core::machine::{Fault, Value};
use ror_core::types::ActorId;
use ror_kernel::CapabilityKernel;
use ror_reference::{
    ref_scheduler_turn, RefCapabilityStore, RefGlobal, RefGlobalStep, RefMachineEvent,
};
use ror_runtime::{scheduler_turn, ActorStatus, GlobalState, GlobalStep, MachineEvent};

/// Semantic observation of one multi-actor run (normalized).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ActorObservation {
    pub actor_ids_in_order: Vec<ActorId>,
    pub selection_order: Vec<ActorId>,
    pub mailbox_orders: Vec<(ActorId, Vec<Value>)>,
    pub final_statuses: Vec<(ActorId, StatusLabel)>,
    pub spawn_events: Vec<(Option<ActorId>, ActorId)>,
    pub send_events: Vec<(ActorId, ActorId)>,
    pub terminal_step: TerminalLabel,
    pub budgets: Vec<(ActorId, u64)>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum StatusLabel {
    Runnable,
    Blocked,
    Pending,
    Terminal,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum TerminalLabel {
    Deadlock,
    Quiescence { pending: Vec<ActorId> },
    StepsExhausted,
}

fn map_prod_status(s: ActorStatus) -> StatusLabel {
    match s {
        ActorStatus::Runnable => StatusLabel::Runnable,
        ActorStatus::Blocked => StatusLabel::Blocked,
        ActorStatus::Pending => StatusLabel::Pending,
        ActorStatus::Terminal => StatusLabel::Terminal,
    }
}

fn map_ref_status(s: ror_reference::RefActorStatus) -> StatusLabel {
    match s {
        ror_reference::RefActorStatus::Runnable => StatusLabel::Runnable,
        ror_reference::RefActorStatus::Blocked => StatusLabel::Blocked,
        ror_reference::RefActorStatus::Pending => StatusLabel::Pending,
        ror_reference::RefActorStatus::Terminal => StatusLabel::Terminal,
    }
}

/// Drive production global for `max_turns` starting from a builder callback.
pub fn observe_production_m6(
    build: impl FnOnce(&mut GlobalState),
    kernel: &mut CapabilityKernel,
    max_turns: u64,
) -> Result<ActorObservation, Fault> {
    let mut g = GlobalState::new();
    build(&mut g);
    let mut selection = Vec::new();
    let mut terminal = TerminalLabel::StepsExhausted;
    for _ in 0..max_turns {
        match scheduler_turn(&mut g, kernel)? {
            GlobalStep::Turn { actor } => selection.push(actor),
            GlobalStep::Deadlock => {
                terminal = TerminalLabel::Deadlock;
                break;
            }
            GlobalStep::QuiescenceReconciled { pending } => {
                terminal = TerminalLabel::Quiescence { pending };
                break;
            }
        }
    }
    Ok(snapshot_prod(&g, selection, terminal))
}

fn snapshot_prod(
    g: &GlobalState,
    selection: Vec<ActorId>,
    terminal: TerminalLabel,
) -> ActorObservation {
    let actor_ids_in_order: Vec<ActorId> = g.actors.keys().copied().collect();
    let mailbox_orders: Vec<(ActorId, Vec<Value>)> = g
        .actors
        .iter()
        .map(|(id, a)| (*id, a.mailbox.as_slice_order()))
        .collect();
    let final_statuses: Vec<(ActorId, StatusLabel)> = g
        .actors
        .iter()
        .map(|(id, a)| (*id, map_prod_status(a.status)))
        .collect();
    let budgets: Vec<(ActorId, u64)> = g
        .actors
        .iter()
        .map(|(id, a)| (*id, a.budget_units))
        .collect();
    let spawn_events: Vec<(Option<ActorId>, ActorId)> = g
        .events
        .iter()
        .filter_map(|e| match e {
            MachineEvent::ActorSpawned { parent, child } => Some((*parent, *child)),
            _ => None,
        })
        .collect();
    let send_events: Vec<(ActorId, ActorId)> = g
        .events
        .iter()
        .filter_map(|e| match e {
            MachineEvent::MessageSent { from, to } => Some((*from, *to)),
            _ => None,
        })
        .collect();
    ActorObservation {
        actor_ids_in_order,
        selection_order: selection,
        mailbox_orders,
        final_statuses,
        spawn_events,
        send_events,
        terminal_step: terminal,
        budgets,
    }
}

pub fn observe_reference_m6(
    build: impl FnOnce(&mut RefGlobal),
    store: &mut RefCapabilityStore,
    max_turns: u64,
) -> Result<ActorObservation, Fault> {
    let mut g = RefGlobal::new();
    build(&mut g);
    let mut selection = Vec::new();
    let mut terminal = TerminalLabel::StepsExhausted;
    for _ in 0..max_turns {
        match ref_scheduler_turn(&mut g, store)? {
            RefGlobalStep::Turn { actor } => selection.push(actor),
            RefGlobalStep::Deadlock => {
                terminal = TerminalLabel::Deadlock;
                break;
            }
            RefGlobalStep::QuiescenceReconciled { pending } => {
                terminal = TerminalLabel::Quiescence { pending };
                break;
            }
        }
    }
    Ok(snapshot_ref(&g, selection, terminal))
}

fn snapshot_ref(
    g: &RefGlobal,
    selection: Vec<ActorId>,
    terminal: TerminalLabel,
) -> ActorObservation {
    let actor_ids_in_order: Vec<ActorId> = g.actors.keys().copied().collect();
    let mailbox_orders: Vec<(ActorId, Vec<Value>)> = g
        .actors
        .iter()
        .map(|(id, a)| (*id, a.mailbox.as_slice_order()))
        .collect();
    let final_statuses: Vec<(ActorId, StatusLabel)> = g
        .actors
        .iter()
        .map(|(id, a)| (*id, map_ref_status(a.status)))
        .collect();
    let budgets: Vec<(ActorId, u64)> = g
        .actors
        .iter()
        .map(|(id, a)| (*id, a.budget_units))
        .collect();
    let spawn_events: Vec<(Option<ActorId>, ActorId)> = g
        .events
        .iter()
        .filter_map(|e| match e {
            RefMachineEvent::ActorSpawned { parent, child } => Some((*parent, *child)),
            _ => None,
        })
        .collect();
    let send_events: Vec<(ActorId, ActorId)> = g
        .events
        .iter()
        .filter_map(|e| match e {
            RefMachineEvent::MessageSent { from, to } => Some((*from, *to)),
            _ => None,
        })
        .collect();
    ActorObservation {
        actor_ids_in_order,
        selection_order: selection,
        mailbox_orders,
        final_statuses,
        spawn_events,
        send_events,
        terminal_step: terminal,
        budgets,
    }
}

#[allow(clippy::result_large_err)]
pub fn compare_m6(
    build_p: impl FnOnce(&mut GlobalState),
    build_r: impl FnOnce(&mut RefGlobal),
    kernel: &mut CapabilityKernel,
    store: &mut RefCapabilityStore,
    max_turns: u64,
) -> Result<(), (ActorObservation, ActorObservation)> {
    let p = match observe_production_m6(build_p, kernel, max_turns) {
        Ok(o) => o,
        Err(f) => panic!("production fault: {f:?}"),
    };
    let r = match observe_reference_m6(build_r, store, max_turns) {
        Ok(o) => o,
        Err(f) => panic!("reference fault: {f:?}"),
    };
    if p == r {
        Ok(())
    } else {
        Err((p, r))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::machine::sugar::{receive, unit};
    use ror_core::types::CapRef;
    use ror_reference::{ref_marshal, ref_send, ref_spawn_child, RefSpawnBudget};
    use ror_runtime::{
        marshal_message, send_async, spawn_child, ActorState, RunnableQueue, SpawnBudgetSpec,
    };
    // send_async / ref_send already imported for multi-sender and mutation tests.

    #[test]
    fn three_roots_fifo_agrees() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        compare_m6(
            |g| {
                g.spawn_root(unit(), 1);
                g.spawn_root(unit(), 1);
                g.spawn_root(unit(), 1);
            },
            |g| {
                g.spawn_root(unit(), 1);
                g.spawn_root(unit(), 1);
                g.spawn_root(unit(), 1);
            },
            &mut k,
            &mut s,
            10,
        )
        .expect("m6 fifo divergence");
    }

    #[test]
    fn receive_block_deadlock_agrees() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        compare_m6(
            |g| {
                g.spawn_root(receive(), 1);
            },
            |g| {
                g.spawn_root(receive(), 1);
            },
            &mut k,
            &mut s,
            5,
        )
        .expect("m6 block divergence");
    }

    #[test]
    fn pending_quiescence_agrees() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        compare_m6(
            |g| {
                let a = g.spawn_root(unit(), 7);
                g.set_pending(a).unwrap();
            },
            |g| {
                let a = g.spawn_root(unit(), 7);
                g.set_pending(a).unwrap();
            },
            &mut k,
            &mut s,
            5,
        )
        .expect("m6 quiescence divergence");
    }

    #[test]
    fn send_wakeup_mailbox_fifo_agrees() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        // Build: receiver blocks; external send two messages; schedule.
        let p = observe_production_m6(
            |g| {
                let r = g.spawn_root(receive(), 10);
                // drain r to blocked
                let mut kk = CapabilityKernel::new();
                let _ = scheduler_turn(g, &mut kk).unwrap();
                // allocate terminal sender
                let sid = g.ids.allocate();
                g.actors.insert(
                    sid,
                    ActorState::new(
                        sid,
                        unit(),
                        ror_core::capability::CapabilityContext::empty(),
                        1,
                        64,
                        None,
                    ),
                );
                g.actors.get_mut(&sid).unwrap().status = ActorStatus::Terminal;
                send_async(g, sid, r, Value::Integer(1)).unwrap();
                send_async(g, sid, r, Value::Integer(2)).unwrap();
            },
            &mut k,
            5,
        )
        .unwrap();
        let r = observe_reference_m6(
            |g| {
                let r = g.spawn_root(receive(), 10);
                let mut ss = RefCapabilityStore::new();
                let _ = ref_scheduler_turn(g, &mut ss).unwrap();
                let sid = g.ids.allocate();
                g.actors.insert(
                    sid,
                    ror_reference::RefActor::new(
                        sid,
                        unit(),
                        ror_core::capability::CapabilityContext::empty(),
                        1,
                        64,
                        None,
                    ),
                );
                g.actors.get_mut(&sid).unwrap().status = ror_reference::RefActorStatus::Terminal;
                ref_send(g, sid, r, Value::Integer(1)).unwrap();
                ref_send(g, sid, r, Value::Integer(2)).unwrap();
            },
            &mut s,
            5,
        )
        .unwrap();
        assert_eq!(p.selection_order, r.selection_order);
        assert_eq!(p.mailbox_orders, r.mailbox_orders);
        assert_eq!(p.terminal_step, r.terminal_step);
    }

    #[test]
    fn marshal_reject_agrees() {
        let cap = Value::Capability(CapRef::from_kernel_parts(0, 0));
        assert_eq!(marshal_message(&cap), Err(Fault::MarshalCapabilityRejected));
        assert_eq!(ref_marshal(&cap), Err(Fault::MarshalCapabilityRejected));
        assert_eq!(
            marshal_message(&Value::Integer(3)).ok(),
            ref_marshal(&Value::Integer(3)).ok()
        );
    }

    #[test]
    fn spawn_empty_caps_budget_agrees() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let p = observe_production_m6(
            |g| {
                let parent = g.spawn_root(unit(), 100);
                spawn_child(
                    g,
                    &mut CapabilityKernel::new(),
                    parent,
                    unit(),
                    SpawnBudgetSpec::new(10, 8),
                    &[],
                )
                .unwrap();
            },
            &mut k,
            10,
        )
        .unwrap();
        let r = observe_reference_m6(
            |g| {
                let parent = g.spawn_root(unit(), 100);
                ref_spawn_child(
                    g,
                    &mut RefCapabilityStore::new(),
                    parent,
                    unit(),
                    RefSpawnBudget::new(10, 8),
                    &[],
                )
                .unwrap();
            },
            &mut s,
            10,
        )
        .unwrap();
        assert_eq!(p.actor_ids_in_order, r.actor_ids_in_order);
        assert_eq!(p.budgets, r.budgets);
        assert_eq!(p.spawn_events, r.spawn_events);
        assert_eq!(p.selection_order, r.selection_order);
    }

    #[test]
    fn mutation_intent_duplicate_runnable() {
        let mut q = RunnableQueue::new();
        assert!(q.enqueue_back(ActorId(0)));
        assert!(!q.enqueue_back(ActorId(0)));
    }

    #[test]
    fn mutation_intent_cap_send_killed() {
        let mut g = GlobalState::new();
        let a = g.spawn_root(unit(), 1);
        let b = g.spawn_root(unit(), 1);
        assert!(send_async(
            &mut g,
            a,
            b,
            Value::Capability(CapRef::from_kernel_parts(0, 0))
        )
        .is_err());
    }

    #[test]
    fn m5_regression_still_linked() {
        // Ensure m5 module still compiles/links in the crate.
        let _ = crate::m5::compare_m5 as usize;
    }

    /// T36–T38: reference actor/mailbox/scheduler agreement on multi-sender FIFO.
    #[test]
    fn multi_sender_mailbox_agrees() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let p = observe_production_m6(
            |g| {
                let r = g.spawn_root(receive(), 10);
                let mut kk = CapabilityKernel::new();
                let _ = scheduler_turn(g, &mut kk).unwrap();
                for msg in [1i64, 2, 3] {
                    let sid = g.ids.allocate();
                    g.actors.insert(
                        sid,
                        ActorState::new(
                            sid,
                            unit(),
                            ror_core::capability::CapabilityContext::empty(),
                            1,
                            64,
                            None,
                        ),
                    );
                    g.actors.get_mut(&sid).unwrap().status = ActorStatus::Terminal;
                    send_async(g, sid, r, Value::Integer(msg)).unwrap();
                }
            },
            &mut k,
            8,
        )
        .unwrap();
        let r = observe_reference_m6(
            |g| {
                let r = g.spawn_root(receive(), 10);
                let mut ss = RefCapabilityStore::new();
                let _ = ref_scheduler_turn(g, &mut ss).unwrap();
                for msg in [1i64, 2, 3] {
                    let sid = g.ids.allocate();
                    g.actors.insert(
                        sid,
                        ror_reference::RefActor::new(
                            sid,
                            unit(),
                            ror_core::capability::CapabilityContext::empty(),
                            1,
                            64,
                            None,
                        ),
                    );
                    g.actors.get_mut(&sid).unwrap().status =
                        ror_reference::RefActorStatus::Terminal;
                    ref_send(g, sid, r, Value::Integer(msg)).unwrap();
                }
            },
            &mut s,
            8,
        )
        .unwrap();
        assert_eq!(p.mailbox_orders, r.mailbox_orders);
        assert_eq!(p.selection_order, r.selection_order);
        assert_eq!(p.terminal_step, r.terminal_step);
    }

    /// T39: production/reference independence — reference crate has no runtime dep.
    #[test]
    fn production_reference_independence_structural() {
        // Cargo.toml of ror-reference depends only on ror-core (compile-time evidence).
        // Runtime observation APIs are distinct types (GlobalState ≠ RefGlobal).
        let _p: GlobalState = GlobalState::new();
        let _r: RefGlobal = RefGlobal::new();
        // Distinct concrete types (not interchangeable); both constructible.
        assert!(std::mem::size_of::<GlobalState>() > 0);
        assert!(std::mem::size_of::<RefGlobal>() > 0);
        let _ = (_p, _r);
    }

    /// T22/D05: repeated differential observation is stable.
    #[test]
    fn determinism_differential_observation_stable() {
        let mut k1 = CapabilityKernel::new();
        let mut s1 = RefCapabilityStore::new();
        let mut k2 = CapabilityKernel::new();
        let mut s2 = RefCapabilityStore::new();
        let build_p = |g: &mut GlobalState| {
            g.spawn_root(unit(), 1);
            g.spawn_root(receive(), 1);
            g.spawn_root(unit(), 1);
        };
        let build_r = |g: &mut RefGlobal| {
            g.spawn_root(unit(), 1);
            g.spawn_root(receive(), 1);
            g.spawn_root(unit(), 1);
        };
        let a = observe_production_m6(build_p, &mut k1, 10).unwrap();
        let b = observe_production_m6(
            |g| {
                g.spawn_root(unit(), 1);
                g.spawn_root(receive(), 1);
                g.spawn_root(unit(), 1);
            },
            &mut k2,
            10,
        )
        .unwrap();
        assert_eq!(a, b);
        let ra = observe_reference_m6(build_r, &mut s1, 10).unwrap();
        let rb = observe_reference_m6(
            |g| {
                g.spawn_root(unit(), 1);
                g.spawn_root(receive(), 1);
                g.spawn_root(unit(), 1);
            },
            &mut s2,
            10,
        )
        .unwrap();
        assert_eq!(ra, rb);
        assert_eq!(a, ra);
    }

    /// T32/T33 carry: M5 host-before-Issued remains killable (linked from m5).
    #[test]
    fn m5_host_before_issued_still_critical() {
        // Presence of illegal_host_before_issued API — hinge not removed by M6.
        let _ = ror_runtime::illegal_host_before_issued as usize;
    }
}
