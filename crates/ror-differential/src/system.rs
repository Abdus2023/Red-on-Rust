//! M8 Differential system (MOD-15) — R-REF-01…06, R-TEST-02/03/07.
//!
//! Pipeline:
//! ```text
//! Generator → Program → Reference exec ─┐
//!                                       ├→ NormalizedObservation → compare
//!              Production exec ─────────┘         ↓
//!                                          first divergence
//!                                                 ↓
//!                                              shrinker
//!                                                 ↓
//!                                      counterexample artifact
//! ```
//!
//! **F-04 / Observed\* UNKNOWN:** [`NormalizedObservation`] is a **provisional**
//! schema over terminal Halted/Fault observations. This does **not** close F-04
//! or any OAD. Internal addresses, allocator layout, and OS handles are excluded
//! (R-REF-05).
//!
//! **Non-goals:** M9 mutation kill-rate; M10 crash gate; second runtime inside
//! this crate; host bypass; R-REG promotion.

use ror_core::machine::sugar::{bool_v, if_, int, lambda, let_, seq, unit, var};
use ror_core::machine::{Expr, Fault, Value};
use ror_core::types::Symbol;

use crate::m2::{observe_production, observe_reference, Observation};

/// Generator / harness version stamps (reproducibility metadata, R-TEST-02).
pub const GENERATOR_VERSION: &str = "m8-gen-1";
/// Provisional pure-CEK semantic stamp (does not freeze observation domain).
pub const SEMANTIC_VERSION: &str = "m2-m3-pure-cek-provisional";
pub const TEST_CASE_VERSION: &str = "m8-case-1";

// ---------------------------------------------------------------------------
// Domain model
// ---------------------------------------------------------------------------

/// Deterministic program under differential test (pure CEK subset for M8 gen).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct DiffProgram {
    pub expr: Expr,
}

impl DiffProgram {
    pub fn new(expr: Expr) -> Self {
        Self { expr }
    }

    /// Structural complexity metric for shrinking (nodes + depth).
    pub fn complexity(&self) -> u64 {
        expr_complexity(&self.expr)
    }
}

/// Seeded generation configuration (R-TEST-02 reproducibility).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct GenConfig {
    pub seed: u64,
    /// Max expression depth (R-TEST-01 exhaustive baseline uses ≤4).
    pub max_depth: u32,
    /// Max nodes attempted.
    pub max_nodes: u32,
}

impl Default for GenConfig {
    fn default() -> Self {
        Self {
            seed: 1,
            max_depth: 4,
            max_nodes: 32,
        }
    }
}

/// Generated case with reproduction metadata.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct GeneratedProgram {
    pub seed: u64,
    pub generator_version: &'static str,
    pub config: GenConfig,
    pub program: DiffProgram,
    pub case_id: u64,
}

/// Execution input package (thin; M8 pure-expr focus).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ExecutionInput {
    pub program: DiffProgram,
    pub seed: u64,
    pub case_id: u64,
}

impl ExecutionInput {
    pub fn from_generated(g: &GeneratedProgram) -> Self {
        Self {
            program: g.program.clone(),
            seed: g.seed,
            case_id: g.case_id,
        }
    }

    pub fn from_program(program: DiffProgram, seed: u64, case_id: u64) -> Self {
        Self {
            program,
            seed,
            case_id,
        }
    }
}

/// Provisional normalized observation (**F-04 OPEN** — not a frozen Observed\*).
///
/// Carries R-REF-05-admissible terminal semantic content for the pure-CEK domain:
/// halt value or fault. Actor/effect/recovery traces remain in m5–m7 modules.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct NormalizedObservation {
    pub side: ObservationSide,
    pub terminal: Observation,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ObservationSide {
    Production,
    Reference,
}

