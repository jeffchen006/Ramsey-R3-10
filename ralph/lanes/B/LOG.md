# Lane B reproducibility and round notes

## Round 4: checked slices, two degree-distribution reductions, and gluer pilots

### Exact completed slice and queued disjoint tails

The up86 job exited before 19:42 CET with exact terminal counts (4,751,963
distinct e88 graphs, 4,641 checked chunks, zero MTF completions). Source is
the 1,800 canonically distinct HoG order-30/e86 inputs. Every triangle-free
edge addition preserves the independence bound. Intermediate e87 count and
edge check: 133,434. Audits: `logs/up86_audit_r4.log`, `logs/edgeup2_full86.log`
(all scratch paths here under `scratch/B`); canonical e88 strict ordering
checked with `LC_ALL=C sort -cu`. The initial e86 validity checks and source
count passed earlier; the fully regenerated prefix e86 exact equality and
147,335 e87 census checks are **still pending**. Independent graph validation
and independent SAT gluing agreed on all 32 freshly sampled e88 inputs (seed
410674, `logs/up86_r4_{valid_sample,sat_sample}.log`). The SAT recheck is a
sample, not a per-input certificate. Full up86 production ~1.45 CPU-h.

`profile_census 30` is calibrated against the exact e63 sixty-graph census
and independent exclusion filter (24 survivors). Scanned the entire up86
e88 slice in 6.23 CPU-s; profile masks 0 and 4 both empty, meaning every
graph has a d5/e<=58 or d6/e<=51 root. Thus this slice is contained in the
*intended* prefix scope, not evidence about the unscanned anchor complement.
`logs/profile_census_r4.log` lists all eight exact mask counts. Scope does
not extend to the other 13,901 e87 parents or to edge-critical e88 duals.

`checkpoint_prefix_lower.sh` collected the lower levels from a snapshot
of atomically finished prefix chunks: all 1,800 e86 canonically match HoG,
and the 147,334 B-generated e87 graphs plus one from up86 give the exact
147,335 benchmark count. 67.26 CPU-s (`logs/prefix_checkpoint_r4.log`).
Both files are fixed by `logs/prefix_checkpoint_r4.sha256`. A direct
branch-and-bound pass using `audit_duals.c` validated all e87 inputs in
3.69 CPU-s (60 e63 controls pass and wrong independence threshold fails).
The independent Python checker also passed 64/64 dispersed e87 inputs.
The original
sleeping watcher 392466 was retired without running any solver; replacement
2576750 starts from this exact checkpoint once e43 releases its slot, rather
than waiting until the entire prefix job ends.

The tail checks `133434 + 13901 = 147335` by canonical ordered merge, partitions
the tail descendants into overlapping and novel e88 lists, and binds the
per-chunk e88 scan source by SHA-256. The bound chunk control covers 7 exact
inputs over 3 chunks, and rejects a reordered source (same input count).
The disjoint edge-addition control `replay_tail_accounting.sh` partitions
all 15 e21 order-16 parents into 11 prior and 4 tail; 130 old plus 29 novel
e22 graphs match the exact complement of the 42 edge-critical graphs in
the full 201-graph e22 census (`logs/tail_accounting_control.log`).
With prior measured up86 addition/MTF rates, estimate ~1.06 M raw tail e88
children and conservatively ~0.33 CPU-h plus sorting, 25–55 min wall at one
worker. The e43 job is separate; its exact 1,521 input order-22 census check
passed, but its terminal gluing/MTF counts are still pending. Neither scan
substitutes for the proof of complete e88 input coverage.

`CYCLE162.md` gives hand reductions for the two e=162 U88 distributions under
the inherited t8/t9 floors (also checked t7 floor for the second). The small
labelled replay confirms the four- and six-vertex shapes. These do not exclude
either case. Complete U88 would remove 13 conditional cases on G's
checked round-3 `round3_cases.csv` baseline. G's round-4 eight-cut proposal
overlaps precisely the e168 `(7,1,1,31)` row (`round4_cases.csv`), so the
conditional count falls to 12 if the new cuts are accepted. The old 20 and
intermediate 17 are superseded.
The two-degree incidence LP `root_projection.py` passes substitution of
the actual C35 rooted histogram into each exact row. For the e88 complement,
it counts both global and internal degrees at each vertex and incorporates the
degree-specific neighbor-sum caps and MTF private-cell cap. The floating
relaxation leaves 29 of 31 degree-nine root profiles feasible, including at
least one in every one of the 13 U88 distributions; the other two are the
already excluded nonzero degree-seven attachments at e162, n7=2. No new cut.

