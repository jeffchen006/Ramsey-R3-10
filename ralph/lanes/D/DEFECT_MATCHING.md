# Two disjoint deficient pairs in R(3) — round 10

**Submitted `hand + enum`.** In any 40-vertex 9-regular Ramsey graph of
maximum nonedge codegree three, there must be **two vertex-disjoint
nonedge pairs of codegree one**. This is a necessary root, not closure
of R(3). No cycle-length or maximum-square condition is assumed.
The no-defect case (hence the whole max-square-12 stratum of D-010)
also has a separate short graph-only exhaustion. There is no Section 7
certificate for the new structural result.

Let `J` have the same vertices as G, with edges the pairs of codegree one.
Codegree zero on a nonedge would extend a full neighborhood to an I10.
If J has no disjoint edges, either one vertex meets every edge, or its
nonisolates form a triangle. Indeed, two intersecting edges `ab,ac` can
be missed by a third edge not through `a` only if it is `bc`. An edge
intersecting all three is then one of those three. Empty J is included in
the first alternative. In particular the hub search allows **arbitrarily
many partners of its marked hub**, not only one partner.

## One common hub: complete marked cover

Use D-015 (an induced P6 in some edge kernel), not a small-stratum
survivor set. The source is all 2,434 earlier eight-star P6 boundary
profiles. The new input orders vertices as the two roots then the six
path vertices. Old-coordinate → new-coordinate map is `(1,2,4,6,0,5,7,3)`.
Try each anchor and one exterior point per equal-mask cell as the hub. An
already exact singleton-codegree pair of anchors must contain the hub.
This leaves 27,289 marks. `defect_receipts.py` reconstructs the graph in
the **old** coordinates and checks all 40 possible hub locations against
the saved source. The 2,434 profiles have respectively 0/1/2/3 internal
deficient pairs with counts 1027/1147/257/3. End-to-end placement counts
and per-root SHA bindings are in `scratch/D/ind10/{bindings.log,terminal.tsv}`.

`defect_graph.cpp` is a graph-only decision search. Lower edges come from
explicit frozen stars, upper edges initially allow every unpinned pair.
Maintain exact degree nine and triangle-freeness. A nonedge needs one
common neighbor if incident to the hub, otherwise two; upper codegree
is always three. If the possible common neighbors just attain the lower
bound, force all those two-edge paths; if the mandatory intersection
attains the upper bound, forbid additional witnesses. An optional pair
with too few possible witnesses must be adjacent. A forced nonedge with
at most one possible witness already spends a defect (and cannot avoid
the hub). Contradict an I10 even in the upper graph. If an optional edge
xy has eight further upper-independent vertices avoiding x,y in the
upper graph, it must be present. Iterate. These are necessary rules,
not assumptions that every pair of compatible stars extends.

Branch by an entire still-unfrozen row. In its free cells, two points with
identical neighborhoods on **explicitly frozen** stars and the same marked
status are interchangeable. Already-forced graph edges are derived, not
additional initial decoration. Try a prefix of each cell at every feasible
size, honouring fixed-star codegrees and degree. Freeze the selected row,
recompute its consequences and recurse. A cutoff is an unresolved input.

Later stages can use the *whole* preceding cutoff set as the library of
allowed marked P6s. On each forced six-vertex path in a kernel, check that
its closing edge is impossible before using the library: a C6 has no
such membership obligation. In a completable degree-two kernel there is
no other possible chord of this path. Both orientations are loaded with
the root swap. Project onto full stars (degree already nine). The hub
is coded by its exact core position or its projected exterior mask. The
additive 64-bit fingerprint only indexes options: a collision can add a
candidate, not turn a real mapped pattern into an absent one. For buckets
of ≤64 candidates, `hub_deck.hpp` also checks that the **same** pattern
admits a matching from exterior vertices to all its exterior mask slots,
respecting mandatory and possible bits and the position of the marked hub.
Larger buckets skip this strengthening. No hub is relabelled independently
between views.

| Stage | Source | Exhausted | Unresolved | Nodes | CPU-s |
|---|---:|---:|---:|---:|---:|
| No library, cap 500 | 27,289 | 25,372 | 1,917 | 1,666,116 | 227.60 |
| Prior 1,917, cap 900 | 1,917 | 1,295 | 622 | 866,717 | 123.41 |
| Prior 622, cap 1,400 | 622 | 485 | 137 | 343,242 | 45.82 |
| Prior 137, cap 2,600 | 137 | 131 | 6 | 66,300 | 8.46 |
| Prior six | 6 | 6 | 0 | 6 | <0.01 |