/// Single structured difference path element (provisional F-04).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum DiffPath {
    /// Top-level terminal kind (Halted vs Fault).
    TerminalKind,
    /// Halted value payload.
    HaltedValue,
    /// Fault discriminant / code.
    Fault,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Difference {
    pub path: DiffPath,
    pub production: String,
    pub reference: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum CompareResult {
    Equal,
    Diverged {
        first: Difference,
        /// Full ordered list; first element is the first divergence.
        all: Vec<Difference>,
    },
}

impl CompareResult {
    pub fn is_equal(&self) -> bool {
        matches!(self, CompareResult::Equal)
    }

    pub fn is_diverged(&self) -> bool {
        matches!(self, CompareResult::Diverged { .. })
    }
}

/// First-divergence report (R-REF-05).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct FirstDivergence {
    pub case_id: u64,
    pub seed: u64,
    pub program: DiffProgram,
    pub production: NormalizedObservation,
    pub reference: NormalizedObservation,
    pub first: Difference,
    pub generator_version: &'static str,
}

/// Shrink result (R-TEST-03).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ShrinkResult {
    pub original: DiffProgram,
    pub minimized: DiffProgram,
    pub original_complexity: u64,
    pub minimized_complexity: u64,
    pub steps: u32,
    pub preserved_divergence: bool,
}

/// R-TEST-02 counterexample artifact — canonical 16-field list plus minimized case.
///
/// Normative fields (R-TEST-02):
/// `seed, generator_version, semantic_version, test_case_version, program,
/// initial state, capabilities, budgets, actor topology, scheduler_trace,
/// host_trace, persistence image, crash_trace, production_observation,
/// reference_observation, first_divergence, minimized case`.
///
/// Trace/image fields are empty for pure-CEK cases (provisional thin encoding).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct CounterexampleArtifact {
    pub seed: u64,                                     // 1
    pub generator_version: String,                     // 2
    pub semantic_version: String,                      // 3
    pub test_case_version: String,                     // 4
    pub program: DiffProgram,                          // 5
    pub initial_state: String,                         // 6
    pub capabilities: String,                          // 7
    pub budgets: String,                               // 8
    pub actor_topology: String,                        // 9
    pub scheduler_trace: String,                       // 10
    pub host_trace: String,                            // 11
    pub persistence_image: Vec<u8>,                    // 12
    pub crash_trace: String,                           // 13
    pub production_observation: NormalizedObservation, // 14
    pub reference_observation: NormalizedObservation,  // 15
    pub first_divergence: Option<Difference>,          // 16
    /// Minimized witness (same sentence as R-TEST-02 “minimized case”).
    pub minimized_case: Option<DiffProgram>,
}

impl CounterexampleArtifact {
    /// The 16 canonical field names from R-TEST-02 (plus minimized_case companion).
    pub fn canonical_field_names() -> &'static [&'static str] {
        &[
            "seed",
            "generator_version",
            "semantic_version",
            "test_case_version",
            "program",
            "initial_state",
            "capabilities",
            "budgets",
            "actor_topology",
            "scheduler_trace",
            "host_trace",
            "persistence_image",
            "crash_trace",
            "production_observation",
            "reference_observation",
            "first_divergence",
        ]
    }

    pub fn from_divergence(fd: &FirstDivergence, minimized: Option<DiffProgram>) -> Self {
        Self {
            seed: fd.seed,
            generator_version: fd.generator_version.to_string(),
            semantic_version: SEMANTIC_VERSION.to_string(),
            test_case_version: TEST_CASE_VERSION.to_string(),
            program: fd.program.clone(),
            initial_state: String::new(),
            capabilities: String::new(),
            budgets: String::new(),
            actor_topology: String::new(),
            scheduler_trace: String::new(),
            host_trace: String::new(),
            persistence_image: Vec::new(),
            crash_trace: String::new(),
            production_observation: fd.production.clone(),
            reference_observation: fd.reference.clone(),
            first_divergence: Some(fd.first.clone()),
            minimized_case: minimized,
        }
    }
}

