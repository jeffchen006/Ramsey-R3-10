# Lane F — round 22 complete

**No order-40 candidate. No running, stopped or detached jobs.** The entire one-exceptional-site ID8 construction is excluded for a target (pending critic review), conditional on the previously checked marked cover. This is **not** a result about unrestricted four-vertex deletions, involutions or degree distributions. Round 21 archived in `LOG.md`. Evidence and replay instructions: `ROUND22.md`, `ROUND22_FREEZE.sha256`, `round22_replay.sh`.

| Label (pending critic review) | Result and evidence | Metered core-h |
|---|---|---:|
| hand + local cert + enum | All 668 frozen marked rows terminal: 412 have no bare 36-card, 251 admit no arbitrary 37th vertex, final five admit no **nonadjacent** pair of new vertices. 1,305 labels / 31 reversal-fixed. `scratch/F/r22/{terminal.tsv,terminal37.tsv,finalindex.stdout,receipts.sha256}`; clean 668/668 bare/pole replays in `clean/clean.log`. 1,137 exterior marginal rows unchanged; no separate exterior or distribution debit. | 0.4443 total |
| hand + local cert + enum | Five remaining masks 3024,3032,6049,6064,14241: 111 normalized signings, 450 candidate pole masks, all 2,147 unordered nonadjacent pairs rejected by physical tens. Signing covers and mask lists dual-LRAT; independently rebound pairs in `scratch/F/r22/signcount/{cov_*,fbind_*}.stdout`. Positive C13 plant with both exterior vertices forcing missing verticals. | included |
| enum | 256 gated 36-card models, five gated 37 models; each **specific** 37 graph has zero exact extensions in `scratch/F/r22/concrete/`. No order-40 score; old degree-valid best 24 independent tens at 178,179 edges (`round22_nearness.tsv`). | included |
| estimate/open | Deleting the exceptional pair leaves a wider 34+6 question. Bare sign inventory hit its 256-model cap in 376 steps, 1.00 CPU-s (`scratch/F/r22/wider/corepilot.{stdout,time}`). No denominator, unrestricted six-pole search or transferred cutoff. | included |

### Jobs — all exited

Historical job directories below are relative to `scratch/F/r22/`. Command wrappers, forecasts, per-stage timings and full argv in `forecast.txt`, `{.,ext,signcount,concrete,wider}/jobs.tsv` where applicable. Foreground stages were nice/timeout/prlimit/VM-limited. Active queue at handoff: none.

| Real PID / timeout PID | Command / log | Cores | Start | End Zurich, 2026-11-22 |
|---|---|---:|---|---|
| 1605016 / 1605012 | `exception_queue.py 0`, `worker0.log` | 1 | 19:25 | 19:26:32 |
| 1605017 / 1605014 | `exception_queue.py 1`, `worker1.log` | 1 | 19:25 | 19:26:33 |
| 1847491 / 1847483 | `exception_extqueue.py 0`, `ext/extworker0.log` | 1 | 19:31:29 | 19:34:49 |
| 1847490 / 1847485 | `exception_extqueue.py 1`, `ext/extworker1.log` | 1 | 19:31:29 | 19:34:42 |
| 2000913 / 2000909 | `exception_plainqueue.py 0`, `plainworker0.log` | 1 | 19:36:04 | 19:43:42 |
| 2000914 / 2000911 | `exception_plainqueue.py 1`, `plainworker1.log` | 1 | 19:36:04 | 19:42:54 |
| 2362140 / 2362131 | `exception_finish.py all .. 0 1`, `clean/clean.log` | 1 | 19:44:39 | 19:56:04 |
| 2596816 / 2596814 | `exception_fixed.py TAG INDEX` loop, `signcount/fixedworker.log` | 1 | 19:50:47 | 19:51:46 |

1599.60 summed stage CPU-s (0.4443 core-h; excludes lightweight outer dispatch loops), including 356.19 CPU-s for the separate clean replay; ~0.63 wall hours from assignment to handoff. Peak measured RSS 264,272 KiB; new logical scratch ~306 MB. No independent five-minute busy-count series was collected. Both allocated cores were used for all three main queues. Two hash-index attempts wall-timed out on filesystem reads, never used for credit; decoupled index and full 4,427-file content hash completed. One initial all-sign two-pole run reached conflict cap and remains merely an attempted route; the successful finite signing/pair split is separate.

### Next round

Do **not** rerun these 668 rows or the exterior marginal, the cyclic ID8 family, or the nonadjacent-pair queue. H/critic: independently replay and ledger the family-scoped closure, not 668 distributions and not 2,147 graphs. If authorized, price **34 ordinary vertices + six genuinely arbitrary exterior vertices**, without assuming an exceptional pair survives. Triangle-freeness among six gives an independent triple. First calibrate on a smaller positive where exterior poles force a deleted vertical, then price the contact-mask triple test on a finite disjoint signing branch. The 256 cap is not a full signing census; do not allocate a wider batch on it alone.
