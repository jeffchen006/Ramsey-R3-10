# P3 diagonal five: high-edge reduction and e64 extension

The hand proof is `proofs/path_three.md`. In R(6) every span of three
distinct consecutive codegree-six roots leaves a 22-vertex triple
residue X of independence number at most six. If the exterior roots
have codegree five, Hall's condition in the central neighbourhood
implies e(X)<=64 and fixes the full deleted graph at equality. No
restriction on the rest of J is required, so this does not depend on
the P4 certificate. All 59 CNFs at e64 have checked LRATs, with
identical regenerated CNF/proof hashes and a second full CakeLPR
replay. The combined e(X)<=63 result is submitted for critic review.

## Calibration and small boundary audit

- For all 42 oriented planted C21 triples, the wing separation,
  block sizes, residual alpha and exact edge identity hold (e(X)=12
  and f=9 in the smaller parameters, `scratch/C/p3_partition_control.log`).
- `path_three_top.py --control` reconstructs the C21 graph using the
  actual fixed boundary, accepts its entire attachment assignment,
  and rejects the assignment with one attachment flipped. The planted
  graph independently passes the graph checker. Logs
  `scratch/C/p3_top_{control,independent_control}.log`.
- `verify_p3_boundary.py --min-f 18` independently audits the hand
  reduction by enumerating all 512 labelled Y--Z patterns and all
  allowed wing masks for the four active central vertices. Check both
  Hall matchings and the absence of an independent five-set in Y+Z.
  Nine labelled choices at f=19, modulo swapping the two private
  vertices, give precisely one orbit under independent permutations of
  the wings. No f>19 choices. At f=18 there are 234 choices in 13
  orbits, all surviving fixed-boundary alpha/codegree/biclique
  checks. The output `p3boundary-e63.log`
  gives the 13 explicit representatives with block orders fixed.
  This is boundary coverage only, not an extension test for e63.
  The independent boundary isomorphism against the SAT fixture is
  logged at `scratch/C/p3e64-boundary-bind.log`.

## Static extension CNF

Using the e64 boundary, the only possible unknown edges are from X
to the fifteen nonroot vertices of the deleted graph; the three roots
have no X-edges. Fix both induced graphs. Use degree deficits on both
ends. Each same-side pair counts its fixed shared neighbours plus
one AND selector per possible shared neighbour across the cut. For
fixed adjacent pairs the across-cut selectors are all forbidden (no
triangle); for fixed nonadjacent pairs require total codegree in [1,6].
For a cross pair x,b, a common neighbour is either in the fixed X
neighbourhood of x and attaches to b, or in the fixed boundary
neighbourhood of b and attaches to x. Use those single edge literals
as its possible common neighbours, with upper bound six, and
disjoin them with the edge literal for maximality. The same-side
triangle rows already ensure a cross edge cannot have a common
neighbour. This covers every triangle type.

For every independent I in X, independently examine every maximal
independent set of the deleted graph. All its members with no
neighbour in I, including any roots, may augment I; require the
total size at most nine. Every independent set of the boundary is
contained in a maximal one, so these are the exact independence
tests. A one-way gate forces each availability literal true when
all relevant attachments are false; setting each gate to its
semantic value conversely extends any true completion. Thus these
static CNFs contain no guessed or lazy Ramsey clauses. They use the
same sequential-counter encoder as the P4 package.

## Reproduction

From `scratch/C`, use the following commands. Do not overwrite retained
proofs. Proof calibration checked spread rows 0, 95 and 139 (107.37
CPU-s with proof checking; LRATs ~70 MB each); the production shards
skip those three. See STATE for live and completed status.

```sh
ulimit -v 16777216
lane=../../ralph/lanes/C
census=../../gluing/val/r3_7_22.g6
bin=../../opt/bin
nice -n 5 timeout 60 python3 -B "$lane/verify_p3_boundary.py" --min-f 18
nice -n 5 timeout 180 python3 -B "$lane/p3_e64_index.py" "$census"
nice -n 5 timeout 1200 python3 -B "$lane/p3_e64_proofs.py" "$census" "$bin" \
    p3e64-proofcal --verify --row 0 --row 95 --row 139
for shard in 0 1 2 3; do
    nice -n 5 timeout 1200 python3 -B "$lane/p3_e64_proofs.py" "$census" "$bin" \
        p3e64-full --verify --shards 4 --shard "$shard" \
        --skip-row 0 --skip-row 95 --skip-row 139
done
```

Match the row, CNF and proof hashes from each replay against the
producer logs (ignore the CPU-s column). The exact index auditor binds
all 59 expected 64-edge rows to the proof files with no omissions
(`scratch/C/p3e64-index.log`). Production used 2103.22 CPU-s and the
full replay 967.98 CPU-s. The four `p3e64-replay-*.log` files record
exact matching and the pilot replay covers the other three rows.
Diagonals three and four, isolated c6 pairs, and the lower diagonal-five
residue strata are separate open cases.
