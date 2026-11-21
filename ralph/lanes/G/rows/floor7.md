# Degree-seven residual floor 107: demand incompatibility

Let `G` be MTF with `alpha(G)<=9`, `n=40`, `d_G(v)=7`, `A=N_G(v)` and
`H=G-N_G[v]`. As usual `H` is a `(3,9;32)`-graph, each attachment
`S_a=N_G(a) cap V(H)` is independent, and `A` is independent.

## Hand lemma, any order or root degree

A **demand** is a singleton `{x}` of `H` or a pair `{x,y}` at distance at
least three in `H` (including disconnected pairs). Every demand is
contained in one attachment: by MTF `v,x` have a common neighbour in `A`
for a singleton. A pair is nonadjacent in `G` and there is no common
neighbour in `H`; its MTF common neighbour is not `v`, hence lies in `A`.
Call two demands incompatible if an `H` edge joins a vertex of one to a
vertex of the other. They cannot be in the same independent attachment.
Thus `d_G(v)+1` pairwise incompatible demands refute an MTF extension.
For each supplied clique the verifier checks mask size, distance using
adjacency intersections, and the edge condition on every pair. It does
not trust the clique search, any local degree cap, or LP arithmetic.

## Finite application

GR Tables 4/14 give minimum 104 and 39/952/18598 classes at 104/105/106
edges. The 39 minimal residues are from the House of Graphs catalogue;
successive legal edge additions find all 952 and 18598. In replay, the
39 are fully verified; `verify_uncovered.py` then independently regenerates
legal additions in Python, compares exact canonical sets and checks the
published counts, vertex orders, edge counts, and triangle-freeness.
Independence number cannot increase on adding an edge. No degree-nine or
degree-eight gluing result is an input.

At 104/105/106 the exact replay accepts 39/951/18531 incompatibility
cliques. The complementary 0/1/67 inputs have the full necessary MTF
CNF from `root_residue.md`, with seven attachments. Both LRAT checkers
pass; `replay_floor7.sh` binds the exact complement, regenerates the CNF,
checks fingerprints and uses both checkers again. Consequently every
degree-seven root has **`e(H)>=107`**, independent of `e(G)`. This is an
MTF result only. The degree-six floor is not a premise of this proof.

The row for the class LP is `Z(v)<=e(G)-107` for each degree-seven root
profile. `scan_root_floor.py` uses this with the degree-six floor 120 and
the previously reported degree-eight gluing bound. T9 bounds are exact
Farkas certificates; their conversion to case exclusions is conditional
on the existing degree-nine gluing bound too.
