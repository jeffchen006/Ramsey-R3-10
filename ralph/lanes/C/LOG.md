# Lane C — round 2 in progress, 2026-11-21

P4 census scan estimate (before launch): 96 evenly spread core families took
5.34 user seconds, including all-census preprocessing, of 13,613 families and
31,994 markings. Naive linear projection ~757 CPU-s (0.21 CPU-h); 1800 s
wall timeout, 1 core and 16 GiB virtual memory. Sample was 18 retained rows.
Positive C21 control recovered 42/42 oriented paths and deleted-row test failed.
P5 attachment exhaustive estimate (before launch): 96 evenly spread rows in
3.98 user seconds; full 1,156 rows estimated 48 CPU-s (~0.013 CPU-h).
Single foreground process bounded to 240 wall seconds and 16 GiB.
P4 cross propagation estimate (before full scan): 96 evenly spread rows
used 1.15 CPU-s, with 1,344 cross assignments tried; estimate ~29.4 CPU-s
for all 2,454 rows. Foreground cap 150 s, one core/16 GiB.
P5 trace certification estimate: 24 spread rows (3,075 nodes) checked in
1.18 user-s; bottom-up extrapolation gives ~57 CPU-s by rows or ~111 CPU-s
by nodes. Foreground cap 240 s, one core/16 GiB.

**Open:** Case R and R(3) remain open. Complete R(7) nonextension was
independently replayed by A; formal acceptance of the non-SAT certificate
by the critic is pending. No candidate graphs.

Read required report and notes; no round-1 critic directives. Share 4 cores.
New approach: project an edge kernel's outside vertices to multiplicities of
their kernel-neighbourhood masks. A type must hit every independent d-set of
the kernel. Regular degree and codegree constraints, independent-set residue
order bounds, and degree caps in the residues give a mask-count LP. HiGHS
searches only for integer-weight Farkas proofs, checked independently of the
solver with integral arithmetic.

## Results

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| hand | Mask-count constraints are necessary for any regular edge extension | `ralph/lanes/C/proofs/edge_kernel_projection.md` | — |
| enum | Replayed actual masks at all 140 edges of C35 and 660 edges of the ten known 6-regular order-22 graphs, plus C5; small n=6 negative control | `scratch/C/calibrate.txt` | 0.010 |
| cert | 78 of the 238 R(3) kernels have no regular extension of codegree cap 3. Exact integer Farkas recheck of every refutation. 160 feasible projections (not graph completions) remain for lane D. | `scratch/C/R3_part{0,1}.jsonl`, logs, `scratch/C/R3_survivors.g6`, `kernel_projection.py verify` | 0.116 scan+verify |
| enum | Stronger rows (expanded star, shared masks, globally minimum rooted edge) pass C35/22 replays but all eight sampled baseline survivors still have feasible LPs. | `scratch/C/calibrate_strong.txt`, `scratch/C/R3_strong_sample.log` | 0.020 |
| enum | R7 boundary-pair projection passes all seven known K2,2 pair controls on 22 vertices. First R7 seed still allows 261,824 unordered package-pairs; 90 s wall cap reached before all four seeds reported. Not an exclusion. | `pair_packages.py`, `scratch/C/pair_calibration.log`, `scratch/C/pair_r7.log` | <0.025 |
| enum | R7 set-variable SAT model recovers valid regular extensions from all seven order-22 controls. Large pilot bounded to 360 s wall per seed; no reliable extrapolation of solve time. | `pair_set_sat.py`, `scratch/C/set_sat_calibration.log` | <0.001 calibration |
| enum | R7 C-colour packing DFS recovers completions on all seven planted order-22 side-pair controls. On 64 evenly spaced pairs at seed 0: 64 no-extension, 3,641 total nodes (0.01 CPU-s, generation 55.77 CPU-s). | `colour_packing.cpp`, `scratch/C/colour_calibration.log`, `scratch/C/R7_sample{_gen,_packing}.log` | 0.016 |
| estimate | Full R7 scan per seed: about 56 CPU-s pair generation + ~40 CPU-s packing at pilot mean; could be much more if tail dominates. Four independent seeds; allow 1200 s wall per seed under high shared load. | `scratch/C/R7_sample{_gen,_packing}.log` | ~0.11 estimated |
| enum, independently replayed | R(7): all four fixed e85 seeds from Lemma R7 have no extension. 977,008 total pairs, zero SAT or limits, max 198 nodes/pair. Produced 49,569,079-node trace; A verified exact independent package cover and every node. Retain enum until critic accepts non-SAT cert. Full order-22 shape calibration recovered exactly seven known classes: 973 packages, 80 labelled outputs. | `proofs/pair_packing.md`, `TRACE.md`, `scratch/C/R7_full.*.log`, `scratch/C/full_control.log`, `ralph/lanes/A/R7_REPLAY.md`, `scratch/A/rc7/replay-X*.log` | 0.087 enumeration + 0.029 trace + 0.015 A replay |
| hand | Every (3,10,40)-graph is K3,6-free and K4,5-free, without regularity. | `proofs/bicliques.md`, `scratch/C/bicliques_fast.log` | <0.001 |
| hand | In Case R the graph of codegree-six pairs has path components on at most ten vertices or eight-cycles; four consecutive vertices have adjacent endpoints in G and both diagonal codegrees three. Sharp C21 path control. | `proofs/codegree_six_paths.md`, `scratch/C/codegree_paths.log` | <0.001 |
| enum, exact profile replay | In R(6) there is no eight-cycle component. 191 order-22 census graphs → 270 placements → 32 X families; no complementary pair of loads from 95,984 words. Compact obstructions on at most eight of 16 coordinates per X replayed exactly; corrupted proof rejected. The codegree-six graph in R(6) therefore must be a union of short paths if this exclusion is accepted. | `proofs/cycle8_join.md`, `scratch/C/cycle8_profiles.log`, `scratch/C/cycle8_obstructions.json`, `scratch/C/cycle8_{verify,bad_verify}.log` | 0.002 scan + <0.001 check |

