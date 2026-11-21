# Round 7: path/leaf strip certificates

The structural proof and limitations are in `rows/path_leaf_windows.md`.
There are two terminal scopes: both path/leaf with centre codegree 3,
and both path/leaf with codegree 2 **and** minimum paired-window degree
3. The order-25 low-degree batch is separate. Neither e168 degree
distribution is excluded. Nothing here changes the round-6 baseline.

## Inputs and smaller controls

Work in a reviewer-owned directory; paths here assume `scratch/G/round7`.
Use `ulimit -v 16777216`, `nice -n 5`, capped solver jobs, and at most
the reviewer's allocated slots. Set:

```sh
root=../../..
src=$root/ralph/lanes/G
py=$root/opt/venv/bin/python
bin=$root/opt/bin
c++ -std=c++20 -O3 -Wall -Wextra -Werror "$src/strip_window.cc" -o strip_window.replay
"$bin/geng" -qt 8 > control8.replay.g6
nice -n 5 timeout 45s "$py" -B "$src/test_strip_window.py" ./strip_window.replay control8.replay.g6
nice -n 5 timeout 45s "$py" -B "$src/strip_completion.py" completion.control.g6 --control
```

`completion.control.g6` contains C13(1,5), C35(1,7,11,16), and
the old `scratch/G/exoo39.matrix` complemented and saturated by
`check_rows.saturated`; the controls report α = 4, 8, 9. Negative
controls enforce each same degree pin and alpha lowered by 1.

## Codegree three

```sh
nice -n 5 timeout 120s ./strip_window.replay pair 4 4 3 \
  < ../round5/r38_27.canon.g6 > pair27.replay.keys
cmp pair27.replay.keys pair27.keys
cmp ../../A/path7/pair27.A.keys pair27.keys
nice -n 5 timeout 90s "$py" -B "$src/index_strip_proofs.py" pair27.keys ../round5/r38_27.canon.g6 \
  --proofs proof-sample c3.sample.all.log --proofs proof-full c3.production.all.log \
  --output c3.replay.index.tsv
cmp c3.replay.index.tsv c3.certificates.tsv
```

`pilot.keys` names the 32 keys in `proof-sample`; `remaining.keys`
names the 1,956 in `proof-full`. To replay proofs, for each disjoint
shard use `prove_strip_windows.py KEYS PROOF_DIR --replay --shard I N`
with no `--eager`, no `--cut-budget`, and no `--overlays` options.
It rebuilds DIMACS and runs both proof checkers. The production and
replay CNF hashes must agree. Producer proof jobs took 785.07 CPU-s.
Lane A independently verified all 1,988 pin maps, formula hashes and
proofs (577.28 CPU-s); see `scratch/A/path7/replay.{0,1}.log`.
G's exact index rejects one missing or one duplicate receipt, as
shown in `c3.{omission,duplicate}.rejected`.

## Lower-order source

`gluing/val/r3_7_22.g6` is the repo's copy of the complete 191-class
order-22 `(3,7)` catalogue (D-G3). `source22.canon` is its distinct
canonical class list; all 191 pass `tools/check_graph.py --n 22 --k 7`.
This complete size and graph validity are separate from the proofs.
Source `glue3.c` in scratch is a byte-identical copy of
`gluing/src/glue3.c`; see its independence-subset recurrence. It
adds the new root last, adjacent to exactly the d new independent
neighbours. The positive gluer control reconstructs exactly C13 from
the three order-eight `(3,4)` classes, see `glue3.control.log`.

```sh
gcc -O3 -march=native -I"$root/gluing/src" glue3.c -o glue3.replay
nice -n 5 timeout 180s ./glue3.replay -k 7 -d 3 -m 3 -M 7 -e 91 \
  < source22.canon > lowdegree26.replay.raw.g6
cmp lowdegree26.raw.g6 lowdegree26.replay.raw.g6
nice -n 5 timeout 180s ./strip_window.replay pair 4 4 4 \
  < lowdegree26.replay.raw.g6 > lowdegree26.replay.keys
cmp lowdegree26.full.keys lowdegree26.replay.keys
nice -n 5 timeout 90s "$py" -B "$src/canon_strip.py" lowdegree26.replay.keys lowdegree26.replay.canon.keys
cmp lowdegree26.canon.keys lowdegree26.replay.canon.keys
```

