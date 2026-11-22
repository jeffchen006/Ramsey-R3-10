# No global maximum path of six vertices in R(3) — hand + enum

Submitted for critic/H review. R(3) is the 9-regular order-40 branch with
maximum nonedge codegree 3. `L` counts **vertices** in a longest simple path
in any edge kernel, not edges. This result does not close R(3).

## Premise order

1. D-015 gives an induced P6 somewhere and every C6 component reroots to a
   P7. In particular, in this paragraph only, assume global `L=6`.
2. The earlier graph-first census and the first **18** frozen row refutations
   reduce the P6 profile list to `2298,2386,2424,2431`.
3. Only now is the high-hole lemma available: the nineteenth refutation
   eliminates `2386`. D-016 and `PATH_ROOT.md` document this dependency.
4. At any induced P6 in this stratum, the order-eight full-star profile
   must therefore appear in the **three**-profile library, up to the two
   orientations. No starting panel or maximum-square root is necessary.

## Matched attachment pilot

For a decorated original edge, complete the two 9-neighbor star decks on the
**same** 22 exterior attachment rows. Any triple link path in a short star
obeys the no-triangle/no-P4 restrictions. Two intersecting link edges and
an exact double at one end exhibit a six-vertex path; its four same-side
points have six codegrees from an oriented library profile. Coupled clauses
involve distinct exterior witnesses for the two triples and double. No
reordering of fixed panel labels. All 48 C22 component marks pass and a false
library fails. Weak/joint comparison on the three surviving roots:

| root / panel | weaker | joint | solver CPU-s (weak / joint) |
|---|---|---|---:|
| 2298 / 5 | SAT projection | SAT projection | 0.46 / 2.66 |
| 2424 / 0 | SAT projection | SAT projection | 2.38 / 3.11 |
| 2431 / 6 | SAT projection | SAT projection | 0.65 / 6.12 |

Exact eight-star CNFs at simultaneous fixed and one-extra-edge reroots also
pass the 48 controls (827 windows, 404 planted active). All three degree-only
instances SAT; all three degree+triangle+codegree instances CPU-capped at
30 s. These six runs are not used for any exclusion.

## Exact star graft

Maintain **complete** adjacency rows of a frozen ordered set `S`, initially
the eight anchors. No other edges are pinned irreversibly. The residual
vertices with the same `S` mask form a cell; their permutations fix all
earlier rows. When fixing a new pivot `p`, exclude `p` itself from its cell.
Its neighbors in each remaining cell can be represented by an initial
segment of that cell. This is a cover: inductively relabel a completion by
permuting within the current cells, fixing `S` and `p` pointwise. It does
not assume an automorphism of the completed graph. **No fixed panel** is
retained in this tree; the decorated pilots never feed it.

If seven anchors of another forced P6 already lie in `S`, let `p` be the
eighth. Its row, together with the seven frozen stars, must realize one
oriented library key. In each of the seven-bit cells (on vertices outside
that P6), the key specifies exactly how many also see `p`. The search
allocates these totals among the finer `S`-mask cells, respecting fixed
adjacencies, and intersects the options from every such occurrence **for the
same pivot on the same labelled row**. If all eight are fixed, just look up
the full profile. If no seven-star window exists, branch on a free row with
degree nine, cap-three, and domination to each frozen anchor. Choices for
this pivot still use only the current pointwise stabilizer.

Finite-obstruction leaves: a pair with four common neighbors; an actual
seven-vertex kernel path; two forced nonneighbors without any possible
common neighbor; ten vertices independent even in the *upper* graph; or
an infeasible row/full marginal. The upper graph excludes, in particular,
edges intersecting a frozen neighborhood mask, and all unchosen edges at a
saturated vertex. These are necessary restrictions in a triangle-free
regular graph. No full-depth completion, depth cap, time cap or unexpanded
leaf occurred in the final trees. `2431` needs no arbitrary free row;
`2298` and `2424` each reduce to one ten-star state before their first free
choice. The two trees were nevertheless searched separately, both using
all three keys (no circular dependency).

| root | total nodes | branches | terminal leaves | independent row-CNF obligations | dual-checked bundles |
|---:|---:|---:|---:|---:|---:|
| 2298 | 5,347 | 652 | 4,695 | 1,204 | 51 |
| 2424 | 5,438 | 650 | 4,788 | 1,191 | 50 |
| 2431 | 379 | 36 | 343 | 76 | 4 |

## Independent check and reproducibility

`star_graft.py` is the producer; its transported positive controls reach all
22 stars for **48/48 physical marks**. `graft_audit.py` does not import the
producer, its row generator, its core finder, or its validator. It reconstructs
the pinned graph from explicit edges, traverses the submitted tries, finds
simple path/independent-set witnesses by separate algorithms, and emits
fresh labelled SAT obligations using PySAT sequential counters. An internal
node asks whether there exists a canonical necessary pivot row *different
from every recorded child*. A marginal leaf asks whether such a row exists
at all (or provides an already frozen bad eight-star pattern). `--mutate`
deletes a real child and is rejected with a satisfying missing row. All
672 actual C22 canonical rows pass the checker construction.

Every block CNF is a disjunction of at most 24 independent row obligations,
with private variable ranges: a selected disjunct must satisfy its entire
formula. CaDiCaL produced native text LRAT, verified by both `cake_lpr`
and `lrat-check` for **105/105** blocks. `witnesses.jsonl` binds each obligation
or explicit witness to a trie path (zero-based obligation index within each
root; divide by 24 to find its block). Overall reduction, orbit coverage and
source are **hand + enum with checked projected CNFs, not a Section 7 cert**.

From workspace root, set `R=$PWD; cd scratch/D/joint9`. Under the usual
nice/timeout/CPU/RAM limits, use `$R/opt/venv/bin/python -B` for each script:

```
$R/ralph/lanes/D/star_graft.py ../punct8/path.tsv --index 2298 --cutoff 40 --free --out NEW.jsonl
$R/ralph/lanes/D/graft_audit.py ../punct8/path.tsv 2298 NEW.jsonl --out NEW.bundle
bash $R/ralph/lanes/D/graft_proof.sh NEW.bundle/0000.cnf
```

Repeat for each fresh block, for `2424`, and for `2431` without `--free`.
Frozen tries: `free-{2298,2424}.jsonl`, `deep-2431.jsonl`. The independent
graft argument proves no `L=6`, conditional on the earlier cover. Thus any
remaining R(3) graph has an induced P7: a simple seven-vertex path in a
bipartite degree-two kernel cannot have an endpoint chord (the ends are on
the same side). It need not have global maximum exactly seven.