## Jobs

| Timeout PID / initial worker PID | Command from `scratch/C` (each via `setsid nohup nice -n 5 timeout 1500 bash`) | Log | Cores | Start CET | Expected end CET |
|---|---|---|---:|---|---|
| — | No running detached jobs | — | 0 | — | — |

Detached R3 scan PIDs 267941 and 267942 completed both scan and recheck.
Set SAT pilot PIDs 594938/594939 elapsed to 360 s without verdict; no survivors
or refutations from those probes. The new DFS is entirely separate.
The four complete packing runs (PIDs 759502/759503/759504/759506, start
16:56:06) all recorded `complete`, with zero `node-limit` and zero `SAT`.
Trace runs (timeout PIDs 897148/897149/897150/897151; 17:01:09 start)
completed with identical text outcomes and expected byte counts. No remaining jobs.

## Next

R3 list given to D; clustering equivalent oriented kernels reduces those
survivors to 110 representatives in D's work. H asked to formalize short
lemmas. Critic should review independent R7 trace and C8 census projection.
Next round: try overlap joins on long codegree-six paths using their 22-vertex
triple residues; handle short P3 components (three possible diagonal values)
and isolated codegree-six pairs separately. Never assume C8 is the only R(6)
case. `RESULTS.md` gives regeneration and evidence details.

Round 2 detached scan: timeout PID 2770701, 1 core, start 17:56:02, expected end by 18:26:02, C-host local time. From `scratch/C`, `python3 -B ../../ralph/lanes/C/path_windows.py ../../gluing/val/r3_7_22.g6 ../../opt/bin/labelg --output p4_full.g6`; `p4_full.log`.

## Rounds 2–3: path window evidence and completed jobs

- P4 cover: 31,994 marks / 13,613 X20 families → 2,454 labelled A26
  rows in 72.47 CPU-s (PID 2770701). A matched in 49.82 CPU-s. The
  MTF criterion leaves 1,356 rows. Explicit branching over 36,039
  D0--D3 patterns with degree/TF/MTF/codegree propagation yields the
  same 1,356 rows; this was not an extension test.
- P5 cover: 177 window families / 47,031 port pairs → 1,156 labelled
  H30 rows, 10.55 CPU-s; A's independent full-set comparison modulo
  reversal in 10.87 CPU-s. Extension: 940 unsupported MTF pairs,
  216 trees (289,649 nodes; max 10,760), 42.34 CPU-s; separate trace
  replay 71.25 CPU-s. C21 controls, removal/corruption tests and all
  regeneration details in PATH_REPLAY.md / PATH_INPUTS.sha256. Critic
  confirmed C-009 at `enum`, not `cert`, in round 002.
