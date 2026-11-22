# Round 9: rounded incidence bounds and matched six-set join

Scope throughout: `R(6)`, a whole codegree-six P3 component with
diagonal four and arm counts 8/8. The hand arguments and audit bridge
are in `proofs/p3_rounded_incidence.md`. No case or residue row closes.

## Exact incidence bounds — hand + enum, pending critic

The round-8 freeze passed, and a full regeneration produces byte-equal
90 two-layout bindings and all 420 residue rows (90 excluded and 330
live). The independent integer replay uses only the supported row
names: degree, avoid, and tagged avoid. Explicit mask enumeration and
the forced adjacency test cover the nine layouts and all 105 compatible
zero multisets with q at most two; no triple of zero masks is compatible.
The audit checks the original 34 contradictions and all 71 new bounds.
It rejects a scale corruption. It does not call the LP, use its objective,
or import the production mask or row construction.

Let `S` be the singleton count, `q` the number missing all four common
columns, and `U,V` the numbers meeting three and four. Exactly
`S+2q=20+U+2V`. On 47 surviving zero patterns `U=V=0`; on the other
24 `V=0, U<=1`. Thus no quadruple and at most one triple in any still
open pattern. The unique-zero named layouts `1:0:1:1:1` (e62) and
`3:0:1:2:1` (e63) separately give `3S<=56` and `3S<=55`: each has
exactly 18 singles and three doubles. The expanded per-tag witnesses
give combined avoider-deficit plus mask-margin budgets 2 and 1,
respectively. Only the first layout was run through the joins below.

```sh
cd scratch/C/r9
ulimit -v 16777216
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
py=../../../opt/venv/bin/python
lane=../../../ralph/lanes/C
census=../../../gluing/val/r3_7_22.g6
nice -n 5 timeout 80 "$py" -B "$lane/p3_zero_residue.py" "$census" ../r8/zero-all.json replay-residue.tsv
cmp replay-residue.tsv ../r8/zero-residue-bindings.tsv
nice -n 5 timeout 45 "$py" -B "$lane/p3_singleton_cover.py" "$census" replay-singleton.tsv --verify ../r8/capacity.json --tagged
cmp replay-singleton.tsv ../r8/singleton-bindings.tsv
nice -n 5 timeout 80 "$py" -B "$lane/p3_round_upper.py" verify excess.json
nice -n 5 timeout 35 "$py" -B "$lane/p3_upper_audit.py" ../r8/zero-all.json excess.json
nice -n 5 timeout 35 "$py" -B "$lane/p3_common_cover.py" verify rounded.json
```

## Private-wing projections — enum / estimate

Treat all three columns of each private wing jointly, conditioning on
the exact zero mask `{0,4,14}` and its position. In a wing triple the
same choice of each column is used in its two pair tests; all three
must lie in the image of a common allowed row mask at each row. The
indexed variant additionally forbids a pair missing the same independent
six-set. Two different wings are tested as separate necessary joins;
survival is not a lift through both wings or a SAT result. The planted
C21 attachment passes with its two exact zero masks; the impossible
mutation fails. A separate seeded three-column arithmetic comparison
checks both branches against direct enumeration (371 passes, 541 exact
six-set rejections across its small samples).

| Bound rows | Zero positions | Baseline wing tuples | Indexed wing tuples | Baseline / index CPU-s | Both wings survive |
|---|---:|---:|---:|---:|---:|
| Six scout rows | 84 | 7,247,933,808 | 254,424 | 77.604 / 28.901 | 84 / 84 |
| 24 held-out rows | 336 | 28,720,249,242 | 971,463 | 320.175 / 115.566 | 336 / 336 |

The sums count partial tuples across the two wings, not full join keys.
Held-out CPU is 2.77x faster inside the timed traversal (2.75x total
process CPU including control setup). Comparison binds every placement
key and confirms monotonicity. No placement or layout/residue exclusion;
do not scale this as a stand-alone approach.

```sh
nice -n 5 timeout 40 "$py" -B "$lane/p3_six_join.py" control
for sample in scout heldout; do
  for mode in base index; do
    nice -n 5 timeout 600 "$py" -B "$lane/p3_six_join.py" "$mode" "$sample" "replay-$mode-$sample.tsv"
    cmp "replay-$mode-$sample.tsv" "$mode-$sample.tsv"
  done
done
```

## Common-column join, tag DP and SAT pilot — enum / estimate / open

The four sorted independent six-set columns cover exactly X minus the
known zero position with no triple incidences. An exhaustive arithmetic
control on C21 residue independent sets includes both actual common
columns and two planted subcolumns; the impossible double requirement
is rejected. On the same six e62 scout rows the cover produces 455,546
unordered four-column choices for 84 positions (21.964 traversal CPU-s).
The budget-aware per-tag DP retains 300,018 choices (23.733 CPU-s
including cover enumeration), with exact equality of baseline counts
per position. Small DP/direct controls give 37 finite and 83 impossible
tests. Every position remains open; these counts do not justify a batch.

Row 17 only was attempted with CaDiCaL LRAT producing, matched on
the same e62 layout: the `pin` formula adds the unique-zero option
and `tight` also adds h<=2 and the weighted deficit limit. Both
exited 137 at the 45 CPU-s hard limit under a 75-s wall wrapper.
No verdict; partial LRATs deleted. The halt is **CPU-cap kill**, not
an UNSAT, SAT, or a wall TIMEOUT. C21 pin control accepts the true
q=2 and rejects q=1; weighted-deficit control accepts the measured
budget and rejects budget minus one. No further row was attempted.

```sh
nice -n 5 timeout 25 "$py" -B "$lane/p3_common_cover.py" control
nice -n 5 timeout 110 "$py" -B "$lane/p3_common_cover.py" run rounded.json --layout 1:0:1:1:1 --sample scout --output replay-common.tsv
cmp replay-common.tsv common-scout.tsv
nice -n 5 timeout 120 "$py" -B "$lane/p3_tag_join.py" scout replay-tag.tsv
cmp replay-tag.tsv tag-scout.tsv
nice -n 5 timeout 35 "$py" -B "$lane/p3_tight_sat.py" control
for mode in pin tight; do
  nice -n 5 timeout 45 "$py" -B "$lane/p3_tight_sat.py" "$mode" --row 17 --out replay-tight
  cmp "replay-tight/$mode-17.cnf" "tight/$mode-17.cnf"
done
```
