# Fixed degree-six residue proof bundle

**Scope: cert for 68 supplied residues only; open for the incomplete e119
cover.** Lane G confirmed the retained source at
`scratch/G/root/replay_core119_clean` and its exact input at
`ralph/lanes/G/root_certs/partial33_le119.g6`. The self-contained data bundle
at `scratch/A/root-residue/retained-v1` stores only a 68-line catalogue, a
TSV index, and gzip-compressed ASCII LRATs (3.5 MiB on disk). It needs no
bulk gluing data, retained DIMACS files, or new SAT runs. The catalogue
contains five e118 residues and 63 of the 69 e119 classes; `shortg` returns
68 distinct classes. No e167 closure or new class discovery follows.

`residue_bundle.py` independently reconstructs Lane G's necessary CNF in
the original clause order, validates the residual graphs, and compares CNFs
byte-for-byte during packing. The four clause families are MTF domination
from each attachment, triangle-freeness of each attachment, positive and
upper bounded attachment load at each exterior vertex, and MTF two-step
coverage for uncovered exterior nonedges. See
`ralph/lanes/G/rows/root_residue.md` for the graph reduction. Neither a
total edge count of the full graph nor a gluing floor is assumed by the
CNFs. The index records the residue's order in the catalogue, its edge
count, and separate SHA-256 values for the labelled graph6 without newline,
exact DIMACS, and uncompressed LRAT. The manifest pins the index and the
exact ordered raw catalogue. Both checkers must return their explicit
success lines on the independently reconstructed DIMACS.

## Reproduce

```sh
root=$PWD
sha256sum --strict -c ralph/lanes/A/RESIDUE_BUNDLE.sha256
cd scratch/A/root-residue
ulimit -v 16777216
ulimit -t 60
tool=$root/ralph/lanes/A/residue_bundle.py
nice -n 5 timeout 90s python3 -B "$tool" calibrate "$root/gluing/val/r3_7_22.g6"
nice -n 5 timeout 90s python3 -B "$tool" replay retained-v1 --bin "$root/opt/bin"
```

For a new proof, `pack CATALOGUE SOURCE_DIR NEW_BUNDLE` expects files
`0001.cnf`, `0001.lrat`, etc. in `SOURCE_DIR`, starting at the first line
of `CATALOGUE`. Use a new scratch bundle name; do not replace the retained
snapshot. Then `replay NEW_BUNDLE --bin "$root/opt/bin"` verifies the
whole new bundle. The `--row` option is for diagnostics on a single
1-based index and does not prove anything about the omitted rows.

## Checks

- Positive substitution at all 220 roots of the ten six-regular (3,7,22)
  controls satisfied every reconstructed clause.
- Six prior e119 inputs passed the pilot. Substituting row 2's proof for
  row 1's proof failed the index check; changing its index to match the
  tampered proof reached and failed `lrat-check`.
- Full bundle: 68 byte-identical CNFs, all 68 LRATs accepted by both
  `lrat-check` and `cake_lpr`; 2.12 CPU-s to pack, 4.91 CPU-s to replay.
  Logs and both negative controls are in `scratch/A/root-residue`.