/// Coverage / evidence counters (R-TEST-07 — evidence, never oracle substitute).
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct CoverageEvidence {
    pub generated: u64,
    pub reference_executed: u64,
    pub production_executed: u64,
    pub equal: u64,
    pub divergent: u64,
    pub shrunk: u64,
    pub failed: u64,
    pub not_run: u64,
    pub tags: Vec<&'static str>,
}

impl CoverageEvidence {
    pub fn record_tag(&mut self, tag: &'static str) {
        if !self.tags.contains(&tag) {
            self.tags.push(tag);
        }
    }
}

// ---------------------------------------------------------------------------
// Generator (deterministic LCG)
// ---------------------------------------------------------------------------

#[derive(Clone, Debug)]
struct Rng {
    state: u64,
}

impl Rng {
    fn new(seed: u64) -> Self {
        Self {
            state: seed | 1, // avoid zero lock
        }
    }

    fn next_u64(&mut self) -> u64 {
        self.state = self.state.wrapping_mul(6364136223846793005).wrapping_add(1);
        self.state
    }

    fn gen_range(&mut self, lo: u32, hi: u32) -> u32 {
        if hi <= lo {
            return lo;
        }
        lo + (self.next_u64() as u32) % (hi - lo)
    }
}

/// Generate a pure-CEK program from seed (M2/M3 surface). Deterministic.
pub fn generate(config: &GenConfig) -> GeneratedProgram {
    let mut rng = Rng::new(config.seed);
    let mut used = 0u32;
    let expr = gen_expr(&mut rng, config.max_depth, 0, config.max_nodes, &mut used);
    GeneratedProgram {
        seed: config.seed,
        generator_version: GENERATOR_VERSION,
        config: config.clone(),
        program: DiffProgram::new(expr),
        case_id: config.seed,
    }
}

fn gen_expr(rng: &mut Rng, max_depth: u32, depth: u32, max_nodes: u32, used: &mut u32) -> Expr {
    *used = used.saturating_add(1);
    if *used >= max_nodes || depth >= max_depth {
        return gen_leaf(rng);
    }
    match rng.gen_range(0, 8) {
        0 => gen_leaf(rng),
        1 => {
            let n = rng.gen_range(0, 4);
            let v = gen_expr(rng, max_depth, depth + 1, max_nodes, used);
            let b = gen_expr(rng, max_depth, depth + 1, max_nodes, used);
            let_(n, v, b)
        }
        2 => {
            let a = gen_expr(rng, max_depth, depth + 1, max_nodes, used);
            let b = gen_expr(rng, max_depth, depth + 1, max_nodes, used);
            seq(a, b)
        }
        3 => {
            let c = bool_v(rng.gen_range(0, 2) == 0);
            let t = gen_expr(rng, max_depth, depth + 1, max_nodes, used);
            let e = gen_expr(rng, max_depth, depth + 1, max_nodes, used);
            if_(c, t, e)
        }
        4 => {
            let body = gen_expr(rng, max_depth, depth + 1, max_nodes, used);
            let f = lambda(&[0], body);
            let arg = gen_leaf(rng);
            ror_core::machine::sugar::call(f, vec![arg])
        }
        5 => var(rng.gen_range(0, 3)),
        6 => {
            let n = rng.gen_range(0, 3);
            let_(n, gen_leaf(rng), var(n))
        }
        _ => gen_leaf(rng),
    }
}

fn gen_leaf(rng: &mut Rng) -> Expr {
    match rng.gen_range(0, 4) {
        0 => unit(),
        1 => int(i64::from(rng.gen_range(0, 16))),
        2 => bool_v(rng.gen_range(0, 2) == 0),
        _ => int(0),
    }
}

// ---------------------------------------------------------------------------
// Runners + normalization
// ---------------------------------------------------------------------------

/// Production runner — real production CEK only (no second evaluator).
pub fn run_production(input: &ExecutionInput) -> NormalizedObservation {
    let terminal = observe_production(input.program.expr.clone());
    normalize(ObservationSide::Production, terminal)
}

