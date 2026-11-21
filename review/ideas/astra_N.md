# Near-regular MTF cases: three ranked experiments — astra_N, 2026-11-21

**Recommendation: B should import the 1,142 new critical keys before spending another core-hour on gluing.**
The 376 in the brief is the round-3 count. The checked round-5 ledger has **278** near-regular distributions plus R;
the MTF floors at degrees 6/7/8/9 are 120/108/97/88 (the last two inherited from gluing).
The ten conditional U88 keys and twenty e168 keys with a degree-six vertex are not exclusions.
Evidence below is in `scratch/ideas/astra_N/` unless prefixed by a lane path. No order-40 case closure is claimed.

## 1. Feed degree-seven gluing from the next order up, not from its exhausted swap component

**Measured (enum, supplied keys).** `handoff.g6` is a sorted, ordinary-nauty-canonical delta against B's frozen
`scratch/B/work/e108_r6_follow/pass4/union.g6`. Its 1,142 graphs all have 32 vertices, 108 edges, no triangle,
and independence number at most eight; deleting *any* edge creates an independent nine-set. Intersection with
B's 2,102,885 keys is empty. An independent Traces count gives 1,756 distinct graphs in the union with B's 614
critical keys. Adding the 2,102,271 reducible keys gives **2,104,027 of 2,104,151** (GR, Table 14 / §6; B's
`ROUND6_REPLAY.md`): **124 missing**, down from 1,266. This is partial input coverage, **not** floor 109.

**Mechanism (proved).** Take a known `(3,9;33)` host F from **G**. For each vertex v form the induced card F−v.
Delete edges in increasing index order toward 108. In a current card K an edge xy is deletable iff
`α(K − (N(x) ∪ N(y))) ≤ 6`: a new independent nine-set would have to contain x,y and seven common non-neighbours.
Once nondeletable, always nondeletable under further edge removals that keep the graph legal. Thus the DFS can
discard a node if it has fewer still-eligible edges than its deficit. Conversely **every** legal target subgraph
of that card remains legal along the sorted deletion path. At 108 keep only edge-critical leaves. This proves
completeness *within a card*, not that every target embeds in a supplied host. Run B's already tested critical
one-edge exchange **only on the newly reached components**. A fixed point there is not a global census.

| Disjoint discovery stages | Measured yield |
|---|---:|
| All 74 order-33 e118/119 hosts + 248 spaced e121 + 243 spaced e122 | 178 new direct critical seeds; 0.75 CPU-s descent |
| B's exchange from those seeds | +371, +335, +87, +6, +0: **977** new in total |
| 327 hosts stratified across critical e121–123 and e124–127 sources | 5 *further* direct seeds in 1.12 CPU-s |
| Exchange from those five | +25, +42, +45, +34, +12, +2, +0: **165** more including the seeds |

**Basis and novelty.** B's same-order search ended at a fixed point after scanning >2 million parents; exact
rewires, multi-edge edits and higher-edge excursions from those parents had returned no more keys. Here the
change is the **host order and source family**, not the swap rule. G's earlier 34→33 thinning is a precedent;
what was not tested is using G's thousands of 33-vertex hosts to enter B's *unreached* 32-vertex components.
This recovered **90.2% of the gap** in seconds of generation. B's direct d7/e58 branch alone projects to 38.6
CPU-h; even a 60-second pilot budget is >2,300× smaller, **not** an equal-coverage runtime comparison. Tail
warning: 52 min-degree-five hosts gave no critical leaves; three order-39 hosts, deleting transversals of all
independent nine-sets and then thinning, gave no additional 108 keys. Don't scan more copies of the same family.

**Payoff (conditional exact arithmetic).** If the last 124 are found **and** all remaining e108 completions are
excluded, G's combined profile model gives nine incremental contradictions relative to 278 (six overlap U88).
`impact.py`, `impact.log`, `floor109.conditional.jsonl`: rational multipliers checked; each of the nine same
models is feasible with 108 substituted for 109. This uses floors 120/97/88 and the existing degree-six bridge
where applicable. Do not subtract nine now; do not add nine and ten. B estimates ~2.3 CPU-h for proof generation
and replay on a complete e108 census, not for acquiring the census.

