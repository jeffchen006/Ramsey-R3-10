# Lane E state — round 2

2026-11-21, core share 16, one core at a time except brief overlap of two
bounded foreground checks. All results are for all graphs, not merely
MTF. No candidate graph sent to the flow and no new Ramsey verdict.
Round 1 details (including PIDs and calibrations) are in `LOG.md`.

## Jobs

No detached jobs launched in round 2. All round 1 PIDs collected, none
live. The bounded foreground checks and their estimates/results follow;
all logs are in `scratch/E`, all use `nice -n 5`, `timeout`, a CPU limit,
and the 16 GB virtual-memory limit in `limited.sh`.

| Check (1 core each) | Start host time; CPU / wall cap | Log and outcome |
|---|---|---|
| `crown_sieve` partition-first pilot, PID 2818480 | 17:57; 90 / 180 s | `crown27.sample.log`: CPU-limit kill, 84.53 CPU s, zero completed anchors; not UNSAT |
| `crown_sieve_v3 32-1 < crown27.g6` | 18:00; 60 / 120 s | `crown27.full.log`: completed, 2.78 CPU s; 33-anchor pilot 0.96 CPU s |
| `replay_crown32_t1 < crown27.g6` | 18:02; 90 / 180 s | `crown27.replay.full.log`: completed, 10.56 CPU s; 33-anchor pilot 2.15 CPU s |
| `replay_crown32_t1 all-windows` e87 control | 18:04; 90 / 180 s | `crown27.replay.e87.control.log`: 17/17 match optimized branch |
| `order3_a4_profiles.py` | 18:08; 60 / 120 s | `order3_a4_profiles.v2.log`: completed, 9.20 CPU s; all profile relaxations feasible |
| `crown30_windows.py . --probe11` (complete pair/triple mode) | 18:15; 130 / 210 s | `crown30_probe11.v3.log`: completed, 89.51 CPU s; pair-only precursor 80.33 CPU s |
| `crown30_windows.py . --a4-w12` | 18:16; 40 / 60 s | `crown30_a4_w12.log`: completed, 2.97 CPU s; 1.19 CPU s profile-count pilot |
| `crown28_windows.py . 8 7 6 5 4`, PIDs 3611467/3611477 | 18:20; 50 / 80 s | `crown28.replay.log`: completed; partial survivors at 4–6, no jobs remain |

## Claims and results (for H/critic)

| Claim or result | Label | Evidence | Core-hours (decisive runs) |
|---|---|---|---:|
| `(2,32)` with sizes `5,5,5,6` fully excluded. No-isolate branch: 1,470 distinct valid anchors, 13,279 eligible `W` windows, zero required `6,5,5` partitions. Different independent subset/color replay matches every anchor. Add E-006 for isolates. | enum | `ralph/lanes/E/crown32_t1.md`, `scratch/E/crown27.{manifest,full.log,replay.full.log}`, `scratch/E/cal_crown_v3.log` | 0.0037 |
| `(2,30,a=5)` now requires `|W|≤10`; `(2,30,a=4)` now requires `|W|≤11`. Single extremal deletions checked in both directions; then optimistic pair and triple packing excludes the next size. | enum | `ralph/lanes/E/crown30_windows.md`, `scratch/E/crown30_windows.log`, `scratch/E/crown30_probe11.v3.log`, `scratch/E/crown30_a4_w12.log` | 0.0262 |
| `(2,28,a=4)` now requires `|W|≤6`; complete 3/9 core censuses give no pair at 8 or triple at 7. Higher-multiplicity necessary test leaves 3/15, 6/9, 6/6 cores at sizes 6,5,4. | enum (upper bound only) | `ralph/lanes/E/crown28_windows.md`, `scratch/E/crown28.{w78.log,w456.probe.log,replay.log}` | 0.0049 |
| Order three, root with four fixed neighbors: exactly 12 moved neighbors, never 15; eight pinned templates cover the residue. A singleton in any position of an ordered block decomposition yields the forbidden sixth independent vertex. | hand | `ralph/lanes/E/order3_a4.md`; 5-orbit `2,1,2` witness in `scratch/E/order3_a4_profiles.v2.log` | <0.003 |
| All 16 `(f=7/10,a=4,pin)` cases survive the local order-three profile relaxation. This is not a SAT model or new closure; six prior UNKNOWN open-branch runs were not relaunched. | open | `ralph/lanes/E/order3_a4_profiles.py`, `scratch/E/order3_a4_profiles.v2.log` | 0.0026 |
| Preserve `(5,5)` four checked proof packages and exact `δ≥5` dependency. Round 2 verified all retained proof/CNF/witness/map hashes, not a mathematical rerun. | cert (round 1) | `ralph/lanes/E/slim5.md`, `scratch/E/cert_sha256.txt`, `scratch/E/slim5_hash_recheck.log` | <0.001 this round |

`W` means the fixed vertices without moved neighbors. The `(2,32)`
crown depends on the universal Review 4 `δ≥5` certificate (plus its
published C35 hypothesis); the `(2,28)/(2,30)` crown bounds do not.
`(2,32,a=5)` is separately excluded as E-002, and `(2,34)` as E-001.

## Next steps

- Ask H/critic to replay new enum claims and keep them scoped. The board
  gives F exact search exclusions; no blanket f or a exclusions from the
  new partial window bounds.
- For `(2,28,a=4,|W|=6)`, add joint triangle information between
  attachments on the three surviving W core classes. The current complete
  optimistic graph permits cross-part triangles by design. Use forced
  pair edges (delete an allowed edge and test the independence bound) or
  exact small residual SAT; complete smaller test before scaling.
- For the `(2,32)` t=2,3,4 crown, attempt the complementary pair cover:
  two selected attachment masks together must hit every independent
  7-set in the anchored residual, or the remaining `W+Ai` fails. Do not
  scale raw partition-first enumeration; it made no progress at 85 CPU s.
- For order three use cross-orbit footprint interactions, not raw time.
  Two outside orbits sharing an attached fixed vertex of `A` cannot
  join (triangles); combine their masks with antineighborhood independence
  bounds. `(5,0)`, open order-three `a=2/3`, and involutions with fewer
  fixed points remain distinct and unresolved.