Calibration: 239 physical C22 induced-P6 placements, both directions and
all 22 choices of a distinguished vertex, give 765 inputs and 880 distinct
anchor-and-hub-coloured canonical graphs. Plain, hash-only and matched
searches recover the same 880 exactly (`marked-cal.log`, `match-cal.log`).
These positive tests **do not require** every defect to be incident to
the chosen site; imposing that would have no positive here. Separate tests
enforce the actual vertex-cover predicate on C22 (one dropped member
fails) and mark Clebsch with no frozen stars (`hub-cal.log`). Empty deck
is rejected on all 765 controls. An earlier oracle using only site 0 was
incomplete; all 22 sites replace it. No target result uses that oracle.

## Intersecting but not a star: the triangle

Let a,b,c be the three mutually deficient vertices. They are independent.
Their three common neighbors must be distinct: a shared witness z for all
three would make `(N(a)−z)∪{b,c}` independent of size ten. Index the
witnesses by the *opposite* center. Each meets exactly the other two
centers; witnesses are pairwise nonadjacent since each pair has a common
center. The six fixed vertices form a C6. This does **not** impose a C6
prohibition on any kernel. No other pair can be deficient in this case.

Every center has seven private exterior neighbors. A private neighbor
at center i may see only witness i, by triangle-freeness. The number
seeing that witness is exactly the nonedge codegree of the opposite
center–witness pair, 2 or 3. The remaining thirteen exterior points see
no center. The three witness neighborhoods in that 13-set have sizes
`7−p_i`; pair intersections have size 1 or 2 (the witnesses already
share one center). Choose the triple intersection, then all eight cell
multiplicities follow. Permute the three centers and their opposite
witnesses together. `defect_triangle.py` gives 136 labelled profiles,
44 orbits. Independent generic six-mask incidence recursion in
`defect_receipts.py` reproduces the labelled count and all orbit keys.
All 44 roots run **without a library**; the first cap exhausts 30 and
the remaining 14 terminate with at most 30,617 nodes each. 32.39 CPU-s
total. The order-22 analogue recovers exactly its one occupied orbit in
42 possible profiles, covering all 11 physical triangle marks; other
defects outside the marked triangle are allowed in the positive control.

## Redundant checks and scope

* **No defects at all:** independently run `pair_domain.cpp` on all 2,434
  P6 profiles. With all nonedge codegrees 2 or 3, the high-pair adjacency
  matrix H obeys `A²=(d−2)I−2A+2J_all+H`, so `AH=HA`; every row of H has
  12 ones. The propagator keeps edge/low/high domains, their cardinalities
  and the two directed edge–high intersection counts. The optional flat
  edge-square quota is **disabled** in `full6--1.out`. 2,428 exhaust at 600
  nodes; all six tails exhaust by 1,375. Graph-only `audit6.out` has no
  colour quotas, no commutation, no library: 2,434 terminal / 28,005 nodes
  / 4.40 CPU-s. Zero-defect already follows from the hub result, but these
  are much faster audit routes. `pair-cal.log`, `model-check.log`: planted
  colours/negative quotas and complete unrooted C13/Clebsch controls.
* **Exactly one defect:** both endpoints can individually serve as the
  hub. From the *first* 1,917 still-live single-hub rows try each unordered
  pair, respecting repeated exterior cells and known anchor defects. The
  independent labelled ledger matches all 4,741. Both individual hub
  views first apply; 533 unresolved. Then a library of **both** marks on
  one P6 leaves six; the six-pattern library excludes all six. Separate
  planted two-mark census (195 exact classes), also with empty/nonempty
  predicates, at `pair-cal22.log` and `jointpair-cal.log`. This result is
  redundant for the matching theorem and not a premise of its hub chain.
* **Proof pilot:** `defect_cnf.py` uses no symmetry and no independent-set
  assumptions, only labelled frozen stars, degree, triangle and nonedge
  codegree 2..3. IDs 2010 and 2070 have dual-checked LRATs, independent
  of the colour or graph search. The 1785 run hit its CPU cap; no proof
  claimed. `proofs/` retains the completed bindings and checks. These are
  two formula refutations, not an LRAT proof of a whole unrooted case.

Replay: compile `defect_graph.cpp` with `g++ -O3 -std=c++17 -march=native`.
In `scratch/D/ind10`, the arguments are `40 9 8 780 39 5 500` on `hub1/h??`;
for stages 2..5 use `40 9 8 780 39 269 CAP PREVIOUS/live.tsv`.
Triangle uses `40 9 0 3 39 37 CAP` on `tri.in`, `tri-tail.in`. The first
cap is 3500; the second is 50000. Independent binding command from root:
`opt/venv/bin/python -B ralph/lanes/D/defect_receipts.py scratch/D/ind10`.
All searches used resource limits. See `plan.txt` for decisions and
`terminal.tsv` for ordered per-input evidence (not a proof format).
