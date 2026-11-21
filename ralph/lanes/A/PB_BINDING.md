# Bind the retained PRc7 base check to a full Lean export

This is a provenance task for the old SMS base only. R(7) is already closed
by the separate packing trace; do not regenerate cubes. Round 1 ran the PB
check successfully against `scratch/H/emit/out/cube_R.opb` (provisional) and
`scratch/A/rc7/Rc7b.cnf`; see `scratch/A/rc7/base-cert.log`.

After H produces the actual `R310.Files` export and confirms its provenance,
run from the workspace root:

```sh
root=$PWD
(cd scratch/A/rc7/base-cert && sha256sum --strict -c "$root/ralph/lanes/A/PB_ROUND1.sha256")
python3 -B ralph/lanes/A/bind_base.py scratch/H/project-export/out/cube_R.opb \
    scratch/A/rc7/Rc7b.cnf scratch/A/rc7/base-cert
```

The binder checks the raw SHA-256 of the export and base against the original
check log, independently regenerates the 89,717 PRc7 case rows (six forced
edges, nine units fixing the codegree-7 pair, definitions and at-most-seven
constraints for the common-neighbour auxiliaries, two `e(X)=85` bounds),
and compares all 189,418 ordered constraints in the original PB proof input
with export plus augmentation, stripping proof labels and whitespace only.
These additional assumptions are justified by the hand/Lean reduction rather
than emitted as part of `cube_R.opb`. Do not relabel the fresh SMS cube runs
based on this bind; they never had a checked cover.

Control: all comparisons passed for the provisional input, see
`scratch/A/rc7/bind-provisional.log`. A pass for a given file establishes
byte equality and composition, not that the caller really obtained that file
from a full `R310.Files` build. The retained proof digests were recorded in
round 2; the round-1 check log pins the provisional cube and CNF hashes.
