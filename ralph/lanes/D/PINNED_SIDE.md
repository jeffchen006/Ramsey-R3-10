# One-sided support pins (round 3)

## Shared local witness (`hand`)

For a fixed center, use one vertex for each support occurrence (including
the fixed opposite-kernel occurrences), with an occurrence bit for each
threshold of a unary count. Label equal supports arbitrarily. Sound
optional edge bits imply the presence of both endpoints; intersecting
supports forbid the edge. The common graph must be triangle-free. Its
incident edges and common-neighbor counts (including counts toward a
coordinate outside a support) are lower bounds on the full graph's, so
degree and codegree upper bounds remain valid when other edges are omitted.

`--shared 2` represents singleton-to-singleton edges only. An existing
two- or three-element support together with all its singleton occurrences
requires an edge among those singletons: otherwise they and the support
form an independent set that pads to size `d+1` with the unused coordinates.
`--shared 3` instead represents disjoint-support edges with union at most
three. For a window `T` of at most three coordinates, a group of `|T|+1`
occurrences with union exactly `T` needs an edge by the same padding. All
possible edges inside such a group are represented. Its cardinality and
triangle constraints use the **same** edge whenever windows overlap.
This only strengthens the projection; a graph of the represented edges
is not itself a full extension.

**Replay (`enum`).** `scratch/D/factor_cal16_shared/check.log`: exact
per-kernel labelled C16 sets unchanged for both widths across all 13
kernels (five unrooted classes). `scratch/D/shared_sample.tsv`: matching
against 800 retained local profiles, 501 pass the baseline incorporating
the old unique-triple rule; 501 pass shared singletons, 500 pass width
three. Rejected profile is kernel 151, side 1, line 34. These outputs
are not a uniform sample. No scale-up of the shared joined model.

## Pinned one-side completion (`hand` specification)

Pin an occurrence multiset for one side of a fixed oriented root edge
kernel. Relabel the outside vertices in mask order; equal-mask labels
may be assigned arbitrarily. Then all edges incident to the selected
root or its neighborhood are fixed, including the other root as a
coordinate (no outside vertex can hit that coordinate). The other
kernel side has fixed masks consisting of the other-root coordinate and
its F-neighbors. Among the exterior occurrences, candidate edges are
exactly the disjoint-support pairs. In particular the opposite kernel
side stays independent because its supports all contain that coordinate.

`pinned_side.py` supplies triangle and exact degree rows and all-pair
codegree cap rows. In full mode diameter two is necessary because a
nonedge with disjoint neighborhoods would let one endpoint pad the
other endpoint's entire neighborhood. If `x` has singleton support
`{i}` and `y != x` has a support containing `i`, then the codegree of
`x,y` is at least two: `x,u,y` are all in `N(i)`, `c(x,u)=1`, and the
singleton-codegree pairs in `N(i)` form a matching. The lazy independent
clauses are full `(d+1)`-set edge clauses, with pinned constants folded.
With `--min-edge`, for each edge incident to either root the cycle count
must be at least `e(F)`. At the selected root that count is fixed by the
masks. At the other root `v`, incident edge `vb` for `b` in its open
kernel side counts (i) paths through `b-a` for `a` in the selected root's
open side, contributing `deg_F(a)` each, and (ii) paths through `b-x`
for an outside `x`, contributing a product for each other `b'` adjacent
to `x`. This matches the root-adjacent minimum restriction, not a proof
that every edge away from the roots has that bound.

Pinned mode with no min-edge restriction, diameter, private rows or lazy
independence still tests a necessary condition. A model in this mode is
only a feasible relaxation. For fixed labels of an oriented kernel,
the value of one side's multiset is an exact split under relabelling X.
`--profile-lex` acts only on one side; a globally smallest count vector
under the kernel's color-preserving automorphism group survives every
added lex inequality. Generator and transposition inequalities alone
need not pick a unique orbit representative. Neither method claims a
partition of unrooted R(3) graphs across different root kernels.

## Measurements (`enum`, no whole-kernel exclusion)

- C16: 241 enumerated side multisets, exact per-kernel canonical outputs
  match the baseline on all 13 kernels, including all five known outputs
  (`scratch/D/pinned_cal16/check.log`). With profile lex, 100 projections
  and the same complete per-kernel canonical results (`scratch/D/lex_cal16/check.log`).
- R(3): `scratch/D/pinned_r3/manifest.tsv` pins the first six usable
  profiles per side for each of 149, 151, 88, 227 from existing local
  outputs, skipping duplicate triples and the width-three rejection.
  All 48 exhausted at zero independent cuts, 23.73 CPU-s total,
  max 0.92 CPU-s incl. start-up; 8 CPU-s cap per child. The six in each
  bucket are distinct up to rooted kernel automorphism (`scratch/D/lex_r3/orbits.log`).
- Ablation on the first profile of each bucket (`pinned_r3/ablation/`):
  all eight finish UNSAT with only the disjoint-edge graph, exact degrees,
  triangles and the max-codegree rows. In `ablation2/`, all eight feasible
  with degree plus only coordinate caps, or only degree plus triangles.
  Combining those coordinate caps and triangles gives eight caps at
  3 CPU-s. Full codegree cap without exterior triangles gives one feasible
  and seven caps. A cap is not an UNSAT or SAT. Individual/pair disjoint
  neighbor-pool size bounds reject none of the 48.
- One emitted **bare** fixed-profile CNF (149/side 0/line 1) passed
  `drat-trim` and CakeLPR (`scratch/D/pinned_r3/proof/k149-0-1.lrat-check`,
  three proof hash pins beside it). This checks CNF UNSAT, not the
  section 7 encoding/coverage links; still `enum`, not `cert`.
- `profile_core.py`: same bare formula built without substituting support
  pins, plus assumptions giving exact masks. All 241 C16 controls agree
  with the substituted bare model (44 feasible, 197 infeasible).
  Cores can be reused whenever a bipartite matching injects each
  constrained outer slot into an actual outer occurrence consistent
  with its required/forbidden coordinate bits. Unconstrained slots can
  be filled arbitrarily, so this is sound under outer relabelling. On
  kernel 149/side 0, 3 of requested 4 cores finish before 20 CPU-s; each
  constrains 21 or 22 of 22 slots and matches only its source among 100
  tested profiles. Do not scale this no-transfer variant.
- On the kernel 149 side-0 lex throughput pilot, base/lex reach 160
  outputs in 7.22/11.04 CPU-s, representing 159/160 distinct profile
  orbits. Do not infer a useful throughput gain or total orbit count.
  Passing the 48-profile completion smoke did not measure marginal size.

## Replay from `scratch/D`

With `ulimit -v 16777216` and `ulimit -c 0`:

```sh
nice -n 5 timeout -k 2 24 prlimit --cpu=8:9 ../../opt/venv/bin/python -B \
  ../../ralph/lanes/D/pinned_side.py 9 catalogues/R3.g6 149 0 \
  marginal_smoke/k149-0-local.profiles pinned_r3/replay.g6 --line 1 --min-edge --mode first
base=pinned_r3/proof/k149-0-1
sha256sum -c "$base.sha256"
nice -n 5 timeout -k 2 30 ../../opt/bin/cake_lpr "$base.cnf" "$base.lrat"
```

Next useful test: search for a lower-dimensional, reproducible necessary
condition between side count profiles and fully pinned SAT, or bound the
projected orbit count for a specific kernel before a sweep. The cheap
conditional refutations by themselves do not reduce the 110 root-orbit
cover or justify multiplying the observed pin time by an unknown count.
