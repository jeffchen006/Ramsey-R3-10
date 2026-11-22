# Round 11 — cap-five reciprocal windows on 22 and 21 vertices

No candidate. This concerns only a complete K3,3 in the 9-regular
case with maximum codegree at most five, with anti-triple window
orders exactly 22 and 21. The order-22/order-22 exclusion was already
independently confirmed (R-001, `ROUND10_REPLAY.md`). No result on
22/20, 21/21, cap six, R(5) as a whole, or the Ramsey number.

## Source and complete stream — enum

The order-22 source contains 191 distinct, valid catalogue classes
as checked in round 10 [D-C7]. The order-21 source contains 1,118,436
graphs; the critic matched B's regenerated catalogue to the
independent McKay-sourced catalogue byte-for-byte after canonicalization
(`scratch/critic/r10/C/provenance.log`). Freeze the exact raw row order
of both source files; `scratch/C/r11/inputs.tsv` binds every order-21
row to one of 73 nonoverlapping zero-based half-open intervals. The
intervals include every host, not merely ones which yield a map. Four
16,384-host-total staged intervals came before expansion. All 84,713
staged exact map keys, including 1,250 domain obstructions, matched
the independent audit. The 395 planted asymmetric positives and
4,882 exact bounded no-index keys reproduced byte-for-byte.

The stream constructs one left mark index per batch worker and kept
every aligned rooted key, without isomorphism deduplication. Final
counts from the 73 exact intervals:

| Terminal test or stream status | Rooted maps |
|---|---:|
| Independent ten in the upper graph | 9,593,683 |
| Fixed undominated pair | 1,150,020 |
| Already over codegree cap | 759,744 |
| Independent ten after row-domain pruning | 78,883 |
| Forced-edge domain contradiction | 31,276 |
| Row/column contradiction | 26,635 |
| Empty row domain | 16,905 |
| Stream-live (subsequently repaired by LRAT) | 32 |
| **Total** | **11,657,178** |

By successive catalogue quartiles: 872,906, 2,063,570, 8,221,305,
499,397. The busiest third quarter contains over 16 times as many
rooted alignments as the fourth. Logical map-journal size is
1,299,926,766 bytes. Interval paths and hashes
are in `scratch/C/r11/*.stream.sha256.tsv`. Raw alternate mark lists
are deleted only after audit; their hashes and the matched card lists
are retained. Rebuilding the raw lists is deterministic.

## Independent replay

The independent C++ scout enumerates the right marked cards before
left-key filtering. Python regenerates the exact marks and enumerates
the degree-compatible adjacency bijections for every matched card
pair; each exact role key must remove one and only one key from the
stream journal. It checks the three direct witness types against a
separately merged lower graph and replays all domain rejections using
the scout Python propagator. No domain UNSAT is inferred just from
a timeout. The final ledger checks the SHA-256 of the catalogue
concatenated from interval sources and compares both passes' totals,
and requires an exact proof receipt for every stream-live key.

**Complete (hand + enum; checked LRATs for the 32 repairs).** Both passes
agree on all 11,657,178 exact rooted maps, including 11,503,447 direct
witnesses and 153,699 domain contradictions. The independent replay
also leaves exactly the same 32 maps for proof repair. The final ledger
binds both catalogues, every shard and all repair receipts, with zero
unresolved maps. See `scratch/C/r11/{coverage.tsv,coverage.log}`.

The eight stream batches cost 1,021.11 CPU-s including index builds;
successful independent source, index and audit cost 1,175.64 + 761.49
+ 4,417.87 CPU-s. Two early Python audits were stopped by CPU limits
(767.68 CPU-s in those audit processes, signal 24). Four disjoint resume
jobs covered the missing intervals; no capped shard is counted before
replay. Large shards used a shell-cache optimization that exactly
matches the uncached merge on 395 planted and 4,882 small no-index
maps and on 28,658 + 27,246 exact target maps in the staged cross-checks.
In the first staged timing it cut the audit from 18.36 to 12.64 CPU-s.
The cache does not remove any rooted map. Logs are in
`scratch/C/r11/{merge-smaller.log,merge-cal/,merge-cal-q3/}`.

Together with 22/22, this excludes opposite union 12 or 13 when A
is a codegree-five triangle with exactly three common neighbours B.
If B also has all three codegrees five, B must have exactly five
common neighbours and a window of order 20. This corollary is proved
in `proofs/reciprocal_r11.md`. Await critic review of the exact scope.

## Exact repairs and bounded pricing — cert / estimate

All 32 stream-live keys fall in `[645234,661618)`. The conservative
original dense formula and the new row-selector formula independently
give UNSAT on every key. Both `cake_lpr` and `lrat-check` verified
every proof in both families. The dense formula needs no codegree cap.
`scratch/C/r11/live.tsv` gives their keys; `live-proofs/receipts.tsv`
and `live-proofs-dense/receipts.tsv` bind each key and both file hashes.
Repair generation and verification take 25.71 CPU-s together.

On 132 specifically matched domain keys in the staged quartiles 1
and 4 and the busiest interval of quartile 3, the thin CNFs are
literal clause subsets of the original dense CNFs and both proofs
pass both checkers. On 96 of those keys, selector CNFs also pass
both checkers. The selector proof encoding is justified in
`proofs/reciprocal_r11.md`; all 395 smaller positives retain a model.
For the matched 96 keys, the generation/solver/checker sums are
54.38 CPU-s dense, 22.77 thin, 14.33 selector. A separate relabeling
pilot on 1,250 staged domain keys finds 985 representatives, checking
each explicit coloured graph isomorphism; no match or proof key from
the census is removed on this basis. `scratch/C/r11/proof-ledger.log`
projects the 153,699-domain-key proof backlog at 10.37 CPU-h thin
or 6.57 CPU-h selector, excluding audit and driver overhead. These
are pricing results, not a proof for every domain row. The rate
used for each rejection type comes from its own matched sample.

## Replay commands

Set `R310_C_REPLAY_DIR=r11` to validate existing results; by default
the script uses a fresh `scratch/C/r11-replay`. Steps from the root:

```sh
bash ralph/lanes/C/replay_reciprocal_r11.sh prepare
bash ralph/lanes/C/replay_reciprocal_r11.sh worker stage-0
# Run stage-1 through stage-3 too, and check the stage before full-0..3.
bash ralph/lanes/C/replay_reciprocal_r11.sh worker full-0
# Once all four primary streams finish, run the exact repairs and pricing.
bash ralph/lanes/C/replay_reciprocal_r11.sh live
bash ralph/lanes/C/replay_reciprocal_r11.sh pricing
bash ralph/lanes/C/replay_reciprocal_r11.sh verify
```

Each `worker` command consumes one process slot at a time. `audit
full-N` resumes just a worker's missing intervals with bounds scaled
for a large journal. Follow the workspace's core and RAM allocation
when running multiple workers.
