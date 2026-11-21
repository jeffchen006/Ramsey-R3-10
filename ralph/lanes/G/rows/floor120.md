# Degree-six residual floor 120 (hand + cert)

Let `G` be maximal triangle-free on 40 vertices with `alpha(G)<=9`, `v`
of degree six, `A=N_G(v)`, and `H=G-N_G[v]`. Then `H` is a `(3,9;33)`
graph. Tables 4 and 14 of Goedgebeur–Radziszowski, *New Computational
Upper Bounds for Ramsey Numbers R(3,k)*, EJC 20(1), #P30 (2013), give
minimum 118 and exact counts 5 and 69 at 118 and 119 edges. The complete
cover in `../root_certs/complete33_le119.g6` has these counts, and each
graph is validated and canonically distinct. Completeness uses **those
published counts**, not completeness of the seeded replacement search.
The `e=118` sublevel matches the originally sourced list canonically.

For each input, `root_core.py` generates the necessary MTF/core clauses
of `root_residue.md`; the argument there is independent of `e(G)`. Both
`lrat-check` and CakeLPR verify all 74 CNFs UNSAT. Thus `e(H)>=120` at
**every** degree-six root in the stated MTF class. Neither the degree-eight
nor degree-nine gluing result is a premise. Scope does not include graphs
before MTF saturation. The shared 294 rooted controls in round 2 certify
that actual smaller MTF extensions satisfy the same necessary clauses.

The existing private-cell estimate `Z(v)>=48` follows because the 33
exterior vertices are all covered by attachments, and each of six private
cells has at most `9-(6-1)=4` members. Since `A` is independent,
`e(G)=e(H)+Z(v)>=168`. So at `e(G)=167` add row `n6<=0`, and for each
pinned distribution with `n6=q>0` combine it with `-n6<=-q` (unit weights)
to obtain `0<=-q`. This refutes all 56 such distributions in the original
near-regular 524, one of which had already been closed using the previous
LP and gluing floors. The exact incremental list of 55 is
`../root_certs/closed167.csv`. 399 near-regular cases remain, plus Case R,
counting the already reported gluing and LP exclusions. The new cut
overlaps three old U88 cases, so successful complete `e88` gluing would
now remove 17 more, not 20; these are conditional counts only.

For `e>=168`, replace the degree-six admissible profile floor 119 by 120
and keep `t8>=97` as supplied by the degree-eight gluing. Matched `combined`
LP tests at the preceding threshold produce 35 strictly improved t9
upper bounds out of 213 eligible `n6>0` profiles, 36 total exact Farkas
certificates (including one extra step in a bound tightened by two).
This creates no further exclusions at the existing degree-nine gluing
floor and no additional U88 cases. Proof of individual LP row families
is unchanged; replay via `../scan_root_floor.py`.
