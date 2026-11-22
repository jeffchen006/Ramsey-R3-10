# Lane E, round 22 — 2026-11-22 CET

## Mixed 11-edge core closure (hand + enum + cert; pending critic)

Scope: `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, universal
`δ(G)≥5`, mixed incidence profile `(10,10,11,11)`, and the inherited
all-graph E-021 necessary condition that all four order-26/e74 windows
are isomorphic to the sole class missing from the 1,624-class list.
All four omitted-window roles and `K=6,7,8`; no MTF assumption.

| Zero-based core | First branches (empty) | Shards | Projections | Lifts | Projected graph deaths (lifts) | Other graph deaths | Fusion deaths | Marked deaths | Checked LRATs | Open |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 6 `G?bav_` | 70 (1) | 254 | 296,087 | 2,527,837 | 1,518,045 | 888,610 | 112,226 | 8,679 | 277 | 0 |
| 9 ``G?q`v_`` | 37 (1) | 179 | 192,113 | 1,909,123 | 1,235,134 | 591,697 | 74,524 | 7,138 | 630 | 0 |
| 18 ``GCpb`o`` | 50 (1) | 156 | 189,014 | 1,342,418 | 704,367 | 525,579 | 103,501 | 8,716 | 255 | 0 |
| Total | 157 (3) | 589 | 677,214 | 5,779,378 | 3,457,546 | 2,005,886 | 290,251 | 24,533 | 1,162 | 0 |

Independent support generators agreed byte-for-byte on each source.
The half-open byte, projection and cumulative lift intervals reconcile
to each full parent; each shard lies within one first branch and its
rows bind to both source generators. All obstruction receipts passed
the unchanged Python replay with explicit omitted ordinal (or a
projection-wide receipt). The check distinguishes a skipped shard
from an open terminal. Each terminal width-three CNF was generated from
the physical support, compared with an independent reconstruction, and
checked as a clause subset of the regenerated width-eight reference.
No target fallback, SAT, proof cap or missing receipt. Both LRAT
checkers passed at production. `audit.*.final` independently bound
all 1,162 physical IDs to archived proof digests and marker logs;
fresh CNF regeneration and a second dual check of all 1,162, split
across 25 disjoint replay subsets, matched those precise digests.
No extra proof debit for the pilots or the earlier snapshot rechecks.

Combined 19/19 mixed-core map (zero-based `r5_saturated/e11.g6`):

| Core | Disposition |
|---|---|
| 0,1,2,3,4 | E-020, E-046, E-023, E-022, E-024 respectively |
| 5,6,7,8,9 | E-036, R22, E-029, E-038, R22 respectively |
| 10,11,12,13,14 | E-027, E-028, E-025, E-030, E-026 respectively |
| 15,16,17,18 | E-041, E-032, E-034, R22 respectively |

E-018 gives exactly two 11-edge profiles. Combine the above mixed
coverage with **E-019**, which excludes `(10,10,10,12)`, to close
**only** the whole `t=4, δ(W)≥2, e(W)=11` stratum of `(2,32)`.
E-021 is used only on the mixed side. No whole involution exclusion,
MTF-distribution debit or candidate graph.

### Pricing, staging, and replay

| Core | Sampled rows / lifts | Terminals / both-width pairs | Planning CPU-s | Incremental archive plan | Actual production CPU-s |
|---|---:|---:|---:|---:|---:|
| 6 | 1,656 / 12,795 | 4 / 2 | 21,912 | 419 MB | 2,648.08 |
| 9 | 864 / 8,830 | 5 / 4 | 76,354 | 1,191 MB | 1,997.46 |
| 18 | 1,176 / 8,955 | 11 / 8 | 19,045 | 202 MB | 1,734.80 |

Every nonempty first branch contributed front, interior and tail
samples. Branch-max estimates charge both proof routes at 3× the
maximum sampled combined time and maximum retained proof size; no
tail guarantee. Every pilot reran smaller six-site positive/fallback
and negative controls, native-vs-Python small exhaustive controls,
wrong degree / wrong physical lift, wrong core, and another valid
omitted ordinal. The audit rejected four order/coverage mutations.
Per active job: 1 GiB VM, finite wall and CPU, 40 MiB scan and 80 MiB
proof live leases, and a 2.85 GB per-core envelope. Both checkers ran
sequentially under the worker slot. The 25-way fresh replay took
911.64 CPU-s, on top of production.

The first 22 core-6 wrappers were operator-terminated after the
filesystem refused cross-directory renames (`EXDEV`); no shard or
proof accepted from that attempt. Restarted only after putting all
outputs in place and validating a 12,000-lift shard. One later
core-9 wrapper exited before claiming a shard on a concurrently
deleted temporary file during quota accounting; the manifest had no
gap and the scanner now tolerates disappeared temps. These are not
solver caps or UNSAT evidence. Exact hook cutoffs and inspection are
recorded in `jobs.tsv`, `exits.tsv`, and `reconcile.log`.

All evidence under `scratch/E/r22_shared/`. Check `freeze.sha256`
from that directory. `core.CORE/{parent.json,branches.jsonl,shards.jsonl}`
bind each parent and shard; `core.CORE/shards/` has gzip receipts,
terminal ledgers and compressed LRATs. The CNFs are regenerated from
the preserved cover and independently bound. `audit.CORE.final/`
gives exact accepted and empty residual/unfinished ledgers.
`recheck.CORE.OFFSET.log` preserves each independent proof check.

## 8-edge core: deficit-two branch excluded (hand + enum)

Scope still `(p,f,t)=(2,32,4)`, `δ(W)≥2`, all graphs and universal
`δ(G)≥5`; now `e(W)=8`, attachment degree deficit `P=2`.
Use E-018's underlying degree-saturation argument (`window73.md`) and
the independently published complete order-26/e73 class count (62;
locally bound to the same distinct checked catalogue). It gives
`d_F(w)=8` for `w∈W`. The 24 attachment vertices have fixed-degree
deficits summing to two from degree seven. Thus `e(F)=115`, and
`e(H_i)=73+P_i` for `H_i=F\A_i`, `P_i` the deficit in `A_i`.

Write `b_i=e(W,A_i)`. Each W row hits every group. At most six rows
can be singletons in any group: distinct singleton rows sharing their
only neighbor would be nonadjacent (triangle freedom) and produce an
independent seven in `W∪A_i`. That set can add three independent moved
vertices, on the crown side with the index `i` omitted. It follows
that `b_i≥10` and, more generally, `α(W∪A_i)≤6`. Also `Σ b_i=48`.
At least two `P_i` vanish. Each associated 73-edge card has at most
two d7 vertices; degree-seven W vertices are exactly singleton rows
of the omitted group, so `b_i≥14` for these omissions. The entire
incidence budget is used: `(b_i)=(10,10,14,14)` and `(P_i)=(1,1,0,0)`.
Each b14 group has exactly two singles and six doubles (its surplus
above one-per-row is six). Each b10 group has six singles and two
doubles. In either 73-edge card `W` contains exactly the two d7 sites
and six d6 sites. Since `δ(W)≥2` and `e(W)=8`, `W` is an induced
`C8` or `2C4`. Its other 18 vertices must split into three independent
six-sets with the retained incidence totals `(10,10,14)` and with
`α(W∪A)≤6` in each group.

Complete enumeration with **two** methods (degree-filtered subset
enumeration vs induced cycles; independent-set mask join vs literal
partition enumeration) agrees on all 62 cards. Among 31 eligible
cards, 93,093 six-subsets give 67 actual W masks on 25 cards. There
are **zero** retained `(10,10,14)` partitions. An additional retained
large-group contact test was not needed. The smaller controls use
planted `C8`, `2C4`, a forced isolate, and a positive/one-edge-deleted
marked partition. A seven-card pilot took 1.14 CPU-s; full exact run
took 3.35 CPU-s. See `deficit73.{pilot,final}.log` and the empty
`deficit73.final.jsonl`. No E-021 hypothesis for this exclusion.

## 8-edge core: saturated branch has at least two missing cards (hand + enum filter)

Same scope at `e(W)=8`, **`P=0`**. All four deletion cards are now
26/e74; all `b_i≥10` and sum to 48. A group with `b_i≤11` produces
at least five singleton W rows, hence an E-021 missing card. For
`b_i=12`, a card in the known 1,624-class catalogue has at most four
d7 vertices. It must have exactly four d7 sites (all in W) and four
d6 W sites: at least four singles are forced, and equality accounts
for the four doubles. This does **not** assume the other three cards
are known or that their support totals are 12.

Of the 160 known cards with four d7 sites, 79,200 four-subsets leave
six induced-cycle W masks on six cards. Neither the all-twelve
partition test nor the broader one that permits **any** support
totals for the three retained groups found a partition. The broader
test requires only independent six-sets `A` with `α(W∪A)≤6` and uses
the same two independent partition checks. Both matched the smaller
positive/one-edge-deleted controls. Runtimes 1.00 and 1.68 CPU-s.
Consequently every `b_i≤12` induces the missing class. At least two
`b_i` are ≤12 since `3·13+10>48`. In `(12,12,12,12)` all four
cards must be missing. This is **not** a closure of `P=0`, nor a
claim about the missing class's identity. See `known74.{pilot,final,relaxed}.log`.

## Next queue

All round-22 finite work completed. Do not replay the 19 mixed cores
for new credit. The saturated `e(W)=8` case can now split by the
number of forced missing windows (`b_i≤12`) and reuse rooted
compatibility only on these roles. For `m=9,10` retain all profiles;
test a cheap projection-first pilot for the `(10,10,10,14)`
10-edge profile or a deck join before authorizing a full support
census. Involutions with `δ(W)<2`, other `t` or `f`, and other
prime-order cases remain unaffected. No new priced unresolved
production queue at handoff.
