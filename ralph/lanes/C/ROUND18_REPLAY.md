# Round 18 — exact joint exclusions for two marked one-neutral slices

**Hand + enum, pending critic.** For a cap-five marked `K4,4` with
one neutral and ordered 16/17 windows, the following two degree/shape
slices cannot complete. These are not whole degree keys, not the full
one-neutral branch, and not an exclusion of Case R or R(5).

| `(D16,d16;shape16,shape17)` | Raw | Neither | Forward only | Reverse only | Both | No joint tuple | New joint tests |
|---|---:|---:|---:|---:|---:|---:|---:|
| `(67,5;2333,3334)` | 32,340 | 17,904 | 13,644 | 746 | 46 | 46 | 46 |
| `(68,4;2333,3334)` | 28,301 | 15,241 | 12,944 | 92 | 24 | 24 | 23 |

The two side counts are `1,078 × 30` and `311 × 91`. A's frozen raw
frame bindings and independent literal margin sweep (`A/ROUND18_PHYSICAL_IDS.md`)
cover all 60,641 raw headers; no symmetry weight is used. C inherited
only the 70 physical both-pass headers for compatibility. It checked
all 32 old marginal overlap vectors, 16 per slice. Only one both-pass
header overlaps the round-16 joint pilot: `(2501780,31298)` in the
second slice, old zero-based pilot row 286. That ID's complete eight
domain counts and zero joint result agree once again. Thus this is a
new joint-stage debit of 69, not 70 or 60,641. Starting from C-043's
2,542,514,492 marginal survivors, the 47 prior and 69 new failures leave
**2,542,514,376** untested joint-stage IDs elsewhere.

## Physical and independent checks

- `panel18_bind.py` independently reads the window catalogue rows and
  checks the marks, neutral, degree equalities, triangle/codegree
  conditions on fixed data, full singleton label groups, original
  row and column axes, ID/mask cross-references, and orientation. It
  checks all 70 companion receipts. The reverse check is a transpose
  in the original host labels, not a separate crossing. On all 153
  named asymmetric 6/7 plants it independently recovers the actual
  rows from the full graph and rejects 306 one-direction flips.
- `panel18_marginals.py` recomputes nonemptiness by independent-set
  absence bitmaps, verifies all **12,762** exact A predicate bits, and
  recomputes all **11,250** host-pair products (5,472 and 5,778). Each
  of the 42 positive pairs has exactly its correct physical survivor
  mass in A's roster. This process uses only the two selected shape
  cell tables; it does not form another physical header product.
  Calibration matches 2,067 small predicate bits and all 29,220
  products covering 34,504 smaller IDs. Four-row demands are checked
  separately against literal subset hitting: 23 yes and 1,462 no over
  three named order-seven catalogued hosts.
- `panel16.cpp` constructs all eight physical package domains for
  each target ID. All 70 literal native joins finished uncapped
  (max 1,929,968 probes); rectangle arc revision independently leaves
  an empty domain for each. The largest original group domain is
  2,182. The Python audit reconstructs all eight matching domain
  lengths for every ID; it exhausts the signed-overlap indexed join
  with max 20 matching package probes and compares the keyed tuples.
  **Zero compatible tuples**, so no terminal call and no surviving
  assignment to preserve. This is not a claim about a graph obtained
  from a compatible tuple. The independent control joins are
  nonvacuous: 1,596 tuples including all 153 plants, 20 terminal
  triangle failures and 1,576 locally live outcomes.

See `proofs/panel18_signed_join.md` for the hand argument and
`ROUND18_PREFLIGHT.md` for the preregistered scope and price. The first
straight marginal recheck hit its 45-second CPU cap; it is not evidence.
The exact bitmap replacement took 40.72 CPU-s, native joins 0.47 CPU-s,
and independent joint audit 163.02 CPU-s. The first pass, including
builds and setup (and the capped attempt), uses 256.50 measured CPU-s.
The clean replay used 238.14 CPU-s. All 12 timing-free output files
match byte for byte and all four timed files match after omitting
timings. Total measured charge **494.64 CPU-s / 0.13740 core-h**;
peak RSS 291,768 KiB with compiler, 99,248 KiB for checks. At most
two foreground workers were active simultaneously. No jobs remain.

## Replay

```sh
sha256sum -c ralph/lanes/C/ROUND18_FREEZE.sha256
bash ralph/lanes/C/replay_panel18.sh "$PWD/scratch/C/r18-review" "$PWD/scratch/A/r18"
cmp scratch/C/r18/keyed.tsv scratch/C/r18-review/keyed.tsv
cmp scratch/C/r18/summary.log scratch/C/r18-review/summary.log
```

Primary logs and receipts are under `scratch/C/r18/`. The exact physical
package result is enum, not a SAT proof or a flow candidate verdict.
