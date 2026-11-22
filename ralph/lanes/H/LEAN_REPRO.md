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

## Round 4: fixed-root attachments and demands

`lean/R310/RootDemand.lean` adds four checked statements:

- `IsMTF.attachment_dominates`: every root neighbor's attachment
  dominates the exterior. Independence is the existing neighborhood lemma.
- `IsMTF.exists_attachment_for_demand`: every singleton exterior demand
  or nonedge with no exterior common neighbor lies in one attachment.
- `IsMTF.card_incompatible_demands_le_degree`: choose such an attachment
  for each demand, then an actual cross edge for each pair of demands
  forces different choices by independence. The resulting map into the
  root neighborhood is injective. No independence-number bound is needed.
- `IsMTF.total_edges_of_degree_six_residue`: with MTF, `alpha ≤ 9`,
  degree six and a supplied residual floor `L`, the graph has at least
  `L+48` edges. The existing MTF private-neighbor inequality gives 48.

Neither the finite catalogue nor its demand witnesses or LRATs are
formalized. The fourth theorem assumes the residual floor, so it is not
a Lean proof of e(H6)≥120. `FLOOR6_REVIEW.md` documents the external
dependencies of that floor and the exact distribution accounting.

From `lean/`, with the pinned cache and CPU 148 (or a permitted CPU):

```sh
export PATH="$HOME/.elan/bin:$PATH" LEAN_NUM_THREADS=1 LEAN_STACK_SIZE_KB=8192
ulimit -v 16777216
timeout 200 nice -n 5 taskset -c 148 lake --packages="$PWD/../scratch/H/packages-local.json" build --old R310.RootDemand
timeout 150 nice -n 5 taskset -c 148 lake --packages="$PWD/../scratch/H/packages-local.json" env lean -j1 -s8192 ../ralph/lanes/H/AxiomsRound4.lean > ../scratch/H/root-demand-axioms.log
python3 -S -B ../ralph/lanes/H/check_axioms.py ../ralph/lanes/H/AxiomsRound4.lean ../scratch/H/root-demand-axioms.log
timeout 275 nice -n 5 taskset -c 148 lake --packages="$PWD/../scratch/H/packages-local.json" build --old R310
python3 -S -B ../ralph/lanes/H/check_root_demand_control.py
```

The targeted and umbrella builds passed; no Mathlib source build. The
audit allows only `propext`, `Classical.choice`, `Quot.sound` and found
exactly four reports. The Python test has five tight C5 controls;
non-MTF C6/C7 fail the singleton/pair demand as expected. The ten known
six-regular order-22 graphs give 220 rooted controls, 3,300 singleton and
2,259 pair demands, and 28,866 incompatible pairs with disjoint attachment
choice sets. Logs: `scratch/H/root-demand-{build-v2,axioms-audit,integrated,control}.log`.

## Round 5: tight signatures, complete arms, degree-five residue

- `lean/R310/PrivateSignature.lean`: common-anchor independent-family
  bound, pair uniqueness given one full private cell, and the fixed
  order-40 degree-six equality consequence at `e(G)≤e(H6)+48`.
  There are six private cells of four and nine distinct double signatures.
  Applicable at e168/e120 and e169/e121; no residue floor or census.
- `lean/R310/CompleteArms.lean`: an outside vertex must hit a maximum
  independent set; a T-avoider in the specified complete-arm path cannot
  hit either wing. The complete-wing excess identity and 26-vertex bound
  assume the support data; the partition, graph premises and e(X) upper
  bounds are not in Lean.
- `lean/R310/ResidueDegreeFive.lean`: a nonadjacent degree-six pair gives
  residue degree five. If n6≥3 and e≤169, a minimum-degree-five order-33
  residue through e121 is necessary, assuming the published R(3,8)≤28.
  This reduction does not certify the finite residue search.

From the workspace root, with the pinned cache (the launcher enters
`lean/` and binds one permitted CPU; set `H_CPU` if needed):

