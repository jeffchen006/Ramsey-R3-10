# Lane H — round 23 handoff, November 22, 2026

**No candidate and no active, stopped or detached lane-H PIDs.** Two-core
ceiling; work was foreground only, no production solver. Ledger checked
through r022: **238 near-regular MTF distributions plus Case R**, **ten
conditional U88 keys**, and **five missing e108 criticals**. B's floor is
still 108. E's three former conditional mixed cores now close the entire
11-edge stratum under its inherited premises, not the entire involution.

## Jobs

| PID | Command | Log | Cores | Start / end CET |
|---|---|---|---:|---|
| — | No live, stopped or detached job | — | 0 | — |
| foreground, finished | Pinned `env lean`, cached `--old build R310`, 5 targeted and 374 project axioms | `scratch/H/round23-{dev,dev2,build,axioms-targeted,axioms-project,axioms-project-retry,strict,toolchain}.log` | 1 per task, at most 2 | ~20:52–20:58 |
| foreground, finished | `check_selected_witness.py` (bounded), freeze/ledger checks and focused source reading | `scratch/H/round23-{controls,a-freeze-check,ledger-audit}.log` | 1 for control | ~20:56–21:01 |

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean H-039 (pending) | Graph-to-clause soundness for an explicit physical witness of size at least the bound (10): selected identities injective, all unordered pairs represented, a real edge must give a true positive literal. Compact vs full equivalent if omitted literals are guarded false; each such condition can follow from a base channel containing only guards in the outer row. No SAT-to-graph converse/general target binder. | `lean/R310/SelectedWitness.lean`, `ROUND23_REVIEW.md`, `ROUND23.sha256` | ~0.0451 metered incl. failed retries and controls |
| enum (controls, included in H-039) | C13 α=4, all 39 independent fours, 5,148 valuations, 78 failures when the sole live edge is omitted. Three width-three α=6 adverse plants. Four frozen h5 relaxation I10s, 180 literal physical pairs, 87,000 base clauses and 21 precise deletion-channel bindings. Cached Lean/Mathlib v4.35.0 build; strict 5 targeted and 374 project axiom reports pass. Single-threaded retry fixed a thread creation failure; failed invocation does not count. | `check_selected_witness.py`, `scratch/H/round23-{controls,strict,build}.log` | included |
| ledger through 022 | 18 scoped confirmed entries and two separate rejected recipes, D's mixed 2,686 tally and G's stale reversed reader. D m15 149/149 rebinding, all 539 same-pole m14 keys including five split keys (589 proof leaves), S/O open at cutoff. E-048 superseded by 5,779,378 lifts / 1,162 terminal IDs; E e8/P=2 closed and e8/P=0 only narrowed. F-040 superseded by 668 restricted rows, includes 405. G h6 confirmed all 49 / 51 proofs; h5 224 includes 211. No kernel, distribution, or flow graph debit. No referee-022 or scout-022 artifact. | `ralph/CLAIMS.md`, `ralph/critic/round_022.md`, `scratch/H/round23-ledger-audit.log` | negligible |
| ledger pending 023 (concurrent cutoff) | Staged A's transport regression and compact witness controls, H-039, and separately G's board 52 and 271/0 pilot receipts; 271/1 resource signal is open. No new baseline count. C's 20:58 six-edge equality is a preliminary board message, not yet a staged claim; check its final evidence together with E's interaction. B–F were still writing new state at ledger cutoff. | A `ROUND23_BLOCKERS.md` and freezes; `scratch/G/round23/work/{z052_bm,z271_0,z271_1}`; `ralph/BOARD.md` | — |
| pub / open (limited search) | DS1 rev. 18 is 40–41; Angeltveit's journal §7 partial lower count 43,225,483; no newer classical decision or public bulk order-39 / exact dense order-30 count located. New primary arXiv:2611.08375 concerns cyclic/ordered, no classical improvement. | `LIT.md` (§ Round 23 focused check) | negligible |

## Next

- Import final r023 verdicts with frozen rosters; include all lanes' late
  completed records that were not available at this handoff. Never add
  pilot leaves to whole-board totals unless complementary keys close.
- H-039 needs independent Lean and controls. G's production checker must
  still bind physical names, distinctness, true/false constants and all
  actual rows. Do not turn the four controls into proof of that binder.
- Best direct progress remains D's scoped m14 S/O frontier and G's
  concrete h5 residual boards; E's completed stratum has unusually clean
  terminal evidence but narrower reach, and its e8/P=0 branch is open.
  Monitor C/E's physical-overlap condition from `crown23_two_window_factor.md`
  if the next critic asks for a short formal bridge. No repeat of row22
  proof production, no H solver queue.
