# An induced eight-vertex root for every R(3) (`hand`, submitted for audit)

No maximum/minimum-square or forest hypothesis here. `P_k` means a path
on **k vertices**. At any edge `uv`, the edge kernel `F_uv` induced by
`(N(u)-v) union (N(v)-u)` is bipartite of maximum degree two and has
matching number at least seven (its independence number is at most nine).
It has no C4 by the no-K3,3 lemma (`SATURATED_BICLIQUE.md`).

**Claim:** some `F_uv` contains an *induced* P6. Thus one eight-vertex
core with all eight stars pinned covers R(3): `K4,4` minus an edge-disjoint
`P4 + K2` on six vertices (the missing graphs are vertex-disjoint as well).
The full two core vertices are the ends of the selected edge. This is a
cover across roots, not a partition of unrooted graphs.

## Step 1: some kernel contains a simple P6

Following `review/ideas/astra_R.md`, join two unordered codegree-three
pairs when they are opposite diagonals of a square. Call this graph D.
Each of its `n3=240+n1` vertices has three candidate neighbors. A
codegree-two opposite pair accounts for at most one failed incidence
since it has only two common neighbors; a codegree-one pair accounts
for none. Hence `sum deg(D) >= 3*n3-n2 = 360+5*n1`, using
`n2=360-2*n1`. A D-edge gives the six-vertex punctured K3,3. The degree
of either endpoint in D is one plus the number of full–tip doubles
on the *opposite* core side: the other two candidate opposite pairs
consist of its opposite full vertices individually paired with their tip.

For each of the four edges joining two full vertices in a puncture,
the other four core vertices form a P4 in its edge kernel. At either
end of that P4, extension is possible exactly when the corresponding
selected full vertex has an exterior neighbor also hitting its tip.
At most one such neighbor exists. Extensions at the two ends are
distinct (the two classes are disjoint). Conversely every simple P4
in every `F_uv` defines this puncture: its central two vertices and
`u,v` give the full square, and its endpoints are the tips. No endpoint
chord is possible because kernels have no C4.

Suppose there were no simple P6. Then no puncture has doubles on
both sides (one could select both corresponding full vertices).
Every D-edge therefore has a leaf endpoint. D consists of stars of
at most three leaves and isolates, so its average degree is at most
3/2. The displayed lower bound divided by `240+n1` is at least 3/2,
with strict inequality for `n1>0`. Equality forces `n1=0`, every
component of D to be a three-leaf star, and *every* codegree-two
pair to be opposite a codegree-three pair. Thus no `F_uv` has an
isolated vertex (that would have codegree one with the other root),
or an isolated edge (the corresponding square has both diagonals of
codegree two). Each puncture has doubles on exactly one side, on
**both** its full vertices. Every P4 therefore extends at exactly
one end; no component is P4. No cycles are possible (they would
have length at least six). Each 16-vertex F consists solely of P3
and P5 components. The only size decomposition is `2*3+2*5=16`,
of matching number six, contradicting the matching bound seven.
In particular the original six-vertex cover can choose `p>=1`,
leaving eight rather than eleven profiles without denying that the
other three could occur at nonchosen roots.

## Step 2: replace a closing C6 by an induced P7 elsewhere

A simple P6 in a graph of maximum degree two is induced unless its
ends join, giving a C6 component. The latter gives a core with
classes `a0..a3`, `b0..b3`, all cross edges except `ai-bi` for
`i=1,2,3`; the original edge is `a0-b0`. For each outside vertex v
record its mask of core neighbors, of size `s(v)`. This is an independent
subset of the core. It uses a slot for each pair of core neighbors:
same-side nonfull pairs each have one remaining common-neighbor slot
(six slots in total), the three missing cross-pairs have three each,
and there are no others. Total 15. The 32 outside vertices carry
`8*9-2*13=46` incidences. Therefore

```
unused pair slots + empty masks + sum_{s(v)>=3} binom(s(v)-1,2)
  = 15 + 32 - 46 = 1.
```

The only possible triples are the three nonfull vertices of one side.
Choose a side without such a triple, say B. At most one of its three
pair slots is unused, so some `bi` has both its slots `bi,bj` and
`bi,bk` used by **distinct** outside vertices. In `F_(a0,bi)` the
five other core vertices `bj,ak,b0,aj,bk` form a P5, and these two
outside vertices extend its endpoints. This P7 is induced: max degree
two leaves only a possible endpoint chord, and the endpoints are on
the same side. So an induced P6 always exists. If a graph has global
maximum simple kernel path at most six, it cannot have a C6 kernel
component at all, hence every simple P6 there is induced.

## Calibration and finite profile cover (`enum`)

