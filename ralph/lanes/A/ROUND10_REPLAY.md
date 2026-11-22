# Round 10: residual mixed strip selector and certificate binding

Scope throughout: e168 distribution `(n6,n7,n8,n9)=(2,7,4,27)`;
one path/leaf strip A and a matching/incident or path/middle strip B;
the A pivot is its noncross degree-seven centre. Only **noncross B
pivots** are considered. The accepted degree-six strip premises and
the older scoped certificates are in G's `rows/path_leaf_windows.md`,
`rows/mixed_pivot_windows.md`, and A's `ROUND8_REPLAY.md` and
`ROUND9_REPLAY.md`. Nothing here covers a degree distribution, pure
strip cases, crossed pivots, or Case R.

## Codegrees and window bounds (hand)

For a noncross B pivot b of degree d and codegree j with the A centre,
`T=G−N[a]−N[b]` has `n=31−d+j` vertices, α≤7, and retains four
anchors on each side and their cross edge. Maximality gives j≥1;
R(3,8)=28 gives n≤27. R(3,7)=23 gives δ(T)≥n−23 by deleting
another closed neighbourhood in T, and Δ(T)≤7 by triangle-freeness.
Before removing opposite-exclusive signatures, the two retained
four-column degree sums (including their cross contact) are 29 and
27 or 25 for d=8 or 9. The exclusive lists have sizes `6−j` and
`d−1−j`. Deduct at least one incidence per lost signature and cap the
other `n−8` degrees at seven. This gives the following bounds; upper
minima are only averages, not attainability claims.

| B degree | j | n | Residual δ(T) interval before round 10 terminal proofs | e(T) cap |
|---:|---:|---:|---|---:|
| 8 | 1 | 24 | 1–5 | 78 |
| 8 | 2 | 25 | 2–5 | 83 |
| 8 | 3 | 26 | 4–6 (δ=3 excluded in round 9) | 87 |
| 8 | 4 | 27 | excluded in round 8 | 92 |
| 9 | 1 | 23 | 0–5 | 73 |
| 9 | 2 | 24 | 1–5 | 78 |
| 9 | 3 | 25 | 2–5 | 82 |
| 9 | 4 | 26 | 3–5 (now only 4–5 if round 10 proofs accepted) | 87 |
| 9 | 5 | 27 | excluded in round 9 | 91 |

These bounds are the same in either orientation of a marked window.
Matching/incident has three d8 noncross pivots and one d9;
path/middle has two of each. The cross endpoint belongs to degree
nine in matching and degree eight in middle. It is **not** in the table.

## One assignment across pivots (hand + enum)

Let `D_A=N(a)∩X`. For a retained B anchor t in a window rerooted
at b, write h(t) for the number of its missing pairs, s(t) for its
cross status, and j(t) for its incidence count on `D_A`. The exact
retained degree is

```
d_T(t) = 8 − h(t) + s(t) − [double bt exists] − j(t) + [double bt is on D_A].
```

Indeed the double `bt`, if present, is the sole exterior vertex in
both B rows, and its deletion must be counted only once. On retained
A, the initial degree `7+s(t)` loses precisely the B-pivot contacts
on `X−D_A` that also see that A anchor. The A star thus needs at least
one loss for each noncross pivot. Enumerating the common part's
B-centre doubles and then assigning the remaining B-centre doubles to
B-only labels fixes all five B rows on **one** support assignment.
The missing signatures are fixed up to disjoint exclusive-class
relabellings. The common labels may be sorted by B support, with no
loss. A-centre doubles cannot touch A's star, and all their labels
are in `D_A`, which every tested window deletes. Any two legal A
doubles placed on distinct `D_A` labels suffice for this relaxation.
A B-only double to B's star is forbidden on a label seeing A's star.

Code: `mixed_selector.py`. The selector checks every retained anchor
for each noncross B pivot on that *same* assignment. It does not
enforce exterior degrees in the other windows, their edge sets, or
full maximality or α≤9 in G. It should not be confused with G's
stronger SAT attachment projection. A retained role is not a
completion. With no fixed mark, the B-side necessary screen alone
retains 2,660 of 6,431 six-signature multisets (34 sorted codegree
profiles) in matching and 3,357 of 6,431 (49 profiles) in middle.
Both allow all four noncross codegrees to equal one in this weaker
relaxation. Thus no lower bound forcing a residual long window follows.

