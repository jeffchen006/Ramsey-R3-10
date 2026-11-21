# Round 1 evidence and reproduction

## R(7): exact trace of the four complete side-package covers

Seed graph6 file `scratch/A/rc7/r38_27_e85.g6` has SHA-256
`6b2373618c34d588dfbf073e28794dab68400a15ef6e06d96bc618b490c8ce57`.
The census cardinality four is the premise D-C8e; individual input graphs
and absence of duplicates were checked independently by lane A. Set SAT
was not used in the proof: two 360-second pilots produced no verdict.

| seed | side packages | trace nodes | max nodes/pair | CPU seconds (generate + DFS) |
|---:|---:|---:|---:|---:|
| 0 | 261824 | 14556539 | 198 | 83.08 |
| 1 | 261586 | 14709733 | 197 | 82.64 |
| 2 | 226943 | 10195771 | 119 | 75.69 |
| 3 | 226655 | 10107036 | 116 | 72.83 |

To regenerate, from workspace root compile `colour_packing.cpp` twice, to
`scratch/C/colour_packing` and `scratch/C/colour_packing_trace`, using
`c++ -std=c++20 -O3 -Wall -Wextra -pedantic`. From `scratch/C`, stage the
e85 graph6 as `R7_X.g6`, and use each seed index separately with
`nice -n 5 timeout 1200 bash ../../ralph/lanes/C/run_packing_seed.sh INDEX`
and then `nice -n 5 timeout 300 bash ../../ralph/lanes/C/run_packing_trace.sh INDEX`.
Both scripts impose lane RAM limits. Logs and proof files are in `scratch/C`.
Lane A's `ralph/lanes/A/replay_r7.sh` independently checks coverage and
the traces. H reviewed the hand reduction in `ralph/lanes/H/R7_REVIEW.md`.

The stronger full positive control (all possible packages, not just planted
ones) is in `scratch/C/full_control.log`. It recovers exactly the seven
known 6-regular (3,7;22) classes possessing this K2,2 anchored nonedge.
Use `pair_packages.py calibrate ... --out full_control --all-out`, run
`colour_packing 1000000 enumerate` on each emitted text file, then
`check_packing_control.py full_control duo/reg6_22.g6 opt/bin/labelg`
with paths interpreted from the chosen working directory.

## R(6): the codegree graph's cycle case

The McKay 191-census file `scratch/A/rc7/r37_22.g6` has SHA-256
`228d886ee01b3003d90c768af57804954f7adccbca901a3eeb3c69ccc020e8c5`.
Nauty canonicalization gives 191 distinct inputs. From `scratch/C`:

```sh
ulimit -v 16777216
nice -n 5 timeout 45 python3 -B ../../ralph/lanes/C/cycle8_profiles.py \
  ../A/rc7/r37_22.g6 --output cycle8_candidates.tsv
nice -n 5 timeout 90 python3 -B ../../ralph/lanes/C/cycle8_join.py \
  ../A/rc7/r37_22.g6 cycle8_candidates.tsv --labelg ../../opt/bin/labelg \
  --verify-obstructions cycle8_obstructions.json
```

Replace `--verify-obstructions` with `--write-obstructions` to regenerate
the proof. Without either flag the program uses both search implementations.
The certificate table uses only an adjacency-labelled choice of at most
eight coordinates per family and the exact count of possible profiles on
those coordinates. Proof generation tests both DFS and meet-in-middle;
verification regenerates the family library and checks exact tuple sums.
Deleting all coordinates from a proof row was rejected. Candidate TSV
SHA-256 `d68522f779df7a8aa72b268e101dd8b25e67e2955a795758b192d4ef5a5c53c1`;
proof JSON SHA-256 `cc6eee9b265b9711d075ef48037eaeb70951e01a70f3f026e60c735ab5664f0c`.
See `proofs/codegree_six_paths.md` and `proofs/cycle8_join.md` for the covers.

## R(3): integer-weight certificates on projected edge kernels

The catalogue is D's independently regenerated `scratch/D/catalogues/R3.g6`.
The checked evidence files `scratch/C/R3_part0.jsonl` and
`scratch/C/R3_part1.jsonl` have SHA-256 values
`6abd5f052dabb958a7ec0ca5ebafcd3556992bac4d3560da9044846a2e449e18` and
`1cf652e9e4896b086bb51f615f3cf9c09ea42a84c9a70a39682986c7dc4a5c86`.
Their ordered graph6 column reproduces the catalogue exactly. Pipe either
file through `python3 -B ralph/lanes/C/kernel_projection.py verify` with
default settings for integer checking; SciPy is not imported in this mode.
The remaining oriented list is `scratch/C/R3_survivors.g6`.
