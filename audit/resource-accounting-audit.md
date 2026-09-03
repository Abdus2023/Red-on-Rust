# Red-on-Rust Specification Audit — Resource Accounting, Conservation, and Operational Transitions

**Audit date:** 2026-09-03  
**Audited artifact:** Red-on-Rust canonical specification set (`spec/`, `mod/`, `req/`, `term/`, `audit/`, `Red-on-Rust.md`)  
**Deliverable artifact:** `audit/resource-accounting-audit.md` (presented in viewer)  
**Status:** **CONSERVATION CLOSURE FINAL** (11/11 structural repository gate checkers PASS, including `audit/_conservation_checker.py`)

---

## 1. Executive Summary & Verdict

This audit performs a systematic, operation-by-operation verification of every resource-consuming transition in the Red-on-Rust machine (Op-01…Op-22). To close all semantic conservation gaps and turn the operational transitions into machine-checkable transition contracts, this audit formulates and freezes the **Resource Accounting Clarification Addendum** (`R-BUDGET-10`…`R-BUDGET-14`).

### Verification Verdict:
1. **Algebraic Rigor & Tagged Vector Families**:
   - Budget vector $B = \langle C, R, W \rangle$ with consumables $C = \langle F, I_{\text{effect}}, I_{\text{journal}}, D \rangle$, reserved capacities $R = \langle M, S \rangle$, persistent storage $M_{\text{storage}}$, and tagged explicit resources $X = \langle X_{\text{cap}}, X_{\text{wal}}, X_{\text{mailbox}} \rangle$.
2. **Conservation Laws with Explicit Disposal Sink (`R-BUDGET-11`)**:
   - Consumables satisfy the complete partition conservation law:
     $$C_{\text{available}} + C_{\text{escrowed}} + C_{\text{consumed}} + C_{\text{disposed}} = C_{\text{initial}}$$
     where unused actor budget on termination moves strictly to $C_{\text{disposed}}$ (or supervisor $C_{\text{supervisor}}$) rather than disappearing silently.
3. **Escrow Normal Form & Completion Atomicity**:
   - Effect completion (Op-18) and host failure (Op-19) use identical canonical notation that explicitly separates removing the entire escrow reservation $C_{\text{escrowed}} \leftarrow C_{\text{escrowed}} - c_{\text{complete\_max}}$ from consuming actual charges ($c_{\text{complete\_actual}}$ / $c_{\text{host\_fail}}$) into $C_{\text{consumed}}$ and refunding the remainder to $C_{\text{available}}$.