- Round-2 P4 control 8 SAT + 5 UNSAT, 8 independent witness checks;
  matched larger pilot 15/15 cap (6.79 user-s). Do not rescale the old
  lazy-cut approach. Round 3 exact eager side test matched all 13
  control keys and reached 14/15 checked proofs on the spread pilot.
- The P4 cert route is now fully exhausted in both e strata, not just
  a filter. See P4_REPLAY.md and P4_INPUTS.sha256, with all 2,222
  retained LRATs and exact replay. C-013 scope: P4 spans only, not R(6).

| Finished Round-3 job | Timeout PIDs, one core each | Actual host period | Command shorthand from `scratch/C` | Logs |
|---|---|---|---|---|
| High P4 | 1236776, 1236779, 1236793, 1236803 | 18:55:52–18:59:55 | `timeout 1200 python3 -B ../../ralph/lanes/C/p4_factor_proofs.py p4_forced_full.g6 ../../opt/bin p4proof-high --min-e 79 --seconds 8 --join --shards 4 --shard S` | `p4proof-high-S.log` |
| Low P4 | 1505265, 1505267, 1505271, 1505275 | 19:00:16–19:05:06 | same driver, `p4proof-low --max-e 78 --seconds 10 --pins --shards 4 --shard S` | `p4proof-low-S.log` |
| Replay P4 | 1859760, 1859814, 1859819, 1859866 | 19:06:06–19:15:06 | `timeout 1200` wrapper, `bash ../../ralph/lanes/C/replay_p4.sh high S` and then `low S` | `p4replay-S.log` |

Each used `setsid nohup nice -n 5` and a 16 GiB virtual limit.
High estimate 650 CPU-s from spread sample; actual 795.49 CPU-s.
Low estimate 800 CPU-s from pinned LRAT pilot; actual 839.28 CPU-s.
Replay estimate ~435 CPU-s high and 400–700 CPU-s low; actual
about 441 and 508 CPU-s, all CNF and proof hashes identical.

P3 diagonal-five/e64 producer: timeout PIDs 2344024, 2344030, 2344035,
2344039 (workers 2344028, 2344037, 2344046, 2344050), four one-core
shards, 19:16:03–19:26:51. Under 16 GiB virtual cap and `setsid nohup
nice -n 5 timeout 1800`, ran `python3 -B ../../ralph/lanes/C/p3_e64_proofs.py
../../gluing/val/r3_7_22.g6 ../../opt/bin p3e64-full --seconds 100
--shards 4 --shard S --skip-row 0 --skip-row 95 --skip-row 139` from
`scratch/C`. Logs `p3e64-full-S.log`. All terminal, 56/56 checked,
1995.85 CPU-s actual versus 2240 CPU-s estimate, no caps. Pilot three
already checked (107.37 CPU-s), with byte-identical pilot replay
(50.97 CPU-s). `p3e64-index.log` independently confirms all 59 keys.

P3 e64 replay: timeout PIDs 3160833, 3160842, 3160849, 3160857,
four slots 19:27:29–19:32:11, hard cap 19:42:29. From `scratch/C`
with 16 GiB cap and `setsid nohup nice -n 5 timeout 900` wrapper:
`python3 -B ../../ralph/lanes/C/p3_e64_proofs.py ../../gluing/val/r3_7_22.g6
../../opt/bin p3e64-full --verify --shards 4 --shard S --skip-row 0
--skip-row 95 --skip-row 139` then diff exact hash columns against
producer logs. `p3e64-replay-S.log`: all `IDENTICAL`, 917.02 CPU-s
checking 56 proofs versus 950 CPU-s estimate; 50.97 CPU-s for the
three pilot replays separately.
# Round 4 handoff

Complete transcripts are in `scratch/C`. Completed job inventories:
`p3e63-probes.tsv`, `p3e63-minpilot.tsv`, `p3e63-full.tsv`,
`p3e63-replay.tsv`, `p3flex-pilot.tsv`, `p3flex-upper.tsv`,
`p3flex-upper-replay.tsv`, `p3flex-midpilot.tsv`, `p3low-pilot.tsv`,
`p3extra-pilot.tsv`, `p2anchor-pilot.tsv`, `p2anchor-full.tsv`.
Active PIDs at handoff are in STATE and `p3e62-{full,replay}.tsv`.
Exact costs and proof/replay scopes are in `ROUND4_REPLAY.md`.

