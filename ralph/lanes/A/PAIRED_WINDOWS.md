# Round 7: paired degree-seven path centres

This uses the accepted adjacent degree-six equality strips at e168
(`ADJACENT_DEG6.md`). Neither degree pin is fully closed here. There are
no new e120/e121/e122 inputs, and no changed census or pinned e169 proof.

## One-centre window (hand + enum)

In a lower H=X+B half, a path/leaf mark has absent pairs 01,02,
with 0 the centre and 1 the cross endpoint. Delete the closed
neighbourhood of 0. The four remaining anchors are independent, with
four singles each and all six doubles once. They have degree seven.
The 26-vertex window has alpha at most seven, by adjoining 0 to any
independent set in it. All four anchors dominate the window: the
independent neighbourhood of a degree-seven vertex already reaches
the alpha bound, so explicit domination clauses simplify away.

The edge level is 72 plus the number of opposite-strip doubles among
the six deleted exterior neighbours, plus their total degree defect
sum(9-d_G). H obtains cap 82 on the n8=2 pin using the root codegree
bound. The cap alone cannot refute the marked window: a checked
82-edge model exists. The weaker 74 and 78 cap searches stopped on
CPU limits; neither is UNSAT. No marks occur among the supplied 62
e73 and 1,624 e74 inputs, but e74 is not a complete census.

`audit_path_leaf.py` rechecks lower alpha after deleting any added
edges and projects the mark. All four addition choices bind to the
same window on 36 smaller half-strip/leaf labels (18 directed roots).
The wrong cross role and a lower-alpha failure are rejected. The
eager CNF pins an arbitrary star of private-cell perfect matchings:
for each pair of p-vertex private cells, append their common double
and the other anchors to an independent set to get alpha at most p
within the two cells, then use König's theorem. Seven marks occur
in the smaller order-12 catalogue; the CNF returns a validated model.
All 191 order-22 rows lack the mark, matching a terminal CNF UNSAT
(enum calibration). Evidence is in `scratch/A/path7/`.

## Exact pair cover for c=3 (hand + enum)

Use two path/leaf strips and delete both centres' closed neighbourhoods.
The six exterior neighbours of each centre form D_A and D_B. The
centres are nonadjacent, so MTF and the codegree cap give intersection
size c=1..3, order 24+c and alpha at most seven in the remainder.
For c=3 the window keeps two independent four-sets joined by one cross
edge plus 19 vertices meeting both sides in one or two anchors. There
are at most four singles per column and at most one double per pair.

For any marked pair A<B (integer masks), delete the cross endpoint b
on B from A union B. This leaves an independent (2w−1)-set J for strip
width w. The endpoint b has a unique contact in J. Every other outside
vertex has one to four contacts in J; if it has exactly one it must hit
b or miss an entire strip. Enumerate J and b, then choose the rest of
A and test the two signature margins directly. This independently
recovers every mark. In `scratch/A/path7/`, `lineage27.log` binds the
477,142 distinct normalized McKay keys to G's source; `control8.A.log`
matches 21 marks on 10 of 410 smaller rows. The full A output matches
all 1,988 G marks on 1,980 classes byte-for-byte (`pair27.A.{log,keys}`)
in 17.17 CPU-s. Omission and duplicate controls fail comparison.

## Missing-signature prefilter (hand + enum)

The nine deleted exterior vertices consist of three shared and two
exclusive triples. Each centre has four copies of its singleton and
two doubles with distinct nonleaf retained columns. The opposite
exclusive triple contains exactly the three missing occurrences from
the four retained columns' complete signature list. For each choice
of the noncross leaf, permute each centre multiset against the three
known gap slots and three shared slots; zip the two shared lists.
This covers every overlay, possibly with repeated symmetric copies.
Fourteen actual C7 controls recover the unique planted supports;
missing cross coverage and deficient Hall controls are rejected.