**Calibration and kill.** From the three `(3,4;8)` hosts the card search recovers exactly the known 7-vertex
6-edge class (`cal7.g6 == ref7.g6`); direct descent also agrees. A useful negative control: all seven
`(3,6;17)` hosts yield only **3/5** of the known 16-vertex 32-edge classes. This falsifies the tempting cover
theorem. Stop a proposed new source pool if two dispersed batches of 256 yield no new component after exchange.
Never replace GR's count by convergence or by a prediction for the last 124.

**B, with G supplying different hosts — first three steps.** (1) Run `audit_handoff.sh` from this scratch dir
under the usual limits; it checks the exact hash, B's validator, disjointness, Traces and explicit deletion
witnesses. (2) Try 256 previously unsampled hosts from each of two *different* critical/higher-edge 33-host
families; compare *post*-exchange gain to 1,756 criticals, and measure CPU per new component. (3) At exactly
1,880 distinct criticals plus the reducible set, audit the whole union and run the pinned proof pipeline.
Short of that count, preserve the delta; do not launch a purported floor proof.

## 2. Join the two degree-six signatures first; let a failed matching force an interior edge

**Block.** Nine of G's twenty e168 keys have two degree-six vertices. Use A's `ADJACENT_DEG6.md`, not just an
e120 edge cap: adjacent roots u,v have five private neighbours on each side, A and B, with exactly one cross
edge `a*b*`. The other 28 vertices X have 84 edges. Relative to *each* side X has four singletons per label
and eight distinct doubletons (K5 minus two pairs). A one-sided half SAT pilot capped on every endpoint role.

**Mechanism (proved).** Before choosing *any* of the 84 edges, pair the two lists of 28 signatures. Each x gets
a support `S(x) ⊆ A∪B`. No support may contain both cross endpoints; every other `(a,b)` needs a joint occurrence
by MTF: no root or boundary vertex can be their common neighbour. If supports intersect, xy is a forbidden
edge. For either independent nine-set `I=(A∪B)−{a*}` or `(A∪B)−{b*}`, take a clique Q of these forbidden pairs
(an independent set in the unknown X). Its members **must have distinct representatives in I** from their
supports. Proof: the bipartite graph induced on `Q∪I` has independent number `|Q|+9−ν` by König's theorem;
without a matching saturating Q this is at least ten. Testing maximal Q suffices by restriction.

**Force, don't merely reject.** For an undecided pair xy, temporarily forbid it. Test maximal forbidden cliques
containing x,y. A Hall violation now **forces xy to be present**. Two forced edges at z forbid their third triangle
edge. Iterate, including the degree bounds `7−|S(x)| ≤ d_X(x) ≤ 9−|S(x)|` (u,v are the only degree-sixes)
and `e(X)=84`. The induction is sound: at each step a contradiction to forbidding an edge occurs already in
the relaxation. A trace can give Q and its Hall-deficient subset for each forced edge; no SAT oracle is needed.

**Measured, not a proof.** `overlay.cc`, `overlay2.log`: one million random list bijections per unordered pair
of the three marked endpoint roles (missing pairs: path/centre, path/leaf, matching/incident). Out of **6M**,
**88,270** passed cross-edge/MTF coverage; **1,543** survived the ten individual column Hall tests; just **46**
survived all forced-independent cliques; **zero of the 46** survived propagation. 1.83 user CPU-s. Thus
1,919× fewer of the MTF-compatible *sampled* overlays even before propagation. These are labelled samples,
not isomorphism classes or a runtime forecast. Even factoring out permutations within all ten private
four-sets leaves at least `28!/(4!)^10 ≈ 4.8×10^15` raw tables before marked-label symmetries or feasibility
tests: an end-of-table check alone will not do. The falsifiable bet is that partial tables fail early.

**New vs G/A.** The previous forest matching pins join private cells within *one* signature system; the
signature LP optimizes edge counts; the marked-half SAT omits the opposite system. Here the 9-by-Q tests
arise only after overlaying **both** systems, and yield interior edge literals, not just counts or a Hall cut
on a fixed bipartite kernel. This does not address the eleven single-root keys or give a global e120 floor.

**Calibration and next steps (G + A).** (1) `overlay2.cal13`, `overlay2.cal22`: the general matching/forcing
rule retains every oriented-as-stored edge of C13 (26) and every edge of all 191 order-22 graphs (12,127);
every inferred edge/nonedge was checked against the actual graph. General rule uses `|Q|−ν ≤ α−|I|`.
(2) Enumerate **integer tables** `n_ST` with the two signature multiplicity margins, not 28! permutations;
fix the two marked shapes, canonicalize row/column label symmetries, and apply Hall as soon as each group
is filled. Pilot a complete *prefix* on C13 against brute force, including orbit sizes and an omitted-row
test. (3) Log prefix counts and CPU, then replay branch/force witnesses independently. Kill the route if
the estimated exact traversal exceeds 10 CPU-h per shape pair or if a complete small overlay is lost.
**Plausible** order-of-magnitude improvement in leaf work; feasibility of enumerating all prefixes is open.

