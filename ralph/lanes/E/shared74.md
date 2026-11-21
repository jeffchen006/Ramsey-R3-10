# Round 7: shared 74-edge windows

## Cut and scope

**Hand + enum + cert, pending critic review.** Exclude the mixed incidence
profile `(10,10,11,11)` **only for the core `W=G?bBro`**, at
`(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, with the same universal
`δ(G)≥5` premise as `m11.md`. This uses all graphs, not an MTF
assumption. It is distinct from the round-6 `G?Beto` proof.

The inherited E-021 count and saturation imply that the four windows
`H_i=F\A_i` must all be copies of the sole missing 74-edge class.
Its identity and degree-seven multiplicity need not be known. The
following necessary compatibility condition gives a reusable filter.

1. Let `S_i` be the vertices of W with exactly one neighbor in `A_i`.
   These are precisely the degree-seven vertices of `H_i` inside W,
   since each W vertex has fixed degree eight. A vertex outside W in
   `H_i` has degree seven iff it misses `A_i`, since its fixed degree
   is seven. For any two such vertices `x,y`, choose an omission other
   than `i` and their group(s). That window contains `A_i,x,y`; if
   `xy` is absent these form an independent eight-set. Thus the extra
   degree-seven vertices form a clique of size at most two, and two
   extras must lie in distinct groups and have disjoint W supports.
2. Let `K` be the common number of degree-seven vertices. A size-ten
   group has six singleton W rows, so `6≤K≤8`. A size-eleven group
   can have either five or six singletons. In particular, **do not
   drop `K=8`**: it requires six singleton rows in both size-eleven
   groups, and 268 of the 36,612 tested lifts have this row pattern.
3. For an isomorphism `H_i→H_j`, at least `|S_i|+|S_j|−K` vertices
   of `S_i` map to `S_j`. On subsets of that size, the rooted graph
   and the multiset of all exterior adjacency masks into those roots
   are exact from the W/support pins. They must agree under a root
   mapping. Moreover the entire induced degree-seven graph must
   agree under the same mapping: enumerate the 0/1/2 extra vertices
   in each window, preserve their root adjacency masks, and compare
   the edges between the remaining degree-seven vertices. These edges
   are specified by W, the W supports and the forced edge between two
   extras. The pair tests allow different extra assignments for
   different comparisons, a relaxation; only failure is decisive.

`shared74.py` implements an invariant screen and then canonical exact
small rooted pattern comparison. `replay_shared74.py` instead checks
explicit root permutations and support multisets. The rooted tests
pass 520 translated positive C13(1,5) deletion-card pairs (468 with
nonempty forced root overlap), and reject 520 planted one-bit changes.
Inherited exact support/graph/SAT controls are documented in `m11.md`;
the graph and SAT controls were rerun in this round.

## Measured cover

| Stage | Terminal count |
|---|---:|
| Projected exact support orbits with viable omitted group | 7,046 |
| All full support orbits (lifts) | 36,612 |
| 4,879 projection graph witnesses | 23,294 lifts |
| Lift incompatibility, all applicable K checked | 12,939 |
| Other single-window graph witnesses | 322 |
| Checked native LRAT on the four-window CNF | 57 |

`bind_shared74.py` independently iterates normalized full support
quadruples (44 size-ten and 542 size-eleven supports, 8 core
automorphisms), compares all projected and lifted identities, then
regenerates every residual DIMACS and rechecks its LRAT. The receipt
replay checks every graph witness and incompatibility. All 57 SAT
instances were UNSAT with checked proofs; no cap, open lift, or missing
receipt. The LRATs need not encode the compatibility filter: they
refute a superset of the lifts with the four anchored windows, exact
attachment degrees and the width-8 subset of alpha clauses.

On the matched complete cover, graph propagation alone leaves **785**
lifts (10.55 CPU-s). Isomorphism-first leaves **57** (71.32 CPU-s);
**graph-first** leaves exactly the same 57 IDs in **16.28 CPU-s**, a
13.8× proof-queue reduction against graph propagation alone. The
three selected proof pilots checked; full production was about
86 CPU-s (including proof checks) and fresh CNF/LRAT replay 36 CPU-s.
The final census, production and independent replays used ~0.07
core-hours, excluding matched pilots and exploratory runs.

Matched 120-row samples from the old core 9 and core 18 covers tested
987 and 774 full supports, respectively. Compatibility alone leaves
35 and 8; these are samples, not exclusions. The eight-degree-seven
option survives in two core-9 sample lifts (both also allow K=7).
The reverse catalogue is still 1,624/1,625. No catalogue expansion,
unmodified capped scan, or proof replay of the other cores was run.

## Reproduction and boundaries

From `scratch/E/r7_shared` under `limited.sh`, use:

```sh
sha256sum -c freeze.3.sha256
L=../../../ralph/lanes/E
python3 -B "$L/bind_shared74.py" cover.3.jsonl --key 'G?bBro'
python3 -B "$L/replay_shared74.py" cover.3.jsonl scan.3.final.jsonl
python3 -B "$L/bind_shared74.py" cover.3.jsonl --trace scan.3.final.jsonl --proofs proof.3
```

For a new core, regenerate the mixed support cover using
`m11_support.py census ../r5_saturated/e11.g6 COVER --core ID --profile 1`,
then use `shared74_scan.py COVER TRACE --graph-first`. The residual
plan is the `(projection index, lift index)` pair of each `open`
record, in trace order. `prove_shared74.sh COVER PLAN PROOFDIR OFFSET
STRIDE` settles that plan, followed by receipt and fresh-CNF replay.

Logs: `bind.cover.3.log`, `replay.3.final.log`, `bind.proof.3.log`,
`scan.3.graphfirst.log`, `scan.3.unfiltered.log`, `marked.final.pilot.log`
and `prior.freeze.log`. Prior core 0 and profile A rehash unchanged;
no changes to f=28 or the e12 bundle. Remaining: 17 mixed cores,
m9/m10 and the relevant m8 branches, and f=32 outside the crown scope.
This result is not an entire degree-distribution or fixed-point case
exclusion.
