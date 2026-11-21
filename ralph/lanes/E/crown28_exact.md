# Certified exclusion of `(p,f,a)=(2,28,4)`

**Claim (`cert`, pending critic review):** No triangle-free graph on 40
vertices with independence number at most 9 has an involution fixing
28 vertices and maximum fixed attachment size 4. This covers all
graphs, not just maximal triangle-free graphs. It does not use the
universal minimum-degree-five certificate. The case `a=6` remains open.

## Reduction and cover

Let `F` be the 28 fixed vertices. There are six moved pairs `O_i`.
Use the six-pair reduction in `involution.md` (the argument also allows
internal pair edges initially). Every pair of moved orbits is joined by
exactly one matching, and the matchings make the two sides of a crown
after switching labels. The sets `A_i=N(O_i)∩F` are disjoint and
independent. Write `W=F\(∪ A_i)`. One crown side is independent and
anticomplete to `W`, so `α(W)≤3`, whence `|W|≤8` by `R(3,4)=9`.
The `A_i` have size at most four, so `|W|≥4`. Their total shortfall
from six size-four sets is `|W|−4`. Thus at least `10−|W|` sets are
full. At `|W|=4` all six have size four, and at `|W|=5` the sizes
are `(3,4,4,4,4,4)`. In those two cases all moved pairs are independent:
each has a fixed neighbor, so an internal edge would make a triangle.

Use these clauses on the fixed side, pinning the induced core `W` and
the internal nonedges of each represented attachment:

1. For `|W|≥6`, represent any `10−|W|` full attachments. For `|W|=4,5`,
   represent all six. For any independent set `S` of represented fixed
   vertices, choose one crown side and delete from it exactly the moved
   vertices whose attachments meet `S`. The combined independent set
   has size `|S|+6−#{i:S∩A_i≠∅}`. Hence any proposed `S` of weight
   `|S|−#{occupied attachments}≥4` needs an edge. The static projection
   needs only weight exactly four with no singleton attachment: delete
   all singleton attachments, then reduce weight one at a time by
   deleting a core vertex or shrinking a group, deleting the resulting
   singleton as needed.
2. For `|W|=4,5`, any independent eight-set in `F\A_i` could add both
   vertices of `O_i`. It therefore needs an edge. The C++ search
   supplies witness masks; Python independently validates the weight
   or eight-set condition and reconstructs the associated clauses. A
   proof uses only the validated clauses, not the search's UNSAT claim.
3. All triangles in the represented fixed graph are forbidden. The
   fixed-degree cap is nine on `W` and seven in the attachments (two
   moved neighbors). With the full fixed side, use the universal
   degree lower bound four in `G`; no degree lower bound is imposed on
   a projection. Prefix counters encode these bounds. For a feasible
   input assignment counters can be set to the actual threshold counts;
   an overflow forces a conflict.

The independent census checker `check_crown_cores.py` verifies the
supplied graph6 rows by exhaustive single-vertex extension of every
preceding representative, starting with the empty graph. The property
is hereditary. Exact permutation orbits check class coverage and
nonduplication; no trust in `geng` or a published class count is needed.

| `|W|` | Core classes | Labelled cores | Verified proofs |
|---:|---:|---:|---:|
| 4 | 6 | 40 | 6 |
| 5 | 9 | 322 | 9 |
| 6 | 15 | 2,812 | 15 |
| 7 | 9 | 13,842 | 9 |
| 8 | 3 | 17,640 | 3 |

## Why the extra W4 pins are sound

For every `x∈W`, `d_{F\A_i}(x)≤7`: its neighborhood is an independent
set in a graph with independence number at most seven. If `d_F(x)=9`,
then `x` has at least two neighbors in each of the six disjoint
attachments, impossible. Thus `d_F(x)≤8`.

Every full size-four `A_i` has a neighbor of every `x∈W`; otherwise
`{x}∪A_i` is an independent fixed set of weight four. For any pair of
distinct vertices `x,y∈W` with exactly one neighbor apiece in `A_i`,
the two neighbors must differ. For adjacent `x,y` a shared neighbor
makes a triangle; for nonadjacent `x,y` a shared neighbor leaves
three vertices of `A_i` that can join `x,y`, again weight four.
Consequently, if exactly four `W–A_i` edges occur, they form a perfect
matching. Call such an attachment clean. The total number of `W–A_i`
edges above the mandatory 24 is at most
`4·8−2e(W)−24=8−2e(W)`. Thus at least `max(0,2e(W)−2)` attachments are
clean. Pin that many first, with their matching fixed by individually
relabelling each attachment. Additional clean groups are allowed.

All lexical reductions are changes of labels: sort the vertices of
each group by their W-neighborhood words, then sort equal-size groups
by the resulting word tuples within each side of the clean/nonpinned
boundary. The pinned perfect matchings already agree with that order.
For `W=C4`, all six groups are pinned clean; keep the first arbitrary
and sort groups 2–6 by their 4-by-4 edge blocks into that first group.
No independent global choice of W labelling is needed. All resulting
orderings satisfy the prefix-lex CNF by setting each prefix flag to
the actual prefix equality.

## Calibration and replay

`calibrate_crown_exact.py` and `crown_static.py --control` matched
explicit triangle and independent-subset tests on every completion
of four small crowns. The controls include a Petersen-sized positive
and the impossible ten-vertex `α≤3` case. The extra W4 cap, clean
pins, and anchor sort have the direct label/bound proofs above.

Evidence folder: `scratch/E/crown_cert/`. `SHA256SUMS` binds all 42
CNFs, DRAT, LRAT, the 15 witness-cut files, and the five core lists.
`wW.I.log` records each cold proof run (`s UNSATISFIABLE`, `s VERIFIED`
from `drat-trim`, `c VERIFIED` from `lrat-check`); `wW.I.regen.log`
records byte-for-byte CNF regeneration and another LRAT check.
W4 exploratory results are retained in `w4.*.tight.log` and
`w4.6.strong.log`; narrower caps elsewhere are not used as evidence.
The W4 C4 experiment hit the 65 CPU-s limit before the anchor sort and
pair-cut seeds; the revised run solved in 2.04 CPU s before cold replay.

From the repository root:

```sh
cd scratch/E
sha256sum -c crown_cert/SHA256SUMS
nice -n 5 timeout 30 bash ../../ralph/lanes/E/limited.sh 15 \
  python3 -B ../../ralph/lanes/E/check_crown_cores.py .
for order in 4 5 6 7 8; do
  while read -r idx core; do
    bash ../../ralph/lanes/E/replay_crown28.sh "$order" "$idx" verify || exit 1
  done < "crown_w$order.rows.tsv"
done
```

`verify` does not call a SAT solver. `rebuild` optionally regenerates
the witness cuts before producing a fresh proof after compiling
`crown_exact.cc` as `scratch/E/bin/crown_exact_v4` (C++20, headers and
static library from `opt/cadical`). Regeneration from retained cuts
does not require the C++ search binary or its exact traversal order.