### Accuracy and performance probes

On the exact 430 rooted e63 positive controls, static degree lookahead,
exact attachment-size group plans, summed convex attachment cost, and the
bitset/cost variants all reproduced the independently filtered labelled
multisets. On four dispersed eight-parent blocks these probes preserved the
exact target outputs. The rows probe also uses relaxed, nonempty e88 controls.
These are isolated compile-time experiments in lane B's copy of `gluecheap.c`;
the running prefix and e43 binaries were not replaced.

| Variant | e52 CPU s/input | e44 CPU s/input | log under `scratch/B/logs` |
|---|---:|---:|---|
| Static degree lookahead depth 4 vs reference | 0.377 vs 0.398 | not timed | `lookahead52.log` |
| Exact size plans, ascending / rare / descending | 0.482 / 3.040 / 9.190 | not timed | `plans_r4.log` |
| Convex weighted incidence floor depth 2 vs reference | 0.408 vs 0.380 | 3.521 vs 3.366 | `convex_r4.log` |

Static lookahead uses
`Z(x) >= sum_{y adjacent in base} lower_deg(y) + s*(deg(x)-base_deg(x)) + bonus(x)`,
where `s` is the guaranteed lower degree of a new neighbor and `bonus` is
the selected neighbors' actual excess. The convex prune uses
`sum_{u in new neighbors} Z(u) = D^2 + sum_x c_x*(base_deg(x)+c_x)`;
it lower-bounds the latter by the separable Lagrangian with one integer price,
and obtains an upper sum from exact remaining size budgets. Both were safe on
the controls, but the depth-4 lookahead rejects just twelve late e52 nodes
and the convex variant rejects only one e52 attempt. Neither merits scale-up.

For equal pair-compatibility signatures (same missed maximum independent base
sets), `signature_probe.py` calibrates on C4 and counts 208,624 critical
size/signature keys among 208,741 eligible nonempty signatures on e52 (e44:
199,694 of 199,806). This would not compress the search materially. The local
neighbor-degree incidence LP (`anchor_profiles.py`, exact e63 census control)
does not remove either existing anchor branch at the relaxation level or
justify the tested stronger one-side restrictions. No exact exclusion from LP.

Skipping the greedy coloring bound (`-DCOLMIN=99`) was the only material
speedup. The 32-parent e52 sweep took 0.304 vs 0.374 CPU-s/parent;
the 128-parent untuned e52 holdout took 0.298 vs 0.379 including input/output
(support-only addition: 0.307). `bench_holdout.sh` also checks all 191
canonical order-22 control graphs, with exact equality. The e44 sample
took 1.852 vs 3.628 CPU-s/parent with no coloring and bit-plane attachment
counts (`-DBITPLANE_ATTACHMENTS`); e52 did not benefit from bit planes.
Sort/shortg on those pilots finished in <0.1 s per sampled block; their
small output volume does not bound full-scale canonicalization overhead.

Optimistically extrapolating generation alone gives 856 CPU-h for 10,326,716
e52 parents plus 37 CPU-h for 72,353 e44 parents, or 49.6 h at 18 fully busy
cores. This exceeds the remaining flow window even with free final sorting,
the MTF scan, and no current workers. Do not scale. The required generation
speedup of 10x was not met. Evidence: `logs/{rows_r4,coloring52_r4,coloring44_r4,holdout_r4}.log`.

The bench executables were built with `cc -O3 -march=native` from the lane
copy of `gluecheap.c`, and `-DCOUNT_DEPTH` for lookahead, size plans and convex
cost (`-DSTATIC_PROFILE_LOOKAHEAD`, `-DEXACT_SIZE_PLAN`, `-DCONVEX_STAR_BUDGET`).
For bitset support and the cursor, see `-DCHECK_SIZE_SUPPORT` and
`-DFAST_BOOLEAN_ROWS`; the coloring sweep uses `-DCOLMIN=N` and for two
variants adds `-DBITPLANE_ATTACHMENTS` or `-DEXACT_LAST_SIZE`.

