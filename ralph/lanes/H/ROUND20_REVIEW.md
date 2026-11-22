# Round 20 — lower matching interface and ledger

## H-035 (Lean, pending critic)

`lean/R310/PrivateMatching.lean` formalizes a partial matching in an
explicit `SimpleGraph`. Its two shores are independent and disjoint;
a third disjoint set has no edges to either shore or itself. An
independence cap `cap` applies to their union. For any subset `S` of the
left shore, `S ∪ (right \ N(S)) ∪ isolated` is independent, so
`|S| ≤ |N(S)| + (|left|−lower)` when `cap+lower ≤ total`. Introduce
exactly `|left|−lower` fresh dummy targets using a sum type and apply
pinned Mathlib's `Finset.all_card_le_biUnion_card_iff_existsInjective'`.
Discard the dummy assignments: enough real assignments remain and the
partner map sends distinct physical sites to distinct actual neighbours.

For disjoint four-site cells and cap five, the theorem yields a
matching of size at least three off-cross; the isolated double site
raises this to four at the cross. `private_grid_row_bound_of_indep`
feeds the constructed matching into H-034 to obtain
`s−t ≤ 1−[row=crossRow]`, with columns by transposing the graph inputs.
No matching size is a premise of this composed theorem. The graph
application still supplies the disjoint cells, cross-site isolation,
local independence cap (from the four other anchors in G's proof),
and the correspondence of singleton supports to boundary contacts.
It does not certify a signature/board enumeration, a SAT binding, or
an exclusion. It formalizes the missing local inference in G-043 and
H-034 rather than redoing their cases.

The independent Python control enumerates 170 small physical graphs
on shores of size `(0,2)`, `(1,2)`, `(2,2)`, `(2,3)` with/without one
isolated site, using independent-set subset enumeration and separate
injective partial-assignment enumeration. The two-site and four-site
tight examples are attained. Adding one isolated site to the `4+4`
size-three matching raises alpha from five to six, so the false
size-four conclusion fails its cap premise. An adverse three-anchor
example counts only two real matches because its double-supported
site cannot be reused. Controls are not target covers.

Replay (Lean and Mathlib 4.35.0; pre-existing binary cache):

```sh
python3 -SB ralph/lanes/H/check_private_matching.py
bash ralph/lanes/H/build_private_signature.sh --old build R310
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 -DElab.async=false ../ralph/lanes/H/AxiomsRound20.lean
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 -DElab.async=false scripts/Axioms.lean
sha256sum -c ralph/lanes/H/ROUND20.sha256
```

The single pinned worker built the new module and `R310`, not Mathlib
from source. Strict verification: 3 targeted and 359 project reports,
only `propext`, `Classical.choice`, `Quot.sound`. Total measured
wrapper time including the first failed elaboration, controls, build,
both suites and version: 79.05 CPU-s (0.02196 core-h), peak 3,449,500 KiB.
No solver or detached job, no new literature screen per directive.

## Round 19 import and round 20 scope

`ralph/critic/round_019.md` confirms C-045/046/047 separately: the
deletion shortcut is hand, the fifth-row gate cuts 0/578 rows, and the
unchanged independently replayed signed join supplies the 12 fresh
exclusions. The remaining both-positive balances are 2,542,514,364
explicitly signed-untested and 2,542,514,308 neither signed-tested nor
vetoed; R's 56 structural vetoes remain distinct. A's physical index
and held-out flags are not the signed exclusion. F counted unsigned
choices, E-043's sixteen proofs were inherited, and D-046 counted
necessary marked assignments, not graphs. H-034 remains the
conditional capacity implication. The failed round-19 referee turn
left a report with no mathematical GAP; the D=7 check had 0/220
survivors (all rejected). Its sampled G-019 inner checks do not prove
the complete inner cover.

G-055's 57,947 fresh labels leave 21,125 checked-ledger outstanding
`h=8` ranks. G-056 now reports a single local receipt for all 21,125,
pending critic; 58,929 of 80,054 in scope overlap old receipts. If
accepted, the marked aligned `h=8` slice is closed, not the equality
case or a distribution. `h=7` remains at 51/1,213 two-sided contexts.
The transferable fixed-shape certificates have the strongest measured
cost reduction; E's exact 115 residual is a separate, sized next
target if accepted. Checked global balance remains 238 near-regular
MTF distributions plus R, ten conditional U88 keys, four conditional
mixed cores. The flow has verified no graph.
