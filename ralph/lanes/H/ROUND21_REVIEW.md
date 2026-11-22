# Round 21 — graph padding and scoped ledger

## H-036 (Lean; pending critic)

`lean/R310/PrivatePadding.lean` defines a site's actual contacts as
its adjacent vertices in `Graph.neighborFinset root`. The general
`root_two_anchor_padding` proves that any independent set of exterior
sites supported on two root neighbours can be augmented by every
unused root neighbour. The exterior condition makes the sets disjoint;
triangle-freeness makes the root neighbourhood independent; the exact
contact filter rules out every edge to the unused neighbours. Lean
counts the disjoint union and bounds it by the global independence
number.

`private_grid_row_bound_of_root_contacts` specializes to degree six
and global alpha at most nine. The marked anchor and the peer lie in
the neighbourhood and are distinct, so the unused set has size four
and every independent subset of the two cells and the optional double
site has size at most five. Different contact classes are disjoint;
each singleton class with the double class has a common neighbour,
so each is independent and the double class is isolated in the local
graph. An edge from a grid site to a physical partner in the peer
cell is an actual contact at the peer, which its opposite singleton
label determines. Apply H-035 and H-034 to derive the noncross
row margin `s−t ≤ 1−[row=crossRow]`; transpose for columns. Neither a
local cap nor a matching is assumed. The theorem still asks for the
equality populations, exterior membership, the actual contact classes,
and exclusion of the crossed column from the peer's private cell.
It does not prove the outer equality classification, bind any SAT
formula or enumerate alignments.

Independent literal controls: C13(1,5) has alpha four and all 78
root/anchor-pair tests attain the padded cap. Artificial degree-four
and degree-six graphs check both crossed and off-cross tight margins;
the degree-six graphs have local alpha five and attain matchings four
and three, respectively. With only three matches at the crossed row
and a single extra contact at its unmatched site, the graph is still
triangle-free with global alpha nine, but the putative local set has
alpha six and cannot be padded with all four anchors. This adverse
control fails the exact-support premise, not the conclusion under the
premises. In both degrees the controls reconstruct the physical wing
crossing and contacts directly from edges rather than assigning masks.

```sh
python3 -SB ralph/lanes/H/check_private_padding.py
bash ralph/lanes/H/build_private_signature.sh --old build R310
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 -DElab.async=false ../ralph/lanes/H/AxiomsRound21.lean
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 -DElab.async=false scripts/Axioms.lean
python3 -SB ralph/lanes/H/check_axioms.py ralph/lanes/H/AxiomsRound21.lean scratch/H/round21-axioms-targeted.log
python3 -SB ralph/lanes/H/check_axioms.py lean/scripts/Axioms.lean scratch/H/round21-axioms-project.log
sha256sum -c ralph/lanes/H/ROUND21.sha256
```

Use fresh log paths when replaying. Pinned Lean/Mathlib v4.35.0 and
the existing Mathlib binary cache; only the new module and aggregate
rebuilt. Strict allowlist passes all 3 targeted and 362 project
reports. Timed Lean work and final controls: 144.75 CPU-s including
two failed elaborations (0.04021 core-h), peak 3,453,896 KiB. No SAT,
board enumeration, candidate or detached jobs.

## Ledger and evidence priority

Imported all 12 confirmed round-20 decisions. Unlike the round-19
referee's sample, the critic replayed the complete G-019 chain: all
477,142 validated catalogue entries, 118 feasible envelope cores,
984 unrooted expansions, and no outer survivors. A's independent
expansion also distinguishes 985 rooted orbits from 984 unrooted
classes. G-019 stays `pub + enum`, and G-021's `n6≤2` still requires
MTF and that enumeration. G-056 closes only the marked aligned `h=8`
slice. E's 32 checked physical IDs include 16 fresh IDs, not 32 new
proof credits; D's three marked support zeros are not kernels; F's
435 marginal footprints and 1,979,210 unsigned joints are different
units; C's fifth-gate test cut no right keys.

Round 21 is pending. G adds 184 scoped `h=7` context keys if accepted
(235/1,213, leaving 978); A's comparison denominator is exact but
there is no matched fixed-alignment timing. E certifies its last 115
physical IDs; if the critic accepts the branch cover, only conditional
mixed core 1 closes, leaving cores 6, 9 and 18. D cuts nine further
marked supports, B tightens only the all-tight layer shape, C shows a
shared-degree obstruction only on a calibrated toy, F cuts none of
14. Best narrow closure evidence is E; best coverage per receipt is G,
subject to the cost and proof-size tail. No global debit: 238
near-regular MTF distributions plus R, ten conditional U88 keys, and
four conditional mixed cores at the last accepted snapshot. No flow
graph. The limited literature recheck is in `LIT.md`.