`punct_path.py` enumerates core masks of size >=3 first; then all
unused pair slots, double masks, residual singleton counts, and a
possible empty cell. These are uniquely determined once the higher
masks and unused slots are chosen. The displayed slack identity uses
the corresponding capacities for the chosen core (slack six for P6).
Fixed colour classes are unique up to swap since the core is connected
bipartite. Exhaust all core permutations preserving adjacency and fixing
the central edge as a set. C6: 12 labelled / 4 orbits; P6: 4,756 / 2,434.
All twelve complete C6 incidence patterns have the claimed induced
P7 even before any outer edges are specified. On the 191 C22 census,
all three cap-three regular classes contain induced P6s: 239 placements
with one direction of the central edge, all recovered by the generator.
This smaller census has no C6 placements and is not used to prove the
target C6 rescue. Evidence: `scratch/D/punct8/path.log`, `path.tsv`,
`cycle.tsv`.

Bounded local-link pilot: unlike the censored complete puncture/restricted
panel runs, this is a projection for the separate global maximum-six
stratum. A selected triple of neighbors of a core anchor means some
vertex other than that anchor sees all three. Fix one member of the
triple as center and draw its other two as a link. A three-link path
on four distinct points implies a kernel P7; the three intermediate
witnesses must differ, since a repeated one would see four neighbors
of the original anchor. A triangle of links is similarly a C6 and is
forbidden in this stratum by Step 2. The smaller pinned tests include
both accept and reject outcomes for the six-cap, every eight-cap accepts.
Pilot three separated surviving indices 461/2388/2433 with 20 CPU-s
and 65 wall seconds each; this bounds initial solve cost at ~0.017 CPU-h.
Earlier full-target arms capped at 60 s, so do not scale a censored run.

## Shortest remaining stratum: there is a P6 but no simple P7

Let `L` be the maximum number of vertices in a **simple** path in any
edge kernel. Step 1 gives `L>=6`. If `L=6`, Step 2 excludes all C6
components; larger cycles contain P7 and C4 was already excluded. Every
kernel is therefore a union of paths of order at most six. No such premise
applies when `L>=7`.

For each eight-anchor profile, erase edges with both endpoints outside the
eight stars. A connected component on at least seven vertices in one of
the remaining edge kernels already implies a simple P7, since kernel
degrees are at most two. Independent component and exhaustive walk
checks on all 2,434 profiles give 1,228 with a known eight-vertex path,
1,184 more with a seven-vertex path, and **22 left at six**. An independent
unary-SAT census with 32 exterior vertices, eight degree equalities and
the pair capacities exhausts exactly the 4,756 labelled boundary
multisets (the 2,434 keys and their reversals). Evidence:
`scratch/D/punct8/audit-{boundary,paths}.log`.

### Projected UNSATs, conditional on L=6

Each frozen CNF needs only a *necessary* condition. In all formulas,
set all eight stars, forbid exterior pairs sharing a core anchor, and
enforce degree nine. For a fixed anchor `r`, a vertex not in `N[r]`
has between one and three neighbors in `N(r)`. For a triple in `N(r)`
record existence of an outside vertex seeing all three, using equivalent
conjunction/disjunction gates. No triple can occur twice (K3,3).
There are at least 12 such triples by the two-walk identity. At each
`a` in `N(r)` use triples containing `a` as the links on the other
eight coordinates. Triangle or P4 links are forbidden as described
above. These constraints suffice for 16/22 native CaDiCaL UNSATs;
the other six are SAT **projections**, not graphs.

Exact arm: for links `ij,jk`, if both `i,k` have codegree three with
`a`, each endpoint of the corresponding kernel P5 has another neighbor.
The extensions are distinct or close a C6; both alternatives are
forbidden here. Also impose triangle-freeness among exterior vertices
and common-neighbor cap and domination on exterior pairs. Two more
UNSATs (`2388,2421`); the other four hit 20 CPU-s without a decision.
Inputs and receipts in `scratch/D/punct8/{links,exact}/`.

For these eighteen results `path_audit.py` rebuilds byte-identical CNFs
and replays a proof with both `cake_lpr` and `lrat-check`. On four base
inputs (2291/2404/2419/2423) the construction already emits an empty
clause. The solver trace alone is accepted by Cake but *not* flagged
verified by `lrat-check`; use the generated one-line `.empty.lrat`
citing the existing empty clause, accepted by both. A crossed proof
is rejected. These are checked proofs of the frozen projections. The
global root argument, catalogue and semantics above are `hand + enum`,
**not a new Sec. 7 certificate of an unrooted Ramsey case**.

### Local packing bound (`hand`)

