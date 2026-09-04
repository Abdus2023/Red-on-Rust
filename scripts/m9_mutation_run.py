#!/usr/bin/env python3
"""M9 mutation runner (R-TEST-06): inject → build → targeted → differential → classify.

Isolated scratch copies only — never mutates the live working tree.
Derived consumer of mutations/registry.toml (final/04 §2 authority).

Exit 0 iff MutationKillRate == 100% over non-equivalent registered mutants
and no critical survivor.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "mutations" / "registry.toml"
ENV = os.environ.copy()
# Preserve offline toolchain.
_tc = Path.home() / ".ror-toolchain" / "ror-stable" / "bin"
if _tc.is_dir():
    ENV["PATH"] = f"{_tc}:{ENV.get('PATH', '')}"
ENV["RUSTUP_TOOLCHAIN"] = ENV.get("RUSTUP_TOOLCHAIN", "ror-stable")
ENV["CARGO_TERM_COLOR"] = "never"

# Exclude heavy / non-source trees from scratch copies.
SKIP_NAMES = {
    "target",
    ".git",
    ".arena",
    "__pycache__",
    ".cache",
    "node_modules",
}


@dataclass
class MutantMeta:
    mid: str
    defect: str
    obligations: list[str]
    component: str
    security: bool
    differential: bool
    equiv: bool
    kind: str = "machine"


@dataclass
class Result:
    mid: str
    classification: str
    build_ok: bool
    targeted_failed: bool
    differential_failed: bool
    kill_evidence: str
    security: bool
    obligations: list[str] = field(default_factory=list)
    defect: str = ""


def parse_registry(text: str) -> list[MutantMeta]:
    rows: list[MutantMeta] = []
    cur: dict | None = None

    def flush():
        nonlocal cur
        if cur is None:
            return
        rows.append(
            MutantMeta(
                mid=cur["id"],
                defect=cur.get("defect", ""),
                obligations=cur.get("obligations", []),
                component=cur.get("component", ""),
                security=bool(cur.get("security", False)),
                differential=bool(cur.get("differential", False)),
                equiv=bool(cur.get("equiv", False)),
                kind=cur.get("kind", "machine"),
            )
        )
        cur = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "[[mutant]]":
            flush()
            cur = {}
            continue
        if cur is None:
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip()
        if v.startswith('"') and v.endswith('"'):
            cur[k] = v[1:-1]
        elif v in ("true", "false"):
            cur[k] = v == "true"
        elif v.startswith("["):
            inner = v[1:-1].strip()
            items = []
            for p in inner.split(","):
                p = p.strip()
                if p.startswith('"') and p.endswith('"'):
                    items.append(p[1:-1])
            cur[k] = items
    flush()
    return rows


def copy_tree(src: Path, dst: Path) -> None:
    def ignore(directory: str, names: list[str]):
        return [n for n in names if n in SKIP_NAMES]

    # dst may already exist (mkdtemp); copy contents into it.
    if dst.exists():
        for item in src.iterdir():
            if item.name in SKIP_NAMES:
                continue
            target = dst / item.name
            if item.is_dir():
                shutil.copytree(item, target, ignore=ignore, symlinks=True)
            else:
                shutil.copy2(item, target, follow_symlinks=False)
    else:
        shutil.copytree(src, dst, ignore=ignore, symlinks=True)


def run(cmd: list[str], cwd: Path, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        env=ENV,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout,
    )


def cargo_test(cwd: Path, package: str, test_filter: str | None, timeout: int = 300) -> subprocess.CompletedProcess:
    cmd = ["cargo", "test", "-p", package, "--lib", "--", "--test-threads=1"]
    if test_filter:
        cmd.insert(-2, test_filter)  # before --
        # cargo test -p pkg FILTER --lib -- --test-threads=1
        cmd = ["cargo", "test", "-p", package, "--lib", test_filter, "--", "--test-threads=1"]
    return run(cmd, cwd, timeout=timeout)


def cargo_check(cwd: Path, timeout: int = 300) -> subprocess.CompletedProcess:
    return run(["cargo", "check", "--workspace"], cwd, timeout=timeout)


def replace_once(path: Path, old: str, new: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        return False
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


def replace_all(path: Path, old: str, new: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        return False
    path.write_text(text.replace(old, new), encoding="utf-8")
    return True


def apply_mutant(root: Path, mid: str) -> bool:
    """Apply one registered machine/document mutant. Return False if could not apply."""
    R = root

    def p(*parts: str) -> Path:
        return R.joinpath(*parts)

    # --- M001 reverse argument evaluation (bind params zip reversed) ---
    if mid == "M001":
        return replace_once(
            p("crates/ror-runtime/src/cek.rs"),
            "for (name, val) in function.params.into_iter().zip(args.into_iter()) {",
            "for (name, val) in function.params.into_iter().zip(args.into_iter().rev()) {",
        )

    # --- M002 skip arity precheck ---
    if mid == "M002":
        return replace_once(
            p("crates/ror-runtime/src/cek.rs"),
            """    // Arity precheck BEFORE any argument evaluation (REQ-CEK-014).
    if args.len() != function.params.len() {
        return StepResult::Fault(Fault::ArityMismatch {
            expected: function.params.len(),
            actual: args.len(),
        });
    }

    let mut remaining = args;""",
            """    // MUTANT M002: skip arity precheck
    let _ = function.params.len();
    let mut remaining = args;""",
        )

    # --- M003 allow non-function application ---
    if mid == "M003":
        return replace_once(
            p("crates/ror-runtime/src/cek.rs"),
            """    let function = match value {
        Value::Function(f) => f,
        other => {
            return StepResult::Fault(Fault::TypeError {
                expected: "Function",
                actual: value_kind(&other),
            });
        }
    };""",
            """    let function = match value {
        Value::Function(f) => f,
        // MUTANT M003: treat non-function as identity-ish unit thunk
        other => {
            let _ = other;
            return apply_function(
                state,
                FunctionValue {
                    params: vec![],
                    body: Box::new(Expr::Value(Value::Unit)),
                    env: caller_env.clone(),
                },
                vec![],
            );
        }
    };""",
        )

    # --- M004 accept revoked capability ---
    if mid == "M004":
        return replace_once(
            p("crates/ror-kernel/src/lib.rs"),
            """        if !node.live
            || self
                .revocation_set
                .contains(&(cap.index(), cap.generation()))
        {
            return Err(KernelFault::CapabilityRevoked);
        }""",
            """        // MUTANT M004: accept revoked capability (skip live/revocation check)
        let _ = node.live;
        let _ = &self.revocation_set;""",
        )

    # --- M005 omit capability ceiling ---
    if mid == "M005":
        return replace_once(
            p("crates/ror-core/src/capability.rs"),
            """    op_auth.scope.contains_target(effect.target)
        && op_auth.params.satisfies(effect.param_tag)
        && effect.cost_units <= op_auth.resources.units
        && op_auth.lifetime.contains(t)""",
            """    op_auth.scope.contains_target(effect.target)
        && op_auth.params.satisfies(effect.param_tag)
        // MUTANT M005: omit capability ceiling
        && op_auth.lifetime.contains(t)""",
        )

    # --- M006 permit capability amplification ---
    if mid == "M006":
        return replace_once(
            p("crates/ror-kernel/src/lib.rs"),
            """        if !admissible_constraint_wrt_parent(constraint, &parent_auth) {
            return Err(KernelFault::InvalidConstraint);
        }""",
            """        // MUTANT M006: permit amplification — skip parent-relative admissibility
        let _ = &parent_auth;""",
        )

    # --- M007 omit budget gate ---
    if mid == "M007":
        return replace_once(
            p("crates/ror-runtime/src/effects.rs"),
            """    if !need.saturating_leq(ctx.budget.available) {
        return RequestOutcome::Denied(Fault::BudgetExhausted);
    }""",
            """    // MUTANT M007: omit budget gate
    let _ = need;
    let _ = &ctx.budget.available;""",
        )

    # --- M008 release indeterminate escrow ---
    # Model as: on HostFailed path, restore available (release escrow) without recon.
    if mid == "M008":
        return replace_once(
            p("crates/ror-runtime/src/effects.rs"),
            """        Err(he) => {
            let fault = match he {
                HostError::PolicyDenied => Fault::HostPolicyDenied,
                other => Fault::HostFault {
                    code: other.code().0,
                },
            };
            RequestOutcome::HostFailed { id, fault }
        }""",
            """        Err(he) => {
            let fault = match he {
                HostError::PolicyDenied => Fault::HostPolicyDenied,
                other => Fault::HostFault {
                    code: other.code().0,
                },
            };
            // MUTANT M008: release indeterminate escrow back to available
            ctx.budget.available =
                Consumable::new(ctx.budget.available.units.saturating_add(need.units));
            RequestOutcome::HostFailed { id, fault }
        }""",
        )

    # --- M009 permit negative resources (saturating sub wraps conceptually via underflow allow) ---
    if mid == "M009":
        # Use i64-style wrap: change charge to wrapping_sub interpretation by allowing
        # available to go via wrapping when subtracting need larger than available —
        # actually available is u64; model as skip the budget gate AND charge with wrapping.
        ok = replace_once(
            p("crates/ror-runtime/src/effects.rs"),
            """    if !need.saturating_leq(ctx.budget.available) {
        return RequestOutcome::Denied(Fault::BudgetExhausted);
    }""",
            """    // MUTANT M009 helper: allow charge even when need > available (negative residual)
    let _ = need.saturating_leq(ctx.budget.available);""",
        )
        ok2 = replace_once(
            p("crates/ror-runtime/src/effects.rs"),
            "ctx.budget.available = Consumable::new(ctx.budget.available.units.saturating_sub(need.units));",
            # wrapping_sub yields large positive when underflow — models negative residual as wrap
            "ctx.budget.available = Consumable::new(ctx.budget.available.units.wrapping_sub(need.units));",
        )
        return ok and ok2

    # --- M010 allocate EffectId before authorization (swap order) ---
    if mid == "M010":
        # Move allocate before gate 5 by inserting early allocate and removing later one.
        path = p("crates/ror-runtime/src/effects.rs")
        text = path.read_text(encoding="utf-8")
        needle = """pub fn run_effect_pipeline(ctx: &mut RequestCtx<'_>, effect: Effect) -> RequestOutcome {
    let t = ctx.logical_time;

    // --- Gate 5: Valid CapRef ---
    if let Err(e) = ctx.kernel.valid_result(effect.capability, t) {
        return RequestOutcome::Denied(map_kernel(e));
    }

    // --- Gate 6: Authorize (possession + algebra); ceiling via cost_units in R ---
    let desc = effect.to_desc();
    if let Err(e) = ctx
        .kernel
        .authorize_algebra(Some(ctx.possession), effect.capability, &desc, t)
    {
        return RequestOutcome::Denied(map_kernel(e));
    }
"""
        repl = """pub fn run_effect_pipeline(ctx: &mut RequestCtx<'_>, effect: Effect) -> RequestOutcome {
    let t = ctx.logical_time;

    // MUTANT M010: allocate EffectId BEFORE authorization
    let _early_id = ctx.ids.allocate();

    // --- Gate 5: Valid CapRef ---
    if let Err(e) = ctx.kernel.valid_result(effect.capability, t) {
        return RequestOutcome::Denied(map_kernel(e));
    }

    // --- Gate 6: Authorize (possession + algebra); ceiling via cost_units in R ---
    let desc = effect.to_desc();
    if let Err(e) = ctx
        .kernel
        .authorize_algebra(Some(ctx.possession), effect.capability, &desc, t)
    {
        return RequestOutcome::Denied(map_kernel(e));
    }
"""
        if needle not in text:
            return False
        path.write_text(text.replace(needle, repl, 1), encoding="utf-8")
        return True

    # --- M011 schedule blocked actor ---
    if mid == "M011":
        ok1 = replace_once(
            p("crates/ror-runtime/src/actor.rs"),
            """    pub fn is_schedulable(self) -> bool {
        matches!(self, ActorStatus::Runnable)
    }""",
            """    pub fn is_schedulable(self) -> bool {
        // MUTANT M011: blocked/pending treated as schedulable
        matches!(self, ActorStatus::Runnable | ActorStatus::Blocked | ActorStatus::Pending)
    }""",
        )
        ok2 = replace_once(
            p("crates/ror-runtime/src/actor.rs"),
            """    // Empty → Blocked; remove from runnable; no fuel (R-ACTOR-06).
    actor.status = ActorStatus::Blocked;
    g.runnable.remove(id);
    Ok(None)
}""",
            """    // MUTANT M011: block but keep on runnable queue
    actor.status = ActorStatus::Blocked;
    Ok(None)
}""",
        )
        return ok1 and ok2

    # --- M012    # --- M012 duplicate runnable queue entry ---
    if mid == "M012":
        return replace_once(
            p("crates/ror-runtime/src/actor.rs"),
            """    pub fn enqueue_back(&mut self, id: ActorId) -> bool {
        if self.members.contains(&id) {
            return false;
        }
        self.members.insert(id);
        self.order.push_back(id);
        true
    }""",
            """    pub fn enqueue_back(&mut self, id: ActorId) -> bool {
        // MUTANT M012: allow duplicate runnable queue entries
        self.members.insert(id);
        self.order.push_back(id);
        true
    }""",
        )

    # --- M013 break mailbox FIFO (LIFO) ---
    if mid == "M013":
        return replace_once(
            p("crates/ror-runtime/src/actor.rs"),
            """    pub fn dequeue(&mut self) -> Option<Value> {
        self.messages.pop_front()
    }""",
            """    pub fn dequeue(&mut self) -> Option<Value> {
        // MUTANT M013: LIFO instead of FIFO
        self.messages.pop_back()
    }""",
        )

    # --- M014 accept duplicate canonical map key ---
    if mid == "M014":
        return replace_once(
            p("crates/ror-core/src/canonical/value.rs"),
            """                // R-CANON-06: reject duplicate keys (injectivity).
                if map.insert(key, val).is_some() {
                    return Err(CanonicalError::DuplicateMapKey);
                }""",
            """                // MUTANT M014: accept duplicate keys (last write wins)
                let _ = map.insert(key, val);""",
        )

    # --- M015 ignore WAL sequence gap ---
    if mid == "M015":
        return replace_once(
            p("crates/ror-persistence/src/wal.rs"),
            """            if frame.sequence != expect_seq {
                if frame.sequence.0 < expect_seq.0 {
                    return Err(WalError::SequenceRegression {
                        last: WalSequence(expect_seq.0.saturating_sub(1)),
                        got: frame.sequence,
                    });
                }
                return Err(WalError::SequenceGap {
                    expected: expect_seq,
                    got: frame.sequence,
                });
            }""",
            """            // MUTANT M015: ignore sequence gap/regression
            let _ = expect_seq;
            let _ = frame.sequence;""",
        )

    # --- M016 ignore checksum mismatch ---
    if mid == "M016":
        return replace_once(
            p("crates/ror-persistence/src/wal.rs"),
            """    pub fn verify_checksum(&self, prev: &[u8; 32]) -> Result<(), WalError> {
        let expect = frame_checksum(prev, self.sequence, self.kind, &self.payload);
        if expect != self.checksum {
            return Err(WalError::ChecksumMismatch);
        }
        Ok(())
    }""",
            """    pub fn verify_checksum(&self, prev: &[u8; 32]) -> Result<(), WalError> {
        // MUTANT M016: ignore checksum mismatch
        let _ = prev;
        let _ = self;
        Ok(())
    }""",
        )

    # --- M017    # --- M017    # --- M017 accept mismatched EffectDigest ---
    if mid == "M017":
        return replace_once(
            p("crates/ror-runtime/src/effects.rs"),
            """    if receipt.id != request.id || receipt.effect_digest != request.digest {
        return Err(Fault::ReplayCorruption);
    }""",
            """    // MUTANT M017: accept mismatched EffectDigest (still check id lightly optional)
    if receipt.id != request.id {
        // keep id check weak-pass: also ignore
        let _ = receipt.id;
    }
    let _ = receipt.effect_digest;
    let _ = request.digest;""",
        )

    # --- M018 resume after corrupted receipt ---
    if mid == "M018":
        return replace_once(
            p("crates/ror-runtime/src/effects.rs"),
            """fn validate_and_complete(request: &EffectRequest, receipt: EffectReceipt) -> Result<Value, Fault> {
    if receipt.id != request.id || receipt.effect_digest != request.digest {
        return Err(Fault::ReplayCorruption);
    }
    match receipt.result {
        Ok(rv) => {
            // R-EFFECT-08: ReceiptValue is data-only by construction (no Cap/Fn).
            Ok(receipt_to_value(rv))
        }
        Err(code) => {
            if code == HostFaultCode::POLICY_DENIED {
                Err(Fault::HostPolicyDenied)
            } else {
                Err(Fault::HostFault { code: code.0 })
            }
        }
    }
}""",
            """fn validate_and_complete(request: &EffectRequest, receipt: EffectReceipt) -> Result<Value, Fault> {
    // MUTANT M018: resume after corrupted receipt — ignore id/digest/errors
    let _ = request;
    match receipt.result {
        Ok(rv) => Ok(receipt_to_value(rv)),
        Err(_code) => Ok(Value::Unit),
    }
}""",
        )

    # --- M019 resume with Capability result ---
    if mid == "M019":
        return replace_once(
            p("crates/ror-runtime/src/effects.rs"),
            """            Ok(v) => {
                // Thin completion: optional Completed journal record.
                let result_bytes = match &v {
                    Value::Unit => ReceiptValue::Unit.canonical_bytes(),
                    Value::Bool(b) => ReceiptValue::Bool(*b).canonical_bytes(),
                    Value::Integer(n) => ReceiptValue::Integer(*n).canonical_bytes(),
                    Value::String(s) => ReceiptValue::String(s.clone()).canonical_bytes(),
                    Value::Bytes(b) => ReceiptValue::Bytes(b.clone()).canonical_bytes(),
                    _ => ReceiptValue::Unit.canonical_bytes(),
                };
                let _ = result_bytes;
                let _ = DELTA_T_RECEIPT;
                RequestOutcome::Completed { id, value: v }
            }""",
            """            Ok(_v) => {
                // MUTANT M019: resume with Capability result
                let v = Value::Capability(request.effect.capability);
                let _ = DELTA_T_RECEIPT;
                RequestOutcome::Completed { id, value: v }
            }""",
        )

    # --- M020 resume with closure result ---
    if mid == "M020":
        return replace_once(
            p("crates/ror-runtime/src/effects.rs"),
            """            Ok(v) => {
                // Thin completion: optional Completed journal record.
                let result_bytes = match &v {
                    Value::Unit => ReceiptValue::Unit.canonical_bytes(),
                    Value::Bool(b) => ReceiptValue::Bool(*b).canonical_bytes(),
                    Value::Integer(n) => ReceiptValue::Integer(*n).canonical_bytes(),
                    Value::String(s) => ReceiptValue::String(s.clone()).canonical_bytes(),
                    Value::Bytes(b) => ReceiptValue::Bytes(b.clone()).canonical_bytes(),
                    _ => ReceiptValue::Unit.canonical_bytes(),
                };
                let _ = result_bytes;
                let _ = DELTA_T_RECEIPT;
                RequestOutcome::Completed { id, value: v }
            }""",
            """            Ok(_v) => {
                // MUTANT M020: resume with closure result
                let v = Value::Function(ror_core::machine::FunctionValue {
                    params: vec![],
                    body: Box::new(ror_core::machine::Expr::Value(Value::Unit)),
                    env: ror_core::machine::Environment::empty(),
                });
                let _ = DELTA_T_RECEIPT;
                RequestOutcome::Completed { id, value: v }
            }""",
        )

    # --- M021 authorize without possession check ---
    if mid == "M021":
        return replace_once(
            p("crates/ror-kernel/src/lib.rs"),
            """        if let Some(ctx) = holder {
            if !ctx.contains(cap) {
                return Err(KernelFault::Unauthorized);
            }
        }""",
            """        // MUTANT M021: authorize without possession check
        let _ = holder;
        let _ = cap;""",
        )

    # --- M022 unmarshal accepts capability payload ---
    if mid == "M022":
        ok1 = replace_once(
            p("crates/ror-core/src/canonical/data_decode.rs"),
            """        if tag == TAG_CAP_REF {
            // Validate framing so malformed CapRef still surfaces framing errors,
            // then reject as capability-in-data.
            let mut cursor = ReadCursor::new(bytes);
            let _payload = cursor.read_envelope_payload(TAG_CAP_REF)?;
            cursor.expect_eof()?;
            return Err(CanonicalError::CapabilityInData);
        }""",
            """        if tag == TAG_CAP_REF {
            // MUTANT M022: accept capability payload on data decode path
            return CapRef::decode_canonical(bytes).map(Value::Capability);
        }""",
        )
        ok2 = replace_once(
            p("crates/ror-core/src/canonical/value.rs"),
            """        Value::TAG_CAPABILITY => {
            // R-CANON-12: data decoder must not mint authority from bytes.
            // Consume the nested envelope for strictness, then reject.
            let _ = cursor.read_envelope_payload(CapRef::TYPE_TAG)?;
            Err(CanonicalError::CapabilityInData)
        }""",
            """        Value::TAG_CAPABILITY => {
            // MUTANT M022: mint capability from data bytes
            let payload = cursor.read_envelope_payload(CapRef::TYPE_TAG)?;
            let mut c = ReadCursor::new(payload);
            let cap = CapRef::decode_payload(&mut c)?;
            c.expect_eof()?;
            Ok(Value::Capability(cap))
        }""",
        )
        return ok1 or ok2

    # --- M023    # --- M023 recovery resurrects revoked capability ---
    if mid == "M023":
        # Clear revoked list at end of recover by emptying revoked_caps assignment.
        ok = replace_once(
            p("crates/ror-persistence/src/recovery.rs"),
            "revoked_caps: revoked,",
            "revoked_caps: Vec::new(), // MUTANT M023: drop revocations (resurrect)",
        )
        ok2 = replace_once(
            p("crates/ror-persistence/src/recovery.rs"),
            """                if let JournalRecord::CapRevoked { cap } = &rec {
                    revoked.push((cap.index(), cap.generation()));
                }""",
            """                if let JournalRecord::CapRevoked { cap } = &rec {
                    let _ = cap; // MUTANT M023: ignore revoke records
                }""",
        )
        return ok and ok2

    # --- M024    # --- M024 receive-side registration without kernel revalidation ---
    if mid == "M024":
        return replace_once(
            p("crates/ror-runtime/src/actor.rs"),
            """    if envelope.target_actor() != recipient.0 {
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
    a.caps.insert(child);""",
            """    // MUTANT M024: register without kernel revalidation
    let _ = kernel;
    let _ = before_slots;
    let child = envelope.child_cap();
    let a = g.actors.get_mut(&recipient).ok_or(Fault::ActorNotFound)?;
    a.caps.insert(child);""",
        )

    # --- M025    # --- M025 spawn clones parent context unattenuated ---
    if mid == "M025":
        return replace_once(
            p("crates/ror-runtime/src/actor.rs"),
            """    let t = g.logical_time;
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
    }""",
            """    // MUTANT M025: clone parent context unattenuated (ignore manifest derive)
    let _ = kernel;
    let _ = manifest;
    let child_caps = parent_state.caps.clone();""",
        )

    # --- M026    # --- M026 accept future-tagged proposal ---
    if mid == "M026":
        return replace_once(
            p("crates/ror-agent/src/lib.rs"),
            """    if proposal.observation_sequence != current_planning_epoch {
        return Err(PlannerFault::StalePlan);
    }
    Ok(())""",
            """    // MUTANT M026: accept future-tagged (only reject strictly less)
    if proposal.observation_sequence < current_planning_epoch {
        return Err(PlannerFault::StalePlan);
    }
    Ok(())""",
        )

    # --- M027 observation includes CapRef ---
    if mid == "M027":
        return replace_once(
            p("crates/ror-agent/src/lib.rs"),
            """pub fn admit_observation(obs: &ObservationRecord) -> Result<(), PlannerFault> {
    match &obs.payload {
        ObservationPayload::Data(_) => Ok(()),
        ObservationPayload::Capability(_) => Err(PlannerFault::ObservationAuthority),
    }
}""",
            """pub fn admit_observation(obs: &ObservationRecord) -> Result<(), PlannerFault> {
    // MUTANT M027: allow CapRef in observation
    let _ = obs;
    Ok(())
}""",
        )

    # --- M028 Indeterminate as NotExecuted ---
    if mid == "M028":
        return replace_once(
            p("crates/ror-persistence/src/recovery.rs"),
            """            // T2–T4 Indeterminate — NEVER NotExecuted
            out.push(EffectClass::Indeterminate {
                id: eid,
                digest: d,
                actor,
                effect_bytes: bytes,
            });""",
            """            // MUTANT M028: resolve Indeterminate as Discard (wrong class)
            out.push(EffectClass::Discard { id: eid, digest: d });
            let _ = actor;
            let _ = bytes;""",
        )

    # --- M029 replay skips result-digest verification ---
    if mid == "M029":
        return replace_once(
            p("crates/ror-host/src/lib.rs"),
            """pub fn verify_result_digest(
    expected: &ror_core::digest::EffectDigest,
    result_bytes: &[u8],
) -> Result<(), HostError> {
    let got = ror_core::digest::EffectDigest::of_bytes(result_bytes);
    if got != *expected {
        return Err(HostError::ReplayFault);
    }
    Ok(())
}""",
            """pub fn verify_result_digest(
    expected: &ror_core::digest::EffectDigest,
    result_bytes: &[u8],
) -> Result<(), HostError> {
    // MUTANT M029: skip result-digest verification
    let _ = expected;
    let _ = result_bytes;
    Ok(())
}""",
        )

    # --- M030 inadmissible constraint treated as ⊤ ---
    if mid == "M030":
        return replace_once(
            p("crates/ror-kernel/src/lib.rs"),
            """        if !admissible_constraint_wrt_parent(constraint, &parent_auth) {
            return Err(KernelFault::InvalidConstraint);
        }""",
            """        // MUTANT M030: inadmissible constraint treated as top (identity)
        if !admissible_constraint_wrt_parent(constraint, &parent_auth) {
            // return parent unchanged conceptually: still derive with empty meet skip
            let child_auth = parent_auth.clone();
            let lifetime = parent_lifetime;
            let node = AuthorityNode {
                authority: child_auth,
                parent: Some(parent),
                live: true,
                lifetime,
                generation: 0,
            };
            return Ok(self.insert_node(node));
        }""",
        )

    # --- M031 superseded LE grammar ---
    if mid == "M031":
        # Force little-endian on a BE-required length field in canonical encode path.
        path = p("crates/ror-core/src/canonical/primitives.rs")
        if not path.exists():
            path = p("crates/ror-core/src/canonical/value.rs")
        text = path.read_text(encoding="utf-8")
        # Prefer swapping to_be_bytes -> to_le_bytes on u32 length writes
        if "to_be_bytes()" in text:
            path.write_text(text.replace("to_be_bytes()", "to_le_bytes()", 1), encoding="utf-8")
            return True
        # fallback value encode
        path = p("crates/ror-core/src/canonical/value.rs")
        text = path.read_text(encoding="utf-8")
        if "to_be_bytes()" in text:
            path.write_text(text.replace("to_be_bytes()", "to_le_bytes()", 1), encoding="utf-8")
            return True
        return False

    # --- M032 contains_capability skips FunctionValue.env ---
    if mid == "M032":
        return replace_once(
            p("crates/ror-runtime/src/actor.rs"),
            """        // R-MARSHAL-06 / M032: must walk FunctionValue.env (not skip).
        Value::Function(f) => f
            .env
            .bindings()
            .iter()
            .any(|(_, val)| machine_contains_capability(val)),""",
            """        // MUTANT M032: skip FunctionValue.env
        Value::Function(_f) => false,""",
        )

    # --- M033 enqueue without recipient capacity check ---
    if mid == "M033":
        return replace_once(
            p("crates/ror-runtime/src/actor.rs"),
            """    pub fn try_enqueue(&mut self, msg: Value) -> Result<(), Fault> {
        if self.messages.len() as u64 >= self.capacity {
            return Err(Fault::ReservedCapacityExceeded);
        }
        self.messages.push_back(msg);
        Ok(())
    }""",
            """    pub fn try_enqueue(&mut self, msg: Value) -> Result<(), Fault> {
        // MUTANT M033: no capacity check
        self.messages.push_back(msg);
        Ok(())
    }""",
        )

    # --- M034 release failure silently ignored ---
    if mid == "M034":
        return replace_once(
            p("crates/ror-runtime/src/effects.rs"),
            """    if let Err(e) = ctx.journal.append(prep) {
        rollback_alloc(ctx, prev_next, prev_avail, prev_res);
        return RequestOutcome::Denied(map_persist(e));
    }
    if let Err(e) = ctx.journal.sync() {
        rollback_alloc(ctx, prev_next, prev_avail, prev_res);
        return RequestOutcome::Denied(map_persist(e));
    }

    let iss = issued(id, actor, digest, effect_bytes.clone(), cost);
    if let Err(e) = ctx.journal.append(iss) {
        rollback_alloc(ctx, prev_next, prev_avail, prev_res);
        return RequestOutcome::Denied(map_persist(e));
    }
    if let Err(e) = ctx.journal.sync() {
        rollback_alloc(ctx, prev_next, prev_avail, prev_res);
        return RequestOutcome::Denied(map_persist(e));
    }""",
            """    // MUTANT M034: ignore journal failures (let _ pattern)
    let _ = ctx.journal.append(prep);
    let _ = ctx.journal.sync();
    let iss = issued(id, actor, digest, effect_bytes.clone(), cost);
    let _ = ctx.journal.append(iss);
    let _ = ctx.journal.sync();""",
        )

    # --- M035    # --- M035 stranded escrow silently reclaimed ---
    if mid == "M035":
        return replace_once(
            p("crates/ror-runtime/src/effects.rs"),
            """        Err(he) => {
            let fault = match he {
                HostError::PolicyDenied => Fault::HostPolicyDenied,
                other => Fault::HostFault {
                    code: other.code().0,
                },
            };
            RequestOutcome::HostFailed { id, fault }
        }""",
            """        Err(he) => {
            let fault = match he {
                HostError::PolicyDenied => Fault::HostPolicyDenied,
                other => Fault::HostFault {
                    code: other.code().0,
                },
            };
            // MUTANT M035: reclaim escrow to available without reconciliation
            ctx.budget.available =
                Consumable::new(ctx.budget.available.units.saturating_add(need.units));
            RequestOutcome::HostFailed { id, fault }
        }""",
        )

    # --- M036 document mutant: rotate obligation body (spec layer) ---
    if mid == "M036":
        # Apply a D3-style body rotation on a known obligation pair via checker mutation path.
        # Prefer mutating a copy of a small obligation file if present; else use audit harness method.
        # We rotate two adjacent lines in final/01 R-TEST block as a document defect —
        # the adopted gate is check.py / spec/_check --allowlist (U-38).
        # For isolated tree: swap two obligation short descriptions in final/04 table.
        path = p("final/04-verification-registry.md")
        text = path.read_text(encoding="utf-8")
        a = "| M001 | reverse argument evaluation | R-CEK-05 (LTR) |"
        b = "| M002 | skip arity precheck | R-CEK-05 |"
        if a in text and b in text:
            text = text.replace(a, "| M001 | skip arity precheck | R-CEK-05 (LTR) |", 1)
            text = text.replace(b, "| M002 | reverse argument evaluation | R-CEK-05 |", 1)
            path.write_text(text, encoding="utf-8")
            return True
        return False

    # --- M037 host-visible pre-durability (in-memory before fsync) ---
    if mid == "M037":
        # Call host before issued sync completes: move host before second sync.
        return replace_once(
            p("crates/ror-runtime/src/effects.rs"),
            """    let iss = issued(id, actor, digest, effect_bytes.clone(), cost);
    if let Err(e) = ctx.journal.append(iss) {
        rollback_alloc(ctx, prev_next, prev_avail, prev_res);
        return RequestOutcome::Denied(map_persist(e));
    }
    if let Err(e) = ctx.journal.sync() {
        rollback_alloc(ctx, prev_next, prev_avail, prev_res);
        return RequestOutcome::Denied(map_persist(e));
    }

    // Durable Issued confirmed — only now may host run (step 16).
    let request = EffectRequest {
        id,
        actor,
        digest,
        effect_bytes,
        cost,
        effect,
    };

    // --- Step 16: host ---
    match ctx.host.execute(&request) {""",
            """    let iss = issued(id, actor, digest, effect_bytes.clone(), cost);
    if let Err(e) = ctx.journal.append(iss) {
        rollback_alloc(ctx, prev_next, prev_avail, prev_res);
        return RequestOutcome::Denied(map_persist(e));
    }
    // MUTANT M037: host before durable sync (pre-durability visibility)
    let request = EffectRequest {
        id,
        actor,
        digest,
        effect_bytes: effect_bytes.clone(),
        cost,
        effect: effect.clone(),
    };
    let early = ctx.host.execute(&request);
    if let Err(e) = ctx.journal.sync() {
        rollback_alloc(ctx, prev_next, prev_avail, prev_res);
        return RequestOutcome::Denied(map_persist(e));
    }
    let _ = early;

    // Durable Issued confirmed — only now may host run (step 16).
    let request = EffectRequest {
        id,
        actor,
        digest,
        effect_bytes,
        cost,
        effect,
    };

    // --- Step 16: host ---
    match ctx.host.execute(&request) {""",
        )

    # --- M038 issuance records carry {id,actor,digest} only ---
    if mid == "M038":
        return replace_once(
            p("crates/ror-persistence/src/lib.rs"),
            """pub fn issued(
    id: EffectId,
    actor: ActorId,
    digest: EffectDigest,
    effect_bytes: Vec<u8>,
    cost: EffectCost,
) -> IssuanceRecord {
    IssuanceRecord::Issued {
        id,
        actor,
        digest,
        effect_bytes,
        cost,
    }
}""",
            """pub fn issued(
    id: EffectId,
    actor: ActorId,
    digest: EffectDigest,
    effect_bytes: Vec<u8>,
    cost: EffectCost,
) -> IssuanceRecord {
    // MUTANT M038: drop escrow/effect cost source of truth
    let _ = cost;
    let _ = effect_bytes;
    IssuanceRecord::Issued {
        id,
        actor,
        digest,
        effect_bytes: Vec::new(),
        cost: EffectCost::zero(),
    }
}""",
        )

    # --- M039 Remains-Indeterminate terminal ---
    if mid == "M039":
        return replace_once(
            p("crates/ror-runtime/src/actor.rs"),
            """        for id in &pending {
            // Record Indeterminate binding (thin R-RECOV-08); keep Pending status
            // (do not cancel / NotExecuted).
            g.events
                .push(MachineEvent::EffectIndeterminate { actor: *id });
        }""",
            """        for id in &pending {
            // MUTANT M039: treat remains-indeterminate as terminal disposition
            g.events
                .push(MachineEvent::EffectIndeterminate { actor: *id });
            if let Some(a) = g.actors.get_mut(id) {
                a.status = ActorStatus::Terminal;
            }
        }""",
        )

    # --- M040 δ_t table violation ---
    if mid == "M040":
        ok1 = replace_once(
            p("crates/ror-runtime/src/actor.rs"),
            """        g.events.push(MachineEvent::ActorSelected { id });
        run_one_transition(g, kernel, id)?;
        // δ_t carried by transition: pure/spawn/send/receive/blocked = 0.
        return Ok(GlobalStep::Turn { actor: id });""",
            """        g.events.push(MachineEvent::ActorSelected { id });
        run_one_transition(g, kernel, id)?;
        // MUTANT M040: charge +1 logical time on every scheduler turn
        g.logical_time = LogicalTime(g.logical_time.get().saturating_add(1));
        return Ok(GlobalStep::Turn { actor: id });""",
        )
        # also break spawn_does_not_advance by advancing on spawn
        ok2 = replace_once(
            p("crates/ror-runtime/src/actor.rs"),
            """    // δ_t(spawn)=0 — no logical time advance (R-BUDGET-16).
    Ok(child_id)
}""",
            """    // MUTANT M040: spawn advances logical time
    g.logical_time = LogicalTime(g.logical_time.get().saturating_add(1));
    Ok(child_id)
}""",
        )
        return ok1 or ok2

    # --- M041    # --- M041 post-deadline receipt through normal deadline gate ---
    if mid == "M041":
        return replace_once(
            p("crates/ror-runtime/src/effects.rs"),
            """            Ok(v) => {
                // Thin completion: optional Completed journal record.
                let result_bytes = match &v {
                    Value::Unit => ReceiptValue::Unit.canonical_bytes(),
                    Value::Bool(b) => ReceiptValue::Bool(*b).canonical_bytes(),
                    Value::Integer(n) => ReceiptValue::Integer(*n).canonical_bytes(),
                    Value::String(s) => ReceiptValue::String(s.clone()).canonical_bytes(),
                    Value::Bytes(b) => ReceiptValue::Bytes(b.clone()).canonical_bytes(),
                    _ => ReceiptValue::Unit.canonical_bytes(),
                };
                let _ = result_bytes;
                let _ = DELTA_T_RECEIPT;
                RequestOutcome::Completed { id, value: v }
            }""",
            """            Ok(v) => {
                // MUTANT M041: always re-apply deadline gate on receipt (wrong settlement)
                return RequestOutcome::Denied(Fault::DeadlineExceeded);
                let _ = v;
                let _ = DELTA_T_RECEIPT;
                RequestOutcome::Completed { id, value: Value::Unit }
            }""",
        )

    # --- M042    # --- M042 double duration charge ---
    if mid == "M042":
        return replace_once(
            p("crates/ror-runtime/src/effects.rs"),
            """    // Charge issue+complete_max escrow; hold reserve slots.
    ctx.budget.available = Consumable::new(ctx.budget.available.units.saturating_sub(need.units));
    ctx.budget.reserved =
        Reserved::new(ctx.budget.reserved.slots.saturating_sub(cost.reserve.slots));""",
            """    // Charge issue+complete_max escrow; hold reserve slots.
    ctx.budget.available = Consumable::new(ctx.budget.available.units.saturating_sub(need.units));
    ctx.budget.reserved =
        Reserved::new(ctx.budget.reserved.slots.saturating_sub(cost.reserve.slots));
    // MUTANT M042: double-charge duration component from cost (diagnostic must not debit)
    let dur = cost.issue.units; // stand-in for duration component of cost_C(E)
    ctx.budget.available =
        Consumable::new(ctx.budget.available.units.saturating_sub(dur));""",
        )

    return False


# Targeted test filters per mutant (cargo test filter substring).
TARGETED = {
    "M001": ("ror-runtime", "call_two_args_ltr_binding"),
    "M002": ("ror-runtime", "arity_mismatch_before_arg_eval"),
    "M003": ("ror-runtime", "non_function_call"),
    "M004": ("ror-kernel", "revoke_cascades_to_descendant"),
    "M005": ("ror-core", "authorized_rejects_over_ceiling"),  # ceiling via authorized tests in kernel
    "M006": ("ror-kernel", "amplify_attempt_via_extra_op_rejected"),
    "M007": ("ror-runtime", "deny_budget_never_hosts"),
    "M008": ("ror-runtime", "host_fail_does_not_release_escrow"),
    "M009": ("ror-runtime", "deny_budget_never_hosts"),
    "M010": ("ror-runtime", "deny_path_effect_id_not_consumed"),
    "M011": ("ror-runtime", "blocked_status_not_schedulable"),
    "M012": ("ror-runtime", "runnable_at_most_once"),
    "M013": ("ror-runtime", "mailbox_fifo"),
    "M014": ("ror-core", "duplicate_map_key_rejected"),
    "M015": ("ror-persistence", "mutation_sequence_gap_kills"),
    "M016": ("ror-persistence", "verify_checksum_detects_tamper"),
    "M017": ("ror-runtime", "mismatched_receipt_digest_is_corruption"),
    "M018": ("ror-runtime", "mismatched_receipt_digest_is_corruption"),
    "M019": ("ror-runtime", "receipt_value_is_unit_data_only"),
    "M020": ("ror-runtime", "receipt_value_is_unit_data_only"),
    "M021": ("ror-runtime", "deny_unauthorized_never_hosts"),
    "M022": ("ror-core", "golden_capref_kernel_only"),
    "M023": ("ror-persistence", "mutation_cap_revocation_monotonic"),
    "M024": ("ror-runtime", "delegation_wrong_target_leaves_ctx_identical"),
    "M025": ("ror-runtime", "spawn_empty_manifest_does_not_clone_parent_caps"),
    "M026": ("ror-agent", "accept_current_only"),
    "M027": ("ror-agent", "observation_rejects_capref"),
    "M028": ("ror-persistence", "t2_issued_indeterminate"),  # may need filter name
    "M029": ("ror-host", "result_digest_mismatch_rejected"),
    "M030": ("ror-kernel", "amplify_attempt_via_extra_op_rejected"),
    "M031": ("ror-core", "golden"),
    "M032": ("ror-runtime", "machine_contains_capability_walks_function_env"),
    "M033": ("ror-runtime", "mailbox_capacity_sender_pays"),
    "M034": ("ror-runtime", "persist_fail_no_host"),
    "M035": ("ror-runtime", "host_fail_does_not_release_escrow"),
    "M036": ("document", None),
    "M037": ("ror-runtime", "host_invoked_exactly_once_on_success"),
    "M038": ("ror-persistence", "issued_preserves_cost"),
    "M039": ("ror-runtime", "quiescence_indeterminate_no_time_or_budget_mut"),
    "M040": ("ror-runtime", "spawn_does_not_advance_logical_time"),
    "M041": ("ror-runtime", "completed_receipt_not_deadline_denied"),
    "M042": ("ror-runtime", "budget_charge_matches_issue_plus_complete_max_only"),
}

DIFFERENTIAL = {
    "M001": ("ror-differential", "m3"),
    "M002": ("ror-differential", "m3"),
    "M003": ("ror-differential", "m3"),
    "M004": ("ror-differential", "m4"),
    "M006": ("ror-differential", "m4"),
    "M011": ("ror-differential", "m6"),
    "M012": ("ror-differential", "m6"),
    "M013": ("ror-differential", "m6"),
    "M015": ("ror-differential", "m7"),
    "M016": ("ror-differential", "m7"),
    "M023": ("ror-differential", "m7"),
    "M025": ("ror-differential", "m6"),
    "M028": ("ror-differential", "m7"),
}


def run_document_m036(root: Path) -> Result:
    """M036: document mutant killed by repository gate (U-38 allowlist)."""
    # Run check.py or the M036-specific checker mutation path.
    # Adopted gate: python3 check.py includes audit/_checker_mutations which locks K18/M036.
    # Simpler direct: run audit/_checker_mutations.py -k M036 if present, else check.py subset.
    cp = run([sys.executable, str(root / "audit" / "_checker_mutations.py"), "-k", "M036"], root, timeout=600)
    out = cp.stdout or ""
    killed = cp.returncode != 0 or "KILLED" in out.upper() or "killed" in out.lower()
    # The checker_mutations harness exits 0 only if mutations are killed — for -k M036,
    # exit 0 means the M036 injection was detected (killed). Confirm semantics:
    # From header: "Exit 0 iff every mutation is killed."
    if cp.returncode == 0:
        classification = "KILLED"
        targeted_failed = True
        evidence = "audit/_checker_mutations.py -k M036 exit 0 (mutant killed by gate)"
    else:
        # try check.py allowlist path after rotation already applied in scratch
        cp2 = run([sys.executable, str(root / "check.py"), "-q"], root, timeout=600)
        if cp2.returncode != 0:
            classification = "KILLED"
            targeted_failed = True
            evidence = "check.py failed after M036 rotation"
        else:
            classification = "SURVIVED"
            targeted_failed = False
            evidence = f"M036 survived: mut_rc={cp.returncode} check_rc={cp2.returncode}"
    return Result(
        mid="M036",
        classification=classification,
        build_ok=True,
        targeted_failed=targeted_failed,
        differential_failed=False,
        kill_evidence=evidence,
        security=False,
        obligations=["R-SCOPE-03", "R-CLAIM-02"],
        defect="rotate obligation body",
    )


def classify_run(
    meta: MutantMeta,
    build: subprocess.CompletedProcess | None,
    targeted: subprocess.CompletedProcess | None,
    differential: subprocess.CompletedProcess | None,
) -> Result:
    build_ok = build is None or build.returncode == 0
    t_fail = targeted is not None and targeted.returncode != 0
    d_fail = differential is not None and differential.returncode != 0

    # Compilation failure alone is NOT a kill unless tests also run — R-TEST-06 wants tests.
    # Exception: if mutant does not compile, treat as INCONCLUSIVE (not KILLED).
    if build is not None and build.returncode != 0:
        return Result(
            mid=meta.mid,
            classification="INCONCLUSIVE",
            build_ok=False,
            targeted_failed=False,
            differential_failed=False,
            kill_evidence="build failed",
            security=meta.security,
            obligations=meta.obligations,
            defect=meta.defect,
        )

    if t_fail or d_fail:
        evidence_parts = []
        if t_fail:
            evidence_parts.append("targeted_tests_failed")
        if d_fail:
            evidence_parts.append("differential_tests_failed")
        return Result(
            mid=meta.mid,
            classification="KILLED",
            build_ok=True,
            targeted_failed=t_fail,
            differential_failed=d_fail,
            kill_evidence="+".join(evidence_parts),
            security=meta.security,
            obligations=meta.obligations,
            defect=meta.defect,
        )

    return Result(
        mid=meta.mid,
        classification="SURVIVED",
        build_ok=True,
        targeted_failed=False,
        differential_failed=False,
        kill_evidence="all selected tests passed under mutant",
        security=meta.security,
        obligations=meta.obligations,
        defect=meta.defect,
    )


def execute_one(meta: MutantMeta, keep_scratch: Path | None = None) -> Result:
    if meta.equiv:
        return Result(
            mid=meta.mid,
            classification="EQUIVALENT",
            build_ok=True,
            targeted_failed=False,
            differential_failed=False,
            kill_evidence="canonical equivalent disposition",
            security=meta.security,
            obligations=meta.obligations,
            defect=meta.defect,
        )

    scratch = Path(tempfile.mkdtemp(prefix=f"m9-{meta.mid}-"))
    try:
        copy_tree(REPO, scratch)
        if meta.mid == "M036" or meta.kind == "document":
            if not apply_mutant(scratch, "M036"):
                return Result(
                    mid=meta.mid,
                    classification="INCONCLUSIVE",
                    build_ok=False,
                    targeted_failed=False,
                    differential_failed=False,
                    kill_evidence="could not apply document mutant",
                    security=meta.security,
                    obligations=meta.obligations,
                    defect=meta.defect,
                )
            # Document path: use checker gate
            # For M036 rotation in final/04, also run the official M036 harness.
            return run_document_m036(scratch)

        if not apply_mutant(scratch, meta.mid):
            return Result(
                mid=meta.mid,
                classification="INCONCLUSIVE",
                build_ok=False,
                targeted_failed=False,
                differential_failed=False,
                kill_evidence="operator could not apply (anchor mismatch)",
                security=meta.security,
                obligations=meta.obligations,
                defect=meta.defect,
            )

        # Build package under test (faster than full workspace when possible)
        pkg, filt = TARGETED.get(meta.mid, (meta.component if meta.component.startswith("ror-") else "ror-core", None))
        if pkg == "document":
            pkg = "ror-core"

        build = run(["cargo", "test", "-p", pkg, "--lib", "--no-run"], scratch, timeout=600)
        if build.returncode != 0:
            # try workspace check
            build = cargo_check(scratch)

        targeted_cp = None
        if build.returncode == 0 and filt:
            targeted_cp = cargo_test(scratch, pkg, filt, timeout=300)
            # If filter matched nothing, cargo still exits 0 — broaden to package tests.
            if targeted_cp.returncode == 0 and "running 0 tests" in (targeted_cp.stdout or ""):
                targeted_cp = cargo_test(scratch, pkg, None, timeout=600)

        diff_cp = None
        if meta.differential and build.returncode == 0:
            dpkg, dfilt = DIFFERENTIAL.get(meta.mid, ("ror-differential", None))
            diff_cp = cargo_test(scratch, dpkg, dfilt, timeout=600)

        return classify_run(meta, build, targeted_cp, diff_cp)
    finally:
        if keep_scratch is None:
            shutil.rmtree(scratch, ignore_errors=True)
        else:
            keep_scratch.mkdir(parents=True, exist_ok=True)
            # leave last scratch path recorded
            (keep_scratch / f"{meta.mid}.path").write_text(str(scratch), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-k", "--only", help="run single mutant id")
    ap.add_argument("-o", "--out", type=Path, default=REPO / "mutations" / "m9-results.json")
    ap.add_argument("--matrix", type=Path, default=REPO / "mutations" / "m9-matrix.md")
    args = ap.parse_args()

    registry = parse_registry(REGISTRY.read_text(encoding="utf-8"))
    if len(registry) != 42:
        print(f"BLOCK-CANONICAL: registry count {len(registry)} != 42", file=sys.stderr)
        return 2

    ids = [m.mid for m in registry]
    expected = [f"M{i:03d}" for i in range(1, 43)]
    if ids != expected:
        print(f"BLOCK-CANONICAL: id order/set mismatch: {ids}", file=sys.stderr)
        return 2

    if args.only:
        registry = [m for m in registry if m.mid == args.only]
        if not registry:
            print("unknown mutant", file=sys.stderr)
            return 2

    results: list[Result] = []
    for i, meta in enumerate(registry, 1):
        print(f"[{i}/{len(registry)}] {meta.mid} …", flush=True)
        r = execute_one(meta)
        print(
            f"  → {r.classification} build_ok={r.build_ok} "
            f"targeted_fail={r.targeted_failed} diff_fail={r.differential_failed} "
            f"evidence={r.kill_evidence}",
            flush=True,
        )
        results.append(r)

    # Kill-rate
    equivalent = sum(1 for r in results if r.classification == "EQUIVALENT")
    non_eq = len(results) - equivalent
    killed = sum(1 for r in results if r.classification == "KILLED")
    survived = sum(1 for r in results if r.classification == "SURVIVED")
    not_run = sum(1 for r in results if r.classification == "NOT-RUN")
    inconclusive = sum(1 for r in results if r.classification == "INCONCLUSIVE")
    rate = int(killed * 100 / non_eq) if non_eq else 0
    critical_survived = any(
        r.security and r.classification == "SURVIVED" for r in results
    )

    payload = {
        "registered": len(results),
        "non_equivalent": non_eq,
        "killed": killed,
        "survived": survived,
        "equivalent": equivalent,
        "not_run": not_run,
        "inconclusive": inconclusive,
        "kill_rate_percent": rate,
        "critical_survived": critical_survived,
        "results": [r.__dict__ for r in results],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # Human matrix
    lines = [
        "# M9 Mutation Matrix",
        "",
        "| ID | Classification | Build | Targeted fail | Diff fail | Security | Evidence |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r.mid} | {r.classification} | {r.build_ok} | {r.targeted_failed} | "
            f"{r.differential_failed} | {r.security} | {r.kill_evidence} |"
        )
    lines += [
        "",
        f"**Kill rate:** {rate}%  ({killed}/{non_eq} non-equivalent)",
        f"**Critical survived:** {critical_survived}",
    ]
    args.matrix.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({k: payload[k] for k in payload if k != "results"}, indent=2))
    if critical_survived:
        return 3
    if rate != 100 or survived or not_run or inconclusive:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