For each overlay, require coverage of the 24 nonedge cross pairs and
potential MTF witnesses for all exterior–anchor nonedges. Pairs with
shared support are forbidden edges; kept-window edges are fixed.
Each retained exterior vertex must hit both centre sets, so it needs
at least two new neighbours if no shared one is possible. Degree seven
requires two singleton supports (accepted degree-six root codegree
bound). Test the exact two exterior degree profiles with optimistic
independent degree choices and the identity
`e(window)=76+sum(9-d_G(x) for x deleted)+e(exclusive-cross)`.
The constant accounts for the edge between the roots. Bound the last
term by potential disjoint-support exclusive pairs. Finally, for each
forced-nonedge clique Q and either independent nine-set of strip
vertices I, require the incidence matching into I to saturate Q.
Otherwise König's theorem gives an independent ten-set on Q union I.
Testing maximal cliques suffices by restricting their matchings.

`filter_strip_supports.py` ran on all 1,988 keys in 114.07 CPU-s.
It leaves 633 keys for exterior `(n7,n8)=(5,2)` and 591 for `(6,0)`,
union 633. These are not completions. The raw overlay counters are not
orbit counts, and the scan stops at the first hit for each profile.
See `scratch/A/path7/supports.full.log` and `support-survivor.keys`.
Neither c=1,2 nor any mixed strip role is covered by this filter.

## Full proof replay (cert, pending critic)

`audit_strip_proofs.py` independently reconstructs the fixed edge map
from the exact cover keys, roots, centre sets and sorted gap copies.
It checks equality with G's map and binds the rebuilt optimized CNF's
SHA-256 to the receipt. The full receipt union is 1,988 distinct keys:
32 pilot and 1,956 production. Both LRAT checkers independently
accepted every supplied trace against its rebuilt CNF. The two sorted
replay shards match the cover exactly; an omitted or duplicate receipt
and a crossed proof are rejected. No proof was generated by A. This
rebuild uses G's cardinality encoder, with an independent fixed-edge
map; the clause semantics and labeling argument are in
`ralph/lanes/G/rows/path_leaf_windows.md`. The CNFs require no lazy
independence or symmetry-breaking clauses. Evidence is in
`scratch/A/path7/{proof-receipts.tsv,replay.0.log,replay.1.log}`.
Replay took 577.28 CPU-s (0.1604 core-h), two foreground slots.

This excludes both-path/leaf, e168, c=3 on the two low-n8 pins only.
For the n8=2 pin, any remaining graph has centre codegree one or two.
For the n8=4 pin, the mixed-role branch is also open. No whole degree
distribution is closed and there is no new R(3,10) verdict.

## Replay

Run in a lane-owned scratch directory with `opt/env.sh` sourced,
`PYTHONDONTWRITEBYTECODE=1`, and `ulimit -v 16777216`. With `root=../../..`
and `src=$root/ralph/lanes/A`:

```bash
nice -n 5 timeout 20s c++ -std=c++20 -O3 -march=native "$src/replay_strip_marks.cpp" -o replay_strip_marks
nice -n 5 timeout 90s prlimit --cpu=60 ./replay_strip_marks 4 4 3 \
  < "$root/scratch/G/round5/r38_27.canon.g6" > replay.keys
cmp replay.keys "$root/scratch/G/round7/pair27.keys"
nice -n 5 timeout 360s prlimit --cpu=240 python "$src/filter_strip_supports.py" replay.keys
nice -n 5 timeout 65s prlimit --cpu=35 python "$src/audit_strip_proofs.py" replay.keys \
  "$root/scratch/G/round7/proof-sample" proof-audit-new "$root"/scratch/G/round7/proof-sample.*.log --sample 4
```

For each full replay shard `shard=0` or `1`, use:

```bash
g="$root/scratch/G/round7"
nice -n 5 timeout 950s prlimit --cpu=700 python "$src/audit_strip_proofs.py" replay.keys \
  "$g/proof-sample" "replay-new.$shard" "$g"/proof-{sample,full}.*.log \
  --alternate "$g/proof-full" --require-cover --sample 0 --shard "$shard" 2
```
