# Round 14 — cap-five 17/17 ordered census, exact prefix only

**Status: hand + enum for the completed alignment prefix, pending critic.**
The unscanned remainder is open. This is not an exclusion of the full
17/17 marked block, general bicliques, R(5), or Case R. No SAT, proof
jobs, candidate graphs, or unresolved fillings within the checked prefix.

## Cover and control

- `proofs/panel17_census.md` explains why every actual two-neutral cap-five
  `K4,4` yields some ordered alignment. It uses `R(3,6)=18` and the seven
  published classes D-R1/D-G3. The local graph6 catalogue byte-matches the
  separately retrieved McKay file `scratch/C/r14/McKay.r36_17.g6`.
  The finite rejection rules are proved in `proofs/reciprocal_panel17.md`.
- C groups oriented right frames by a header tuple then scans compatible
  members in right-ID/bit order. The A scanner visits all raw ordered
  right-frame/bit pairs and tests the header from the two graphs. Its
  independent inventory reconstruction checks every one of the 55,055
  physical frames, and its exact subset-alpha atlas of 9,959 packages agrees
  bytewise in every shard. The two panel algorithms compare every header
  ID and stage bytewise from pipes, with no large text manifest saved.
  Each panel ID is passed to both the C++ and independent scout Python
  terminals, and all five reason counts are compared per ID.
- Before production, the smaller controls matched all 366 atlas entries;
  3,448 real rectangles were retained, 31,032 single-crossing mutations
  rejected, and 2,118 planted partial graphs survived propagation. Lane A
  also verified the nonempty repeated-row package. The merger accepts a
  fixed positive binary stream and rejects a missing map, a duplicate,
  and an altered stage. Lane A's separate first-shard audit includes
  23,100 old left-triple and 42,709 old pilot depths and 9 old pilot
  terminal vectors; all match. See A's round-14 BOARD entry.

## Gates and exact frontier

First shard `[0,2048)`: 4,322,749 headers → 1,002,255 forward signature →
475,368 reciprocal signature → 475,228 local → 785 panel → 174 with
joint fillings → 0 unresolved; 3,086 joint fillings all rejected.
Terminal calls fell **605×**, not a measured end-to-end ratio. Each
terminal reason vector matches; A's separate roster digest is
`b85ba1c25268e491de9e16e94b40acca81282293452c19482af766e28a34af62`.
First complete shard 20.741 CPU-s, or 756 CPU-s extrapolated by headers;
the original 366-stratum pilot extrapolates to 2,651 CPU-s conservatively
including its terminal setup cost. Both plus setup are below 7,200 CPU-s.
A fresh first-only rebuild reproduced all three digests and all counts.

| Scope | Header | Forward | Reciprocal | Local | Panel | Joint IDs | Unresolved |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `[0,24576)` (12 disjoint shards) | 67,417,211 | 20,960,185 | 8,079,434 | 8,076,698 | 12,594 | 3,464 | 0 |
| Remaining `[24576,55055)` (15 shards) | 90,054,790 | — | — | — | — | — | — |
| Full independent header roster | 157,472,001 | — | — | — | — | — | — |

Both identification bits, identical physical frame IDs, and both side
orientations are included, even when already examined in the past. In
the prefix the two terminal implementations agreed on all 12,594 panel
IDs, including 9,130 with no joint filling. There were **148,231 joint
fillings**, rejected for degree / triangle / codegree / forced `I10` in
counts **7,584 / 0 / 36,245 / 104,402**. Reduction in terminal call count
across the prefix: **641×**. A separate header generator agrees on the
exact normalized ID digest and both bit counts for all 12 shards, not
just totals. `scratch/C/r14/coverage.tsv` is the checked partition;
`unresolved.tsv` and `unchecked_panels.tsv` are empty. Across all
completed shards, concatenating normalized terminal lines
`left right bit degree triangle codegree I10 open\n` in lexicographic ID
order gives SHA256
`b41dddffbf00ade7f4c669b9456d5c707deda28c585bd5d2197c81a4bbd935bf`.
The stage hash roll-up uses `low high stage_sha256\n` in shard order:
`edf72215d301977c4f05c37d8ff27c56314df37ea9d5d6df1ea3a4668dbd5692`.

## Why it stopped

The predeclared per-ID gate was 100 ms C / 1,000 ms Python. In
`[22528,24576)`, six Python terminal IDs exceeded 1 s, with maximum
3,859.940 ms; C max 59.938 ms. Each of `(23155,26938,1)` and
`(23155,23155,1)` has 7,059 joint fillings, all individually rejected by
`I10` by both terminals. The final shard used 114.886 CPU-s vs 20.741
for the first one; it completed successfully, but the scheduler did
**not** start `[24576,26624)`. The stop was the expensive-tail policy,
not exhaustion, a timeout, a scanner disagreement or a surviving model.
Production shards consumed 511.474 CPU-s (264.346 screening). Lane C's
including build, controls, first digest capture and separate first-shard
replay was about 571 CPU-s (0.159 CPU-h), with at most four simultaneous
core slots during the added first replay and about 11 MiB retained.

## Audit and next use

From repo root, a fresh calibrated first-shard replay is:
`bash ralph/lanes/C/replay_panel17_r14.sh CALLER_OWNED_EMPTY_WORKDIR`.
To cheaply verify the frozen prefix **without** rescanning, run
`python3 -B ralph/lanes/C/audit_panel17_r14.py scratch/C/r14 scratch/C/r14/A.coverage.tsv`
with an owned work copy if not lane C (the audit writes three ledgers).
The single compressed first stream is retained; all other stage streams
are represented by their byte-compared digests. `ROUND14_INPUTS.sha256`
and `ROUND14_RESULTS.sha256` bind inputs and results.

Ask critic to approve a tail-specific optimization and then price on the
six observed >1 s IDs and a representative low-cost control before any
continuation. An early `I10` test on the upper graph tightened by unions
of compatible row neighborhoods is sound (every actual package edge
must be among those possibilities); no saving is measured. If repriced,
start at left ID 24576, not at zero; keep both independent terminals and
the same frozen header checks. The order 16/17, 15/17 and 16/16 routes
are separate, unpriced here. H may formalize the short 17/17
two-neutral-cover equivalence without the computation.
