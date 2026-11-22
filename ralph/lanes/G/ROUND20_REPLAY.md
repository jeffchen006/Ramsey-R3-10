# Round 20 — one matching formula, any right

**Hand + enum + local cert, pending critic.** The formula and receipt
cover the 21,125 previously outstanding labelled alignments in the
marked aligned `h=8` slice of `e=170` adjacent degree-six equality.
Thus that slice is locally closed, conditional on the accepted
structural reductions and prior receipts, not the entire equality
case or a degree distribution. `h=7` remains at 51/1,213 checked
two-sided contexts, and 238 near-regular distributions plus R are
still open. There is no candidate or change to U88, `t9`, or any floor.

## Accounting

`matching-physical.tsv` gives the `(scheme,rank)`, exact physical
support masks and corresponding selectors for each of **80,054**
historical IDs in 17 schemes. The checker enumerates the 900 physical
hole-list pairs and partitions them by crossing-fixing simultaneous
permutations and transpose. It enumerates admissible matchings in
historical support-mask order, applies each chosen map to the 20
grid sites and the two masks of each actual double site, and checks
that the resulting eight distinct selectors hit all four missing-cell
MTF rows. Seven scheme maps transpose; the six residual schemes already
have the fixed matching on the left. The first preflight caught a
metadata error in our auxiliary check: the catalogue integer is a
fixed-left multiplicity, **not** the size of the physical orbit.
No target was run then; the final audit verifies the physical
partition directly, without using that integer.

The reproduced outstanding rank lists equal the accepted round-19
lists entry for entry. Under the combined proof union, 22,943 IDs in
seven leaf+matching schemes and 34,497 in four matching+middle schemes
are already excluded, as are 1,489 prior IDs within matching+matching.
Only the following six lists, **21,125** total, are new credit:

| `matching+matching` scheme | Historical IDs | Old credit | Fresh |
|---|---:|---:|---:|
| `.0` | 3,091 | 149 | 2,942 |
| `.1` | 3,188 | 116 | 3,072 |
| `.2` | 3,918 | 365 | 3,553 |
| `.3` | 4,248 | 347 | 3,901 |
| `.4` | 4,073 | 283 | 3,790 |
| `.5` | 4,096 | 229 | 3,867 |

The full debit is `matching-debit-if-verified.json`; the residual is
`outstanding-if-verified.json` (empty). Per-scheme transformations and
counts are in `matching-crosswalk.json`. The scope of the proof union
is the 169,635 labelled IDs in 30 marked aligned schemes, not arbitrary
completions of an `e=170` marked pair.

## Replay

The independent literal binder checked all 22,841 clauses on 693
variables: 12 existence (8 left slots, 4 MTF), 478 exclusivity, 1,130
triangle, and 21,221 padded. It rejected a bogus edge unit, unguarded
optional-edge row, false slot mutex, shortened MTF row, and an
all-grid blocker made from the complete edge list for `(0,1),(1,2),
(2,0)` with insufficient independent padding. That last forged row
passes the pair-edge test but has no possible extra forced nonneighbor:
its three rows and columns are all distinct, and any extra cell meets
at most two of the three supports. Three sites plus the remaining at
most six boundary vertices cannot reach ten.

Smaller orders 15/16 reproduce the exact canonical **24/0 aligned**
and **129/11 one-defect** class sets and plant every reconstructed
model in the projected encoding. Of 355 labelled plants, 208 change
the right double list relative to the left. The frozen leaf and middle
proofs pass both checkers again without re-solving. A clean replay
regenerates the matching CNF and four rank/crosswalk artifacts byte for
byte and rechecks the retained LRAT with both checkers.

From the repository root, in a fresh lane-owned directory, no target solve:

```sh
sha256sum -c ralph/lanes/G/ROUND20_FREEZE.sha256
mkdir -p scratch/G/round20-audit
timeout --kill-after=2 65 bash ralph/lanes/G/round20_matching.sh review "$PWD/scratch/G/round20-audit"
```

Cost: 6.33 setup + 13.87 baseline + 3.41 target/checks + 13.87 clean
replay = **37.48 CPU-s (0.01041 core-h)**, including the failed setup
check. Solver alone: **0.92 CPU-s**, exit 20; both checkers accepted
the 5,680,596-byte LRAT. CNF+LRAT: 6,252,508 bytes. Peak reported RSS:
134,604 KiB; apparent peak disk about 19 MiB with the clean comparison,
about 12.3 MiB retained. No remaining jobs, caps, or kills. The middle
CNF was 598,246 bytes, correcting the byte-count typo in the pinned
preregistration (matching is still about 4% smaller by bytes).