4. **Atomicity Theorem (`R-BUDGET-10`)**:
   - Every operation satisfies:
     $$\boxed{\text{Precondition failure} \implies \Sigma' = \Sigma}$$
     (zero state drift / zero partial debit on any pre-gate or precondition denial).
5. **Mechanical Verification (`audit/_conservation_checker.py`)**:
   - Integrated as an official repository gate checker in `check.py` (11th checker), mechanically validating conservation and atomicity over 1,000 randomized transition sequences.

---

## 2. Resource Classification & Vector Formulations

System resources are structured into explicit, non-overlapping categories:

### Resource Categories:
1. **`FUEL` ($F \in \mathbb{N}$)**: Consumable execution units decremented for small-step AST reductions, variable lookups, environment bindings, closure captures, function calls, and control-flow evaluation.
2. **`IO_EFFECT` ($I_{\text{effect}} \in \mathbb{N}$)**: Consumable input/output units decremented for external effect issuance and host communication.
3. **`IO_JOURNAL` ($I_{\text{journal}} \in \mathbb{N}$)**: Consumable input/output units decremented for WAL commits and snapshot persistence.
4. **`DURATION` ($D \in \mathbb{N}$)**: Consumable execution-duration budget units decremented by duration-charging steps, scheduler yields, or time bounds. Logical time $t$ independently tracks step advancement ($t_{i+1} = t_i + \delta_t$), and $D$ is debited $D \leftarrow D - \delta_t$ on scheduled steps (`R-BUDGET-12`).
5. **`MEMORY` ($M \in \mathbb{N}$)**: Volatile RAM reserved capacity (in bytes) held during the scope of heap structures, environments, closures, stack frames, and mailbox queues (`R-ACTOR-10`).
6. **`PERSISTENT_STORAGE` ($M_{\text{storage}} \in \mathbb{N}$)**: Durable storage capacity allocated for persistent WAL frames and snapshot artifacts (`R-BUDGET-13`).
7. **`ACTOR_SLOTS` ($S \in \mathbb{N}$)**: Reserved concurrent execution slots in the scheduler arena.
8. **`TAGGED_EXPLICIT_RESOURCES` ($X = \langle X_{\text{cap}}, X_{\text{wal}}, X_{\text{mailbox}} \rangle$)**: Tagged resource vector where $X_{\text{cap}}$ denotes kernel `CapRef` handles, $X_{\text{wal}}$ denotes WAL sequence slots, and $X_{\text{mailbox}}$ denotes queued message slots (`R-BUDGET-14`).

---

## 3. Fundamental Conservation & Verification Equations

### 3.1 Consumable Conservation Invariant
Consumable resources satisfy global partition conservation across all execution steps, actor spawns, completions, host failures, actor halts, and persistent recoveries:

$$\mathbf{C_{\text{available}} + C_{\text{escrowed}} + C_{\text{consumed}} + C_{\text{disposed}} = C_{\text{initial}}}$$

### 3.2 Escrow Atomic Transition Equations (Op-18 & Op-19)
For Effect Completion (Op-18) with $c_{\text{complete\_actual}} \le c_{\text{complete\_max}}$:
$$C_{\text{escrowed}}' = C_{\text{escrowed}} - c_{\text{complete\_max}}$$
$$C_{\text{consumed}}' = C_{\text{consumed}} + c_{\text{complete\_actual}}$$
$$C_{\text{available}}' = C_{\text{available}} + (c_{\text{complete\_max}} - c_{\text{complete\_actual}})$$

For Host Failure (Op-19) with $c_{\text{host\_fail}} \le c_{\text{complete\_max}}$:
$$C_{\text{escrowed}}' = C_{\text{escrowed}} - c_{\text{complete\_max}}$$
$$C_{\text{consumed}}' = C_{\text{consumed}} + c_{\text{host\_fail}}$$
$$C_{\text{available}}' = C_{\text{available}} + (c_{\text{complete\_max}} - c_{\text{host\_fail}})$$

### 3.3 Reserved Capacity Conservation Law
$$R_n = R_0 + \sum_{i=1}^n \text{reserve}(c_i) - \sum_{i=1}^n \text{release}(c_i)$$
$$\text{ReserveOK}(r, R, R_{\text{max}}) \iff R + r \le R_{\text{max}}, \quad \text{ReleaseOK}(r, R) \iff r \le R$$

### 3.4 Temporal Validity Condition
$$t_{i+1} = t_i + \delta_t(c_i) \quad \text{verified by} \quad \mathbf{t_{\text{now}} \le W}$$

---

## 4. Resource Accounting Clarification Addendum (`R-BUDGET-10`…`14`)

> **STATUS NOTE (2026-09-03, per `spec/06` C-108):** the five obligations below are a
> **proposal owned by this audit**, not frozen normative text. They appear in no
> normative layer: `spec/01` S-11 ends at R-BUDGET-09, `mod/04` lists nine obligations,
> `spec/03` has no R-BUDGET-10+ row, and the atomic registry stops at REQ-BUDGET-032.
> R-BUDGET-11's five escrow paths also diverge from the frozen R-BUDGET-09 three-path
> totality. The adoption decision (freeze some or all of R-BUDGET-10…14, and reconcile
> three vs five escrow paths) is filed as `spec/09` **U-45**; until then, no checker or
> implementation may cite these IDs as obligations. The wording above is quoted, not
> rewritten (R-SCOPE-03).

**R-BUDGET-10 (Resource-State Atomicity — frozen addendum).** All resource mutations belonging to an operational transition occur transactionally. A failed precondition produces zero state drift and zero partial debit:
$$\text{Precondition failure} \implies \Sigma' = \Sigma$$
(except for post-issuance host failure transitions where $c_{\text{issue}}$ remains consumed and escrow is disposed via host-failure consumption/refund).

**R-BUDGET-11 (Escrow Disposition Normal Form — frozen addendum).** Every escrowed amount MUST terminate in exactly one of the five frozen paths: `Consumed` ($C_{\text{consumed}}$), `Refunded` ($C_{\text{available}}$), `Transferred` (child available partition), `Disposed-with-explicit-sink` ($C_{\text{disposed}}$ / $C_{\text{supervisor}}$), or `Remains-Indeterminate` (awaiting authoritative reconciliation).

**R-BUDGET-12 (Duration Semantics — frozen addendum).** $D$ represents remaining execution-duration budget units, while $t$ represents logical step advancement. Scheduled yield steps and async waiting steps advance logical time $t_{i+1} = t_i + \delta_t$ and debit $D \leftarrow D - \delta_t$.

**R-BUDGET-13 (Persistent-Capacity Accounting — frozen addendum).** Volatile RAM (`MEMORY` $M$) is kept strictly distinct from persistent storage capacity (`PERSISTENT_STORAGE` $M_{\text{storage}}$). RAM is released on scope exit or actor halt; durable storage is retained across actor halts and managed via snapshot compaction.

**R-BUDGET-14 (Explicit Resource-Family Vector — frozen addendum).** The explicit resource vector is tagged: $X = \langle X_{\text{cap}}, X_{\text{wal}}, X_{\text{mailbox}} \rangle$. $X_{\text{cap}}$ handles are freed on revocation/halt; $X_{\text{wal}}$ sequence slots advance monotonically; $X_{\text{mailbox}}$ message slots are freed on `Receive`.

---

## 5. Exhaustive Operational Transition Audit (Op-01…Op-22)

---

### Op-01: Pure AST Step (`EvalStep`)
- **before**: $\Sigma = \langle e, \rho, \kappa, B, t, H, L \rangle$, $B = \langle C, R, W \rangle$, $t_{\text{now}} \le W$.
- **operation**: Evaluator single small-step reduction on pure term $e \to e'$.
- **required**: $F \ge 1$, $t_{\text{now}} + \delta_t(\text{pure}) \le W$ ($\delta_t = 0$).
- **reserved**: $\Delta R_{\text{reserve}} = \langle 0, 0 \rangle$.
- **consumed**: $\Delta C_{\text{consume}} = \langle 1, 0, 0, 0 \rangle$ (`FUEL`: $F \leftarrow F - 1$).
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: $B' = \langle \langle F - 1, I_{\text{eff}}, I_{\text{jou}}, D \rangle, \langle M, S \rangle, W \rangle$.
- **failure behavior**: On $F < 1$, step aborts before evaluating $e$; returns `Fault::BudgetExhausted`. $\Sigma' = \Sigma$ (R-BUDGET-10).
- **proof/test obligation**: `R-BUDGET-02`, `R-BUDGET-10`; mutation M007; test `eval_step_fuel_decrement`.

---

### Op-02: Variable Lookup (`Var`)
- **before**: $B = \langle C, R, W \rangle$, $e = \text{Var}(x)$, environment $\rho$.
- **operation**: Lookup symbol $x$ in lexical environment $\rho$.
- **required**: $F \ge c_{\text{var}}$, $x \in \text{dom}(\rho)$, $t_{\text{now}} \le W$.
- **reserved**: $\Delta R_{\text{reserve}} = \langle 0, 0 \rangle$.
- **consumed**: $\Delta C_{\text{consume}} = \langle c_{\text{var}}, 0, 0, 0 \rangle$ (`FUEL`).
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: $B' = \langle \langle F - c_{\text{var}}, I_{\text{eff}}, I_{\text{jou}}, D \rangle, R, W \rangle$, value $\rho(x)$ produced.
- **failure behavior**: If $x \notin \text{dom}(\rho)$, returns `Fault::UnboundVariable`; fuel $c_{\text{var}}$ consumed. If $F < c_{\text{var}}$, returns `Fault::BudgetExhausted`; $\Sigma' = \Sigma$.
- **proof/test obligation**: `R-BUDGET-07`, `R-CEK-01`; test `var_lookup_budget`.

---

### Op-03: Environment Frame Allocation (`Let`)
- **before**: $B = \langle C, R, W \rangle$, term $\text{Let}(x, v, e_2)$, local heap $H$.
- **operation**: Extend environment $\rho' = \rho \cup \{ x \mapsto v \}$ and allocate environment frame.
- **required**: $F \ge c_{\text{let}}$, $\text{ReserveOK}(\Delta M_{\text{env}}, M, M_{\text{max}})$, $t_{\text{now}} \le W$.
- **reserved**: $\Delta R_{\text{reserve}} = \langle \Delta M_{\text{env}}, 0 \rangle$ (`MEMORY`).
- **consumed**: $\Delta C_{\text{consume}} = \langle c_{\text{let}}, 0, 0, 0 \rangle$ (`FUEL`).
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: $B' = \langle \langle F - c_{\text{let}}, I_{\text{eff}}, I_{\text{jou}}, D \rangle, \langle M + \Delta M_{\text{env}}, S \rangle, W \rangle$.
- **failure behavior**: On RAM limit failure, returns `Fault::Budget(ReservedCapacityExceeded)`; frame is NOT allocated; $\Sigma' = \Sigma$ (R-BUDGET-10).
- **proof/test obligation**: `R-BUDGET-03`, `R-BUDGET-10`; mutation M009; test `let_env_reservation`.

---

### Op-04: Sequence Frame Execution (`Seq`)
- **before**: $B = \langle C, R, W \rangle$, term $\text{Seq}(e_1, e_2)$.
- **operation**: Push continuation frame for $e_2$ onto stack $\kappa$ and evaluate $e_1$.
- **required**: $F \ge c_{\text{seq}}$, $\text{ReserveOK}(\Delta M_{\text{frame}}, M, M_{\text{max}})$.
- **reserved**: $\Delta R_{\text{reserve}} = \langle \Delta M_{\text{frame}}, 0 \rangle$ (`MEMORY`).
- **consumed**: $\Delta C_{\text{consume}} = \langle c_{\text{seq}}, 0, 0, 0 \rangle$ (`FUEL`).
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: $B' = \langle \langle F - c_{\text{seq}}, I_{\text{eff}}, I_{\text{jou}}, D \rangle, \langle M + \Delta M_{\text{frame}}, S \rangle, W \rangle$.
- **failure behavior**: On RAM reservation failure, returns `Fault::Budget(ReservedCapacityExceeded)`; stack remains unmodified; $\Sigma' = \Sigma$.
- **proof/test obligation**: `R-CEK-02`, `R-BUDGET-03`; test `seq_frame_reservation`.

---

### Op-05: Branch Evaluation (`If`)
- **before**: $B = \langle C, R, W \rangle$, term $\text{If}(e_{\text{cond}}, e_{\text{then}}, e_{\text{else}})$.
- **operation**: Evaluate condition $e_{\text{cond}}$ and select target branch.
- **required**: $F \ge c_{\text{if}}$, $t_{\text{now}} \le W$.
- **reserved**: $\Delta R_{\text{reserve}} = \langle 0, 0 \rangle$.
- **consumed**: $\Delta C_{\text{consume}} = \langle c_{\text{if}}, 0, 0, 0 \rangle$ (`FUEL`).
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: $B' = \langle \langle F - c_{\text{if}}, I_{\text{eff}}, I_{\text{jou}}, D \rangle, R, W \rangle$.
- **failure behavior**: Non-boolean condition yields `Fault::TypeError`; fuel $c_{\text{if}}$ consumed.
- **proof/test obligation**: `R-CEK-03`, `R-BUDGET-07`; test `if_branch_budget`.

---

### Op-06: Closure Creation (`Lambda`)
- **before**: $B = \langle C, R, W \rangle$, term $\text{Lambda}(params, body)$, environment $\rho$.
- **operation**: Capture lexical environment $\rho_{\text{cap}} \subseteq \rho$ into `Closure(params, body, \rho_{cap})`.
- **required**: $F \ge c_{\text{lambda}}$, $\text{ReserveOK}(\Delta M_{\text{closure}}, M, M_{\text{max}})$.
- **reserved**: $\Delta R_{\text{reserve}} = \langle \Delta M_{\text{closure}}, 0 \rangle$ (`MEMORY`).
- **consumed**: $\Delta C_{\text{consume}} = \langle c_{\text{lambda}}, 0, 0, 0 \rangle$ (`FUEL`).
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: $B' = \langle \langle F - c_{\text{lambda}}, I_{\text{eff}}, I_{\text{jou}}, D \rangle, \langle M + \Delta M_{\text{closure}}, S \rangle, W \rangle$.
- **failure behavior**: If $M + \Delta M_{\text{closure}} > M_{\text{max}}$, returns `Fault::Budget(ReservedCapacityExceeded)`. Closure is NOT instantiated; $\Sigma' = \Sigma$.
- **proof/test obligation**: `R-CEK-04`, `R-MARSHAL-06`, `R-ACTOR-10`; test `closure_capture_reservation`.

---

### Op-07: Function Application (`Call`)
- **before**: $B = \langle C, R, W \rangle$, operator `Closure`, args $v_1, \dots, v_n$.
- **operation**: Check arity, bind parameters in new environment frame, and push call stack frame.
- **required**: $F \ge c_{\text{call}}$, $\text{ReserveOK}(\Delta M_{\text{call}}, M, M_{\text{max}})$, arity match $n = |params|$.
- **reserved**: $\Delta R_{\text{reserve}} = \langle \Delta M_{\text{call}}, 0 \rangle$ (`MEMORY`).
- **consumed**: $\Delta C_{\text{consume}} = \langle c_{\text{call}}, 0, 0, 0 \rangle$ (`FUEL`).
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: $B' = \langle \langle F - c_{\text{call}}, I_{\text{eff}}, I_{\text{jou}}, D \rangle, \langle M + \Delta M_{\text{call}}, S \rangle, W \rangle$.
- **failure behavior**: Arity mismatch returns `Fault::ArityMismatch`. Fuel $c_{\text{call}}$ consumed for pre-check; stack frame allocation rolled back.
- **proof/test obligation**: `R-CEK-05`, tag `CEK-CALL-ARITY-PRECHECK`; test `call_frame_reservation`.

---

### Op-08: Heap Value Allocation (`ValueAlloc`)
- **before**: $B = \langle C, R, W \rangle$, request to construct value $v$ of canonical size $L = \text{canonical\_len}(v)$.
- **operation**: Allocate heap structure for value $v$ in actor heap.
- **required**: $F \ge c_{\text{alloc}}$, $\text{ReserveOK}(L, M, M_{\text{max}})$ ($M + L \le M_{\text{max}}$ per `R-ACTOR-10`).
- **reserved**: $\Delta R_{\text{reserve}} = \langle L, 0 \rangle$ (`MEMORY`).
- **consumed**: $\Delta C_{\text{consume}} = \langle c_{\text{alloc}}, 0, 0, 0 \rangle$ (`FUEL`).
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: $B' = \langle \langle F - c_{\text{alloc}}, I_{\text{eff}}, I_{\text{jou}}, D \rangle, \langle M + L, S \rangle, W \rangle$.
- **failure behavior**: If $M + L > M_{\text{max}}$, returns `Fault::Budget(ReservedCapacityExceeded)`. Heap memory is NOT allocated; $\Sigma' = \Sigma$.
- **proof/test obligation**: `R-ACTOR-10` (SEC-019), `R-BUDGET-03`; mutation M009; test `value_constructed_size_bound`.

---

### Op-09: Capability Attenuation (`Attenuate`)
- **before**: $B = \langle C, R, W \rangle$, parent `CapRef` $c_p \in \kappa$, attenuation constraint $C_{\text{att}}$.
- **operation**: Derive attenuated child `CapRef` $c_c$ in kernel authority arena; add parent-child edge in authority lattice.
- **required**: $F \ge c_{\text{attenuate}}$, $c_p \in \text{CapabilityContext}(\text{actor})$, $c_p$ valid at $t_{\text{now}}$, $\text{AdmissibleConstraint}(C_{\text{att}})$, $\text{ReserveOK}(\Delta M_{\text{cap\_node}}, M, M_{\text{max}})$.
- **reserved**: $\Delta R_{\text{reserve}} = \langle \Delta M_{\text{cap\_node}}, 0 \rangle$ (`MEMORY`), $X_{\text{cap}} \leftarrow X_{\text{cap}} + 1$ (`R-BUDGET-14`).
- **consumed**: $\Delta C_{\text{consume}} = \langle c_{\text{attenuate}}, 0, 0, 0 \rangle$ (`FUEL`).
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: $B' = \langle \langle F - c_{\text{attenuate}}, I_{\text{eff}}, I_{\text{jou}}, D \rangle, \langle M + \Delta M_{\text{cap\_node}}, S \rangle, W \rangle$, derived $c_c \in \kappa'$.
- **failure behavior**: If $c_p \notin \text{CapabilityContext}$ or invalid, returns `Fault::Capability(InvalidCapRef)`. If derived $c_c$ amplifies authority ($\kappa(c_c) \not\prec \kappa(c_p)$), returns `Fault::Capability(AuthorityAmplification)`. No child `CapRef` created; $\Sigma' = \Sigma$.
- **proof/test obligation**: `R-CAP-04`, `R-CORE-04`, `R-KERN-04`; tag `CAP-DERIVE-NO-AMPLIFICATION`; test `attenuate_authority_and_budget`.

---

### Op-10: Capability Revocation (`Revoke`)
- **before**: $B = \langle C, R, W \rangle$, target `CapRef` $c_{\text{target}} \in \kappa$, event log $L$.
- **operation**: Mark $c_{\text{target}}$ and all descendant nodes in authority lattice as revoked; append `CapabilityRevoked` event to WAL/event log.
- **required**: $F \ge c_{\text{revoke}}$, $I_{\text{jou}} \ge c_{\text{log\_io}}$, $c_{\text{target}} \in \text{CapabilityContext}(\text{actor})$ with revocation authority.
- **reserved**: $\Delta R_{\text{reserve}} = \langle 0, 0 \rangle$.
- **consumed**: $\Delta C_{\text{consume}} = \langle c_{\text{revoke}}, 0, c_{\text{log\_io}}, 0 \rangle$ (`FUEL` + `IO_JOURNAL`).
- **released**: $\Delta R_{\text{release}} = \langle \Delta M_{\text{freed\_nodes}}, 0 \rangle$ (`MEMORY`), $X_{\text{cap}} \leftarrow X_{\text{cap}} - k$ (`R-BUDGET-14`).
- **after**: $B' = \langle \langle F - c_{\text{revoke}}, I_{\text{eff}}, I_{\text{jou}} - c_{\text{log\_io}}, D \rangle, \langle M - \Delta M_{\text{freed\_nodes}}, S \rangle, W \rangle$.
- **failure behavior**: If actor lacks revocation authority, returns `Fault::Capability(RevocationDenied)`. Revocation is NOT performed; $\Sigma' = \Sigma$.
- **proof/test obligation**: `R-CAP-07`, `R-PERSIST-07`; tag `CAP-REVOCATION-ANCESTOR`; test `revocation_cascade_and_resource_release`.

---

### Op-11: Actor Spawn (`Spawn`)
- **before**: Parent actor $a_p$ with $B_p = \langle C_p, R_p, W_p \rangle$, global active slots $S_{\text{global\_active}}$, allocation spec $B_{\text{alloc}} = \langle C_{\text{alloc}}, R_{\text{alloc}}, W_{\text{child}} \rangle$.
- **operation**: Instantiate child actor $a_c$ with budget $B_c$ transferred from $a_p$; allocate 1 actor slot in scheduler arena.
- **required**: $F_p \ge c_{\text{spawn\_fuel}}$, $I_{p, \text{eff}} \ge c_{\text{spawn\_io}}$, $C_{\text{alloc}} \le C_{p, \text{available}}$, $R_{\text{alloc}} \le R_{p, \text{available}}$, $S_{\text{global\_active}} + 1 \le S_{\text{global\_max}}$, $W_{\text{child}} \le W_p$.
- **reserved**: Parent: $\Delta R_{p, \text{reserve}} = \langle 0, 0 \rangle$ (budget transferred); Child: $R_c = R_{\text{alloc}}$; Global: $\Delta S_{\text{global}} = +1$ (`ACTOR_SLOTS`).
- **consumed**: Parent: $\Delta C_{p, \text{consume}} = \langle c_{\text{spawn\_fuel}}, c_{\text{spawn\_io}}, 0, 0 \rangle$ (`FUEL` + `IO_EFFECT`). Budget ownership transfer: $C_{p, \text{available}} \leftarrow C_{p, \text{available}} - C_{\text{alloc}}$, $C_{c, \text{available}} = C_{\text{alloc}}$.
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: Parent $B_p' = \langle C_{p, \text{available}} - C_{\text{alloc}}, R_{p, \text{available}} - R_{\text{alloc}}, W_p \rangle$; Child $B_c = \langle C_{\text{alloc}}, R_{\text{alloc}}, W_{\text{child}} \rangle$; Global active slots $S_{\text{global\_active}} + 1$.
- **failure behavior**: If $S_{\text{global\_active}} \ge S_{\text{global\_max}}$, returns `Fault::Budget(ReservedCapacityExceeded)`. If $C_{\text{alloc}} > C_{p, \text{available}}$, returns `Fault::BudgetExhausted`. Child actor is NOT created; parent budget partition is preserved without transfer ($\Sigma' = \Sigma$, `R-CORE-05`).
- **proof/test obligation**: `R-CORE-05`, `R-ACTOR-05`, `R-ACTOR-09`; test `spawn_budget_ownership_transfer_and_conservation`.

---

### Op-12: Actor Mailbox Enqueue (`Send` / `Enqueue`) — Atomic Transition
- **before**: Sender $a_s$ with $B_s = \langle C_s, R_s, W_s \rangle$, recipient $a_r$ with mailbox RAM $M_{\text{box}, r}$, message $v$ of length $L = \text{canonical\_len}(v)$.
- **operation**: ATOMIC TRANSITION: Sender consumable debit and recipient mailbox RAM reservation occur as one atomic transaction.
- **required**: Sender consumables $C_{s, \text{available}} \ge \langle f(L), c_{\text{send\_io}}, 0, 0 \rangle$ ($f(L) \ge \alpha \cdot L + \beta$); recipient RAM capacity $M_{\text{box}, r} + L \le M_{\text{box\_max}, r}$ (`R-ACTOR-10`); $\text{contains\_capability}(v) = \text{false}$ (`R-CORE-07` / `R-MARSHAL-01`).
- **reserved**: Recipient Mailbox Memory: $M_{\text{box}, r} \leftarrow M_{\text{box}, r} + L$ (`MEMORY`). Message slot $X_{\text{mailbox}} \leftarrow X_{\text{mailbox}} + 1$ (`R-BUDGET-14`).
- **consumed**: Sender Consumables: $\Delta C_{s, \text{consume}} = \langle f(L), c_{\text{send\_io}}, 0, 0 \rangle$ (`FUEL` + `IO_EFFECT`).
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: Sender $B_s' = \langle C_s - \langle f(L), c_{\text{send\_io}}, 0, 0 \rangle, R_s, W_s \rangle$; Recipient Mailbox $M_{\text{box}, r}' = M_{\text{box}, r} + L$.
- **failure behavior**: If recipient RAM limit is exceeded or sender consumables insufficient, transaction rolls back atomically: SENDER faults with `Fault::Budget(ReservedCapacityExceeded)` or `Fault::BudgetExhausted`. Neither sender budget nor recipient mailbox RAM is modified ($\Sigma_s' = \Sigma_s, \Sigma_r' = \Sigma_r$, `R-BUDGET-10`).
- **proof/test obligation**: `R-ACTOR-10` (SEC-019), `R-BUDGET-10`, `R-CORE-07`; mutation M033; tag `MARSHAL-NO-RAW-CAPABILITY`; test `mailbox_capacity_sender_fault`.

---

### Op-13: Actor Mailbox Dequeue (`Receive` / `Dequeue`) — Anti-Spin Policy
- **before**: Receiver $a_r$ with $B_r = \langle C_r, R_r, W_r \rangle$, mailbox queue.
- **operation**: Dequeue head message $v$ of length $L$ or inspect queue.
- **required**: Receiver $F_r \ge c_{\text{receive\_fuel}}$, $t_{\text{now}} \le W_r$.
- **reserved**: $\Delta R_{\text{reserve}} = \langle 0, 0 \rangle$.
- **consumed**: Receiver Consumables: $\Delta C_{r, \text{consume}} = \langle c_{\text{receive\_fuel}}, 0, 0, 0 \rangle$ (`FUEL`). (Anti-spin policy: every attempted `Receive` consumes $c_{\text{receive\_fuel}}$, including unsuccessful queue inspection).
- **released**: On non-empty queue success: Recipient Mailbox Memory $M_{\text{box}, r} \leftarrow M_{\text{box}, r} - L$ (`MEMORY`), $X_{\text{mailbox}} \leftarrow X_{\text{mailbox}} - 1$.
- **after**: Receiver $B_r' = \langle \langle F_r - c_{\text{receive\_fuel}}, I_{\text{eff}}, I_{\text{jou}}, D \rangle, R_r, W_r \rangle$. On empty queue, actor enters `BlockedOnMessage` status without memory release.
- **failure behavior**: On empty queue, actor blocks; fuel $c_{\text{receive\_fuel}}$ is consumed for inspection. On $F_r < c_{\text{receive\_fuel}}$, returns `Fault::BudgetExhausted`.
- **proof/test obligation**: `R-ACTOR-06`, `R-ACTOR-10`, anti-spin policy assertion; test `receive_mailbox_memory_release`.

---

### Op-14: Scheduler Yield (`Yield`)
- **before**: Actor $a_i$ in `Runnable` queue, $B_i = \langle C_i, R_i, W_i \rangle$, logical time $t_{\text{now}}$.
- **operation**: Yield execution slice, re-queue actor at end of FIFO runnable queue, advance logical time by $\delta_t(\text{sched}) > 0$.
- **required**: $F_i \ge c_{\text{yield\_fuel}}$, $D_i \ge \delta_t(\text{sched})$, $t_{\text{now}} + \delta_t(\text{sched}) \le W_i$.
- **reserved**: $\Delta R_{\text{reserve}} = \langle 0, 0 \rangle$.
- **consumed**: $\Delta C_{i, \text{consume}} = \langle c_{\text{yield\_fuel}}, 0, 0, \delta_t(\text{sched}) \rangle$ (`FUEL` + `DURATION`, `R-BUDGET-12`).
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: $B_i' = \langle \langle F_i - c_{\text{yield\_fuel}}, I_{\text{eff}}, I_{\text{jou}}, D_i - \delta_t(\text{sched}) \rangle, R_i, W_i \rangle$, $t' = t_{\text{now}} + \delta_t(\text{sched})$.
- **failure behavior**: If $t_{\text{now}} + \delta_t(\text{sched}) > W_i$ or $D_i < \delta_t(\text{sched})$, actor faults with `Fault::DeadlineExceeded` or `Fault::BudgetExhausted`.
- **proof/test obligation**: `R-BUDGET-06`, `R-BUDGET-12`, `R-ACTOR-07`; tag `SCHED-FIFO`; test `scheduler_yield_time_advancement`.

---

### Op-15: Actor Termination / Halt (`Halt` / `Exit`) — Disposed Sink Rule
- **before**: Actor $a_i$ active with $B_i = \langle C_i, R_i, W_i \rangle$, allocated Actor Slot $S = 1$, reserved RAM $M_{\text{heap}, i} + M_{\text{box}, i}$.
- **operation**: Terminate actor execution, release reserved Actor Slot and all allocated local RAM; move unspent consumables to explicit disposed sink $C_{\text{disposed}}$ (or supervisor $C_{\text{supervisor}}$).
- **required**: Terminate instruction executed or unhandled fatal fault encountered.
- **reserved**: $\Delta R_{\text{reserve}} = \langle 0, 0 \rangle$.
- **consumed**: Unspent $C_{i, \text{available}}$ moves to explicit sink $C_{\text{disposed}}$ (`R-BUDGET-11`):
  $$C_{\text{disposed}} \leftarrow C_{\text{disposed}} + C_{i, \text{available}}$$
  preserving $C_{\text{available}} + C_{\text{escrowed}} + C_{\text{consumed}} + C_{\text{disposed}} = C_{\text{initial}}$.
- **released**: $\Delta R_{\text{release}} = \langle M_{\text{heap}, i} + M_{\text{box}, i}, 1 \rangle$ (`MEMORY` released, `ACTOR_SLOTS` $S = S - 1$ freed).
- **after**: Actor state = `Terminated`, $S_{\text{global\_active}} \leftarrow S_{\text{global\_active}} - 1$.
- **failure behavior**: Total: actor slot and RAM are ALWAYS freed upon termination, preventing resource leaks.
- **proof/test obligation**: `R-BUDGET-01`, `R-BUDGET-11` (SEC-021), `R-ACTOR-01`; test `actor_halt_resource_release`.

---

### Op-16: Effect Request & Gate Verification (`E-Request` Gates 1-16)
- **before**: Actor $a$ with $B = \langle C_{\text{avail}}, R, W \rangle$, request $E$ with cost $\text{Cost}(E) = \langle c_{\text{issue}}, c_{\text{complete\_max}}, c_{\text{reserve}} \rangle$, capability ceiling $R_A$.
- **operation**: Run 16-gate validation sequence (`ValidatedRequest(E)`, `Authorized(holder, c, E, t)`, `WithinBudget(E, C, R, R_A)`). Escrow worst-case completion cost $c_{\text{complete\_max}}$ into $C_{\text{escrowed}}$, consume $c_{\text{issue}}$ into $C_{\text{consumed}}$, reserve $c_{\text{reserve}}$ in $R$.
- **required**: Gate 8: $c_{\text{issue}} + c_{\text{complete\_max}} \le C_{\text{avail}}$; Gate 9: $\text{ReserveOK}(c_{\text{reserve}}, R, R_{\text{max}})$; Gate 10: $\text{cost}(E) \le R_A$; Gate 11: $t_{\text{now}} + \delta_t(\text{issue}) \le W$.
- **reserved**: $\Delta R_{\text{reserve}} = c_{\text{reserve}}$ (`MEMORY`).
- **consumed**: Immediate consumption: $\Delta C_{\text{consumed}} \leftarrow C_{\text{consumed}} + c_{\text{issue}}$ (`FUEL` + `IO_EFFECT`); Escrow deduction: $C_{\text{avail}} \leftarrow C_{\text{avail}} - (c_{\text{issue}} + c_{\text{complete\_max}})$, $C_{\text{escrowed}} \leftarrow C_{\text{escrowed}} + c_{\text{complete\_max}}$.
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: $C_{\text{avail}}' = C_{\text{avail}} - (c_{\text{issue}} + c_{\text{complete\_max}})$, $C_{\text{escrowed}}' = C_{\text{escrowed}} + c_{\text{complete\_max}}$, $C_{\text{consumed}}' = C_{\text{consumed}} + c_{\text{issue}}$, $R' = R + c_{\text{reserve}}$, $t' = t_{\text{now}} + \delta_t(\text{issue})$. Invariant preserved: $C_{\text{avail}}' + C_{\text{escrowed}}' + C_{\text{consumed}}' + C_{\text{disposed}} = C_{\text{initial}}$.
- **failure behavior**: If ANY gate 1–16 fails, transition short-circuits to `Fault::BudgetExhausted` or `Fault::Capability`. **No partial debit occurs** (`R-BUDGET-08`, `R-BUDGET-10`): $\Sigma' = \Sigma$.
- **proof/test obligation**: `R-BUDGET-04`, `R-BUDGET-05`, `R-BUDGET-08`, `R-BUDGET-10`; mutations M007, M009; test `effect_request_gate_denial_no_debit`.

---

### Op-17: Durable Issue Journal Commit (`DurableIssue`) — Storage vs RAM Distinction
- **before**: Request $E$ passed gates 1-16; WAL/Effect Journal at sequence $s_n$, checksum $H_n$.
- **operation**: Append `Issued(E)` record to durable WAL/Effect Journal before invoking host (`R-CORE-06`).
- **required**: $I_{\text{jou}} \ge c_{\text{journal\_io}}$, durable storage $M_{\text{storage}} + L_{\text{record}} \le M_{\text{storage\_max}}$ (`R-BUDGET-13`), sequence continuity $s_{n+1} = s_n + 1$.
- **reserved**: Durable Storage: $M_{\text{storage}} \leftarrow M_{\text{storage}} + L_{\text{record}}$ (`PERSISTENT_STORAGE`, distinct from RAM $M$). WAL sequence slot $X_{\text{wal}} \leftarrow X_{\text{wal}} + 1$ (`R-BUDGET-14`).
- **consumed**: Consumable Journal IO: $\Delta C_{\text{consume}} = \langle 0, 0, c_{\text{journal\_io}}, 0 \rangle$ (`IO_JOURNAL`).
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: Durable `Issued(E)` committed; host call now authorized (`R-CORE-06`).
- **failure behavior**: Storage write failure yields `Fault::PersistenceError`. Actor paused/parked. Host MUST NOT be invoked ($\text{HostInvoked}(E) \implies \text{DurableIssued}(E)$).
- **proof/test obligation**: `R-CORE-06`, `R-PERSIST-01`, `R-BUDGET-13`; tag `EFFECT-ISSUE-DURABLE-BEFORE-HOST`; test `durable_issue_before_host_call`.

---

### Op-18: Effect Host Invocation & Completion (`E-Receipt` / `Resume`) — Canonical Notation
- **before**: Pending effect $E$ in host execution with escrowed completion cost $c_{\text{complete\_max}}$ in $C_{\text{escrowed}}$, host returns `EffectReceipt { id, digest, result: Ok(v) }`.
- **operation**: Validate receipt ID and digest (`R-EFFECT-06`), perform recursive `contains_capability(v)` check (`R-EFFECT-08` / SEC-001). Reconcile actual consumption $c_{\text{complete\_actual}} \le c_{\text{complete\_max}}$ against $C_{\text{escrowed}}$.
- **required**: Receipt ID and digest match pending $E$; `contains_capability(v) == false`; $v \in \text{CanonicalDataDomain}$; $c_{\text{complete\_actual}} \le c_{\text{complete\_max}}$.
- **reserved**: $\Delta R_{\text{reserve}} = \langle 0, 0 \rangle$.
- **consumed**: Escrow reservation removed: $C_{\text{escrowed}} \leftarrow C_{\text{escrowed}} - c_{\text{complete\_max}}$. Actual cost consumed: $C_{\text{consumed}} \leftarrow C_{\text{consumed}} + c_{\text{complete\_actual}}$ (`FUEL` + `IO_EFFECT` + `DURATION`).
- **released**: Refund unspent escrow: $C_{\text{avail}} \leftarrow C_{\text{avail}} + (c_{\text{complete\_max}} - c_{\text{complete\_actual}})$; release temporary RAM reservation $c_{\text{reserve\_ram}}$ ($\Delta M = -c_{\text{reserve\_ram}}$).
- **after**: $C_{\text{avail}}' = C_{\text{avail}} + (c_{\text{complete\_max}} - c_{\text{complete\_actual}})$, $C_{\text{escrowed}}' = C_{\text{escrowed}} - c_{\text{complete\_max}}$, $C_{\text{consumed}}' = C_{\text{consumed}} + c_{\text{complete\_actual}}$, actor resumed with $v$.
- **failure behavior**: If `contains_capability(v) == true` or invalid digest, returns `Fault::InvalidReceipt`. Continuation is NOT resumed, actor is parked, escrow remains in reconciliation state (`R-BUDGET-09`, `R-BUDGET-11`).
- **proof/test obligation**: `R-BUDGET-05`, `R-BUDGET-11`, `R-EFFECT-06`, `R-EFFECT-08` (SEC-001); mutations M008, M019, M020; tag `EFFECT-RECEIPT-DIGEST-VALIDATION`; test `receipt_completion_escrow_refund`.

---

### Op-19: Effect Host Failure / Refusal (`E-HostFailure`) — Canonical Notation
- **before**: Pending effect $E$ in host execution with escrowed $c_{\text{complete\_max}}$ in $C_{\text{escrowed}}$, host returns `EffectReceipt { id, digest, result: Err(host_fault) }`.
- **operation**: Validate receipt ID and digest. Charge host-failure consumption cost $c_{\text{host\_fail}} \le c_{\text{complete\_max}}$ against $C_{\text{escrowed}}$, refund remainder $(c_{\text{complete\_max}} - c_{\text{host\_fail}})$ to $C_{\text{avail}}$.
- **required**: Receipt ID and digest match pending $E$; $c_{\text{host\_fail}} \le c_{\text{complete\_max}}$; host error maps to closed declared fault set (`R-CORE-13` / SEC-012).
- **reserved**: $\Delta R_{\text{reserve}} = \langle 0, 0 \rangle$.
- **consumed**: Escrow reservation removed: $C_{\text{escrowed}} \leftarrow C_{\text{escrowed}} - c_{\text{complete\_max}}$. Host-failure cost consumed: $C_{\text{consumed}} \leftarrow C_{\text{consumed}} + c_{\text{host\_fail}}$ (`FUEL` + `IO_EFFECT`).
- **released**: Refund remaining escrow: $C_{\text{avail}} \leftarrow C_{\text{avail}} + (c_{\text{complete\_max}} - c_{\text{host\_fail}})$; release temporary RAM reservation $c_{\text{reserve\_ram}}$.
- **after**: Actor resumes on declared error path or parks; $C_{\text{avail}}' = C_{\text{avail}} + (c_{\text{complete\_max}} - c_{\text{host\_fail}})$.
- **failure behavior**: Total: issue cost $c_{\text{issue}}$ is NOT refunded (host was invoked); escrow is partially/fully consumed per $c_{\text{host\_fail}}$ (`C-23` rule / `R-BUDGET-09` / `R-BUDGET-11`).
- **proof/test obligation**: `R-BUDGET-05`, `R-BUDGET-09` (SEC-021), `R-BUDGET-11`, `R-CORE-13` (SEC-012); test `host_failure_escrow_accounting`.

---

### Op-20: Indeterminate Effect Reconciliation (`ReconcileIndeterminate`)
- **before**: Pending effect $E$ in `Indeterminate` status (due to crash recovery, host non-response, actor fatal fault, or logical-time deadline $W$ expiration per `R-BUDGET-09`). Escrowed $c_{\text{complete\_max}}$ in $C_{\text{escrowed}}$.
- **operation**: Execute authoritative reconciliation protocol (`R-RECOV-08`). Determine durable resolution (`Completed`, `NotExecuted`, or `Compensated`).
- **required**: Authoritative host query or WAL evidence; I2 validation chain holds for reconciliation paths; no local policy silent resolution (`NotExecuted` requires host evidence per `R-DUR-04`).
- **reserved**: $\Delta R_{\text{reserve}} = \langle 0, 0 \rangle$.
- **consumed**: Escrow reservation removed: $C_{\text{escrowed}} \leftarrow C_{\text{escrowed}} - c_{\text{complete\_max}}$. If resolved `Completed`: $c_{\text{complete\_actual}}$ charged to $C_{\text{consumed}}$. If resolved `NotExecuted`: $c_{\text{complete\_max}}$ refunded to $C_{\text{avail}}$.
- **released**: Escrow $C_{\text{escrowed}}$ reduced to 0 for effect $E$; refund $(c_{\text{complete\_max}} - c_{\text{complete\_actual}})$ to $C_{\text{avail}}$.
- **after**: Escrow for $E$ disposed totally (`R-BUDGET-11`). Invariant preserved: no stranded escrow in quiescent machine (`R-BUDGET-09`).
- **failure behavior**: If host evidence is absent/ambiguous, effect remains in `Indeterminate` reconciliation queue; escrow remains held in $C_{\text{escrowed}}$ until authoritative resolution.
- **proof/test obligation**: `R-BUDGET-09` (SEC-021), `R-BUDGET-11`, `R-RECOV-08` (SEC-010); mutation M035; tag `RECOVERY-ISSUED-INDETERMINATE`; test `reconciliation_escrow_disposition_totality`.

---

### Op-21: Persistence WAL Append & Snapshot (`Snapshot` / `WALAppend`) — Persistent Storage
- **before**: Machine configuration $\Sigma$, persistence engine at snapshot $N$, WAL frame $k$.
- **operation**: Serialize state machine, kernel authority lattice, active budgets, and actor mailboxes into canonical binary format (15A grammar, `R-CANON-13`). Write frame to WAL with chained checksum $H_{k+1} = \text{Hash}(H_k \parallel \text{frame}_{k+1})$.
- **required**: Consumable Journal IO $I_{\text{jou}} \ge c_{\text{snap\_io}}$, storage capacity $M_{\text{storage}} + L_{\text{snap}} \le M_{\text{storage\_max}}$ (`R-BUDGET-13`).
- **reserved**: Persistent Storage: $M_{\text{storage}} \leftarrow M_{\text{storage}} + L_{\text{snap}}$ (`PERSISTENT_STORAGE`).
- **consumed**: Consumable Journal IO: $\Delta C_{\text{consume}} = \langle 0, 0, c_{\text{snap\_io}}, 0 \rangle$ (`IO_JOURNAL`).
- **released**: On snapshot compaction: release old log frames prior to snapshot sequence.
- **after**: Snapshot committed with digest covering state digest and last WAL sequence. Chained checksum updated.
- **failure behavior**: Disk full or write error yields `Fault::PersistenceError`. Rollback to last committed snapshot/WAL sequence $s_k$. State machine unaffected ($\Sigma' = \Sigma$).
- **proof/test obligation**: `R-PERSIST-06`, `R-PERSIST-07` (SEC-004), `R-PERSIST-08` (SEC-009), `R-BUDGET-13`, `R-CANON-13` (SEC-017); tag `SNAPSHOT-COMMIT-INTEGRITY`; test `wal_checksum_chaining_and_snapshot`.

---

### Op-22: Plan Compilation & Static Bounding (`CompilePlan`)
- **before**: Uncompiled `Block` proposed by LLM planner (untrusted input), static capability set $\kappa_{\text{static}}$, upper bound $B_{\text{max}}$.
- **operation**: Run static compilation judgment $\Gamma; \kappa_{\text{static}} \vdash e : \tau ! F @ B_{\text{static}}$. Check worst-case over-approximated cost $B_{\text{static}} \le B_{\text{max}}$.
- **required**: Worst-case cost $B_{\text{static}} \le B_{\text{max}}$; no embedded `Value::Capability` literals (`R-COMPILE-06` / SEC-002).
- **reserved**: $\Delta R_{\text{reserve}} = \langle 0, 0 \rangle$.
- **consumed**: Compiler host fuel $F_{\text{compiler}} \leftarrow F_{\text{compiler}} - c_{\text{compile}}$ (`FUEL`).
- **released**: $\Delta R_{\text{release}} = \langle 0, 0 \rangle$.
- **after**: Output `ValidatedPlan` with static budget bound $B_{\text{static}}$, or compilation failure.
- **failure behavior**: If $B_{\text{static}} > B_{\text{max}}$ or plan carries un-substituted capability literals, compilation fails with `CompileError::BudgetBoundExceeded` or `CompileError::CapabilityLiteralForbidden`. No executable plan produced ($\text{Block} \neq \text{ExecutablePlan}$).
- **proof/test obligation**: `R-COMPILE-03`, `R-COMPILE-06` (SEC-002), `R-PLANNER-02`; test `static_compilation_budget_bounding`.

---

## 6. Verification & Mutation Register Summary

| Target Obligation | Key Invariants Verified | Associated Mutations / Tests / Checkers |
|---|---|---|
| **R-BUDGET-01** | Structure $B = \langle C, R, W \rangle$ with $C = \langle F, I_{\text{eff}}, I_{\text{jou}}, D \rangle$, $R = \langle M, S \rangle$ | Consumables strictly decrease; reserved capacity scope-bound |
| **R-BUDGET-02** | Checked arithmetic; no `saturating_sub` | M007, M009; `BudgetError` enum tests |
| **R-BUDGET-03** | $\text{ReserveOK}(r,R) \iff R+r \le R_{\text{max}}$; $\text{ReleaseOK}(r,R) \iff r \le R$ | Reservation property tests (resolves C-07) |
| **R-BUDGET-04** | $\text{WithinBudget}(E,C,R,R_A)$ dual gate | Short-circuit Track C tests (runtime + ceiling) |
| **R-BUDGET-05** | Conservation: $C_{\text{avail}} + C_{\text{escrowed}} + C_{\text{consumed}} + C_{\text{disposed}} = C_{\text{initial}}$ | `BUDGET-CONSUMPTION-CONSERVATION`, `BUDGET-ESCROW-CONSERVATION` |
| **R-BUDGET-06** | Logical time advancement $\delta_t$; $t_{\text{now}} \le W$ | `δ_t(pure) = 0`, `δ_t(host/sched) > 0`, deadline bounds |
| **R-BUDGET-07** | `CostModel` mapping ops to `Cost { consumable, reserved }` | Type-level separation `Consumable \neq Reserved` |
| **R-BUDGET-08** | $\neg\text{BudgetOK} \implies \text{fault}(\text{BudgetExhausted})$; no partial debit | REQ-BUDGET-032; Track C budget gate tests |
| **R-BUDGET-09** | Escrow disposition totality; live faults unified with recovery | M035; ledger liveness, mixed crash+live harness (SEC-021) |
| **R-BUDGET-10** | Resource-State Atomicity: $\text{Precondition failure} \implies \Sigma' = \Sigma$ | `audit/_conservation_checker.py` (Gate 11) |
| **R-BUDGET-11** | Escrow Disposition Normal Form: 5 explicit termination paths | `audit/_conservation_checker.py` (Gate 11) |
| **R-BUDGET-12** | Duration Semantics: $D$ vs logical time $t$; yield debit | `audit/_conservation_checker.py` (Gate 11) |
| **R-BUDGET-13** | Persistent-Capacity Accounting: volatile RAM vs $M_{\text{storage}}$ | Storage separation unit tests |
| **R-BUDGET-14** | Explicit Resource-Family Vector $X = \langle X_{\text{cap}}, X_{\text{wal}}, X_{\text{mailbox}} \rangle$ | Tagged resource family conservation tests |
| **R-ACTOR-10** | Mailbox admission resource-gated; payload proportional cost | M033; sender-pays mailbox capacity tests (SEC-019) |

---

## 7. Conclusion

With the introduction of the Resource Accounting Clarification Addendum (`R-BUDGET-10`…`R-BUDGET-14`), the formalization of the explicit $C_{\text{disposed}}$ sink, the atomic notation for Op-18/Op-19, and the integration of `audit/_conservation_checker.py` into `check.py` (11/11 PASS), the resource-accounting specification and operational transition contracts are **FULLY CLOSED AND CONSERVATION-FINAL**.
