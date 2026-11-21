# Round 7: marked path/leaf windows and ledger

## Source and hypotheses

Use A's paired degree-six decomposition (`A/ADJACENT_DEG6.md`), the
accepted residue floor 120, and the strengthened codegree cap from
G-019/H-013. Write `u,v` for the original roots, `A=N(u)-{v}`,
`B=N(v)-{u}`, and `X` for their common exterior. Both strips are
independent, the sole cross edge is `a0–b0`, and each `X` support in
either strip is a singleton or double. There are four singles per
column and eight distinct doubles per strip. The augmented e122 graph
is just a way to mark the two missing double pairs: all deletions and
independence bounds below are on the **lower** graph.

On a path/leaf half the absent pairs in B form `b0–b1–b2`, with
cross endpoint `b0` and center `b1`. The lower half `H=G[B∪X]` is
order 33/size 120, with alpha at most 8. The center has degree six in
H (four private vertices and two doubles) and degree seven in G
(one additional edge to v and no cross edge). Delete `N_H[b1]` to
form `W`. This is an induced `(3,8;26)` graph. Each other strip
vertex has original H degree 7 or 8 and loses respectively 0 or 1.
Every retained anchor pair has a common neighbor in X, unique since
double supports are distinct; it survives because support size is
at most two. The six witnesses are distinct, and the four private
vertices of each retained anchor survive. In particular the retained
anchors are independent and have degree seven and pair codegree one
in W, not necessarily in G. Path/center alone has the same one-sided
geometry but not the original-center degree seven/uncrossed condition
used for the paired accounting.

## Edge accounting and caps

For `D=N_H(b1)⊆X`, let `s_A(x)` be the size of the opposite A-support,
and `d(x)=d_G(x)`. No x in D sees either original root, so
`d_H(x)=d(x)-s_A(x)`. The neighborhoods are independent. Therefore

```
e(W) = 120 - sum_{x in D} d_H(x)
     = 72 + sum_{x in D} ((s_A(x)-1) + (9-d(x))).
```

Use the strengthened codegree cap on **both** strips:
`1≤s_A,s_B≤2` and `6+s_A,6+s_B≤d(x)`. Thus a d7 vertex can only be
single in both strips; a d9 vertex contributes at most one, and each
other vertex at most two. This gives `e(W)≤84`. If X has no d8, the
two B-doubles in D necessarily have degree nine, giving `e(W)≤82`.
This applies to `(2,8,2,28)` (both strip profiles `(1,1,3)`), and
to `(2,7,4,27)` with one profile `(1,1,3)` and the other `(0,3,2)`.
If both halves of the latter pin are path/leaf, X has five d7 and
two d8. Their two D sets share at most three vertices, so at most
10 sub-nine vertices are counted with multiplicity; summing the two
window budgets gives at most `2*78+10=166`. At least one window then
has at most 83 edges; this does **not** cap both at 83.

The five exported Lean lemmas in `lean/R310/MarkedStrip.lean` check
the retained degree, unique witness, order/alpha, edge identity and
cap with an arbitrary set of known degree-nine vertices. They assume
the displayed structural hypotheses; no template enumeration, U88
result or global proof is inside Lean.

## Two-window reverse bounds (hand)

When both halves are path/leaf, let `D_A,D_B` be the six neighbors
in X of the two uncrossed degree-seven centers. Their respective
neighbors outside X are u and v. The centers are nonadjacent, and
their whole common neighborhood is `I=D_A∩D_B`. By MTF and the pair
cap, `j=|I|` is 1, 2 or 3. Intersection of the two one-side windows
is precisely `Y=X\(D_A∪D_B)` (17–19 vertices). Deleting both *closed*
center neighborhoods **in G** leaves the bigger window P on Y and
the two retained strips (eight anchors; order `24+j`). P is `(3,8)`
because an independent set there can be joined to both centers.

For the edge identity, subtract the degree sum over the *union* of
the two open neighborhoods. Each constituent is independent. The
only edges internal to the union are `uv` and edges of X between
`D_A\I` and `D_B\I`, so add these back once. The resulting row is

```
e(P) = 49 + 9*j + sum_{x in D_A∪D_B} (9-d(x))
                      + e_X(D_A\I,D_B\I).
```

Thus in the c=3 cover the final two terms sum to `e(P)-76`. Each
y in Y hits both D sets in G: it cannot be adjacent to a deleted
center itself, and neither original root can witness a center–y
nonedge. If y avoids I, it loses at least two neighbors. In
particular a d7 vertex with P degree six loses just one neighbor
and that neighbor belongs to I; P degree seven forces original
degree at least eight (nine on the n8=2 pin). These are lift filters,
not sufficiency. The exact `(3,8;27)` catalogue is a source only
for j=3. The j=1,2 sources are order 25,26; do not assume they can
be augmented to order 27 with alpha still at most seven. The one-
center catalogue test through e74 is not a test of both windows
and the supplied e74 set is incomplete.

## Reproduction and controls

- `python3 -SB ralph/lanes/H/check_strip_window.py`: complete smaller
  12-graph `(3,5;12)` catalogue gives 18 oriented two-addition path
  windows, every one `(5,5)` with alpha at most two, and 18 rejected
  triple-witness mutations. The 191-graph `(3,7;22)` catalogue gives
  no path pin, not a positive control for the pin. Generic paired
  deletion accounting checks all 526 and 31,994 nonedge pairs
  respectively; 526 and 31,994 need the crossing correction. The
  independent arithmetic control checks all nine allowed support/
  original-degree triples, caps 84 and 82. CPU: 0.80 s.
- `bash ralph/lanes/H/build_private_signature.sh build --old R310`,
  then the same wrapper with `env lean -j1 -s8192` on
  `../ralph/lanes/H/AxiomsRound7.lean` and on `scripts/Axioms.lean`.
  Compare each log with `check_axioms.py`. Pinned Mathlib cache, no
  Mathlib source build. Logs `scratch/H/round7-final-*.log` and
  `scratch/H/round7-axiom-audit.log`.

## Other audit notes

- D's max12 `Smax=2` dense/balanced split is sound as a hand
  argument: `M2=60+M0+2w≥60`, and the alternate upper bound
  `sum_v d2(v)^2≤6*M2` combined with Cauchy–Schwarz forces equality
  and all 40 degrees equal to three. The score-two root counts twice
  in its two stars, so the dense threshold in the other 16 is five.
  Every root-star kernel has one side in the fixed block, so fixing
  attachments fixes every cross edge of the kernel. This validates
  the hand projection, not all CNF clauses or any target exclusion.
- Round-006 verdicts filed: C excludes only the `(12,12)` wing split
  of global `R(6),f*=9`; E excludes one whole incidence profile and
  `G?Beto` only in the mixed profile under its stated hypotheses;
  B's new e108 critical certificates apply only to the supplied 614.
  The operator-reported 1,142 additional e108 classes require B/critic
  binding separately from the existing proofs and are not silently
  merged into B-016. No distribution count changes.