## Round 3: anchors and star-lift slices

`ANCHOR88.md` is a hand proof that an e88 dual not covered by the prefix and
the d7,e43 branch has at least four threshold roots (d6/e52 or d7/e44) with
every neighbor of degree >=5. `glueanchor` is `src/gluecheap.c` with `-S 5`
and optional `-P` for pairwise overlap propagation; build with
`cc -O3 -march=native .../gluecheap.c -o build/glueanchor` from `scratch/B`.
`src/bench_anchor.sh 52 44` reuses fixed dispersed blocks and checks exact
labelled outputs against independent filtering; the e63 control contains 430
labelled outputs. Preserve the joint cover: neither restricted branch by
itself covers the remainder. The e43 running wrapper uses the older binary
and must finish before using its absence of completions in the deduction.

Measured exact paired results (four dispersed blocks of eight inputs at each
edge level): e52 anchored 0.373 CPU s/input (range 0.319-0.468), versus 0.468
with the original outside-prefix filter; e44 anchored 3.450 CPU s/input (range
2.461-4.155), versus 4.085. The overlap prefilter did not improve aggregate
throughput (0.374 and 3.557). Baseline plus independent postfilter and both
variants gave identical labelled outputs in all blocks. The 64 tests gave
zero outside-prefix anchored outputs, so there is no sound full-catalogue
output volume estimate from the pilot. Even **before** sort/I/O/final scan,
the gluing-alone estimate is about 1,071 + 69 CPU-h (63 h at all 18 cores);
do not launch either full branch now. On e52 this is only a 1.26x speedup
over the prior outside-prefix code, not the 10x target.

For star lifts, let U=H−v, and suppose the given H has alpha <= a. Replacing the
star of v by S preserves triangle-freeness iff S is independent in U, and
preserves the alpha bound iff S hits each independent a-set in U. Select an
unhit a-set and partition by the first allowed vertex of this set used by S;
after the obligatory hits are made, adding independent extras gives all exact
target-size sets once. The `-c` option emits only inclusion-minimal hitting
sets: every vertex in the new neighborhood has a private witness independent
a-set meeting S only there. Global edge-criticality implies this local test,
but not conversely, hence the subsequent `irreducible` check. Varying every
root and using target size old+1 enumerates the relevant slice; reversibility
covers exactly those graphs of the next edge level with a down-star to one of
the supplied parents. It does not establish coverage by itself.

Small calibration (`logs/starlift_control.log`): direct fixed-size independent
subset enumerator matched exact labelled multisets both ways, 378 lifts of
30 e62 parents and 336 downward moves from 60 e63 graphs; the lifts recover 58
of the known 60 canonical e63 graphs. Independent brute force on the retained
e88 edge-critical example finds no one-star reduction either (6.94 CPU s,
`logs/starlift_critical88_ref.log`). This example is from the d5 prefix, so it
does not refute a cover formed by the prefix plus the lifts; no proof that
such a union is complete is known.

**Star slice estimate, before launch.** On 128 dispersed e87 parents from the
two-edge slice, unfiltered star-lift emitted 22,081 raw / 12,293 canonical,
of which 37 were outside up86. With `-c`, 42 raw/unique and 34 outside up86,
with exactly the same 21 globally critical new graphs. Star generation took
0.21 CPU s and canonicalization <0.01 CPU s for `-c`; `labelg` plus sort
matches `shortg` exactly on the sample. Scale ×1042: ~219 CPU s generation,
~22k critical outputs before global deduplication, ~30 CPU s MTF scan at
~1 ms/input, and <60 CPU s checking, sorting and I/O. Expected ~5–12 min
wall on one worker, hard cap 45 min, <100 MB incremental scratch. This adds
a partial critical slice, not a substitute for e52/e44. It can run as the
one spare worker while 16 prefix workers and either the up86 scan or e43
use the other 17; label and sort are sequential. See `logs/starlift_pilot.log`.