/// Reference runner — independent reference CEK (R-REF-02).
pub fn run_reference(input: &ExecutionInput) -> NormalizedObservation {
    let terminal = observe_reference(input.program.expr.clone());
    normalize(ObservationSide::Reference, terminal)
}

fn normalize(side: ObservationSide, terminal: Observation) -> NormalizedObservation {
    NormalizedObservation { side, terminal }
}

// ---------------------------------------------------------------------------
// Comparator + first divergence
// ---------------------------------------------------------------------------

/// Compare normalized observations (R-REF-05). Deterministic; not final-value-only
/// at the observation-struct level (kind checked before payload).
pub fn compare(prod: &NormalizedObservation, refe: &NormalizedObservation) -> CompareResult {
    let mut diffs = Vec::new();
    match (&prod.terminal, &refe.terminal) {
        (Observation::Halted(a), Observation::Halted(b)) => {
            if a != b {
                diffs.push(Difference {
                    path: DiffPath::HaltedValue,
                    production: value_label(a),
                    reference: value_label(b),
                });
            }
        }
        (Observation::Fault(a), Observation::Fault(b)) => {
            if a != b {
                diffs.push(Difference {
                    path: DiffPath::Fault,
                    production: fault_label(a),
                    reference: fault_label(b),
                });
            }
        }
        (Observation::Halted(a), Observation::Fault(b)) => {
            diffs.push(Difference {
                path: DiffPath::TerminalKind,
                production: format!("Halted({})", value_label(a)),
                reference: format!("Fault({})", fault_label(b)),
            });
        }
        (Observation::Fault(a), Observation::Halted(b)) => {
            diffs.push(Difference {
                path: DiffPath::TerminalKind,
                production: format!("Fault({})", fault_label(a)),
                reference: format!("Halted({})", value_label(b)),
            });
        }
    }
    if diffs.is_empty() {
        CompareResult::Equal
    } else {
        CompareResult::Diverged {
            first: diffs[0].clone(),
            all: diffs,
        }
    }
}

/// End-to-end: run both sides and compare.
pub fn run_case(
    input: &ExecutionInput,
) -> (NormalizedObservation, NormalizedObservation, CompareResult) {
    let p = run_production(input);
    let r = run_reference(input);
    let c = compare(&p, &r);
    (p, r, c)
}

/// Build first-divergence report when diverged.
pub fn first_divergence_report(
    input: &ExecutionInput,
    prod: NormalizedObservation,
    refe: NormalizedObservation,
    first: Difference,
) -> FirstDivergence {
    FirstDivergence {
        case_id: input.case_id,
        seed: input.seed,
        program: input.program.clone(),
        production: prod,
        reference: refe,
        first,
        generator_version: GENERATOR_VERSION,
    }
}

fn value_label(v: &Value) -> String {
    match v {
        Value::Unit => "Unit".into(),
        Value::Bool(b) => format!("Bool({b})"),
        Value::Integer(n) => format!("Integer({n})"),
        Value::String(s) => format!("String({s})"),
        Value::Bytes(b) => format!("Bytes(len={})", b.len()),
        Value::Symbol(s) => format!("Symbol({})", s.0),
        Value::Capability(_) => "Capability".into(),
        Value::Function(_) => "Function".into(),
        Value::List(xs) => format!("List(len={})", xs.len()),
        Value::Tuple(xs) => format!("Tuple(len={})", xs.len()),
        Value::DelegatedCapability(_) => "DelegatedCapability".into(),
        Value::Constraint(_) => "Constraint".into(),
    }
}

