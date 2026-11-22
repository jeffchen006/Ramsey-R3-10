# Round 15 — supplied deletion-reducible 32/e108 keys

## Prelaunch scope and estimates

The critic authorized this named list only. Reuse the round-6 and round-14
checked pilots: 4,096 + 32,768 − 64 = 36,800 distinct keys. The residual is
2,065,471 keys in 257 shards by zero-based residual ordinal modulo 257,
each with 8,036 or 8,037 graph6 records. Every shard spans nearly all source
ranks. No source acquisition, critical-key retesting, or floor 109 claim.

At the round-14 production-plus-independent-replay rate (159.74 CPU-s for
32,768), an 8,037-key shard estimates 39.18 CPU-s and the residual 2.80
core-h. The first shard adds archived K7,9, saturated Exoo39 and e104
controls, proof/CNF mutations, and source-rank mutations. Reprice after
that shard, then after the first eight-slot wave. Expect roughly 21–32 min
wall for eight slots, provided the tested rate holds. Shard caps stop on
slow proofs, missing pins, proof/checker failures, or binding failures.
Reserve time for the exact ordered merge. Compact proof packs estimate
~215 MB payload, with index, cliques and ordered dispositions well inside
the 2 GiB added-storage ceiling. These are estimates, not tail bounds.

## First-shard correction and calibration

The initial preflight stopped on the round-6 receipt footer; parsing now
requires both exact footers and matches all 173 indexed LRAT hashes in
the two logs. The first shard then found 7,682 eight-cliques, 354
seven-clique pins and one key without a seven-clique (rank **1,850,896**).
No wave was launched from that attempt. Both checkers validated a direct
unpinned LRAT for that rank (6,748,074 bytes). A six-demand witness gives
a much smaller 7,757-byte LRAT on the same rank.

For either six or seven mutually incompatible demands, choose a covering
row for each demand in an arbitrary completion. Incompatibility makes
this choice injective. Permute the seven rows to put the chosen rows at
the front in demand order; in the six case the last row is unpinned.
Zero-pin cases use the unrestricted core. The two encoders construct the
CNF separately; replay requires both proof verification markers on the
reconstructed bytes. A separate order-30 MTF control with a degree-seven
root verifies the physical six-pin renumbering against every clause and
with a SAT solve. A repeated pin is rejected, as are the old wrong-CNF,
empty-proof, missing-index and invalid-clique mutations.

The corrected end-to-end shard 0 closed all 8,037 ranks with 7,682
cliques and 355 dual LRATs (320 RUP, 35 CaDiCaL): **30.56 CPU-s,
32.45 s wall** including controls. It wrote 865,793 packed proof bytes.
From that shard alone, residual work estimates ~2.18 core-h; the older
2.80 core-h reference remains a conservative planning rate, not a bound.
The first multiworker wave is stripes 1–8 only, with 80 CPU-s soft per
worker and 240 s wall per worker, and a 1,200 CPU-s campaign gate. A
failure leaves all unfinished stripes open.

Wave 1 passed all eight shards in **237.75 CPU-s, 33.22 s wall**;
individual workers took 27.69–32.23 CPU-s and at most 33.15 s wall,
with peak RSS under 57 MiB per worker. At that repriced rate, the
remaining 248 shards estimate **~2.05 core-h and ~17–22 min wall**.
Keep eight slots (no increase), an outer 42-min wall cap, and a 13,900
CPU-s main-campaign gate so that the already measured setup/controls/wave
and final merge have room under 4 aggregate CPU-h. Per-worker caps and
the storage preflight stay enabled; retain exact gaps on any stop.

## Replay contract

From `scratch/B`, with `ulimit -v 16777216`, `LC_ALL=C` and
`PYTHONDONTWRITEBYTECODE=1`, the main script is
`../../ralph/lanes/B/src/e108_r15.py`. `prepare` streams the exact source,
checks the round-14 freeze, and assigns the 64 overlapping ranks to
round 14. The original round-6 and round-14 receipt rows remain intact.
For a completed new shard, `recheck work/e108_r15 ID` (use `nice` and a
bounded `timeout`) revalidates every demand witness, rebuilds each CNF,
and runs both LRAT checkers, without any proof search. It uses one fresh
`recheckNNN` directory for reusable temporary files. Each shard stores
ordered clique indices, an exact residual proof index, one packed proof
file, and a receipt published only after full dual replay. `merge
work/e108_r15 --full` recomputes the source partition and the disjoint
stripe alignment, checks receipt and proof payload binding, and writes
one disposition per source rank. Calling `merge` without `--full`
retains exact incomplete or unstarted ranks as open. The merge is an
index/binding audit, not a third checker pass.

## Final result: cert, named reducible list only

Every one of the **2,102,271 supplied deletion-reducible 32/e108 residues**
is excluded as the exterior of an MTF degree-seven root. All 257 new
shards passed, with no skipped, capped or unchecked ranks. The two prior
pilots supply 36,800 distinct keys; none are counted in the new shards.

| Disposition | Verified demand cliques | Dual-checked LRATs | Keys |
|---|---:|---:|---:|
| Adopted round 6, excluding the 64 overlaps | 3,862 | 170 | 4,032 |
| Adopted round 14 | 31,407 | 1,361 | 32,768 |
| Round 15 | 1,980,937 | 84,534 | 2,065,471 |
| **Total** | **2,016,206** | **86,065** | **2,102,271** |

Of the new LRATs, 76,605 were one-line RUP and 7,929 were solver proofs;
84,498 used seven pins, 36 six pins, and none required unpinned fallback.
The largest new packed proof was 15,745 bytes (rank 1,450, shard 141).
The independent streaming index auditor (`src/e108_r15_audit.py`)
matched the merged per-rank transcript without reading the producer's
residual-ordinal table. Its dropped, duplicate and wrong-stripe proof
rank controls all rejected. The ordered SHA256 is
`030a843d10588fd842e673a476aa80691beb3c5e7677f20b8a8e16b2ba138460`;
`unchecked-ranks.txt` is empty.

The main 248 shards finished in **6,870.59 CPU-s / 1,019.70 wall-s**.
Including setup, first-shard controls, initial wave, final merge and
streaming audit, round 15 used **about 1.99 core-h**. The slowest shard
took 32.15 CPU-s; the longest wall time was 58.68 s. Packed new LRAT
payload is 204,501,721 bytes; total run directory is **240 MiB**. No
jobs remain. Evidence is `scratch/B/work/e108_r15/`,
`scratch/B/logs/e108_r15_*`, and `ROUND15.sha256` (from repo root).

The 1,875 previously supplied criticals are outside this campaign, and
five critical classes are still missing. The inventory stays at
2,104,146 / 2,104,151. No floor 109, U88 or degree-profile debit follows.
