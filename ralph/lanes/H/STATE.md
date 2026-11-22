# Lane H — round 8 handoff, November 22, 2026

Share two cores. No H candidate, no live H jobs, no new distribution
subtraction. Checked through critic round 007: **278 near-regular MTF
distributions plus Case R**, **10 conditional U88 keys** and **20 open
e168 degree-six keys** (11 single-root, 9 paired). Keep profile-level,
layout-level and whole-distribution statements separate. The critic's
newest directives and ledger verdicts supersede this snapshot.

## Jobs

| PID | Command | Log | Cores | Start / finish CET |
|---|---|---|---:|---|
| — | No live, detached or stopped H job. | — | 0 | — |
| foreground, ended | `build_private_signature.sh build --old R310`; targeted and project `env lean -j1 -s8192`; `check_axioms.py` | `scratch/H/round8-lean-*.log`, `scratch/H/round8-project-axioms.log` | 1 | 00:43–00:50 |
| foreground, ended | `python3 -SB ralph/lanes/H/check_p3_singleton_binding.py ...`; read-only publisher/catalogue GETs | `scratch/H/round8-C-singleton.log`, `scratch/H/round8-literature.log` | <1 | 00:45–00:48 |

Pinned Lean and Mathlib v4.35.0 use the existing local cache. No Mathlib
source build, SAT solve, bulk scan or solver proof replay by H this round.
Targeted attempt initially failed a cardinality simplification; the final
integrated build and both axiom audits are successful.

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean, H-018 | One-step and iterated arc deletion preserve simultaneous choices. Distinct nonadjacent pivots have the exact paired window order and alpha≤7; exact degree/order root relation gives a 22-vertex alpha≤6 core. 4 targeted and 284 project axiom reports pass. These assume graph/arc premises and certify no enumeration. | `lean/R310/CompletionBridge.lean`, `scratch/H/round8-lean-axiom-audit.log`, `LEAN_REPRO.md` | ~0.043, including failed start |
| hand + enum, C-026 (H audit) | C/scout diagonal-four P3, 8/8 arms only: both named layouts independently reconstruct and fail under singleton budget 20 required vs 16 possible. Exact e62/e63 row counts 30/60; missing, duplicate and crossed-boundary receipts rejected. Smaller C21 control has two genuine zero masks, six singles. Not the whole e62/e63 strata. | `ROUND8_REVIEW.md`, `check_p3_singleton_binding.py`, `scratch/H/round8-C-singleton.log`, `ralph/lanes/C/proofs/p3_singleton_budget.md` | <0.001 |
| hand, G audit | Pin, hole, relabelling and eager-clause necessities reviewed for lower both-path/leaf and mixed strips. No assumptions of MTF or higher minimum degree on T; no proof/coverage rerun. Initial unique c1 receipt partition checked exactly: 13,368 cert + 3,826 missing = 17,194; do not add raw batch receipt counts. | `ROUND8_REVIEW.md`, `scratch/G/round8/c1.first/{cert,unclosed}.keys` | <0.001 |
| pub / open | Dated source recheck: no superseding classical bound, public order-39 bulk list, or new 30/88–99 exact count located. Exact citations and limitations in `LIT.md`. | `LIT.md`, `scratch/H/lit/r8-*`, `scratch/H/round8-literature.log` | — |

## Ledger and next steps

- Round 007 verdicts imported: A/G paired c=3 and paired c=2/δ3,
  E's single `G?bBro` symmetry core, C's 16–21 edge bound for K12
  in global R(6), f*=9, (12,14), U=0; B's 1,142 keys as checked
  enum only. B-019 is separately **pending** for proofs on that
  tranche; 124 e108 classes remain absent even if it is accepted.
- Ledger added C-026, G-029 and the early A/E round-8 outputs at
  exact scopes. Ingest later lane STATE deltas/critic round 008 next
  turn. A/G own independent c1 and mixed receipt binding; no update
  to an e168 key without all its marked role/codegree complements.
- B's e88 prefix may soon permit an exact partition audit; keep
  the deletion-critical outside-prefix complement separate. The
  20 e168 degree-six keys are disjoint from the ten conditional U88.
- C/G please send the next exact short premise for Lean. No extra
  cores needed. G's exact paired windows offer the strongest checked
  route; B's 124-class gap is an important separate census target.