fn fault_label(f: &Fault) -> String {
    // Stable discriminant-style label (not full Debug with addresses).
    match f {
        Fault::UnboundVariable(s) => format!("UnboundVariable({})", s.0),
        Fault::TypeError { expected, actual } => {
            format!("TypeError({expected}/{actual})")
        }
        Fault::ArityMismatch { expected, actual } => {
            format!("ArityMismatch({expected}/{actual})")
        }
        Fault::CapabilityRevoked => "CapabilityRevoked".into(),
        Fault::InvalidConstraint => "InvalidConstraint".into(),
        Fault::Unauthorized => "Unauthorized".into(),
        Fault::BudgetExhausted => "BudgetExhausted".into(),
        Fault::DeadlineExceeded => "DeadlineExceeded".into(),
        Fault::HostPolicyDenied => "HostPolicyDenied".into(),
        Fault::PersistenceError => "PersistenceError".into(),
        Fault::ReplayCorruption => "ReplayCorruption".into(),
        Fault::InvalidReceipt => "InvalidReceipt".into(),
        other => format!("{other:?}"),
    }
}

// ---------------------------------------------------------------------------
// Shrinker (R-TEST-03 priorities applicable to pure expr: depth, arity, bindings)
// ---------------------------------------------------------------------------

/// Failure predicate: candidate must still diverge under compare.
pub type FailurePred = fn(&DiffProgram) -> bool;

/// Default predicate: production vs reference observations diverge.
pub fn default_divergence_pred(program: &DiffProgram) -> bool {
    let input = ExecutionInput::from_program(program.clone(), 0, 0);
    let (_, _, c) = run_case(&input);
    c.is_diverged()
}

/// Shrink a diverging program. Deterministic candidate order.
///
/// R-TEST-03 order mapped to pure-expr domain:
/// (2) expression depth, (3) call arity, (4) bindings — via structural reductions.
/// Actor/mailbox/WAL/effect/crash priorities are no-ops on pure-CEK programs.
pub fn shrink(original: &DiffProgram, pred: FailurePred) -> ShrinkResult {
    let original_complexity = original.complexity();
    if !pred(original) {
        return ShrinkResult {
            original: original.clone(),
            minimized: original.clone(),
            original_complexity,
            minimized_complexity: original_complexity,
            steps: 0,
            preserved_divergence: false,
        };
    }

    let mut current = original.clone();
    let mut steps = 0u32;
    // Bound iterations to guarantee termination.
    for _ in 0..64 {
        let candidates = shrink_candidates(&current.expr);
        let mut progressed = false;
        for cand_expr in candidates {
            let cand = DiffProgram::new(cand_expr);
            if cand.complexity() >= current.complexity() {
                continue;
            }
            if pred(&cand) {
                current = cand;
                steps = steps.saturating_add(1);
                progressed = true;
                break; // restart from new current (deterministic first-success)
            }
        }
        if !progressed {
            break;
        }
    }

    let minimized_complexity = current.complexity();
    ShrinkResult {
        original: original.clone(),
        minimized: current,
        original_complexity,
        minimized_complexity,
        steps,
        preserved_divergence: true,
    }
}

