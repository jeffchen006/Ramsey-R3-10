# Saturated biclique incidence bound (`hand`)

Let a triangle-free graph of order `n` have minimum degree at least `d`
and every nonedge codegree at most `c`. Suppose `A,B` are sides of a
complete bipartite `K_{r,c}`, with `1 <= r <= c`. They are independent
and each vertex outside `A union B` sees at most one side (otherwise
it makes a triangle). A vertex outside cannot hit two members of `A`:
their codegree is already `c`. A pair of members of `B` therefore has
at most `c-r` common neighbors outside the biclique.

For outside vertex `x`, let `k_x` be its number of neighbors in the
biclique. Then `k_x <= 1 + binom(k_x,2)`, with equality only for
`k_x` equal to 1 or 2. Only `B`-pairs can contribute to the binomial
sum, and each contributes at most `c-r`. By counting the incidences
from the biclique outwards,

```
(r+c)d - 2rc <= sum_x k_x <= n - r - c + binom(c,2)(c-r).
```

If the extremes are equal, every outside vertex hits one or two
members of the biclique, and each `B`-pair achieves its outside
common-neighbor allowance. All the biclique vertices have degree `d`.

## Consequences for the rooted covering problem

- `r=c=3, d=9, n=40`: `36 <= 34` is impossible. Hence in R(3), the
  three-element nonedge support at any vertex occurs at most once: two
  occurrences together with that vertex would form one side of a
  `K_{3,3}`. A rooted edge `uv` with a four-cycle in `F` likewise gives
  `K_{3,3}` on the cycle plus `u,v`. This kernel cut excludes 65 of the
  original 238 oriented kernels, **all already excluded** by Lane C's
  integer projections. No surviving root-swap orbit closes. The local
  triple uniqueness cut is not implied by absence of a cycle in `F`.
- `r=c=4, d=9, n=40`: `40 <= 32` is impossible. In R(4) a root kernel
  containing `K_{3,3}` therefore cannot complete; no R(4) sweep claimed.
- `r=3, c=4, d=9, n=40`: equality `39=33+6`. In a hypothetical R(4)
  `K_{3,4}`, each of the three `A` vertices has five exclusive outside
  neighbors. Each of the four `B` vertices has three exclusive outside
  neighbors, plus one shared with each other `B` vertex. These are all
  33 outside vertices, split into 15 `A`-attachments and 18
  `B`-attachments. The former have alpha at most five (pad with `B`),
  the latter alpha at most six (pad with `A`). The three groups of five
  on the `A` side are independent; between any two fixed groups there
  must be a perfect matching by König's theorem, since the two groups
  induce a bipartite graph of order ten with alpha at most five. This
  is only a conditional structure lemma, not exclusion of R(4).

## Checks

`check_biclique_cut.py` checks all five 5-regular cap-3 C16 control
graphs directly, then compares four-cycle hits across the complete R(3)
catalogue and the 110-orbit survivor map. It also tests a square versus
the empty bipartite kernel. See `scratch/D/r3_biclique.log`.
The saturated inequality itself is sharp on `K_{3,3}` with `n=6,d=3`.
For an asymmetric equality control use `K_{5,5}` minus a perfect
matching (`d=4,c=3,n=10`). Choose two left vertices and the three
right vertices outside their two missing partners. The five outside
vertices attach twice singly to the small part and once to each pair of
the large part, attaining the inequality; see `scratch/D/biclique_equal.log`.