Controls: the known C13 passes the direct deletion/degree test on all
52 nonadjacent pairs. Dispersed old n26/n27 marks (terminal caps off
for controls) give 264 triangle-free fixed-mark addbacks and 264
occupied-hole rejections. Rerooted degrees are checked directly in
every positive joint addback. On two held-out d8 j3 matching roles,
an independent literal addback pass tests all seven-slot placements:
role `492 21495810 10780672 matching 18 21 15` has 210 geometrically
legal addbacks, 30 jointly valid; role `517 19398658 12877824 matching
18 22 23` has 180 legal addbacks but **zero** jointly valid. The
literal pass can fix the A-centre double placements because they do
not enter any retained anchor degree. Logs: `c13.control.log`,
`control{26,27}.log`, and `direct.log` in `scratch/A/strip10`.

On 260 **sampled** high-minimum marked windows from G's round-8
256-parent pilot, the d8 j3 selector retains 966/1,096 roles (matching
251/326 and 415/470, middle 136/136 and 164/164 by orientation).
All 223 marks that have a d8 role retain at least one. The d9 j4
selector retains 125/125 roles, all 88 associated marks. It also
retains all 215 exact low-minimum d9 j4 roles. The sampled loss does
not justify a full higher-minimum census or imply a speedup in proofs.

## Exact source/role joins and terminal scope

The n25 δ2 source is the earlier 18,333,381 rooted lifts, 20,181 raw
marks and 17,194 colour orbits independently checked in round 8.
The n26 δ3 source is the earlier 2,712,471 rooted lifts, 2,111 raw
marks and 1,767 colour orbits independently checked in round 9. Both
are weak marked envelopes, so their completeness is not conditional
on a pure strip shape. Independently enumerate both missing fifth-
column pairs and reject any occupied retained hole. Both orientations
are necessary; the first count below uses A's numerical mask first,
the second uses the reversed order. All role **IDs** agree with G,
not just the totals; the edge caps 83/82/87 below drop no role.

| Noncross B pivot and minimum | Matching (first/reversed) | Middle (first/reversed) | Total |
|---|---:|---:|---:|
| d8, j=2, δ(T)=2 | 28,699 / 40,579 | 9,881 / 11,355 | 90,514 |
| d9, j=3, δ(T)=2 | 997 / 1,137 | 1,391 / 2,606 | 6,131 |
| d9, j=4, δ(T)=3 | 3 / 47 | 93 / 72 | 215 |

The three old labelled-role lists also match (7,166, 5,179 and 162).
G's 28 pilot plus 187 production dual-LRAT receipts now refute the
**d9 j4 δ(T)=3** subcase only (both shapes and orientations). The
cut is `4/2/4`; both holes are on the four retained B anchors. A's
`audit_residual_binding.py` checks exact schedule/key union, every
independent fixed-edge pin map and eager ten-set suffix, and all
CNF and compressed trace hashes against G's checked index. A does
not run a second SAT or proof pipeline. Evidence: `binding26.log`,
`source.agreement.log`, and `roles.26.9.edge.keys`; G proof index
`scratch/G/round10/r26.d9.bound/certificates.tsv`. The n25 rows are
cover evidence, not terminal proof claims. Higher minima and all
other codegrees in the grid remain outside this new certificate.

## Replay

From `scratch/A/strip10`, use `../../../opt/venv/bin/python -B`
and scripts in `../../../ralph/lanes/A`. `mixed_selector.py table`
prints the grid and the B-side counts; `scan INPUT OUTPUT --degree
8` or `--degree 9` with `--roles-only` rebuilds ordered role lists.
Use `../../G/round7/lowdegree{25,26}.canon.keys` for the exact
sources and `../../G/round8/source21.delta4.256.canon.keys` for
the sampled joint pass (omit `--roles-only`). `direct-control
heldout.tsv` verifies the two literal cases. `audit_residual_binding.py
.` verifies G's terminal index, using `roles.26.9.edge.keys`.
`sha256sum -c round10.freeze.sha256` binds the inputs and evidence.