```sh
bash ralph/lanes/H/build_private_signature.sh build --old R310
bash ralph/lanes/H/build_private_signature.sh env lean -j1 -s8192 ../ralph/lanes/H/AxiomsRound5.lean > scratch/H/round5-wings-axioms.log
python3 -SB ralph/lanes/H/check_axioms.py ralph/lanes/H/AxiomsRound5.lean scratch/H/round5-wings-axioms.log
bash ralph/lanes/H/build_private_signature.sh env lean -j1 -s8192 scripts/Axioms.lean > scratch/H/round5-wings-project.log
python3 -SB ralph/lanes/H/check_axioms.py lean/scripts/Axioms.lean scratch/H/round5-wings-project.log
python3 -SB ralph/lanes/H/check_private_signature_control.py
```

The integrated build and 12 targeted / 270 project axiom reports pass.
No Mathlib source build. The independent C13(1,5) control has 13 equality
roots, 52 double signatures, 1,872 common-anchor families (208 tight).
K2,3 shows why the full-cell hypothesis cannot be dropped. C's planted
degree-four controls and alpha counterexamples are in
`scratch/C/p3r5-complete-arms.log`. See `ROUND5_REVIEW.md` for premises.

## Round 6 degree-six global bridge and e168 neighbour profiles

The pinned-cache `build --old R310` passed. These theorems live in
`lean/R310/ResidueDegreeFive.lean`; no code from either enumerator is
imported. With the published Ramsey bound and the no-exterior-degree-five
input, the exterior degree is at least six. This implies the strengthened
codegree cap and the clique/count bound `n6 ≤ 2`. The e168 theorem assumes
an adjacent peer, no third degree-six vertex and residue floor 120.

```sh
bash ralph/lanes/H/build_private_signature.sh build --old R310 > scratch/H/round6-integrated.log 2>&1
bash ralph/lanes/H/build_private_signature.sh env lean -j1 -s8192 ../ralph/lanes/H/AxiomsRound6.lean > scratch/H/round6-targeted.log 2>&1
bash ralph/lanes/H/build_private_signature.sh env lean -j1 -s8192 scripts/Axioms.lean > scratch/H/round6-project.log 2>&1
sed '/^wall=/d' scratch/H/round6-targeted.log > scratch/H/round6-targeted-axioms.log
sed '/^wall=/d' scratch/H/round6-project.log > scratch/H/round6-project-axioms.log
python3 -SB ralph/lanes/H/check_axioms.py ralph/lanes/H/AxiomsRound6.lean scratch/H/round6-targeted-axioms.log
python3 -SB ralph/lanes/H/check_axioms.py lean/scripts/Axioms.lean scratch/H/round6-project-axioms.log
python3 -SB ralph/lanes/H/check_round6_scope.py
```

Five targeted and 275 project reports passed; only standard axioms.
The Python run checks key identities and calibrates the separate hand
refinement on C13(1,5) (52 ordered roots). See `ROUND6_REVIEW.md`.

## Round 8: completion bridges

The pinned Lean/Mathlib v4.35.0 cache-backed `build --old R310`
completed with no Mathlib source build. `R310.CompletionBridge`
contains the two domain-shrink preservation lemmas and two exact
window order/alpha lemmas; it does not certify an enumerator.

```sh
bash ralph/lanes/H/build_private_signature.sh build --old R310
bash ralph/lanes/H/build_private_signature.sh env lean -j1 -s8192 ../ralph/lanes/H/AxiomsRound8.lean > scratch/H/round8-lean-axioms.log 2>&1
bash ralph/lanes/H/build_private_signature.sh env lean -j1 -s8192 scripts/Axioms.lean > scratch/H/round8-project-axioms.log 2>&1
python3 -SB ralph/lanes/H/check_axioms.py ralph/lanes/H/AxiomsRound8.lean scratch/H/round8-lean-axioms.log
python3 -SB ralph/lanes/H/check_axioms.py lean/scripts/Axioms.lean scratch/H/round8-project-axioms.log
```

The 4 targeted and 284 project reports pass with only standard
axioms. The initial narrow build failed at an overly broad `simp`
call; `Finset.coe_sort_coe` and `Fintype.card_coe` alone fix it.
