# 02 — Section Hierarchy (Stable Section Index)

24 sections in 8 parts. **Provenance** cites `Red-on-Rust.md` line ranges (the frozen source) and turn numbers `[N]`. "Superseded" marks source material that an earlier draft contained but which the latest frozen text replaces (see `06`).

## Part I — Foundations
| ID | Title | Primary provenance (turn, lines) | Superseded material retained for traceability |
|---|---|---|---|
| S-01 | Scope, status, conventions | [54] L37640–37695; [60] L41280–41320 | — |
| S-02 | Core thesis and central invariants | [33] L27485–27654; [60]/README L41320–41770 | — |
| S-03 | Trust model and TCB | [33] L27611–27624; [35] L28178–28230; [54] L37722–37748 | — |
| S-04 | System architecture and component boundaries | [54] L37750–37790; [17] L9059–9118; [58] L39036–39195 | — |
| S-05 | LLM/planner boundary | [33] L27150–27480; [34] L27920–27931; [54] L37750–37790 | [3] isolation-ladder planner interface (L306–325, illustrative) |
| S-06 | Compilation boundary | [54] L37750–37790; [17] L9059–9097; [58] L39253–39308; [4] L1722–1775 | [5] J1–J4 judgment forms (L1953–1981, superseded by combined judgment) |
| S-07 | Core calculus (syntax) | [20] L12075–12195; [9] L3368–4062 (v2 calculus); [30] L23726–23820; [16] L8653–8707 | [5] 14-constructor calculus (L1910–1952); [7] 12-constructor calculus incl. `await` (L3830–3873) — see C-04 |
| S-08 | CEK machine | [25] L16861–18084 (frozen); [30] L23821–23856; [54] L37800–37862; [23] L14632–14642 | — |
| S-09 | Capability algebra | [11] L6344–6671 (v0.2 frozen); [16] L6672–6815 (API v0.2 + cost algebra v0.1) | [9] v0.1 (L4756–5501); [10] corrections (L5502–6343) — folded in |
| S-10 | Capability kernel | [16] L6672–6729; [27] L19077–19200; [17] L9119–9135; [58] L39370–39410 | — |
| S-11 | Budget model | [16] L8653–9050 (v0.3 frozen); [17] L9140–9245; [35] L28203–28240 (partition) | [11] 5-dim `⟨F,M,C,I,W⟩` (L6730–6763); [13]/[14] pre-fix `BudgetOK` (L7314–7330) — see C-07 |
| S-12 | Effect model and request sequence | [54] L37891–37922 (16-step frozen); [30] L23857–24002 (14-gate); [31] L25479–25492, L25799–25825 (completion accounting) | [13] 15-rule v0.2 (L7156–7248); [18] 14-step (L11053–11090) — see C-01 |
| S-13 | Transactional issuance / durability boundary | [47] L35078–35258 (15B frozen); [54] L37908–37981 | [33] §2 journal sketch (L26146–26177, superseded by unified WAL) — see C-39 |
| S-14 | Host boundary and replay | [31] L25972–25996; [54] L37985–38000; [30] L24003–24030 (HashMap ReplayHost, superseded) | — |
| S-15 | Actors and deterministic scheduling | [32] L25457–26108 (frozen); [31] L24069–25428 (global machine) | — |
| S-16 | Marshalling and delegation | [32] L25674–26001; [54] L37946–37959; [16] L8695–8698 | — |
| S-17 | Canonical serialization (15A) | [45] L32936–33707 (final frozen); [39]/[40] L29451–31298 (revised grammar + vectors); [46] L34987–35024 (duplicate-key patch) | [36] L28718–29094 (15A v1); [38] L29886–30531 (15A revised) — see C-02, C-12 |
| S-18 | Persistence protocol (15B) | [47] L35078–35258 (frozen); [46] L33757–34916 (architecture) | [33] §3–§5 (L26178–26270, sketch) |
| S-19 | Crash recovery | [47] L35159–35258 (frozen matrix + recovery); [33] L26109–27484 (Phase 14) | — |
| S-20 | Independent reference model / differential | [48] L35272–37168 (15C); [54] L37985–38560; [35] L28590–28717 | — |
| S-21 | Test infrastructure / mutation / CI | [54] L38587–38970 (frozen); [49] L37169–37338 (15D); [50] L37339–37459 (closure clarifications) | — |
| S-22 | Repository structure / crates | [58] L39036–41273 (bootstrap pack) | [56] crate-name draft (L38990–38999, superseded by ror-* names) |
| S-23 | Milestones and implementation order | [58] L40763–41273; [54] L37793–37812 (20-step order); [60] L42108–42266 | — |
| S-24 | Conformance claims / prohibited shortcuts | [50] L37416–37459; [54] L38858–38970; [60] L42030–42090 | — |

## Structural invariants of the split
1. No theorem/invariant/contract/type definition spans two sections (e.g., the capability algebra stays wholly in S-09+S-10; the 16-step request sequence stays wholly in S-12; the 15A grammar stays wholly in S-17).
2. Normative text is separated from explanatory material: examples, golden vectors, and sketches are marked **Non-normative** in `01`.
3. Supersession is never silent: every superseded draft is listed in its section's "Superseded material" column and in `06`.

## Dependency ordering (section level)
See `04-dependency-graph.md` for the full graph. Short form:
`S-01…S-06 (foundations) → S-07 → S-08 → {S-09 → S-10} → S-11 → S-12 → {S-13 → S-14} → {S-15 → S-16} → S-17 → S-18 → S-19 → {S-20 → S-21} → {S-22, S-23, S-24}`