**Observed:** exact 133,434 parents, 37,640 raw locally critical outputs,
32,484 canonical, 21,932 outside up86, 14,454 globally critical. Star search
217.83+0.20 CPU s; MTF 14.27+0.92 CPU s, zero outputs, exact chunk audit;
24/24 independent SAT UNSAT (no proof files). Independent graph6 profile
filtering found **0/14,454 outside prefix** at thresholds 58/51/42. Thus this
is a partial enumeration/recheck of a prefix slice, not progress on the
outside-prefix branch coverage itself. Do not spend more cores on this star
route without showing it reaches that complement.

Largest-first `-R`: complement each attachment size by `DMAX-1` and reflect
the edge window accordingly; this permits the same monotone cost search to
choose largest actual attachments first. `src/bench_order.sh` matches all
e63 canonical multisets exactly, but the first 8-input e52 block TIMEOUT
at 120 wall s (112.75 CPU s versus 3.74 CPU s for the ascending baseline).
Do not scale; no output equivalence claim for the capped block.

Use `src/audit_e88_scans.sh up86|e43` only on terminal output. Both audits
refuse the currently unfinished logs. `src/audit_chunks.py` checked the
98,408-input MTF pilot exactly, and rejected a forged expected input count
off by one. The staged `src/edgeup_tail87.sh` also requires the completed
prefix calibration (both lower-level counts and exact e86 equality) before
computing the remaining 13,901 e87 parents. Based on 76 additions per parent,
expect roughly 1.06M raw e88 children before canonicalization and slice
subtraction; at the up86 scan rate, conservatively ~0.33 CPU-h plus sorting,
~25-55 min wall on one worker. Not yet launched.

## Round 2: two-edge slice launch estimate (written before launch)

From every known e86 graph, add one nonedge with no common neighbour, canonicalize,
and repeat to e88. This is exactly the slice of e88 graphs with a two-edge deletion
chain to e86: triangle-freeness and the independence upper bound survive each legal
addition; reversing the deletion chain proves coverage of the slice. It is not the
full e88 class. On the order-22 control the single e60 graph produces exactly the
six canonical e61 graphs; the separate irreducibility checker gives the empty
complement (`scratch/B/logs/edgeup2_pilot.log`).

Pilot on 32 dispersed e86 inputs: 2,592 raw / 2,590 unique e87, 196,999 raw /
98,408 unique e88. Canonicalization of e88 cost 1.29 CPU s / 5.53 s wall.
The exact MTF pilot completed all 98,408 inputs with zero outputs in 104.48 CPU s;
median 1.055 ms/input over 97 chunks, range 0.898–1.338 ms/input. Scaling 32 to
1,800 forecasts up to ~11.1M raw and up to ~5.54M unique e88 before intersample
deduplication, a ~1.6 CPU-h scan at the pilot mean, plus ~0.03 CPU-h canonicalizing.
Recent pilot throughput ~1,000–1,100 MTF inputs/s wall gives a ~1.5–2.5h estimate
including sorting/I/O under contention. Hard cap 5h, 1 solver core (shortg+sort
can temporarily be two busy processes), 16 GB address-space limit, estimated
<4 GB incremental scratch. This is within Lane B's 18-core allocation alongside
the 16-worker prefix and does not authorize the full e88 census.

Observed: 133,434 canonical e87 graphs, then 10,142,430 raw and 4,751,963
canonical e88 graphs, with edge addition taking 9.89 CPU s / 146.87 wall s and
canonicalization 69.28 CPU s / 202.37 wall s at the second level. Continue the
MTF scan before making a slice-level exclusion claim. Independent SAT agreed on
24 dispersed pilot e88 graphs (`logs/edgeup2_pilot_sat.log`, all solver UNSAT,
no checked SAT proof). Once `n30.py` checks the complete e87 census and the
two-edge scan finishes, `src/edgeup_tail87.sh` checks set inclusion, computes the
remaining 13,901 e87 parents, and scans only their new e88 outputs. This would
cover every e88 with *at least one* Ramsey-preserving deletion, but no edge-critical e88.

