# Outside-star and joint edge transport for a maximum-square kernel

## Outer-star projection (`hand`)

Use `K,X`, and `M(x)=N_K(x)` as in `MAX_ROOT.md`. Write `ell=2`
in a tight maximum-square class and `ell=1` otherwise. Outside masks
are distinct: two equal masks of size at least four violate the cap
three. A smaller equal mask has a singleton on at least one side;
with that side's root `u` and the singleton `a`, the two outside
vertices share `a` and extend `N(u)-a` to an independent `d+1`.

For a fixed outer mask `M`, every neighbor of its vertex in `X` has
a mask `N` disjoint from `M`. Select exactly `d-|M|` such masks. For
each boundary coordinate `a` not in `M`, the number of chosen masks
containing `a` lies between `ell-|N_K(a) intersect M|` and
`3-|N_K(a) intersect M|`. For each pair of boundary coordinates the
chosen masks that hit both use only the remaining codegree allowance.
A fixed three coordinates can belong to at most one chosen mask:
two such neighbors would have those three common neighbors plus the
outer center. All these rows neglect unmodeled vertices, hence are
necessary. The optional independent-seed row follows by adjoining the
members of `M` that do not see the seed to the neighbors that avoid
it; it did not improve the matched sample and is not used in sweeps.

Mask groups are orbits of validated, color-preserving kernel
permutations fixing the roots. The orbit trade is sound without
proving that the generators are complete: any verified subgroup gives
an exact partition, and yields identical local feasibility within
each orbit. Remove an orbit only if its representative has no local
solution. At each iteration its input universe excludes only earlier
orbits. Every real completion therefore survives every pass by
induction. This shows validity of the model, not that a solver's
UNSAT is a graph exclusion without checking its particular artifact.

## Joint LP (`hand`)

For every allowed mask take its presence `p_M`, and for disjoint
distinct masks `M,N` an undirected `e_MN` indicating whether the
outside vertices of those masks are adjacent. By distinct masks, a
graph gives binary values, with `e_MN <= p_M,p_N`. For each M the
exact sum of these edges is `(d-|M|)p_M`; each outer-star per-coordinate
and optional pair/triple inequality holds multiplied by `p_M`.
For a fixed edge of K, the term `|E_X(Y,Z)|` in `MAX_ROOT.md` is
now a linear sum of the same `e_MN` terms. Its upper bound follows
from global maximality. In the tight class it is constrained to its
exact value after subtracting the two other square contributions.

With `--star-caps` and a tight class, take `a in M`. The actual edge
`xa` has exactly `m-(d-1)` codegree-three pairs between `a` and the
other members of `N(x)`, since all codes are 2 or 3. For a neighbor
`b in M-a`, `x` and two common K neighbors force codegree three.
For an outside neighbor `y`, `x` and two members of
`N_K(a) intersect M(y)` force it. Their sum cannot exceed that quota.

To shrink the LP, average the actual binary values over the generated
subgroup. The averaged values are constant on mask and unordered
edge orbits. Rows remain valid under the averaging: each image is
again a completion of the same rooted kernel, and every row is
linear. For each row replace the coefficient on an orbit by the sum
of the coefficients at its members. A filtered universe must be a
union of these orbits; `--keep` is explicitly conditional on the
input filter. A `--bounded-dual` replay adds valid unit upper bounds
on every variable. Given a floating dual, round nonnegative weights
to integers and repair any negative column coefficient using its
unit upper bound. This succeeds only when the checked integer
combination still has negative RHS. Floating arithmetic cannot
certify a claim. See `transport_root.py --verify`.

## Scope and controls

- `scratch/D/max_root_sat16/check.log`: both full extension variants
  exhaust all 16 keys and match all 13 exact labeled C16 outputs
  derived independently from the known five graph classes.
- `scratch/D/outer_star_fixpoint_cal16.log`: fixed-point deletion
  preserves all 13 outputs; the pinned control replays all 78
  outside neighborhoods.
- `scratch/D/transport_cal16.log`, `transport_caps_cal16.log`:
  replay all 13 exact rational averages, with/without star-cap rows.
