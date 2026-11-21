# Pinned Lean build and OPB provenance on the flow host

The launcher `ralph/lanes/H/lean_round1.sh` checks the rev of every Lake
dependency checkout, moves package build products under `scratch/H`, and
generates a path-override manifest there. It does not replace the pinned
manifest or edit any dependency source. The path override avoids Git's
slow repeated worktree verification on this filesystem.

Use Lean 4 v4.35.0; mathlib's pinned commit is
`56a005855ea17e0b0958f73ec801ae140b0a1679`. The reproducible setup command
is `timeout 3120 taskset -c 148-149 bash ralph/lanes/H/lean_round1.sh`.
It uses `lake exe cache get`, then checks all Mathlib targets with
`--old --no-build`. The cache check visited 9,045 up-to-date targets;
no Mathlib theorem was built from source. Cache downloads (`.ltar`),
unpacked payloads and the path override live under `scratch/H`.
Cold extraction is I/O-bound and took about seven minutes after the
100-second probe; use the longer bounded run, not the probe cap.

`scratch/H/project-export-direct.log` records export through the actual
Lake-built `R310.Files` and `lean/scripts/EmitCubes.lean`, including
bytewise comparison and SHA-256 for all three OPBs. The R export has
99,701 rows and SHA-256
`bb887a7c81a7f588a84434e1924602b75e0266e7e48632b60967359d03877dd9`.
`scratch/H/pb-bind.log` additionally checks retained proof-input hashes
and all 189,418 rows of the PB input as R export plus 89,717 independently
regenerated augmentation rows. It reuses the accepted VeriPB/CakePB
chain; it does not prove unsatisfiability or supply a cover of SAT cubes.

`check_axioms.py` accepts exactly the requested theorem reports and only
`propext`, `Classical.choice`, `Quot.sound`. The test used Lean output for
`Nat.add_comm` and `propext`; a planted `sorryAx` was rejected. The existing
entry point is `lean/scripts/Axioms.lean`; the new declarations are listed
in `ralph/lanes/H/AxiomsRound1.lean`.

The full project succeeded in 634.70 wall seconds (823.78 CPU seconds)
after the cache check; the integrated rebuild with all three new modules
succeeded in 95.54 wall seconds. See `scratch/H/lake-build.log` and
`scratch/H/lake-integrated.log`. Direct `lean` aborted with a thread-create
error under the 16-GiB cap when importing all of `R310`; `lean -j1 -s8192`
with `LEAN_NUM_THREADS=1` and `LEAN_STACK_SIZE_KB=8192` passed. The audited
logs `axioms-one-legacy.log` and `axioms-one-new.log` contain exactly 263
legacy and 15 new reports. The `R310Cases` heavy table tags are separate
targets and were not rebuilt in this round.

## Round 3: P4 cross-edge and side counts

`R310.adjacent_window_cross_iff_disjoint` in `lean/R310/PathWindow.lean`
formalizes the local filter in `ralph/lanes/C/proofs/path_windows.md`.
Use the middle roots `midLeft=v1`, `midRight=v2` and endpoints
`first=v0`, `last=v3`. The decomposition into D0 through D3 supplies
`hCover`: D0 and D1 see `first`, D2 and D3 see `last`. The preceding
endpoint lemma supplies `hSpan`, not assumed for an arbitrary codegree
path. The middle window is `A`, and deleting both endpoint closed
neighborhoods from `A` gives the overlap `X`. The wing membership
hypotheses exclude the endpoint itself and place both vertices in `A`.

If an opposing wing pair has a common neighbor, triangle-freeness
excludes any neighbor of either endpoint as that witness. This excludes
the endpoints themselves by `hSpan`; `hCover` then excludes the open
middle neighborhoods, and wing membership excludes the middle roots.
Thus a witness lies in `X`. The proof uses `IsMTF.exists_common` for
distinct nonedges and uses triangle-freeness for the other implication.
This proves the precise mask test, not the block decomposition, the
2,454→1,356 finite filter, P4 exclusion, or P5 coverage.

`R310.card_add_unhitIn_le_indepNum` and
`R310.card_add_unhitIn_add_one_le_indepNum` check the two generic
side-counting arguments in `P4_SIDE_REVIEW.md`. For the strengthened
outer-block row, the opposite middle root must be outside and
anticomplete to both the base and the chosen group; it need not avoid
the other boundary block. The projection covers all actual edges from
the chosen group to the independent base. These lemmas check neither
CNF generation nor certificate coverage.

After the pinned setup, run from `lean/` on one allowed CPU (replace
`148` if the CPU affinity changes):

```sh
export PATH="$HOME/.elan/bin:$PATH" LEAN_NUM_THREADS=1 LEAN_STACK_SIZE_KB=8192
ulimit -v 16777216
timeout 300 nice -n 5 taskset -c 148 lake --packages="$PWD/../scratch/H/packages-local.json" build --old R310.PathWindow
timeout 180 nice -n 5 taskset -c 148 lake --packages="$PWD/../scratch/H/packages-local.json" env lean -j1 -s8192 ../ralph/lanes/H/AxiomsRound3.lean > ../scratch/H/p4-lean-axioms-final.log
python3 -B ../ralph/lanes/H/check_axioms.py ../ralph/lanes/H/AxiomsRound3.lean ../scratch/H/p4-lean-axioms-final.log
python3 -B ../ralph/lanes/H/check_p4_cross_control.py
```

The final targeted build and audit used 54.56 CPU-s together. The finite
controls cover all 42 oriented C21 P4 spans (wing nonedges), the C10
cross-edge case, and two counterexamples to dropping the maximality or
the coverage premise. Both side rows hold on 164 independent C21
subsets counted with side labels (26 tight nonempty outer bounds).
Logs: `scratch/H/p4-lean-side-build.log`,
`scratch/H/p4-lean-axioms-final-audit.log`, `scratch/H/p4-cross-control.log`.
No rebuild of the full Lean project, Mathlib, or PB artifacts was needed.
