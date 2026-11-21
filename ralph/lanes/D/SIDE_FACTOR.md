# R(3) side profiles and local forbidden patterns

## Scope and reduction (`hand`)

Let `G` be triangle-free and `d`-regular with `alpha(G) <= d`, and bound its
nonedge codegrees by 3. Root at an edge `uv`. Write `A=N(u)-{v}`,
`B=N(v)-{u}`, `F=G[A union B]`, and let `X` be the vertices outside these
sets and the roots. `F` is the prescribed labelled bipartite edge kernel.
The 110 surviving root-swap representatives cover the candidate rooted
kernels; they do not partition unrooted graphs.

For fixed `u`, record every vertex `y` outside `N[u]` by the nonempty support
`S(y)=N(y) intersect N(u)`. A zero support would allow `N(u) union {y}` as
an independent set. The support has size at most 3 by the codegree cap.
Each `b in B` has a *fixed* support `{v} union N_F(b)`; each `x in X`
uses only `A`. Distinct vertex occurrences with the same support must
be retained. At most one occurrence can have a particular singleton
support, since two with that support are nonadjacent and can be padded
by `N(u)` without the singleton coordinate. Each pair of coordinates
lies in at most two supports, because the pair already shares `u`.
These are the count capacity bounds. The other side is symmetric.

If we restrict attention to kernels at globally minimum edge-four-cycle
count `m=|E(F)|`, we also impose the necessary root-adjacent edge and
singleton lower bounds from `ENCODING.md`. This restriction must not be
read as absolute nonextension of an arbitrary rooted kernel.

### Local exact test

Fix `T subset N(u)`, `|T|=t`. Let `Y` be any collection of occurrences
whose supports are contained in `T`. The induced graph on `T union Y`
must have independence number at most `t`: pad any independent set
there by `N(u)-T`. On `{u} union T union Y` the edges at `u` and `T` are
fixed by the supports; the only optional edges are between disjoint
supports in `Y`. Any completion must be triangle-free and have local
codegrees at most three (common neighbors outside the set can only add
to these codegrees). The test allows all disjoint-support edges, even if
the full kernel forbids some. Thus failure of the local test excludes
that multiset in every full extension, while local success does not
establish any global extension.

For each fixed independent `(t+1)`-set in `T union Y`, a completion must
include one of its available optional edges. The DFS in
`side_obstructions.py` chooses an unhit set, branches on its possible
edges, and discards an edge if it creates a triangle or raises local
codegree above three. These failures persist with additional edges;
every completion takes one branch. If the demands are all hit, the
current edges are a witness. The separate subset loop `brute` checks
the negative answers by trying every optional-edge subset on each
coordinate-permutation representative. Feasibility is hereditary under
deleting occurrences. The generator starts with the empty pattern and
extends all feasible patterns by a single support, checking capacities
and requiring each immediate predecessor feasible. It therefore finds
every minimal forbidden multiset relative to the capacity bounds on
the tested coordinates. The no-cutoff catalogue is `enum`, not an
end-to-end certificate for any R(3) kernel.

### Hand example: a forced triangle (`hand`)

If singleton occurrences `x_i,x_j` and an occurrence `y_ij` with support
`{i,j}` all exist, `x_i` and `x_j` must be adjacent. Both meet the support
of `y_ij` so neither can be adjacent to it, and all three can be padded
by the other `d-2` coordinates if `x_i x_j` is missing. Consequently
the six supports `{i},{j},{k},{i,j},{i,k},{j,k}` are impossible: each
pair of the singleton vertices would have to be adjacent. This is not
just a pairwise-intersection bound on supports.

## Joined encoding and calibration

`factor_sat.py` uses a unary count prefix (one or two bits per support)
for each side. It imposes the side's count, degree deficits, pair
capacity, and optionally minimum-edge bounds. A cheap additional rule
bounds any pairwise-intersecting family of supports by the size of its
union (padding by the unused coordinates as above). With `--obstructions`
the stronger exact local library gives clauses that forbid selecting all
required count thresholds simultaneously, after subtracting the fixed
`B` or `A` occurrences. Eliminating a clause subsumed by another changes
no restriction. `--no-k33` also makes triple counts Boolean whenever
the order/degree bound in `SATURATED_BICLIQUE.md` applies. At join time
selections at each labelled outside slot
are disjoint alternatives, encoded by an at-least-one clause and the
distinct incident bit assignments. Guarded cardinalities link them to
the count prefixes in both directions. The numeric combined masks are
ordered by relabelling `X`; ties are allowed. Joined degree, triangle,
and codegree rows then enforce the graph constraints, and an independent
set oracle adds exact set clauses until the solver returns a valid graph
or no assignment. The extra forced-edge clauses are the two-singleton
case from the hand example. This construction has no checked VeriPB /
CakePB link for the joined encoding, and no claim of a refutation.

Calibration: the M=3 C16 catalogue with 13 rooted kernels recovers the
same five canonical 5-regular (3,6,16) classes as root-only SMS. Exact
canonical equality holds both with and without the local library or
the biclique cut, and the three factored variants have identical labelled
outputs on each kernel. The five graphs pass `tools/check_graph.py`;
they are not just satisfying projected profiles. SMS and the factored
runs are logged under `scratch/D/{calibration16,factor_cal16,factor_cal16_local,factor_cal16_k33}/`.

### Reproduction

From `scratch/D` under the lane RAM and time caps:

```sh
nice -n 5 timeout 110 prlimit --cpu=75:76 python3 -B ../../ralph/lanes/D/side_obstructions.py side_obstructions_orbit.json
nice -n 5 timeout 110 prlimit --cpu=75:76 python3 -B ../../ralph/lanes/D/side_obstructions.py side_obstructions_orbit.json --verify
nice -n 5 timeout 15 prlimit --cpu=8:9 ../../opt/venv/bin/python -B ../../ralph/lanes/D/factor_sat.py 16 5 calibration16/kernels.g6 0 factor_cal16_local/example.g6 --min-edge --shadow-edges --obstructions side_obstructions_orbit.json
```

The first command reports 2/18/266 labelled minimal patterns on 2/3/4
coordinates, in 1/7/22 permutation orbits respectively. Smaller-support
obstructions recur at larger coordinate widths; the figures are per
width, not disjoint. The JSON digest is
`fd24ec97248a5d8da022b4b7bb8dcd6b84026da4e4ce4dfaafc86d96825352c2`.