## Round 5 collection and jobs (CET)

- Round 4 e62 producer wrappers 1345478, 1345482, 1345489, 1345498
  and replay wrappers 1752307, 1752313, 1810068, 1946269 were gone
  at 21:10. All thirty seed groups in each phase were terminal;
  1,308 production + 12 pilot = 1,320, all independently replayed
  and rehashed. Exact costs in `ROUND5_REPLAY.md`. Former expected
  21:13–21:21 wall caps did not determine their completion status.
- e64 production/replay wrappers 3387435, 3387438, 3387440 (diag3,
  shards 0/1/2) and 3387442, 3387445, 3387449 (diag4), all started
  21:11:29, one core/16 GB each, hard cap 21:38:09. From scratch/C:
  `setsid nohup nice -n 5 timeout 1600 bash ../../ralph/lanes/C/p3_e64_shard.sh D S`.
  Producer wall cap per SAT call 65s; replay per checker 180s.
  Logs `p3r5-e64-D-S-{wrapper,produce,replay}.log`. Seen terminal
  before 21:20 and exact coverage 59+59, 8 reused pilot proofs.
  Preestimate 11–13 CPU-s/key production (0.34–0.40 CPU-h),
  conservative 0.61 CPU-h; actual 0.454 CPU-h plus 0.196 replay.
- Mixed-arm pilot rows 13, 44, 79, 133: 4/4 passed both diagonals,
  23.49 and 51.80 CPU-s. Preestimate 56+56 new keys ~1,054 CPU-s,
  conservative 1,700, replay ~0.12 CPU-h and 1.5 GB retained proof.
  Round-5 launch metadata `scratch/C/p3r5-mixed-jobs.tsv`. PIDs
  4019348, 4019352, 4019355 (diag3 shards 0/1/2) and 4019360,
  4019367, 4019373 (diag4 shards 0/1/2), all at 21:28:22 CET,
  one core/16 GB each with wall cap 21:55:02 and expected end
  ~21:32 (diag3), ~21:37 (diag4). Command from scratch/C:
  `setsid nohup nice -n 5 timeout 1600 bash ../../ralph/lanes/C/p3_mixed_shard.sh D S`.
  Logs `p3r5-mixed-D-S-{wrapper,produce,replay}.log`; checker and
  SAT caps 150s/75s per key. All terminal and gone by 21:35:22.
  Audit passed all 120 keys without caps, 1,146.19 CPU-s production
  plus pilots and 326.42 CPU-s replay.
- The earlier C22 controls for isolated pair/anchor results,
  e63/upper fixed-flexible regressions, and expensive generic
  flexible low strata are in `ROUND4_REPLAY.md`; don't rerun them.
# Round 6 — complementary full-wing windows

- Four proof shards started 22:27:33 CET (PIDs 1308534, 1308577,
  1308640, 1308734, hard end 22:39:33); four replay shards started
  22:31:12 (PIDs 1401955, 1401989, 1402053, 1402098, hard end
  22:43:12). All ran under `scratch/C`, one core each. Exact commands
  and logs: `scratch/C/p2r6-cross-{jobs,replay-jobs}.tsv`.
- 1,134 terminal CakeLRAT proofs on the H21/H21 `(12,12)` survivor
  cover and independent CNF regeneration plus full proof replay.
  Evidence `ROUND6_REPLAY.{md,sha256}`. The join and necessary
  screens are enum; no claim about all `f*=9` configurations.
- H19 pilot: 39 necessary profiles, 4,749 marked H19 class keys
  from 381 K12 cores. Raw pairing estimate is prohibitive. K13/side12
  unprofiled capped; aggregate independent-capacity scan had no loss.

## Round 7 (November 21–22)
- New exact one-sided neighborhood-choice arc filter; direct/cached controls agree. See `ROUND7_REPLAY.md`.
- Complete profiled K12-to-H19 generation (1,988,646 rooted windows). High-edge census replay and zero survivors across 317,795,664 selected maps give 16–21 edges in the smaller private K12, only for (12,14) under global f*=9, pending critic (hand + enum). 24 of 39 profiles remain open; no jobs.