The slice is demonstrably incomplete: 3,037 of 5,994 distinct e88 lines sampled
from d5 prefix chunks are outside `up86` (stratified by chunks, not a class-wide
fraction). One of those is provably edge-critical: `critical88.json` contains an
explicit independent 9-set for each single-edge deletion. `src/critical_witness.py
check` uses the workspace graph checker and verifies all 88 deletion witnesses;
a corrupted witness is rejected (`scratch/B/logs/critical88.log`). The separate
Python checker gets the same seven critical graphs as the C gluer/checker on the
97 order-22 graphs through e63. The e88 graph is a dual only, not an order-40 witness.

The exact critical-edge swap rule tests possible additions only inside the
intersection of all independent K-sets created by the deleted edge: a single
addition kills every new K-set iff both endpoints lie in that intersection.
`critical_swaps.py` matched direct delete/add testing at all 12 order-22
controls (seven nontrivial labelled neighbors in total). A bounded walk from
the critical e88 seed expanded 256 labelled graphs, reached 957, and did not
reach an outside-prefix graph; 701 were still on the frontier at the cap
(`logs/critical_swaps_88.log`, 3.19 CPU s). No connectivity or coverage claim.

## Round 2: faster missing-branch generation

`gluetriple`: prefilter future choices after selecting two attachments by hitting
every independent (K-2)-set disjoint from both. The order-22 canonical set of
191 is unchanged at each tested setting, but 24 dispersed e52 inputs took 45.82
CPU s versus 11.04 s with the early filter disabled. Decreasing of node count
(9.08M to 8.34M) is insufficient. Do not scale.