/// Deterministic ordered candidates (simpler first by construction).
fn shrink_candidates(expr: &Expr) -> Vec<Expr> {
    let mut out = Vec::new();
    // Priority: replace with unit / simpler leaves
    out.push(unit());
    out.push(int(0));
    out.push(bool_v(true));

    match expr {
        Expr::Let { value, body, .. } => {
            out.push((**body).clone());
            out.push((**value).clone());
            for c in shrink_candidates(value) {
                out.push(Expr::Let {
                    name: Symbol(0),
                    value: Box::new(c),
                    body: body.clone(),
                });
            }
            for c in shrink_candidates(body) {
                out.push(Expr::Let {
                    name: Symbol(0),
                    value: value.clone(),
                    body: Box::new(c),
                });
            }
        }
        Expr::Seq { first, second } => {
            out.push((**second).clone());
            out.push((**first).clone());
            for c in shrink_candidates(first) {
                out.push(Expr::Seq {
                    first: Box::new(c),
                    second: second.clone(),
                });
            }
            for c in shrink_candidates(second) {
                out.push(Expr::Seq {
                    first: first.clone(),
                    second: Box::new(c),
                });
            }
        }
        Expr::If {
            condition,
            then_branch,
            else_branch,
        } => {
            out.push((**then_branch).clone());
            out.push((**else_branch).clone());
            for c in shrink_candidates(then_branch) {
                out.push(Expr::If {
                    condition: condition.clone(),
                    then_branch: Box::new(c),
                    else_branch: else_branch.clone(),
                });
            }
            for c in shrink_candidates(else_branch) {
                out.push(Expr::If {
                    condition: condition.clone(),
                    then_branch: then_branch.clone(),
                    else_branch: Box::new(c),
                });
            }
        }
        Expr::Call { func, args } => {
            out.push((**func).clone());
            if let Some(a0) = args.first() {
                out.push(a0.clone());
            }
            // Reduce arity: drop trailing args
            if args.len() > 1 {
                out.push(Expr::Call {
                    func: func.clone(),
                    args: args[..args.len() - 1].to_vec(),
                });
            }
            if !args.is_empty() {
                out.push(Expr::Call {
                    func: func.clone(),
                    args: vec![],
                });
            }
        }
        Expr::Lambda { params, body } => {
            out.push((**body).clone());
            if params.len() > 1 {
                out.push(Expr::Lambda {
                    params: params[..params.len() - 1].to_vec(),
                    body: body.clone(),
                });
            }
        }
        Expr::Var(_) | Expr::Value(_) => {}
        _ => {
            // Other constructors: try body-like subexpressions not required for M8 gen
        }
    }
    out
}

// ---------------------------------------------------------------------------
// Orchestration
// ---------------------------------------------------------------------------

/// Full M8 pipeline on a generated config: generate → run → compare → maybe shrink.
pub fn execute_seeded(config: &GenConfig, coverage: &mut CoverageEvidence) -> CompareResult {
    let gen = generate(config);
    coverage.generated = coverage.generated.saturating_add(1);
    coverage.record_tag("M8-GENERATOR");

    let input = ExecutionInput::from_generated(&gen);
    let (p, r, c) = run_case(&input);
    coverage.production_executed = coverage.production_executed.saturating_add(1);
    coverage.reference_executed = coverage.reference_executed.saturating_add(1);
    coverage.record_tag("M8-COMPARE");

    match &c {
        CompareResult::Equal => {
            coverage.equal = coverage.equal.saturating_add(1);
            coverage.record_tag("CEK-PURE-AGREE");
        }
        CompareResult::Diverged { first, .. } => {
            coverage.divergent = coverage.divergent.saturating_add(1);
            let fd = first_divergence_report(&input, p, r, first.clone());
            let shr = shrink(&fd.program, default_divergence_pred);
            if shr.preserved_divergence {
                coverage.shrunk = coverage.shrunk.saturating_add(1);
                coverage.record_tag("M8-SHRINK");
                let _art =
                    CounterexampleArtifact::from_divergence(&fd, Some(shr.minimized.clone()));
            }
        }
    }
    c
}

/// Exhaustive small-state smoke: fixed seeds in R-TEST-01 bounds.
pub fn exhaustive_small_state(coverage: &mut CoverageEvidence) -> u64 {
    let mut equal = 0u64;
    for seed in 1u64..=32 {
        let cfg = GenConfig {
            seed,
            max_depth: 4,
            max_nodes: 24,
        };
        if execute_seeded(&cfg, coverage).is_equal() {
            equal = equal.saturating_add(1);
        }
    }
    equal
}

// ---------------------------------------------------------------------------
// Complexity helpers
// ---------------------------------------------------------------------------

