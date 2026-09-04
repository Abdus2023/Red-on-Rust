# M9 Mutation Matrix (campaign domain B)

Baseline revision: `2e92bf48d624873512831c105601dbbd7e5738f0`  
Baseline: PASS  
Harness (domain A): PASS — not counted in kill-rate  

| ID | Terminal | Materialize | Verify | Build | Targeted | Diff | Security | Evidence |
|---|---|---|---|---|---|---|---|---|
| M001 | KILLED | PASS | PASS | PASS | FAIL | FAIL | False | targeted_detection+differential_detection |
| M002 | KILLED | PASS | PASS | PASS | FAIL | FAIL | False | targeted_detection+differential_detection |
| M003 | KILLED | PASS | PASS | PASS | FAIL | FAIL | False | targeted_detection+differential_detection |
| M004 | KILLED | PASS | PASS | PASS | FAIL | FAIL | True | targeted_detection+differential_detection |
| M005 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M006 | KILLED | PASS | PASS | PASS | FAIL | FAIL | True | targeted_detection+differential_detection |
| M007 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M008 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M009 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M010 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M011 | KILLED | PASS | PASS | PASS | FAIL | PASS | False | targeted_detection |
| M012 | KILLED | PASS | PASS | PASS | FAIL | FAIL | False | targeted_detection+differential_detection |
| M013 | KILLED | PASS | PASS | PASS | FAIL | FAIL | False | targeted_detection+differential_detection |
| M014 | KILLED | PASS | PASS | PASS | FAIL | N-A | False | targeted_detection |
| M015 | KILLED | PASS | PASS | PASS | FAIL | PASS | True | targeted_detection |
| M016 | KILLED | PASS | PASS | PASS | FAIL | PASS | True | targeted_detection |
| M017 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M018 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M019 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M020 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M021 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M022 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M023 | KILLED | PASS | PASS | PASS | FAIL | PASS | True | targeted_detection |
| M024 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M025 | KILLED | PASS | PASS | PASS | FAIL | PASS | True | targeted_detection |
| M026 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M027 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M028 | KILLED | PASS | PASS | PASS | FAIL | FAIL | True | targeted_detection+differential_detection |
| M029 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M030 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M031 | KILLED | PASS | PASS | PASS | FAIL | N-A | False | targeted_detection |
| M032 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M033 | KILLED | PASS | PASS | PASS | FAIL | N-A | False | targeted_detection |
| M034 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M035 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M036 | KILLED | PASS | PASS | PASS | FAIL | N-A | False | audit/_checker_mutations.py -k M036 exit 0 (mutant killed by gate) |
| M037 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M038 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M039 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M040 | KILLED | PASS | PASS | PASS | FAIL | N-A | False | targeted_detection |
| M041 | KILLED | PASS | PASS | PASS | FAIL | N-A | True | targeted_detection |
| M042 | KILLED | PASS | PASS | PASS | FAIL | N-A | False | targeted_detection |

**Kill rate (domain B only):** 100%  (42/42 non-equivalent)
**Critical survived:** False
**Gate OK:** True

Terminal states are mutually exclusive. Build failure ⇒ INCONCLUSIVE (never auto-KILLED). Harness pass ≠ MutationKillRate.