- `scratch/D/outer_star_direct20.log`, `outer_star_direct22.log`:
  Farkas witnesses reduce to first-round deletions only; 24/31 local
  DIMACS LRAT refutations pass `cake_lpr` plus exact Farkas checking.
  Dropped columns outside the initial mask catalogue are justified by
  the tight codegree floor. These are `enum` pending the Section 7
  input bridge, not unconditional deletion of any minimum-root key.

For `--integer-masks`, let an LP variable denote the common orbit
average times orbit size. In an actual graph this total is an integer
even when the graph itself is not invariant under the group. The
pilot enforces integrality on mask totals only and leaves edge totals
continuous. Solver status alone is not a proof; a feasible result is
not a candidate graph. Smaller positive controls 2 and 10 both pass.

Replay commands (from `scratch/D`, use a 16 GiB virtual-memory cap
and one BLAS thread):

```sh
nice -n 5 timeout 300 ../../opt/venv/bin/python -B ../../ralph/lanes/D/max_root.py verify --bounds matching < max_root_matching.jsonl
nice -n 5 timeout 50 ../../opt/venv/bin/python -B ../../ralph/lanes/D/check_max_root.py calibration ../../gluing/val/r3_6_16.g6 max_root_sat16 fixed eager
nice -n 5 timeout 120 ../../opt/venv/bin/python -B ../../ralph/lanes/D/transport_root.py 40 9 19 --bounded-dual --verify transport40/19.sweep.json
nice -n 5 timeout 420 ../../opt/venv/bin/python -B ../../ralph/lanes/D/replay_outer_star.py 40 9 outer_star_orbit22.jsonl outer_star_orbit22.projection --direct --proofs outer_star_direct22
```

## Forest feedback (`hand` conditional on the three exclusions)

After the no-isolate cut, the only cyclic max12 signatures are 19,
20 and 22. Their unfiltered joint LP replays check exactly (`enum`,
pending encoding audit). Every edge of a max12 graph is maximizing,
so **if those exclusions are accepted, every edge kernel is a
forest**, not just the chosen root kernel.

For outer mask `M`, suppose `a` has two F-neighbors `b1,b2` of
degree two, with their far neighbors `a1,a2`. If `M` contains all
three `a,a1,a2`, reroot at the edge from the old root `u` to `a`.
The rerooted kernel contains the 6-cycle
`a1-b1-v-b2-a2-x-a1`; here `v` is the other old root, and `x` has
mask M. This forbids M. Similarly if an F-edge `ab` joins two
degree-two vertices, let their other neighbors be `b'` and `a'`.
An outside edge between masks carrying `aa'` and `bb'` closes the
6-cycle `a'-u-v-b'-y-x-a'` in the kernel at `ab`. This forbids
that arc. Neither rule assumes any other outside edges.

For a root-to-anchor edge `ua`, one side of the new kernel,
`N(u)-a`, is entirely fixed. Each opposite vertex has degree at
most two. Contract the length-two paths through degree-two
opposite vertices to edges on the fixed side, ignoring degree-one
vertices. This multigraph is a forest, so every nonempty subset S
of the fixed side has at most `|S|-1` edges wholly in S. A fixed
opposite vertex contributes a constant; an outside opposite
vertex contributes its mask presence times the indicator that its
two contacts are both in S. This gives the root forest-rank rows.

Controls: `scratch/D/forest_obstructions.log` explicitly reroots
7 pinned triples and 15 pinned arcs and detects their cycles by
leaf peeling. `scratch/D/forest_rank_cal16.log` preserves the
entire tight C16 control and the other C16 replays, where the new
forest premise is applied only to the tight case. The new pilot
uses keys 33 and 34, with and without prior star filtering; LP
limit 42 s, CPU cap 65 s, wall cap 100 s per probe. It must not be
used on max13..16.

The exact `(2,2)` count split first checks key 34 only. Estimate
approximately 48 CPU-s from the 5.28 CPU-s unfiltered forest LP;
cap each of the nine pinned LPs at 22 CPU-s and 35 wall seconds.
All 13 C16 rational replays pass, with the tight control pinned to
its known count six (`scratch/D/split_22_cal16.log`).
