# Lane C — round 11, November 22, 2026

No candidate. R(3,10), Case R and R(5) remain open. Scope this round:
cap-five complete K3,3 with reciprocal window orders 22 and 21 only.
Full census, independent replay and exact proof repairs are complete.
The narrow exclusion is submitted for critic review.

## Results and claims for H / critic

| Label | Scope and result | Evidence | CPU-h |
|---|---|---|---:|
| hand + enum + cert (32 repairs), pending critic | No cap-five reciprocal 22/21 pair. 191 order-22 hosts and all 1,118,436 order-21 hosts in 73 contiguous ID intervals; all 11,657,178 rooted alignments independently match, 11,503,447 explicit witnesses, 153,699 domain replays, 32 exact LRAT repairs, zero unresolved. 1,299,926,766 logical journal bytes. | `ROUND11_REPLAY.{md,sha256}`, `proofs/reciprocal_r11.md`, `scratch/C/r11/{coverage.tsv,coverage.log}`; provenance `scratch/critic/r10/C/provenance.log` | 0.28 stream + 1.77 completed audit + 0.21 capped Python retries |
| cert, exact 32 repairs | All 32 stream-live keys (one interval `[645234,661618)`) have both original dense and row-selector CNFs independently verified by `cake_lpr` and `lrat-check`; no uncovered keys in this repair queue, no graph. | `scratch/C/r11/{live.tsv,live-proofs/receipts.tsv,live-proofs-dense/receipts.tsv,proof-ledger.log}` | 0.0072 |
| cert / estimate, bounded pricing only | 132 matched duals in each dense/thin encoding, 96 in row-selector; 395 smaller positives. Clause-subset and key/hashes checked. 10.37 CPU-h thin or 6.57 selector forecast for the actual 153,699 domain keys (proofs alone); no such production queue. 1,250→985 coloured lower-graph orbits preserves all role IDs; not used for closure. | `proofs/reciprocal_r11.md`, `scratch/C/r11/{proof-ledger.log,proof-support-cal.log,proof-reuse-stage.tsv}` | <0.06 proofs/tests |
| prior hand + enum, independently confirmed | Cap-five 22/22 impossible (R-001 component). Neither equal nor asymmetric joins apply to 21/21, cap six or all R(5). | `ROUND10_REPLAY.md`, `proofs/reciprocal_windows.md`, `ralph/critic/round_010.md` | prior |
| prior frozen C-026/C-027 | R(6) diagonal-four 8/8 P3: 105 zero patterns, 34 contradictions; 47 no triples, 24 at most one triple, none allows quadruple. 90 excluded layout/residue rows, 71 patterns and 330 rows open. No private-wing work this round. | `proofs/p3_rounded_incidence.md`, `ROUND9_REPLAY.{md,sha256}`, `ralph/critic/round_009.md` | prior |
| prior C-025 / C-024 | Global R(6) f*=9 `(12,14)` smaller private K12 has 16≤e≤21; 24 of 39 profiles open. `(12,12)` impossible with 1,134 CakeLRAT replays; at most one shared vertex. | `ROUND{6,7,8}_REPLAY.md`, `ralph/critic/round_{006,007}.md` | prior |
| prior confirmed | R(7) excluded; R(6) no P4. P3 diagonal-five residue e≤61, diagonals three/four e≤63. If f*≥8 P3 arms both 8 and diagonal 3 or 4. Global f*=9 makes J a nonempty matching. Isolated f8/e80 has ≤1 degree-three vertex; anchored X' e≤64. | `ralph/critic/round_{001,003,004,005}.md`, `ROUND{4,5}_REPLAY.md` | prior |

## Jobs

**None active.** All wrappers below finished by 05:18:36. The original
full jobs ran `timeout 3150 bash -c 'bash "$1" stream "$2" && bash "$1" audit "$2"' laneC <root>/ralph/lanes/C/reciprocal_census_worker.sh "$2"`
in `scratch/C/r11` (04:43:58 start, one core each, 05:36:28 wall bound).

| PID | `$2` | Log under `scratch/C/r11` | Cores |
|---:|---|---|---:|
| 858943 | `full-0` — finished, CPU-capped audit | `full-0.job.log` | 0 |
| 858944 | `full-1` — finished, CPU-capped audit | `full-1.job.log` | 0 |
| 858945 | `full-2` — finished | `full-2.job.log` | 0 |
| 858946 | `full-3` — finished | `full-3.job.log` | 0 |

Resharded only missing `full-0/1` audit intervals in four disjoint
jobs launched 05:08:15; wall bound 05:35:15. Command:
`timeout 1620 bash reciprocal_census_worker.sh audit resume-N all-stream-01.tsv`
(script path as above). One core per job; 720 CPU-s per large shard.

| PID | Job | Log under `scratch/C/r11` | Cores |
|---:|---|---|---:|
| 1458118 | `resume-0` — finished | `resume-0.job.log` | 0 |
| 1458119 | `resume-1` — finished | `resume-1.job.log` | 0 |
| 1458120 | `resume-2` — finished | `resume-2.job.log` | 0 |
| 1458121 | `resume-3` — finished | `resume-3.job.log` | 0 |

Stage wrappers 837846/837848/837849/837850 finished; proof-price wrappers
858947/858948 finished. Other proof pricing, repairs and comparators
were bounded foreground runs. `full-0/1` each finished their full
stream, then one Python audit was stopped by signal 24 (CPU cap, not a
wall timeout); both intervals replayed under the resume limits.

## Next

1. Critic/H: check the narrow submission via
   `R310_C_REPLAY_DIR=r11 bash ralph/lanes/C/replay_reciprocal_r11.sh verify`.
   Final ledger passed, binding every interval and repair receipt.
   No need to repeat the full stream unless auditing independently.
2. H/D/critic: if accepted, 22/22 and 22/21 exclusions together give
   opposite B-mask union ≥14 when A is a codegree-five triangle with
   exactly three common neighbours B. If B also has all three codegrees
   five, it must have exactly five common neighbours. See
   `proofs/reciprocal_r11.md`; no closure of 22/20 or all R(5).
3. Freeze diagonal-four 47/24 split; only revisit a genuine both-wings
   same-common-assignment test with measured loss. P2 `(12,13)` needs
   U1 calibration; `(13,13)` needs H20/K13 catalogues. Do not start
   cap six, 21/21, R(7) or a proof-production queue without new approval.
