# The one-triple support census (round 18)

**Hand + enum; marked necessary conditions only.** At `K=2,t=17,m=15` in R(3), the 14 untouched sites of any graph must give one of **162** supports on the seven poles: 99 when the exceptional pole is in the triple, 63 when it is not. These account for 651,000 oriented, pole-labelled supports. None has been extended to wings or proved impossible as a whole. The 162 are not graph classes. The preceding `m=16` exclusion is separate (`MIDDLE17.md`, critic round 017).

## What is being counted

Mark one codegree-one pair `a,b` with middle `h`. The private wings `A,B` have eight sites each, `X=N(h)−{a,b}` has seven poles, and the 14 other sites form `Y`. Let `t=e(A,B)` and `m=e(Y)`. By D-028 the two deficient paths at `K=2` are vertex-disjoint, including their middles. Thus no other nonedge incident with a marked site is deficient, **and** no pole pair has only `h` as witness. Both statements are used below.

The 19-site book `{a,h,b}∪A∪B` has `18+t` edges. Its cut in the 9-regular graph has size `19·9−2(18+t)`; the 21-site complement therefore has `27+t` edges. For a pole, its wing contact counts `l,r` lie in `{1,2}` since its codegrees with the tips are `1+l,1+r`. It has `8−l−r` neighbors in `Y`. The poles are independent, so `m=t−1−Σ(4−l−r)`. At `(17,15)` the deficit sum is one: six poles have `(2,2)` and exactly one pole `e` has `(1,2)` after uniquely orienting the tips. Its Y-degree is five, not four. The 29 incidences with `Y` have row sizes `c(h,y)` in `{2,3}`: one physical triple `T`, thirteen ordinary two-pole rows. These conclusions do **not** locate `e` in `T`.

For a pole pair `i,j`, put `Jᵢⱼ=# ordinary Y rows on {i,j} + [i,j∈T]`. If `P,Q` count the two-pole rows on the short and long shores, respectively, then

`1 ≤ Jᵢⱼ + Pᵢⱼ + Qᵢⱼ ≤ 2`.

The full codegree is that sum plus `h`: the upper bound is the R(3) cap, the lower needs the separate no-other-sole-witness fact. The support census imposes **only `J≤2`** at this stage, not `J≥1`. Each wing site has one or two poles by its codegree with `h`. Thirteen contacts on eight short-wing sites give five paired rows and three singletons; fourteen contacts on the long wing give six paired rows and two singletons. When the pairs are specified, residual singletons at each pole are forced. A shore swap is not a symmetry of this orientation; in particular one must not divide a later join by two.

## Which Hall test is exact here?

Any independent set of `s` Y sites has at least `s` incident poles: with the unused poles and both tips it would otherwise extend to an independent ten. Pairwise-intersecting support rows are necessarily independent by triangle-freeness. We test all these forced independent sets, **not** all independent sets of a future Y graph. Repetitions are different sites.

Among two-sets alone, the exact test is that doubled edges are a matching and no doubled edge lies in an ordinary support triangle (round 17). Here is the additional rule for the triple. Once those ordinary tests pass, a violation using `T` must consist of `T` and a *tight* intersecting family of ordinary rows (size equals number of incident poles) whose union contains `T`. Indeed removing `T` cannot leave a violation, and adding one row can increase the deficit only by one. Each member must meet `T`. Distinct pairwise-intersecting two-sets form a star or a triangle. Thus the only additional forbidden configurations are:

- The three sides of `T` occur as ordinary rows.
- A star centered **inside** `T` has both other triple poles as neighbors and has a doubled edge. The doubled neighbor is outside `T` by `J≤2`.
- A star centered **outside** `T` hits all three triple poles and one of these edges is doubled.

For the star assertion: a star with `s` distinct edges covers `s+1` poles, so tightness requires a repeated edge; at most one can repeat. For a triangle with all three sides no edge may repeat. Conversely, each displayed configuration, including `T`, already has more rows than poles. This criterion does not use `e∈T`. The inside star does require its center to have four ordinary incidences, which on `T` is possible only at `e`. Controls explicitly distinguish the exterior doubled star that ordinary-Hall alone accepts.

## Labelled and marked counts

In the stored normalization `e=0` and `T=012` or `123`. `fixed` counts words for these exact labels and triple; `oriented` allows the exceptional pole and the triple to vary on seven named poles, still with the short wing first and Y rows unordered. For automorphism order `a`, the weights are `48/a` or `36/a` fixed, and `7!/a` oriented. The groups fixing `e,T` are `S₂×S₄` or `S₃×S₃`, respectively. These are equivalences of descriptions, not claims of graph automorphisms.