`g84`: in `-A 58 -B 51 -C 42` mode (K=8, e=88), keep only graphs with no
degree-5/6/7 vertex whose dual is admitted by the existing prefix. For attachment
set S, its vertex's eventual Z is exactly `D + sum_{x in S}(deg_H(x)+1) +
sum_{T != S} |S ∩ T|`, so use mutable slack and prune when any bound fails.
All Z caps use `88 - max(published minimum, prefix input ceiling + 1)` for
the respective degrees; do not read the prefix-input ceiling as a nonexistence
statement. Check actual Z at each vertex before output. Minimum degree 3 at e88
follows from the GR e85 minimum at n27: a degree-2 vertex would have Z>=4.
For n22 e63, the unfiltered profile mode reproduces all 60 graphs, and the
degree-5 dual threshold 33 reproduces the exact independent 24-graph filter.
Toggling the MTF scope is unrelated: these are (3,9;30) duals, only the final
40-vertex scan is MTF-only.

`g84 -I` keeps only graphs for which every edge deletion introduces an
independent (K+1)-set. On a root edge, this demands a (K-1)-set in H disjoint
from the attachment. Performs the general witness search at output. It recovers
the exact independently filtered seven critical order-22 graphs <=63; the
96-input e52 run yields zero critical among 162 raw e88 outputs and takes
49.53 CPU s. No standalone speed gain. Depth counters show ~42.6M early
failed compatibility-set intersections at depths 1 and 2, next to ~4.2M
alpha rejections at depth 2 (`logs/g84_652_irred.log`).

`gluecheap`: skip per-candidate degree scans already enforced by the parent
eligibility mask and visit only known low-degree H vertices for deficit checks;
test the two-child intersection cheaply, use restrict-qualified contiguous
operations on complete words, and check depth-2 alpha after ruling out an
empty child. At larger depths, checks remain early as before. Pair rows ensure
the two-attachment checks. The full canonical order-22 control matches byte
for byte. The 36-parent n23,e51 sample gives exactly 37,550 raw outputs versus
`glue5` (34.24 vs the earlier 44.09 CPU s). On the 96-parent e52 sample the
162 raw e88 outputs match exactly (44.37 vs 49.03 CPU s for `gluetrans`, and
63.25 for `glue5`; edge cap is 88 in all cases, 88 is the only output there).
`src/paired_speed.sh` runs four seeded eight-graph sub-blocks per level, checks
raw equality, and verifies every filtered output against `profile_filter.py`.

| Inner branch | `gluetrans` CPU seconds/input | `gluecheap` CPU seconds/input | `gluecheap` outside-prefix CPU seconds/input |
|---|---:|---:|---:|
| n23 e52 | 0.555 (0.456–0.676) | 0.491 (0.419–0.578) | 0.468 (0.383–0.541) |
| n22 e44 | 4.539 (3.181–5.244) | 3.927 (2.775–4.685) | 4.087 (2.935–4.795) |
| n22 e43 | 6.008 (5.051–6.514) | 5.103 (4.593–5.754) | 5.158 (4.599–5.653) |

Each row is 32 distinct parents in four seeded blocks; ranges are block means.
Outside-prefix outputs were empty on all three sets; raw plain output counts
were 4, 3,356, 66 respectively. For the exact 1,521-parent e43-only branch,
5.158 CPU s/parent predicts 2.18 CPU-h; the observed mean of 5.203 wall s/parent
predicts 2.20h on one worker, and scaling the slowest block gives 2.40 CPU-h.
Reserve 0.3–0.6h for sort, MTF scan, and contention; sampled outside-prefix
canonicalization is empty, and live prefix throughput includes canonicalization
at roughly 7 large chunks/min. Queue e43 behind up86 so e43 can use one worker
and still fit the 18 process slots even when canonicalization uses shortg+sort.
Expected end about 22:00–22:40 CET; cap 6h from queue. The complete missing e52
and e44 levels together project ~1,423 CPU-h before overhead (~79h even at full
18-core occupancy), so do not launch either at full scale in this run.

## Sources and seed lineage

- Read Goedgebeur–Radziszowski, arXiv:1210.5826v4, §3 and Tables 3, 12–14;
  read Angeltveit, arXiv:2401.00392v2, §§3.1, 4.1–4.6. Local PDF/text copies are in `scratch/B/ref/`.
- Read-only HoG data fetched from the `data/ramsey/minramsey/Ramseygraphs_*.g6` paths of the minimal Ramsey metadirectory.
  The Exoo 39-vertex input is the **complement** of the 0/1 adjacency matrix `cs.indstate.edu/ge/RAMSEY/r3.10.39`.
- `src/bootstrap.sh` checks references, recompiles the historical gluers and `onepoint`, and rebuilds the missing order-12–15 R(3,6) classes from order 11 by one-point extension. The regenerated sizes are 116792, 275086, 263520, 64732, matching the historical file lengths. In the order-21 gluing calibration, the possible minimum degree is 3–6. Generate min-degree 3 from the 7 order-17 seeds.
- `src/seed.py small` reconstructs upstream R(3,7) windows; `upper52` reconstructs the (3,8) inputs using exactly checked GR increment inequalities. Each chunk must finish with matching input count before canonical output is published. Graph files and solver logs remain under `scratch/B`.
- `src/n30.py` is the stage-4 port of `t9_88.sh`. In `88 --prefix` mode, it checks (5:3,6:3,7:1) for cap 87 and then glues those inputs with cap 88. In full 88 mode use (5:3,6:4,7:3); the difference is the omitted n23,e52 level feeding d6 and n22,e43–44 feeding d7. Only full mode can support an exhaustive e88 claim, with all counts and scans completed.

## Correctness argument for MTF-only extension

Write the final graph as H plus the neighbours `u_i` of a new root `v`. In a maximal triangle-free (MTF) graph, every nonedge has a common neighbour. For any `x` in H outside `S_i = N(u_i) ∩ H`, the common neighbour of `x,u_i` must be in H: `x` is not adjacent to the root, and the `u_j` are independent. Thus each `S_i` is an inclusion-maximal independent set of H, not merely a subset of one. It cannot contain a vertex already of degree `DMAX` in H. Enumerating maximal independent sets in the allowed induced subgraph, then checking maximality in all of H, retains every possible `S_i`. This does not assume H itself is MTF.

Each vertex in H must get enough attachment neighbours to reach `DMIN` and at least one to dominate its nonedge with `v`. Every nonedge `xy` in H with no common neighbour in H must occur together in some `S_i`. For a chosen unsatisfied requirement, each completion therefore contains an eligible candidate from its support. Branch over that support, removing prior alternatives of this branch from later siblings (a completion goes to the first candidate it uses). Before removing the chosen candidate for later siblings, intersect the child domain with its compatibility row; this preserves multiplicity if the chosen set is self-compatible. Saturated vertex degrees remove any more sets using those vertices. If all requirements are met and fewer than D sets are assigned, branch over all eligible sets. Zero support or insufficient degrees is a valid prune.

Pair compatibility requires hitting every independent (K-1)-set left unhit by the chosen set. Each bitset row is an intersection over those hit columns, computed on demand. For a pair of attachments, the triangle-free residual on `H \ (S_i ∪ S_j)` plus the other D-2 attachments has independence at most K-2. Its order gives `|S_i ∪ S_j| >= m + D - R(3,K-1) - 1`. Higher-subset compatibility is checked by exact alpha lookups for each newly formed subset, so no independent (K+1)-set avoiding `v` survives; those including `v` are excluded by alpha(H) <= K-1. Leaf checks enforce degrees, edge bounds, and all missing internal MTF pairs. Thus `-X` is exhaustive for MTF outputs, not for all triangle-free outputs.

For the order-40 run `-m 6 -M 9 -E 161` uses report Lemmas L1, L5, M1. If full e88 is closed, it is sufficient for the reported 15 **MTF** distributions, but is not a proof of the broader statement for all (possibly non-MTF) graphs. Results are `enum`; independent SAT sample agreement never certifies UNSAT.

## Benchmark record

All times below are CPU seconds on this machine, using the same selected inputs within each pair. Exact canonical output checks on order 22 and raw/canonical comparisons are in `scratch/B/work`. `real_23_*.g6` comes from chunk outputs before final global deduplication; it is not a uniform sample over isomorphism classes.

| Sample | Baseline | Variant | Result |
|---|---:|---:|---|
| 36 × (24,e58), d5, EMAX=88 | glue5 17.22 s | gluepair 7.07 s; gluetrans 9.05 s | same 2,416 raw, identical canonical files |
| 36 × (23,e51), d6 | glue5 44.09 s | gluepair 45.61 s; gluelast 37.17 s | same 37,550 raw; weak improvement |
| 36 × (23,e52), d6 | glue5 23.63 s | gluepair 25.78 s; gluetrans 18.01 s; gluelast 18.59 s | same 2 raw; use gluetrans |
| 96 × (23,e52), d6, uniform over finished class | glue5 63.25 s | gluetrans 49.03 s | same 162 raw outputs; 1.29x |
| 30 synthetic (23,e51), d6 | glue5 32.73 s | gluecut 34.58 s; glueres 33.78 s; gluepair 24.37 s | same 67 raw; not representative |
| 30 synthetic (23,e52), d6 | glue5 18.61 s | gluecut 20.74 s; glueres 19.25 s; gluepair 22.08 s | all zero |
| 12 minimum (24,e56), d5 | glue5 9.61 s | gluefast 20.27 s | same 18,243 raw; no acceleration |
| 24 HoG e86, order-40 MTF glue | gluefast -X 6.00 s | mtfcover eager 1.09 s; mtfcover lazy 0.04 s | all zero; lazy faster than 100x on this sample |
| All 1,800 HoG e86 inputs | historical glue2 879 s (non-MTF scope) | mtfcover lazy 2.53 s (MTF scope) | zero; independent SAT C35 positive, 8/8 e86 negative |
| 40 × n30,e88 from d5 pilot | — | mtfcover 0.04 s | zero; independent SAT 12/12 e88 negative |

Fit estimates: prefix upper bound roughly (364,384 × ~1 s + 132,817 × ~0.2–0.4 s) / 16, about 7–10 hours with overhead. Full e52 stage alone at 0.511 s/input costs ~1,465 CPU-hours, or ~73 hours at 20 busy cores. A complete scan of 5.9M estimated e88 outputs at the e86/pilot e88 rates would cost roughly 2 CPU-hours, but resample the prefix before trusting this extrapolation. Long-mode budget needs <=0.27 CPU s/e52 input (or substantial validated sharing/reallocation). No justified t9<=89 or t8 launch.

## Archived job transitions (rounds 1–14)

- Round 14 PID 2981850 (`e108_r14.py tranche`, 520s wall) finished
  Nov 22 ~09:04:47 CET, status 0; `scratch/B/logs/e108_r14.log`.
- Prefix PID 1180084 (`timeout 18h prefix_pipeline.sh 16`) started Nov 21
  17:10:35, ended Nov 22 ~01:06 CET, status 0. Generation finished ~00:57
  (3,886 chunks); the MTF scan used 5,736 ordered digest-bound chunks.
- PID 3921182 finished at 22:30 CET, all 48 chunks bound, zero e88 outputs.
  PID 2576750 (tail87, 22:30:40–22:52 CET) finished with zero MTF outputs,
  all 945 chunks bound and the independent terminal audit passed.
- Round 6 PID 1105184 (four-way swap, 22:19–22:25) passed all 2,102,271
  parents, adding 479 keys. PID 1276908 added 128 and stopped at a fixed
  point. The unoptimized 512-parent 2→3 pilot `shortg` timed out; the
  calibrated critical-only version completed on the same parents.
- PID 3047886 (`edgeup_pipeline.sh 86 … up86`) finished by 19:42 CET.
  PID 392466 was retired at 20:40 before compute. PID 1367119
  (`starlift_stage.sh`, run ~18:59–19:03) completed with count audit and
  SAT sample replay. `bench_anchor` passed; `bench_order` passed e63 then
  timed out on e52.
- Bootstrap 136395 and seed jobs 418169/453949 exited. The n21 union
  originally omitted degree-three inputs, then generated and restored that
  branch. PID 418169 failed on `shortg`'s in-place default; PID 453949
  passed with explicit stdout. PID 540708 passed all GR T13 counts.

## Other experiments

- Round 15 detached history (CET): PID 865356 (driver 865361),
  `timeout 6m e108_r15.py campaign work/e108_r15 1 9 8 1200`, eight
  slots, `scratch/B/logs/e108_r15_wave1.log`, 10:32:38–10:33:11, exit 0.
  PID 905617 (driver 905620), `timeout 42m e108_r15.py campaign
  work/e108_r15 9 257 8 13900`, eight slots,
  `scratch/B/logs/e108_r15_main.log`, 10:33:28–~10:50:28, exit 0.
  Round 16 found all four absent; its audits used no detached jobs.

- `gluecut`: a witness independent set for one failed candidate must be hit by all future siblings. Correct pruning but witness construction and bitset application offset the node savings in both samples.
- `gluewin -J`: uses the degree-dependent upper GR z-cap on neighbour-degree sums. Around 2% fewer nodes in the sampled case, but no CPU win. `glueres` tightens singleton/pair/higher compatibility by a necessary minimum edge condition on the residual H plus unused attachments. Costs slightly more in the dominant sample. `gluelast` changes condition order and batches the final hitting constraint; does not improve on `gluetrans` at e52.
- `edgeup`: triangle-free one-edge extension of order-16 e21 gives 159/201 of the e22 graphs; at (24,e57) it gives 118069/129347 at e58. `irreducible` independently identifies 11278 non-deletable graphs at e58, exactly the complement count. The sampled n23,e52 had 1/36 irreducible; this is too small a sample to extrapolate. One-edge extension alone is not complete.
- `gluegroup` tries all legal one-edge additions to a common H in batches of 64 (not production). When a residual has alpha exactly the forbidden size, adding edge xy kills all such sets iff both endpoints belong to their intersection; membership is equivalent to lowering alpha by deleting that vertex. Shared search tracks possible additions as a bitmask. This passed the tiny exact independent comparison `work/group_small.{new,old}` (1035 canonical outputs), but on three n23,e51 parents (201 edge additions) it took 175.08 CPU s versus 86.10 s for separate gluing, both empty. Do not scale it.
- `gluetail -P`: if G is not a prefix output, at e88 its degree-5,6,7 vertices have neighbour-degree sums at most 29,36,45, respectively (otherwise one of the prefix roots applies). This version propagates those tighter z-caps and leaf-checks all vertices; it produced no evident throughput gain on the 36-graph e52 pilot. Experimental only, awaiting full calibration against an independent filter of nonempty outputs.