## 3. For critical e88 only: join four root views; enumerate edges only between complementary cells

**Block and precise limit.** B-007 gives at least four good d6/e52 or d7/e44 roots in the uncovered residue H
outside the prefix and e43. It does **not** say they are independent. Start with the subcase having an
independent four-set R of good roots. This attacks a part of all ten U88 keys, not ten exclusions. Neither
independence nor a high prefix pass rate is a permissible cover assumption.

**Mechanism (proved).** Mark the other three roots in each `H−N[r]`, and align the four cards by induced-graph
isomorphisms on every overlap, allowing every consistent identification. Outside R, group vertices by
`S(x)=N_H(x)∩R`. The cell with S=R is **invisible**: explicitly create it, using order and root degrees, rather
than assuming it empty. If `S(x)∩S(y)≠∅`, xy is forbidden. If some r is outside their union, a card gives
xy exactly. Thus the **only** unresolved pairs have complementary signatures, including `∅` against `R`.
Enumerate only those bits, with degree and 88-edge budgets. For a *mandatory* edge xy, even deleting it in
the graph with all unresolved bits zero must permit an independent nine-set if a critical completion exists.
Otherwise reject the **whole** joined record. For an optional edge apply the same witness test with x,y
required (equivalently, seek seven independent common non-neighbours other than x,y); failure forbids that bit.
Monotonicity of independence under adding edges proves both tests; final leaves still need all checks.

**Measured feasibility and negative control.** `fourviews.py`, `viewcritical.py`: all 183,053 independent
four-root markings in the 191 known order-22 graphs obeyed the partition; best marking per graph had median
two unknown bits, maximum four. On B's 162 order-30 e88 positive inner graphs from the fixed e52 control
(not the unknown outside-prefix population), 94 had an independent good four-set. For 598 such markings the
median was **7** unresolved bits, maximum 24; the mandatory-edge test dismissed 449/598 whole records before
completion. It retained all 234 marked records tested on independently identified critical e88 inputs, and
all 39 C13 four-root controls. The 68/162 without a suitable marking illustrate the coverage problem.

**Why not two cards?** `matekeys.py`, `mate.log`: two disjoint 1,024-input samples per level; 55,558 matching
marked `(6,6)` common-window record pairs even after overlap-size and tight-edge-budget tests. Scaling by
`(10,326,716/1,024)^2` predicts order **10¹²–10¹³** candidate record pairs before alignments. **Kill the
materialized two-card join.** Four cards are useful only if triple overlaps are compared *before* materializing
that relation. Unlike B's per-core `gluegroup` or the generic Sec. 8 pair gluing, the four views determine
almost every edge *after* identification; a fast projection is the unvalidated part, not the final ≤88 scan.

**B — first three steps.** (1) Index marked independent triples inside a dispersed slice of each source level;
also index triple-overlap cards with the fourth root and the visible signature colours. (2) Multiway join on
these smaller marked keys, retaining all simultaneous identifications; compare against direct exhaustive
marked reconstruction on the order-22 family. Require exact equality including multiplicities before any
large run. (3) Estimate *total* key production, joins, permutations and residual bit search, not bit count
alone. Against B's ~893 CPU-h baseline, stop unless the covered slice projects below ~9 CPU-h at comparable
scope; keep the no-independent-good-four-set branch separate. **Speculative** 100× target, not achieved.

### Five-line summary
1. B: `scratch/ideas/astra_N/handoff.g6` adds 1,142 verified critical e108 inputs; 124 remain missing.
2. Proving degree-seven floor 109 would cut nine of 278 distributions in the tested model; six overlap U88.
3. G/A: the two-sided Hall rule plus edge forcing rejected all six million sampled joins across the nine two-root e168 keys; exact orbit traversal is untested.
4. B: four independent good roots leave a median seven undecided bits on marked e88 controls; two-card materialization is not viable.
5. No new floor, closed order-40 case, or Ramsey-number verdict is claimed.