| Triple | Raw reps / fixed | Ordinary Hall rejected reps / fixed | Further triple rejected reps / fixed | Passing reps / fixed | Passing oriented |
|---|---:|---:|---:|---:|---:|
| `012` | 536 / 21,638 | 423 / 17,338 | 14 / 420 | **99 / 3,880** | 407,400 |
| `123` | 607 / 18,732 | 536 / 16,740 | 8 / 252 | **63 / 1,740** | 243,600 |

The 22 extra rejected types are 3 `T` triangles, 4 inside stars, 15 outside stars. No overlaps among these three categories on this roster (not a general disjointness claim). With all 14 Y sites separately labelled as well, multiply each oriented weight by `14!/∏(ordinary multiplicity)!`; the passing totals are 14,700,875,245,056,000 and 9,355,102,428,672,000. Neither these weights nor the orbit counts include wing assignments.

## Controls, independent audit and files

`triple18.py` builds bounded multiplicity rows with the required residual degrees and subtracts the orbits under the marked permutations. For each ordinary star and triangle it checks all its rows, then the subfamily meeting `T` together with `T`. This maximal-family test suffices: appending an ordinary two-set to a nonempty intersecting subfamily can add at most one new pole, so an existing violation cannot disappear. For a violation using the triple, keep it in the subfamily from the start.

`triple18_audit.py` imports none of the generator. For every representative it searches cliques of the **physical** intersection graph, retaining a literal row-index witness on every rejection; it also checks the three-motif characterization. It expands labelled images as multisets of actual pole pairs, checks orbit disjointness and every stored weight, and equates the union sizes to a second count: the coefficient at residual degrees of `∏ᵢⱼ Σ_{w=0}^{2−[i,j∈T]} (zᵢzⱼ)^w`. The two coefficient totals are 21,638 and 18,732. This proves no labelled support is omitted; no scout inventory or external graph enumerator supplies the counts.

Controls: 432 literal four-pole hypergraph cases (196 ordinary failures, 40 new triple failures, 196 passes); positive and negative marked-orientation checks; two small weighted orbit catalogues. All 191 order-22 (3,7) controls recover the ten regular hosts, three with cap three. The Hall implication and pair upper bound hold at all 125 physical markings, including 22 with a triple. The target's lower bound is not silently imposed on this smaller control. The two small ordered-join controls have 10/5 and 60/12 ordered pairs/orbits by both direct subtraction/equivalence and fixed-point arithmetic; the latter has nonidentity fixed counts of four.

`S=scratch/D/triple18`. `S/roster.jsonl` includes **all** 1,143 reps and per-row weights/status, not just the 162 survivors. `S/witnesses.tsv` names ordinary vertices 0–12 in lexicographic pole-pair order, then triple vertex 13. `S/{controls,census,audit,price}.log` are the run receipts. Fresh rebuild: `bash ralph/lanes/D/round18_replay.sh scratch/critic/D18-audit`. The script compares roster, witness list and deterministic counts byte-for-byte. `ROUND18_FREEZE.sha256` binds inputs, source and original outputs.

## Price before a target join (estimate; no target pairing performed)

The 4,062 short and 6,202 long marginal words would give **4,081,188,888** naive pairs across the 162 hosts. Before degree constraints, the pair-cap/floor permits at most 283,218,542 ordered outputs on those fixed hosts: for given numbers `j₀,j₁,j₂` of pairs with `J=0,1,2`, take `[u⁵v⁶](u+v+u²+uv+v²)^{j₀}(1+u+v)^{j₁}`. This is an upper bound, **not an estimate of the true output count**. Even hypothetical 16-byte rows at that bound would take 4.53 GB, over the round's budget. Do not materialize this product.

Suggested next stage, only with authorization: count compatible ordered pairs and their marked orbits **without emitting pairs**. Index the long words by bit; intersect 21 precomputed multiplicity masks for each short word, then popcount. For orbit counts apply Burnside: a fixed ordered pair must have both its short and long word fixed by the same marked pole action; restrict the long bitset and loop over fixed short words. The 162 stabilizers have orders `1:103, 2:48, 4:7, 8:2, 12:2`, total 267 actions. Upper workload 1,084,554 word visits, 22,775,634 bigint ANDs and 2,740,488 single-word action tests; one global 6,202-bit index, not a 4-billion-cell table. An intentionally full-width *synthetic* benchmark in `triple18_price.py` prices the inner loops at about 7–13 CPU-s on this host, not measured target compatibility. Build the small right lookup once, cache by `J` value, and allow **90 CPU-s, 64 MiB working memory** for the first count-only pass; stop and reprice rather than expanding any orbit if exceeded. An independent verification pass would need its own cost check. This prices only a count: proof time and disk remain unpriced, and there is no all-`t=17` conclusion.