Make a triple system on `N(r)` from the triple masks above, now at any
vertex `r`. No pair belongs to >2 triples. A triple cannot share two
different pairs with other triples: if `abc,abd,ace` exist then the
link at `a` contains a P4 when `d!=e`, or a triangle otherwise.
Thus triples group into isolated triples and disjoint pairs of triples
sharing one pair. Here disjoint means disjoint *as blocks of triples*,
not necessarily vertex-disjoint. With `t` triples they cover at least
`3t-floor(t/2)` distinct pairs out of 36. Hence `t<=14`. The two-walk
identity gives `t=12+h1(r)`, so **every vertex has at most two codegree-one
partners and `n1<=40` when L=6**. This does not use any target UNSAT.
Calibration counted 37 shared-pair blocks on 34 short C22 stars.

The first eighteen CNFs leave indices 2298,2386,2424,2431. In each of
these four tables and in both orientations of the eight-anchor P6,
the first and fifth path vertices have codegree three (computed from
their full fixed stars, `path_packing.py`). Therefore, for triples
`abc,abd`, if `a,d` have codegree three, their additional witness besides
`r` and the `abd` witness extends `c-X-b-Y-d` to a P6 in `F_(r,a)`.
The witnesses differ by the cap-three rule. This P6 cannot close a C6,
so the four-profile cover forces `c,d` to have codegree three. Add this
implication on the eight stars, the packing bound on triples, `h1<=2`
globally, and `q(e)<=13` on those stars (a 16-vertex forest with paths of
size at most six has at least three components). A third static pilot
refutes **2386** in 13.52 CPU-s; 2298/2424/2431 cap at 20 CPU-s.
`scratch/D/punct8/packed/2386.{cnf,lrat,cake,check}`. This nineteenth
proof **depends on the earlier eighteen**, as well as on the hand lemmas.

**Result submitted for audit (`hand + enum`, with 19 checked formula
refutations):** if L=6 every induced P6 root has one of indices
**2298, 2424, 2431**, zero-based in `scratch/D/punct8/path.tsv`.
They are not three cases for the whole of R(3). If L>=7 an induced P7
is available (its endpoints are on the same side), and none of these
three-profile restrictions may be used there.

### Remaining panel pilot — not a closure

If L=6, the global maximum square count `q*` is 12 or 13: the lower
bound is the standard average, the upper bound the component count.
If 13, a maximizing edge kernel has three paths summing to sixteen,
each of size at most six. Thus one is P6. If 12, all edge square counts
are 12, there are no codegree-one pairs, and choose any P6. In either
case, after removing the P6 component the remaining 5-by-5 panel has
matching number >=4. For q*=12 it has seven edges/no isolates, hence
component sizes `2+2+6, 2+3+5, 2+4+4, 3+3+4` (five oriented types;
the unequal odd paths have two orientations). For q*=13 it has eight
edges and sizes `4+6` or `5+5` (two oriented types). Its row and column
permutations act freely on the two size-five singleton cells prior to
fixing a representative. Profile 2298 has a nonedge of codegree one
from its eight stars (core 1 and 6), so cannot occur at max12. The
same holds for the already refuted 2386. This yields at most 10+6
decorated roots for the residual `L=6` slice, not an exclusion of a root.

On C22, 48 P6-component placements check the smaller catalogue; six
distinct q-range pins accepted and all six deliberately narrowed ranges
rejected. Exact 18-anchor attachment masks preserve all 14 tested
smaller labelled pin types; the one-row overlap filter also preserves
them. On target, the plain instance with panel 0 capped on 4/4 and with
panel 5 had four SAT projections. The mask table decided all eight
pilots, two trivial max12 UNSATs on known codegree-one profiles, six SAT
projections. All four stronger one-row overlap pilots were SAT. Do not
spend more time on single-row supports alone. See `path_panel.py`,
`path_masks.py`, `scratch/D/punct8/{panels,masks,overmask}/`.

### Replay

From the workspace root, `R=$PWD; cd scratch/D/punct8`. Use
`$R/opt/venv/bin/python -B $R/ralph/lanes/D/path_audit.py . MODE` for
`MODE=boundary,paths,proofs` in separate invocations under the usual
limits. `path_audit.py` enumerates only the `links`, `exact`, `packed`
proofs used for the three-key result, not unrelated panel pilots. To
regenerate the graph-first cover in a fresh directory use
`punct_path.py DIR`, then `path_growth.py DIR/path.tsv DIR/growth.tsv`.
For the six-anchor census run `punctured.py DIR --mode base` and repeat
with `--mode panel` in another output directory. The run uses no old
max12 Farkas exclusions, SMS symmetry proofs or independent-set cuts in
the nineteen projected CNF refutations. Formula validity and reduction
chain remain for independent review. Hashes: `scratch/D/round8_evidence.sha256`.