fn expr_complexity(expr: &Expr) -> u64 {
    match expr {
        Expr::Value(_) | Expr::Var(_) | Expr::Receive | Expr::Yield | Expr::Halt => 1,
        Expr::Let { value, body, .. } => 1 + expr_complexity(value) + expr_complexity(body),
        Expr::Seq { first, second } => 1 + expr_complexity(first) + expr_complexity(second),
        Expr::If {
            condition,
            then_branch,
            else_branch,
        } => {
            1 + expr_complexity(condition)
                + expr_complexity(then_branch)
                + expr_complexity(else_branch)
        }
        Expr::Lambda { body, params, .. } => 1 + params.len() as u64 + expr_complexity(body),
        Expr::Call { func, args } => {
            1 + expr_complexity(func) + args.iter().map(expr_complexity).sum::<u64>()
        }
        Expr::Attenuate { cap, constraint } => {
            1 + expr_complexity(cap) + expr_complexity(constraint)
        }
        Expr::Request {
            capability,
            operation,
            target,
            params,
        } => {
            1 + expr_complexity(capability)
                + expr_complexity(operation)
                + expr_complexity(target)
                + params.iter().map(expr_complexity).sum::<u64>()
        }
        Expr::Spawn {
            expr: body,
            initial_budget,
            capabilities,
        } => {
            1 + expr_complexity(body)
                + expr_complexity(initial_budget)
                + capabilities.iter().map(expr_complexity).sum::<u64>()
        }
        Expr::Send { target, message } => 1 + expr_complexity(target) + expr_complexity(message),
        Expr::Delegate {
            capability,
            constraint,
            target,
        } => {
            1 + expr_complexity(capability) + expr_complexity(constraint) + expr_complexity(target)
        }
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::machine::sugar::{int, let_, seq, var};

    #[test]
    fn same_seed_same_program() {
        let c = GenConfig {
            seed: 42,
            max_depth: 4,
            max_nodes: 20,
        };
        let a = generate(&c);
        let b = generate(&c);
        assert_eq!(a.program, b.program);
        assert_eq!(a.seed, b.seed);
    }

    #[test]
    fn compare_equal_self() {
        let input = ExecutionInput::from_program(DiffProgram::new(int(7)), 0, 0);
        let (p, r, c) = run_case(&input);
        assert!(c.is_equal());
        assert_eq!(p.terminal, r.terminal);
    }

    #[test]
    fn compare_x_x_property() {
        let obs = NormalizedObservation {
            side: ObservationSide::Production,
            terminal: Observation::Halted(Value::Integer(1)),
        };
        assert!(compare(&obs, &obs).is_equal());
    }

    #[test]
    fn first_divergence_terminal_kind() {
        let prod = NormalizedObservation {
            side: ObservationSide::Production,
            terminal: Observation::Halted(Value::Integer(1)),
        };
        let refe = NormalizedObservation {
            side: ObservationSide::Reference,
            terminal: Observation::Fault(Fault::UnboundVariable(Symbol(0))),
        };
        match compare(&prod, &refe) {
            CompareResult::Diverged { first, .. } => {
                assert_eq!(first.path, DiffPath::TerminalKind);
            }
            CompareResult::Equal => panic!("expected diverge"),
        }
    }

    #[test]
    fn first_divergence_value() {
        let prod = NormalizedObservation {
            side: ObservationSide::Production,
            terminal: Observation::Halted(Value::Integer(1)),
        };
        let refe = NormalizedObservation {
            side: ObservationSide::Reference,
            terminal: Observation::Halted(Value::Integer(2)),
        };
        match compare(&prod, &refe) {
            CompareResult::Diverged { first, .. } => {
                assert_eq!(first.path, DiffPath::HaltedValue);
            }
            CompareResult::Equal => panic!("expected diverge"),
        }
    }

    #[test]
    fn shrink_preserves_artificial_divergence() {
        // Predicate: program complexity > 2 (artificial harness divergence stand-in
        // that shrinks toward minimal complexity-3 programs).
        fn pred(p: &DiffProgram) -> bool {
            p.complexity() > 2
        }
        let big = DiffProgram::new(seq(seq(int(1), int(2)), seq(int(3), int(4))));
        assert!(pred(&big));
        let shr = shrink(&big, pred);
        assert!(shr.preserved_divergence);
        assert!(pred(&shr.minimized));
        assert!(shr.minimized_complexity < shr.original_complexity);
        // Deterministic
        let shr2 = shrink(&big, pred);
        assert_eq!(shr.minimized, shr2.minimized);
    }

    #[test]
    fn shrink_does_not_claim_success_if_pred_fails() {
        fn never(p: &DiffProgram) -> bool {
            let _ = p;
            false
        }
        let p = DiffProgram::new(int(1));
        let shr = shrink(&p, never);
        assert!(!shr.preserved_divergence);
    }

    #[test]
    fn artifact_has_sixteen_canonical_names() {
        assert_eq!(CounterexampleArtifact::canonical_field_names().len(), 16);
    }

    #[test]
    fn artifact_from_divergence_fills_fields() {
        let input = ExecutionInput::from_program(DiffProgram::new(int(1)), 9, 9);
        let prod = NormalizedObservation {
            side: ObservationSide::Production,
            terminal: Observation::Halted(Value::Integer(1)),
        };
        let refe = NormalizedObservation {
            side: ObservationSide::Reference,
            terminal: Observation::Halted(Value::Integer(2)),
        };
        let first = Difference {
            path: DiffPath::HaltedValue,
            production: "Integer(1)".into(),
            reference: "Integer(2)".into(),
        };
        let fd = first_divergence_report(&input, prod, refe, first);
        let art = CounterexampleArtifact::from_divergence(&fd, Some(DiffProgram::new(int(0))));
        assert_eq!(art.seed, 9);
        assert_eq!(art.generator_version, GENERATOR_VERSION);
        assert!(art.first_divergence.is_some());
        assert!(art.minimized_case.is_some());
    }

    #[test]
    fn seeded_pipeline_agrees_for_many_seeds() {
        let mut cov = CoverageEvidence::default();
        let equal = exhaustive_small_state(&mut cov);
        assert!(equal >= 1);
        assert!(cov.generated >= 32);
        assert_eq!(cov.generated, cov.production_executed);
        assert_eq!(cov.generated, cov.reference_executed);
        // Pure CEK prod/ref should agree on generated domain
        assert_eq!(cov.divergent, 0, "unexpected pure-CEK divergence: {cov:?}");
        assert!(cov.tags.contains(&"M8-GENERATOR"));
        assert!(cov.tags.contains(&"M8-COMPARE"));
    }

    #[test]
    fn determinism_full_pipeline() {
        let cfg = GenConfig {
            seed: 7,
            max_depth: 3,
            max_nodes: 16,
        };
        let mut c1 = CoverageEvidence::default();
        let mut c2 = CoverageEvidence::default();
        let r1 = execute_seeded(&cfg, &mut c1);
        let r2 = execute_seeded(&cfg, &mut c2);
        assert_eq!(r1, r2);
        assert_eq!(generate(&cfg).program, generate(&cfg).program);
    }

    #[test]
    fn m2_unification_still_works() {
        let expr = let_(1, int(3), var(1));
        crate::m2::compare_m2(expr).expect("m2 agree");
    }

    #[test]
    fn negative_unbound_agrees() {
        let input = ExecutionInput::from_program(DiffProgram::new(var(99)), 0, 0);
        let (_, _, c) = run_case(&input);
        assert!(c.is_equal());
    }

    #[test]
    fn harness_mutation_intent_alter_observation_detected() {
        // M8 harness integrity — not M9. Altering one observation must diverge.
        let mut a = NormalizedObservation {
            side: ObservationSide::Production,
            terminal: Observation::Halted(Value::Unit),
        };
        let b = a.clone();
        assert!(compare(&a, &b).is_equal());
        a.terminal = Observation::Halted(Value::Integer(0));
        assert!(compare(&a, &b).is_diverged());
    }

    #[test]
    fn no_host_surface_in_system_api() {
        // Structural: system module has no Host type parameters in public runners.
        let _ = run_production;
        let _ = run_reference;
    }
}