Order-25 generation uses `-k 7 -d 2 -m 2 -M 7 -e 87` instead.
Its graph6 records are 52 bytes each including newline. In each of
the four contiguous ranges with start `i*4583346`, read up to
4,583,346 records (the fourth range has three fewer) via byte-
bounded `dd`. Pass the result through `strip_window.replay pair 4 4 5 rooted`,
adding the range start to printed row IDs, then concatenate in range
order. `lowdegree25.rooted.keys` and `lowdegree25.canon.keys` are
the labelled and deduplicated traversal results. Rooted and ordinary
traversals yield identical marked controls on all 410 small inputs.
`lower.sources.sha256` binds their full input and output files.

For canonical collapsing, the code independently verifies each
mark's inequalities, graph alpha and triangle-freeness. It colours
the two sides and the rest and compares both side orders. The proof
encoding is invariant under isomorphism and exchanging sides, so
every representative suffices for all equivalent marked placements.

## Codegree two: minimum degree three only

There are 2,712,471 labelled gluing outputs; 2,111 marks collapse
to 1,767 coloured-unordered representatives. Base proof run: 38
certificates in `proof-low26-pilot` and 1,697 in `proof-low26`;
retry run: 12 in `proof-low26-eager-pilot` and 20 in
`proof-low26-eager`. For base replays no extra arguments; for retries
use `--eager 10000 --cut-budget`. Keys for these are respectively
`lowdegree26.pilot.keys`, `lowdegree26.pending.keys`,
`low26.cappilot.keys`, `low26.eager.remaining.keys`. For `--replay`
filter the first two key files down to `CERT` keys by their receipts.
The experimental budget/overlay pilot directories are **not** used.
The independent 7-set traversal in `ralph/lanes/A/replay_strip_marks.cpp`
matches the 2,111 labelled marks after sorting (71.00 CPU-s), recorded
in `lowdegree26.A*`. The gluer and canonical collapsing still require
review as coverage premises, independently of the LRAT verdicts.

```sh
nice -n 5 timeout 90s "$py" -B "$src/index_strip_proofs.py" lowdegree26.canon.keys lowdegree26.raw.g6 \
  --proofs proof-low26-pilot proof-low26-pilot.all.log --proofs proof-low26 proof-low26.all.log \
  --proofs proof-low26-eager-pilot proof-low26-eager-pilot.all.log --proofs proof-low26-eager proof-low26-eager.all.log \
  --output c2.delta3.replay.index.tsv
cmp c2.delta3.replay.index.tsv c2.delta3.certificates.tsv
```

For codegree one/minimum degree two, use pilot `lowdegree25.pilot.keys`
with directory `proof-low25-eager` and production `lowdegree25.pending.keys`
with `proof-low25`. The arguments for both are `--eager 10000 --cut-budget`.
Require the union of their `CERT` keys to equal `lowdegree25.canon.keys`
before any claim. The 17,194 representative list is not a census of
all `(3,8;25)` graphs or all paired windows of order 25.

## Mixed codegree four (batch in progress)

`mixed_strip_cover.py pair27.keys mixed-j4.replay.keys` tries both
assignments of strips on each original order-27 marked key and then
all legal missing-double roles. It emits 5,179 keys (3,688 matching,
1,491 path/middle). The `--mixed --eager 10000` proof invocation is
used for both the 24 pilot roles and the 5,155 pending roles. These
files are `mixed-j4.pilot.keys` and `mixed-j4.pending.keys`; proof
directories `proof-mixed-pilot` and `proof-mixed`. The same index
accepts the extended fields as part of the key; the source is still
`../round5/r38_27.canon.g6`. A terminal union would refute only
mixed graphs admitting a noncross d8 pivot of codegree four to the
path/leaf centre, and only at `(2,7,4,27)`.
