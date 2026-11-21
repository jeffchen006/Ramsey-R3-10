# Round 6: e43 and two partial censuses

All commands below are relative to `scratch/B`, with a 16 GiB virtual
memory limit and `nice -n 5`. No order-40 completion was found in these
scopes. The accepted MTF degree-seven floor remains 108 (B-013).

## Outside-prefix d7/e43 branch (enum)

`logs/tail7_e43.log` terminates at zero raw and canonical order-30 e88
outputs, from 1,521 complete `(3,8;22,43)` seeds, with 48 all-successful
generation chunks. No final order-40 MTF input exists in this branch.
Generation cost 9,471.51 solver CPU-s (2.63 CPU-h).

`timeout 4m bash ../../ralph/lanes/B/src/replay_e43_r6.sh` freshly picks
the published e43 level (GR Table 13), binds it byte-for-byte to the
chunk input union, verifies triangle-freeness, order, edge count and
alpha, and checks all 1,521 are nonisomorphic with Traces. Evidence is
`logs/e43_r6_full_binding.log` and the ordered chunk manifests under
`work/d7_e43_outside_prefix/`. This only excludes H30/e88 graphs with a
degree-seven root at e43 **and no prefix root**. Prefix coverage uses
`(d5≤58,d6≤51,d7≤42)` and is still in progress. No implication about
d6/e52 or d7/e44 is asserted.
`logs/r6_increment_replay.log` independently verifies that the full
increment plan reaches precisely those extra levels, while leaving them
out admits 309 degree histograms in the deficiency relaxation.

## Deletion-reducible e88 partition (enum; terminal zero)

The exact GR Table 14 e87 level, from the independently validated and
hash-checked checkpoint, partitions as 133,434 old and 13,901 new e87
keys. All e88 classes admitting one Ramsey-preserving edge deletion
are covered by the one-edge additions from all these e87 parents.
The new children partition as 11,524 overlaps and 967,613 novel keys;
the up86 part contains 4,751,963 e88 keys. The total is 5,719,576
distinct deletion-reducible e88 keys. Both MTF scans terminated with zero
completions. In the tail this covers all 945 bound chunks (1,088.64
solver CPU-s; 1,102.33 total CPU-s including the worker harness).
No exclusion of deletion-critical e88 or of all t9≤88 follows.

`timeout 4m bash ../../ralph/lanes/B/src/replay_tail87_r6.sh` replays the
incidence using a Python bit-patch generator independent of `edgeup.c`,
calibrated on the order-16 e20→e21 control. It checks exact canonical
equality, exact disjoint difference, and exact intersection (`logs/up87_r6_independent_replay.log`).
Add `terminal` to demand actual zero completion and the full ordered chunk
binding. `logs/up87_r6_sat64.log` is a 64/64 dispersed independent SAT
agreement, no proof certificates. It is not a substitute for the scan.
`logs/up87_r6_terminal_audit.log` records the end-to-end independent
incidence replay, both scope bindings and zero completions.

## Known e108 order-32 residues (enum / open)

GR Table 14 and §6 give exactly 2,104,151 valid nonisomorphic classes.
`logs/e108_r6_partial_audit.log` verifies 2,102,885 distinct legal classes
with the separate validity checker and Traces: 2,102,271 reducible, and
614 critical. Round 5 already had 7 critical keys. The full 2,102,271-parent
critical edge-swap scan added 479 unique critical keys (817.00 CPU-s including
canonicalization). Following newly discovered keys added 68, 40 and 20;
the next pass added zero. There remain **1,266** missing critical keys.
Local connectivity is not assumed (`logs/e108_r6_{pass1,follow}.log`).

Subsequent pilots with exact critical vertex rewires, two-edge edits,
excursions to higher edge counts, and direct d7/e58 critical gluing added
no new classes; their scopes and times are in `STATE.md`. They are not
exhaustive beyond the specified inputs and moves. On a 24-seed d7/e58
control the baseline recovered all 12 planted known classes, with 286
canonical outputs already known (97.83 CPU-s). Exact size planning hit
its 180 s wall cap on the paired inputs, so no full comparison or
speedup follows (`logs/e108_r6_sizeplans.log`). No full floor-109 campaign
launched.

## Compact pinned proof pilot (cert, supplied critical inputs only)

For the 614 critical keys, checked pair/singleton demand cliques reject
569, and 45 necessary pinned CNF/LRATs reject the rest. This is only a
certificate for those supplied graph6 classes at degree-seven MTF roots.
Use the same graph-to-CNF bridge as `FLOOR7_108.md` (incompatible demands
force distinct rows; seven demands may be assigned to the seven named
rows after relabeling). `unit_lrat.c` emits a single RUP empty clause with
the ordered unit propagation reasons; independent `lrat-check` verifies
production, and `cake_lpr` verifies replay after canonical CNF regeneration.
CaDiCaL is used when unit propagation does not conflict. Forty-three of the
45 critical cases are unit-refutable. See `logs/e108_r6_critical_proof.log`
and `work/e108_r6_critical_proof/{clique.cliq.tsv,clique.missing.tsv,pins.tsv,production.log,replay.log,proofs/}`.
The `production.log` and `replay.log` indices agree on every input index,
rebuilt CNF digest, and proof digest. No t8/t9 floor or distribution is used.
To rerun the full scoped certificate use
`timeout 3m bash ../../ralph/lanes/B/src/replay_e108_critical_r6.sh`;
the second fresh replay with both proof checkers is recorded in
`logs/e108_r6_critical_dual_replay.log`.

A separate uniform reducible pilot checked 3,923 cliques and 173 dual
LRATs on 4,096 inputs. Compact production and replay took 14.81 CPU-s for
173, versus 23.34 CPU-s for the earlier two-checker production plus two-checker
replay schedule; the compact schedule still uses both independent checkers,
one at each step. It retained just 475,256 B, versus 9,204,271 B with CNFs
and logs. With approximately 89,000 LRATs extrapolated from the pilot, budget
~2.3 CPU-h including clique generation/replay and <0.5 GB in proof payload
(allow ~1 GB allocated with small files). This is an estimate, not a cap.
