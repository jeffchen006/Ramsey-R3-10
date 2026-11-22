# Lane A state

Round 8, November 22, 2026. Share 3. No live or stopped A jobs; no
order-40 candidate or whole-distribution exclusion. Both terminal G
subcases now have independent exact source, receipt, pin and CNF hash
binding. Read `ROUND8_REPLAY.md` and `scratch/A/strip8/round8.freeze.sha256`.
Round 1–7 history is in `LOG.md`; prior A freezes are unchanged.

## Jobs

All paths are relative to `scratch/A/strip8`; times are host local.

| timeout PID / worker PID | Command | Evidence | Cores | Start–end |
|---|---|---|---:|---|
| 1949042 / 1949074 | `replay_lower_marks.sh 0` | `lower.scan.0.{keys,time}` | 1 | 00:44:14–00:47:55 complete |
| 1949043 / 1949068 | `replay_lower_marks.sh 1` | `lower.scan.1.{keys,time}` | 1 | 00:44:14–00:47:46 complete |
| 2254371 / 2254383 | `run_strip_audit.sh lower --fast-hash --shard 0 2` | `lower.hash.0.{log,time}` | 1 | 00:51:59–01:15 complete |
| 2254373 / 2254394 | `run_strip_audit.sh lower --fast-hash --shard 1 2` | `lower.hash.1.{log,time}` | 1 | 00:51:59–01:15 complete |
| 2403272 / 2403285 | `run_strip_audit.sh mixed-prefix --fast-hash --verify` | `mixed.prefix.{log,stop}` | 1 | 00:54:59–00:58 manually stopped after 295 accepted dual LRATs; slot reused |
| 2567868 / 2567878 | `run_strip_deltas.sh` | `mixed.prefix.hash.{log,time}`, `lower.delta.hash.{log,time}` | 1 sequential | 00:59:14–01:20:54 complete |
| 3179513 / 3179529 | `run_strip_audit.sh mixed --require-cover --fast-hash --exclude mixed.prefix.log --exclude mixed.prefix.hash.log` | `mixed.delta.hash.{log,time}` | 1 | 01:15:32–01:18:43 complete |

All foreground controls and sample replays finished. Neither of G's
two proof campaigns is left live; they are G's jobs, not A's.

## Results / claims

| Label | Scope and result | Evidence | A CPU-h |
|---|---|---|---:|
| hand + enum | Exact both-path/leaf c1/δ2 marked cover at the two e168 low-n8 pins: 191 valid core classes, 18,333,381 byte-identical labelled extensions, 20,181 independently matched marks, 17,194 distinct augmented-colour orbits. | `ROUND8_REPLAY.md`, `scratch/A/strip8/{lower.glue.log,lower.source.log,lower.scan.A.sorted}` | 0.129 |
| cert + enum cover, pending critic | Both path/leaf, centre codegree 1, **δ(T)=2 only**, at `(2,8,2,28)` and `(2,7,4,27)`. Producer dual checked all 17,194 keys. 17,204 receipts have exactly ten declared same-CNF pilot repeats, deduped. A matched all 17,194 independent pin maps and freshly built CNF digests; 36 dispersed traces independently replayed with both checkers. No caps in terminal union. | `scratch/A/strip8/{lower.terminal.tsv,lower.union.log,lower.sample.log,lower.retry-sample.log,round8.freeze.sha256}` | 0.938 full hashes, 0.010 pilots |
| cert + enum cover, pending critic | Mixed path/leaf and matching/incident or path/middle at `(2,7,4,27)` only, **some noncross degree-eight pivot has codegree 4**. Rebuilt 5,179 ordered roles with both side assignments; 5,179 producer dual-checked proofs, zero caps. All independent pin maps and CNF digests match. A replayed 295 prefix traces with both checkers plus dispersed samples. | `scratch/A/strip8/{mixed.source.log,mixed.terminal.tsv,mixed.union.log,mixed.prefix.log,round8.freeze.sha256}` | 0.131 full hash-only portions, plus prefix dual and controls |
| hand + enum, not a closure | Boundary compatibility rule preserves all measured C5/C13/C35 projections and all satisfying tuples in the exhaustive three-domain controls; two negative mutations reject. Dispersed c1/δ2 pilot 24/24 marks survive. Do not scale unchanged. | `strip_boundary_arcs.py`, `scratch/A/strip8/arcs.pilot.log` | 0.015 |
| hand + enum, conditional source only | Exact order-27 marked projection calibrated against direct addback on full order-7/8 controls (7 positives, 4 negatives). 29,113 order-26 orbits with δ=4/5/6; misses all 1,767 δ3 lower controls. Covers only mark-preserving-extendible windows, not the whole higher-minimum-degree case. | `project_marked_windows.py`, `scratch/A/strip8/{project26.log,project26.hits}` | 0.0033 |

## Next

- Do not repeat completed proof batches, CNF hashes, or previous c3/c2
  proof production; the round8 freeze is terminal. H/critic can record
  only the two scoped subcases, not subtract a distribution.
- Higher minimum degrees at c1/c2 and smaller mixed codegrees remain
  open. A new argument must cover the nonextendible windows separately;
  the projection pilot is not a substitute and the arc filter did not
  earn more cores. Review G's next bounded structural source first.
- If genuinely new e120/e121/e122 rows arrive, bind only the deltas and
  recheck lower alpha after deleting marked edges (`inspect-upper`).
  Keep e169-pinned and unpinned scopes distinct. Do not reopen the old
  R(7) routes without a new directive or quantitatively different split.