## Round 8 (November 22)
- Independently rebuilt scout boundaries, replayed the missing-blocker control, and bound exactly 90 row IDs. Zero-compatible capacities excluded 34 of 105 multiset keys including every q=0 branch, but no row beyond those two layouts. Exact binding and proofs: `ROUND8_REPLAY.md`.
- Held-out two-site bitmap index rejected 97.6% of 4,910,040 mapped requests early and matched the direct test, but construction and request filling cut net gain to 1.51×. Not a scalable broad join. No jobs.

## Round 9 (November 22)
- Diagonal-four 8/8 P3: independently audited 105 zero keys, with 34 contradictions and 47/24 live split by at-most-one triple. Unique-zero named layouts give 18 singles, three doubles and budgets two/one. Evidence `proofs/p3_rounded_incidence.md`, `ROUND9_REPLAY.md`.
- Held-out e62 indexed wing join 320.175→115.566 CPU-s and 28,720,249,242→971,463 partial tuples; all 336 placements survive. Tag DP reduced covers 455,546→300,018 but all 84 positions survived, with no speedup. The two 45-s CPU-hard-limit SAT pilots exited 137, neither UNSAT nor TIMEOUT.

## Round 10 (November 22)
- Reciprocal 22/21 cap five: all 395 planted matched controls; 4,882 direct/indexed/independent exact bounded keys. Cap-five 22/22 reproduction has zero mates. 8,192 new right hosts: 70,229 checked maps, no undecided, all exact map IDs reproduced. 48 dense and thin dual-LRAT map proofs; 29.63→7.54 whole-process CPU-s. No census, no closure of either R(5) or Case R. See `ROUND10_REPLAY.md`.

## Rounds 11–12 (November 22)
- Round 11 streamed complete cap-five K3,3 reciprocal 22/21: 1,118,436 right hosts, 11,657,178 maps, 32 local dual LRATs, C-033. C-034 pricing only. `ROUND11_REPLAY.md`.
- Round 12 counted 89,187,336 union-≥14 local B marks at order 22 (19,397,413 cards), 1,307 tight `14/222/2` marks, and proved all 9 tight e65 marks impossible: 324 checked dual LRATs; 1,298 tight local marks remain. Upper reroot retained all 1,307 marks (54,384 live wings). Critic accepts e(F_A)≤64 only for the named all-three-B-codegree-five tight slice. No order20 catalogue or general 22/20 join. `ROUND12_REPLAY.md`, `ralph/critic/round_012.md`.

## Round 13 (November 22)
- Independently matched both 9,959-row atlases and 55,055 frames; replayed the prior triple slice and bound a disjoint 1,554,349-ID cap-five 17/17 pilot. 197,502→327 panel, 97 joint, zero open (enum only). Full scope priced, not launched. `ROUND13_REPLAY.md`.

## Round 14 (November 22)
- Calibrated and took two independent streamed stage/terminal readouts of the cap-five 17/17 ordered alignment roster. Complete prefix `[0,24576)`: 12 shards, 67,417,211 headers, 12,594 panel, 3,464 joint IDs, zero unresolved. All stage bytes, independent header digests and terminal reason vectors agree. Stopped at expensive-tail gate; 90,054,790 headers still unscanned. `ROUND14_REPLAY.md`.

## Round 15 (November 22)
- Calibrated exact Python witness reuse, retained unchanged C++ terminal, and scanned all 30 independent HH representative shards under the new gate. Coverage including the old prefix: 92,341,930 direct, 65,130,071 by shore exchange, zero unresolved. Marked cap-five 17/17 excluded, pending critic (`hand + enum`); no broader closure. 270.204 CPU-s production, 390.415 with charged setup. `ROUND15_REPLAY.md`.

## Round 16 (November 22)
- One-neutral cap-five K4,4 16/17: hand cover and group-key proof. A bound 15,051,526,031 labelled headers. Of 544 pilot IDs, 497 had an empty group and 47 passed individual groups but no joint assignment. Both C++ literal/filtered and independent Python audit; eight literal probe caps not counted as rejections. 153 smaller plants and 1,596 matched keyed terminal assignments. Exact pilot-only frontier 15,051,525,487; this is superseded by round 17's weighted first filter. No production; warm estimates 11,400 core-h literal all-domain/4,348 core-h preflight model (not bounds), Python replay 1.84M core-h estimated. `ROUND16_REPLAY.md`, `ROUND16_FREEZE.sha256`.
