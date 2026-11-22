# Round 20 — necessary shape of a saturated 32/e108 exterior

**Hand, pending check.** This narrows only the *possible saturated gap* in
B-038. No source was acquired and no target input, receipt or proof was
read or replayed. B-036/B-037 still cover 2,104,146 named keys; the five
absent critical keys have unknown minimum degrees and addability.

## Private-column bound

Let `H` be triangle-free with independence number at most `k`. For a
root `v`, put `A=N_H(v)`, `d=|A|`, `K=H-N_H[v]`, and `m=|V(K)|`.
Write `q=e(H)-d-e(K)` for the number of A-to-K incidences. For each
vertex of `K` its column is its set of neighbors in `A`. Write `z` and
`s` for the numbers of zero and singleton columns, respectively.

- A zero column is exactly an endpoint of a triangle-safe new edge
  incident with `v`. Such an edge also preserves the independence cap.
- The singleton columns `{a}` form an independent set (all have the
  common neighbor `a`) and so does their union with `A−{a}`. Each of
  the `d` singleton groups therefore has size at most `k-d+1`.
- Counting incidences gives `q >= m-z` and `q >= 2(m-z)-s`. Hence
  `z >= max(0, m-q, ceil((2m-q-d(k-d+1))/2))`.

## Smaller controls (literal, by hand)

- `C5`, `k=2`: `d=m=q=s=2`, `z=0` at each vertex. Each nonedge
  closes a triangle. This is a saturated deletion-critical control:
  one deletion gives a path with an independent triple.
- `C7`, `k=3`: `d=2`, `m=4`, `q=s=2` at vertex 0, and the predicted
  two zero columns are exactly vertices 3 and 4. Withhold `C7` and
  present the parent `C7+03`: deleting `03` recovers the withheld
  deletion-critical graph (deleting any of its own edges gives `P7`,
  which has an independent four-set).
- `C13(1,5)−{1}`, `k=4`: the symmetric steps `±1, ±5` make no
  triangles. Five independent vertices in the original circulant
  would have cyclic gaps at least two summing to 13. The three
  multisets are `(2,2,2,2,5)`, `(2,2,2,3,4)`, `(2,2,3,3,3)`;
  they force either a gap 5 or consecutive gaps 2 and 3, both
  forbidden. At root 0 the rows of `A=(12,5,8)` on `K` are
  `{4,7,11}`, `{4,6,10}`, `{3,7,9}`. Thus `d=3,m=8,q=9`;
  `m-q` alone proves nothing, but the singleton bound proves `z>=1`.
  The unique zero column is indeed vertex 2.

Independent literal subset/triple checks on these three fixed controls
matched all predictions (`scratch/B/logs/r20_saturation_controls.log`,
0.02 CPU-s, 9,284 KiB RSS). No target catalogue was used in the controls.

## Application to order 32 and 108 edges

Use Goedgebeur–Radziszowski Table 3 (`arXiv:1210.5826`, dependencies
D-E8 and D-R2): `K` has independence number at most seven, so `m<=27`,
and the edge minima at orders 25, 26 and 27 are 65, 73 and 85.
Thus `d>=4`; every degree is at most eight because every neighborhood
is independent.

| Root degree | `m` | Upper bound on `q` | Consequence |
|---:|---:|---:|---|
| 4 | 27 | 19 | At least eight zero columns (`m-q`). |
| 5 | 26 | 30 | At least one zero column (`ceil((52-30-20)/2)`). |
| 6 | 25 | 37 | Saturation at the root requires `q>=50-18=32`, or `e(K)<=70`. |

Consequently any saturated `H` at this level has minimum degree **exactly
6** (mean degree `216/32<7`) and at least eight degree-six vertices
(`216 >= 6 n6 + 7(32-n6)`). At **every** degree-six vertex its puncture
is in `R(3,8;25,65..70)`. At the endpoint `e(K)=70` equality forces all
six singleton groups to have size three, and the remaining seven columns
to be doubletons. The seven doubleton masks are distinct: two copies of
`{a,b}`, the three singleton columns of `{a}`, and the four rows
`A−{a,b}` would form an independent nine-set.

## Scope and next trigger

This uses neither deletion-criticality nor an order-40 hypothesis. It
does **not** imply that the five missing keys are addable or that the
saturated slice is empty. If an independent complete e109 source ever
arrives, its descent cannot miss any e108 graph of minimum degree at
most five. Any *saturated* remainder would be covered by d6 lifts from
a complete 25-vertex, e65..70, alpha-at-most-seven source, imposing MTF
also inside the 32-vertex output. Neither full arm has a measured
end-to-end price or a new source here. Do not reopen either arm based
on this note. No search or rescan, no new root obstruction, no floor-109
or U88/distribution debit. Zero solver core-hours and no detached PIDs.
