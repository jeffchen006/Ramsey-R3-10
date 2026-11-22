# Round 8: higher-minimum pilots and proof bundles

All commands assume `scratch/G/round8` unless a directory is specified.
Use your own scratch for independent output; cap solver jobs, RAM and
core use as in `AGENTS.md`. Set `root=../../..`,
`src=$root/ralph/lanes/G`, and `py=$root/opt/venv/bin/python`.

## Both path/leaf, centre codegree one and delta(T)=2

Complete source in round 7: 191 order-22 classes, 18,333,381 labelled
extensions, 20,181 marked rows and 17,194 side-swap-coloured keys.
See `ROUND7_REPLAY.md` for commands and `scratch/A/strip8/` for the
independent byte-matched gluer, scanner and isomorphism audit. Neither
`j=1,delta>=3` nor a mixed role is within this closure.

From `scratch/G/round7`, bind the original capped pilot, incomplete
production, and exact remainder with:

```sh
nice -n 5 timeout -k 4s 600s "$py" -Bu "$src/bind_strip_batch.py" \
  lowdegree25.canon.keys lowdegree25.raw.g6 ../round8/c1.replay --io-workers 4 \
  --batch lowdegree25.pilot.keys proof-low25-pilot 3 proof-low25-pilot \
  --batch lowdegree25.pending.keys proof-low25 16 proof-low25 \
  --retry ../round8/c1.first/unclosed.keys ../round8/proof-c1retry 16 ../round8/proof-c1retry
```

Initial receipts are 32 CERT and 10 CAP in the named pilot, 13,336
CERT and 3,816 unwritten in the original 16-shard batch. The original
production reached the wall cap with 12,023.36 CPU-s. The 3,826-key
remainder took 3,409.59 CPU-s and gives only CERT receipts. G's
terminal union selects 32 non-eager originals, 13,336 production
proofs and 3,826 retries. To replay with `prove_strip_windows.py
KEYS PROOF_DIR --replay --cut-budget`, use `--eager 0` for the 32
original CERTs in `proof-low25-pilot`, and `--eager 10000` for the
selected production and retry proofs. Partition the terminal index
by proof directory and join to `c1.final/cert.keys` on the full key.
The DIMACS SHA for every key must agree with its selected receipt.
A instead selects all 42 eager pilot proofs in its independent union.
For 32 keys the two selected DIMACS hashes differ; never cross-use
proofs. See `scratch/critic/r8/G/{differences,primary.check,eager.check}`.

## Mixed j=4

The earlier mixed cover has 3,688 matching/incident keys and
1,491 path/middle keys, only at `(2,7,4,27)`. It is terminal: 24
pilot and 5,155 production proofs passed both checkers in 6.89 and
1,437.24 CPU-s respectively. From `scratch/G/round7`, use:

```sh
nice -n 5 timeout 200s "$py" -Bu "$src/bind_strip_batch.py" \
  mixed-j4.keys ../round5/r38_27.canon.g6 ../round8/mixed.replay --io-workers 4 \
  --batch mixed-j4.pilot.keys proof-mixed-pilot 2 proof-mixed-pilot \
  --batch mixed-j4.pending.keys proof-mixed 2 proof-mixed
```

Rebuild proofs with `--mixed --eager 10000 --replay`, not `--cut-budget`.
No scope for smaller cross codegree, or for two path/leaf strips.

## Higher-minimum exact source, measured but not launched

If a paired T has `(j,delta(T))=(1,3)` or `(2,4)`, peeling any vertex
of that minimum degree leaves an order-21 `(3,7)` graph. The complete
1,118,436-class catalogue is Brinkmann–Goedgebeur as supplied on
McKay's Ramsey data page (`r37_21.g6.gz`; SHA-256 in the freeze).
The retained four-column roles and edge caps are proved in
`rows/paired_window_budget.md`. All larger minimum degrees need
different sources; no unconditional higher-minimum census.

