# Round 23: marked h5 successor (hand + enum + local cert; pending critic)

## Scope and totals

Only the marked adjacent degree-six `e=170, h=5` stratum is affected.
The byte-for-byte critic baseline is 224/286 whole boards and
121,908/156,112 weak context keys: 45 model roots, 16 raw-proof
failures, and CPU-capped board 285, with board 52's old deep job not
counted another time. At the frozen 21:21:15 CET snapshot there are
**254/286 whole boards** and **138,687/156,112 weak keys from complete
boards**. Direct relabelling within each remaining board stabilizer
covers **144,284/156,112 keys in total** (5,597 additional keys in
partial boards). These are shadow context keys, not SAT placements.
For every additional key, `hole-handoff.json` gives a literal relabelled
hole pair in its orbit and the checked occupancy prefix it matches.
Every one of the 900 labelled hole pairs of each counted whole board
is covered without relying on this partial-orbit credit.

New whole boards: 30; whole-board key increment 16,779; total key
increment including partial-board keys 22,376. The snapshot retains
97 checked receipts (including subcases of open boards), exactly one
unit split step at a time, independently rebound and dual checked.
No complete near-regular distribution, residue-floor increase,
U88 change, exact `t9` debit, h5 completion, or candidate.

## Soundness and calibrations

- `round23_transport.py` is the corrected h6 replay entry point;
  it checks both directions of A's frozen raw-to-representative
  transport on all 22,408 labels and verifies all 19,651 literal keys.
  Reversing the action without inversion fails on 19,908 labels.
  The two non-involution/transpose fixtures also verify physical holes.
  No h6 re-solve; no second G-059 debit. `transport.log` holds controls.
- `rows/e170_h5_physical_deficit.md` proves compact `I10` blockers and
  exact edge accounting. Literal folds on 1,960 smaller positives and
  their independent `I6` failures, 48 smaller edge-total checks, four
  independently supplied target clauses and all three of A's adverse
  guard/option-edge/padding mutations pass. Deficit control includes
  48 small totals and 15 guarded slot projections. The exact local
  debt equals 8 across 47 possible flags; this is the same equality
  as 86 edges of `W`, not an additional empirical restriction.
- The h5 initial split bits are left double slots 0 and 1; then right
  0,1; then both alternating for double slots 2..9. Delta audits
  recompute the exact units, all expected degree-budget clauses,
  and the physical boundary/slot witness literals. Compact witnesses
  omit an edge only for a forced full-support overlap and never omit
  a required negative selector. A Python incremental UNSAT or model
  is not accepted alone; a newly bound and checked LRAT is required.
- Exterior maximality adds about 6,200 rows; literal control finds 56
  smaller native positives, 1,904 negatives and 1,960 after greedy
  exterior saturation. Both target pilots hit limits; do not scale
  without better pricing. The graph-valid rule is not a case debit.
- Checked binary-to-sliced-ASCII proof conversion matches literal
  full and sliced ASCII on PHP(5,4). Reachable RAT is declined by the
  RUP trimmer. Sample ASCII trimming changed 50.22→36.29 and
  201.79→151.50 MB raw, validating both outputs and preserving the
  originals. Binary recovery reopened several archive-limited leaves;
  249/11 capped again. Raw/cpu/file-cap/guard stops remain open.

## Replays and costs

From the repo root, `sha256sum -c ralph/lanes/G/ROUND23_FREEZE.sha256`
checks all code, independent A inputs, snapshots and fresh sample logs.
`sha256sum -c scratch/G/round23/receipt-freeze.sha256` checks every new
accepted CNF, compressed proof, semantic receipt and witness file.
The `.zst` self-check was performed per receipt; this manifest binds
their actual hashes, not just lengths. From `scratch/G/round23`, run
the repo-absolute `round23_h5_replay.sh ID ...` in a fresh directory
or on unseen IDs (it will not overwrite an earlier replay folder).
It regenerates the formula, binds the independently checked delta and
all saved hashes, then runs `lrat-check` and `cake_lpr` on the same
uncompressed proof. Fresh samples `z271_0 z052_bm z283_010d q179_1`
all rechecked. To recompute raw/effective coverage, rerun
`round23_h5_status.py .` then `round23_h5_hole_cover.py . SNAPSHOT`.

At the frozen snapshot: 18,193.97 timed CPU-s (5.054 core-h across the
recorded attempt stages; excludes setup, four fresh rechecks and
in-flight time), 26,975,494,708 cumulative raw proof bytes reported,
3,382,286,169 bytes accepted compressed, peak timed RSS 527,124 KiB.
The bounded staging guard reserves all simultaneous raw conversions,
current/prospective compressed archive, and auxiliary files inside
8.8 GB. Nine further binary rescues began after the frozen snapshot;
their eventual outcomes belong to the next checkpoint, not this debit.
