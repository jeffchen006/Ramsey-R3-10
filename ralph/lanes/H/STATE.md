# Lane H — round 11 handoff, November 22, 2026

Share two cores for round 11. No H candidate or whole-distribution
subtraction. Critic baseline through round 010: **278 near-regular MTF
distributions plus Case R**, **10 conditional U88 keys**, **20 open e168
d6 keys** (11 single-root, nine paired). B's confirmed deficit was 52;
its round-11 submission reports **five**, still pending review and not
floor 109. Full stream is not full replay for C's reciprocal 22/21.

## Jobs

| PID | Command | Log | Cores | Start / end CET |
|---|---|---|---:|---|
| — | No live, detached or stopped H jobs. | — | 0 | — |
| foreground, finished | Pinned-cache `build_private_signature.sh env lean -j1 -s8192`, then `build --old R310`, narrow and integrated axiom audit; rebuilt after degree wrapper | `scratch/H/round11-{anchor*,pairs-first,build*,targeted,project}.log` | 1 each | ~04:46–04:57 |
| foreground, finished | `python3 -SB check_round11_{controls,receipts}.py` (serial invocations) | `scratch/H/round11-{controls,receipts}.log` | 1 each | <6 s each |

Lean/Mathlib v4.35.0, existing cache only. No solver, LRAT checker,
or large source generation in H this round.

## Results and claims

| Label | Result | Evidence | H core-h |
|---|---|---|---:|
| Lean, H-022 pending | Three-anchor exterior capacity `|X|+4≤3α`, hence at most 14 at α≤6. No signature caps. Marked closed-neighbourhood deletion also gives degree ≥ order−22 under explicit paired geometry premises, not the 14-slot deficit type. Catalogue controls 936 / 22,474 / 1,894,780 marks on known orders 13/17/22. | `lean/R310/AnchorSaturation.lean`, `ROUND11_REVIEW.md`, `scratch/H/round11-controls.log` | shared below |
| Lean, H-023 pending | Empty/hub/exact-triangle classification of pairwise-intersecting two-sets. All 32,768 six-vertex families and smaller controls agree. Six targeted / 306 integrated axiom reports passed. Neither D's searches nor the R(3) disjoint-pair theorem are in Lean. | `lean/R310/IntersectingPairs.lean`, `ROUND11_REVIEW.md`, `scratch/H/round11-{targeted,project}.log` | ~0.06 combined Lean incl. initial attempts and audits |
| enum provenance only | B-027 independently merged 47 added rows with prior union (1,875 critical / 2,104,146 total). All 37 clique indices and ten residual graph/digest receipts bound. Not a semantic replay; B's proofs pending critic. | `check_round11_receipts.py`, `scratch/H/round11-receipts.log` | <0.001 |
| open; literature refresh | No decision, public bulk 39 class or new exact dense order-30 count identified. Two adjacent primary methods recorded (fan gluing, four-colour incidence/CNF); neither changes a lane premise. | `LIT.md`, `scratch/H/round11-literature.log` | — |

## Ledger and next steps

- `ralph/CLAIMS.md` imports critic round-010 scopes: independent d9
  j3/δ2 and j4/δ3 minima; d8 j2 middle remains pending; D's disjoint
  pair theorem separate from 78 local proofs; F's ≥25 parity bound
  separate from LRAT zero decision; E's four conditional cores;
  B's 61 already-supplied plus 5 and 6 new extension tranches.
- Round-11 submissions in the ledger are producer results pending
  review, not distribution debits. For C record 32 local certs and
  complete stream but no overall 22/21 decision until replay. A/G's
  equality census has only cross-singleton deficits on supplied order-21
  source; do not infer this from the Lean bound. G's middle-only scope
  remains separate from 69,278 matching roles. E's minimum degree floor
  for ≤74 is not recovery of the missing e74 class.
- Best present line is B's 7,954 untried exact e98 parents, if approved
  by critic: last wave reduced deficit to five, with receipts for all
  47 newly supplied keys. Do not extrapolate a yield after two zero
  batches. Continue to docket C's replay and A/G semantics only at
  actual scope. Pick up D or other late submissions from their next
  STATE/report. Request a small C/G lemma if one helps the next cover.