The pilot samples rows 1, 279609, 559218, 838827, 1118436 and takes a
separate evenly spaced 256-row sample for `j=2,delta=4`. Feed these
to the old calibrated `glue3 -k 7 -d q -m q -M 7 -e E`, where q is
3 or 4 and E is 87 or 91 to match the original measured command.
Then pipe into `strip_window pair 4 4 W rooted` with W=5 or 4.
`strip_window_fast` uses disjoint/at-most-one-codegree anchor pairs,
no triple attachment, and monotone neighbourhood-union bounds.
These are necessary because the only cross edge attaches one
opposite mark to one chosen mark. Byte equality holds across the
sampled output, and the width-two/width-three 410-graph controls
reproduce 21/44 marks. All measured commands and times are in
`scratch/G/round8/{source21*,scanner.*}`. Neither sample is a cover.

| Pilot | Raw outputs | Marks | Old CPU-s | Fast CPU-s | Estimate, fast census only |
|---|---:|---:|---:|---:|---:|
| `j=1,delta=3`, 5 cores | 285,170 | 205 | 6.02 | 1.77 | 110 CPU-h; poor five-row estimate |
| `j=2,delta=4`, 256 cores | 328,559 | 260 | 16.63 | 10.22 | 12.4 CPU-h |

Degree-four pilot 33/33 dual LRATs (19.49 CPU-s), projecting to
roughly 187 CPU-h of proofs before target canonical reductions,
based only on this sample. No broad launch. For a future generator
use `-e 83/88`, and root-type cap `-e 81/86` only if the root is
exterior (do not conflate the two root roles).

## Centre-table relaxation: bounded negative result

Compile `center_prefix.cc` with C++20. `test_center_prefix.py` compares
against a non-matching Python oracle on 52 oriented C13 overlays and
two planted controls (positive edge forcing / negative duplicate).
It additionally checks every inferred literal against C35 and Exoo39
on the 16 selected orientations. `test_window_budget.py` verifies
the paired degree bounds and the general opposite-exclusive MTF
requirement on all smaller controls.

`center_prefix J OFFSET 20` visits exactly 20 first-table prefixes
at offsets 0, 1000, 5000 for each J=1,2. A first prefix fixes the
six A-centre rows, B margins and the overlap codegree; the second
DFS exhausts the B-centre-exclusive rows respecting remaining type
margins. Sorting within identical signatures removes only vertex
order. It checks Hall incrementally for cliques of intersecting
supports on the two independent nine-anchor palettes, then tests
forced edges, opposite-exclusive cross options, cut budget and
whether any retained anchor misses the higher-minimum requirement.
It **does not** assign the other 17/18 exterior vertices. The scout
full-overlay sample remains separate from this exact prefix test.

After Hall the sampled prefixes have 335,539 and 79,242 completed
centre subtables, respectively. Hall/triangle forcing rejects none;
the opposite-exclusive MTF row rejects 4,000 and 3,388; the pair
edge floor rejects zero more. High-minimum marked degrees remain
compatible on 330,893 and 72,112 respectively. There are 30,213 and
21,056 first prefixes before any B-exclusive choice; this attrition
does not justify a broad integer-overlay launch. See `center.*.mtf.*`.

## Alternate pure pivots at order 27

See `rows/alternate_pure_pivots.md` for the two exact max-codegree
roles. Reproduce the role list with

```sh
nice -n 5 timeout 60s "$py" -B "$src/pure_pivot.py" ../round7/pair27.keys pure-pivot.replay.keys
cmp pure-pivot.replay.keys pure-pivot.keys
```

The pilot has 12 leaf keys and one full key; the exact remainder
list has 1,484 keys. All 1,497 certificates are bound in `pure.bound/`.
Producer CPU cost: 4.17 seconds (pilot) and 471.98 seconds (remainder).
To replay use `prove_pure_pivot.py KEYS PROOF_DIR
--eager 10000 --replay`; the output key, compressed length and
CNF hash must match. `bind_strip_batch.py` takes two partition
subsets (pilot and remainder) and the same McKay graph6 source as
the original order-27 pair bundle. These cases are distinct from
the earlier mixed j4, and also do not close low-codegree pivots.

```sh
nice -n 5 timeout 150s "$py" -Bu "$src/bind_strip_batch.py" \
  pure-pivot.keys ../round5/r38_27.canon.g6 pure.replay --io-workers 4 \
  --batch pure-pivot.pilot.keys proof-pure-pilot 1 proof-pure-pilot \
  --batch pure-pivot.pending.keys proof-pure 6 proof-pure
```
