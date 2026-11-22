# Round 8: cyclic unsigned quotient, unrestricted signs

**Claim (hand + enum + cert, pending critic review).** No `(3,10,40)` graph
has a fixed-point-free involution whose 20 two-vertex fibers can be put in a
cyclic order so that translation by one preserves both the vertical-edge
bits and the numbers of edges between every pair of fibers. There is **no**
translation restriction on the matching signs. This is not the old Cayley
exclusion: the cycle is only required on the unsigned quotient. It is not
an exclusion of all fixed-point-free involutions or all of regular case R.

## Why these are all the inputs (hand + enum)

An involution leaves zero, one or two matching orbits between two fibers.
Write their number as 0, 1 or 2. A vertical bit gives the edge inside a
fiber. With cyclic fiber translation the degree is constant; the reported
edge lower bound 161 and degree upper bound 9 force degree 9. Thus a
profile is a vertical bit `v`, weights `w1,...,w10` in `{0,1,2}`, and
`v + 2(w1+...+w9) + w10 = 9`. It determines the entire unsigned quotient.
Multiplication by any unit mod 20 simply relabels fibers. We use only
those equivalences; we do not need a full isomorphism classification.

A double crossing with a vertical at an endpoint, or with an occupied
common neighboring fiber, forces a triangle for every signing. If these
obstructions are absent, crossing every single matching gives a triangle-
free lift: a triangle without a double would have to lie in a bipartite
graph (all edges cross between the two sides). One generator uses this
structural test; another enumerates multisets of distances in the degree
budget and explicitly builds that lift. They agree on 984 degree profiles
before the triangle test, 327 legal profiles and 99 unit-orbit rows (984
is counted by the independent checker). Every one of these 99 rows has
a dual-checked LRAT refutation. No cap or inferred extrapolation.

## What each proof proves (hand + cert)

For a single matching let `x=1` denote parallel and `x=0` crossed. Three
single edges form a physical triangle exactly when the sum of their signs
is odd. Hence each quotient triangle gives an even-parity row. Label swaps
in the fibers toggle incident signs, so one may set signs to zero on a
forest. The proof checker requires the pinned edges to be acyclic.

An independent ten-set may fill fibers `D` twice and use fibers `S` once,
where `2|D|+|S|=10`. For a supported cut the checker requires no vertical
in `D`, no nonzero weight joining `D` to another occupied fiber, and no
double inside `S`. On a single edge `ij` in `S`, independent labels solve
`label(i) XOR label(j) = x(ij)`. Such labels exist exactly when all cycle
sums vanish: choose a root label in each component and propagate along
a tree. Thus **avoiding** this independent set support requires at least
one cycle parity to be one. If the induced single-edge graph on `S` is a
forest, avoiding it is impossible even before branching on signs.

The generator (`cyclic_proof.py`) takes a signing from incremental SAT,
extracts up to two projected independent-set supports, translates the
supports around the quotient, and adds the necessary cycle clauses. It
does **not** assume the current signing or any completion admits that
translation. Only a subset of all possible supports is needed to refute
an input. XOR auxiliaries are defined by four ordinary clauses.

The separate checker (`cyclic_check.py`, no producer imports) reads the
trace, checks each support, expands every parity to a bit vector on the
original edge variables, checks even incidence and cycle-space dimension
by matrix rank, and compares truth-table clauses with the exact DIMACS
multiset. A contradiction from a forest support uses opposite units on a
fresh variable. It independently runs both `lrat-check` and `cake_lpr`.
There are 7,488 recorded supports in the 99 target formulas. The second
complete replay reproduced the first hash receipt byte for byte.

## Controls and matched pilots

Artifacts below are relative to `scratch/F/r8/`.

| Label | Measurement | Evidence |
|---|---|---|
| enum | All 65,536 labelled involution-compatible n8 graphs scanned. Ten legal cyclic quotients; 50 relift decisions agree with direct optima. At ceiling zero, 9 dual LRATs and one positive match the oracle. | `small_oracle.stdout`, `small.expected`, `small.receipt.tsv`, `semantic_small.stdout` |
| enum | At n38, degrees 6–9: 591 legal labelled distance profiles, 67 unit-orbit inputs at zero, one positive row, 66 no, no caps. All nine known cyclic connection sets reappear via one profile orbit; both the original relift and projected CNF produce gated order-38 witnesses. This is not a census of all signings on the positive row. | `cyc38.stdout`, `ctl_all.stdout`, `ctlproof2.{log,gate}` |
| enum | Exact radius-two sparse sign edits about one best abelian lift of each of the 12 pilot rows. Two strictly improve: 644→504 and 1048→632. Across rows the best remains 240 (not proved optimal for arbitrary signs); overall F best remains 24. Edits have zero triangle syndrome; translation deduplicates edits only after explicitly confirming an automorphism of that starting lift. Small oracle: 16 graphs/84 edits; n38 controls 54→0 and 72→0, both gate. | `shell_control.stdout`, `shell.ctl.gate`, `shell_pilot.stdout`, `shell.{5,9}.2.g6`, `target.meta.tsv` |
| enum / estimate | At zero the previous parity tree exhausts 11/12 pilot rows and caps on one at 10,000 nodes. New formula resolves all 12 with LRATs in 1.13 CPU-s; suffix estimate 8.2 CPU-s, actual 6.92. No broad heuristic run. | `zero.pilot.log`, `cnf_pilot.{stdout,time}`, `proof_cost.txt`, `cnf_suffix.{stdout,time}` |
| cert | 12 pilot + 87 suffix proofs, regenerated coverage, independent CNF semantics and two LRAT checkers on each. Seven negative controls reject: missing/duplicate orbit, incomplete cycle rank, noncycle, cyclic gauge pins, flipped CNF literal and crossed LRAT. | `target.receipt.tsv`, `frozen_replay.stdout`, `mutation.stdout`, `round8.sha256` |

The initial small proof export used a literal empty clause already present
in the input; CaDiCaL then emitted an empty proof that `lrat-check` did not
accept. No such bundle is counted. `smallproof2` and all target bundles
use the opposite-unit encoding and both checkers. Bounded nearness probes
at 23 and 239 had respectively 4 and 6 capped rows (`target_pilot.stdout`);
those are open at those ceilings and do not enter the zero-score exclusion.

## Replay and handoff

From a reviewer-owned scratch directory with `ROOT` set to the workspace
root, one slot under the usual resource wrapper suffices:

```
python3 -B "$ROOT/ralph/lanes/F/cyclic_check.py" target \
  --data "$ROOT/scratch/F/r8" --receipt "$PWD/F-r8.review.tsv"
cmp F-r8.review.tsv "$ROOT/scratch/F/r8/target.receipt.tsv"
```

The source and CNF/LRAT/trace hashes are bound by `target.receipt.tsv`;
`round8.sha256` binds that receipt, the scripts, controls, logs, all target
proof artifacts, and the unchanged 33 prior n38 representatives. All 16
registered jobs ended; 34.35 CPU-s (0.00954 core-h), at most two slots.
No graph submitted. Do not search this source or the earlier local trades
again. A distinct noncyclic unsigned source needs fresh controls and a
matched target improvement before a larger launch. Request H/critic review
of the scope and proof bundle, not more cores.
