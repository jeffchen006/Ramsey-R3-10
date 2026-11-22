# Round 9: two ten-cycles on the unsigned quotient

**Claim (hand + enum + cert; pending critic review).** No `(3,10,40)` graph has a
fixed-point-free involution for which the full weighted 20-fiber quotient admits
an automorphism of cycle type `(10,10)`. Vertical bits must be preserved.
**The rotation need not lift to an automorphism of the 40-vertex graph.**
This extends F-011: the square of a 20-cycle acts by two 10-cycles. It covers
both an irregular degree pattern at 170 edges and a regular one at 180, not
either edge count in general. A graph with an involution alone is not excluded.

## Exhaustive source

Index the two cycles A and B mod 10. The quotient is completely specified by
two reflection-symmetric within-block weight words (with vertical bits at
offset zero) and an arbitrary cross word `C[j-i]` from `A_i` to `B_j`.
Each off-diagonal weight is 0, 1, or 2. Every vertex above A has the same degree
`a`, likewise `b` above B; `e=10(a+b)`. The problem's `e>=161` and maximum
degree 9 force `(8,9)`, `(9,8)` or `(9,9)`. No maximality assumption.
A double weight with an occupied common neighbor or an endpoint vertical
forces a triangle for all signs. Otherwise the lift with all singles crossed
is triangle-free: a triangle with singles only would lie in a bipartite graph.

We first treated the dihedral subfamily with identical within-block words.
Here `A_i <-> B_{-i}` is an additional *quotient* automorphism. We then dropped
that condition. Producer `biblock_source.py` reduces affine relabelings and
uses pynauty to suggest quotient isomorphisms; every suggested map is recorded.
The independent audit does not call pynauty or import a source generator.
It checks each map entry by entry, and expands the maps' domains by units,
offset shifts and swapping the two within-block words. The latter is justified
by swapping blocks *and* negating indices, preserving the cross word. Orbits
must be disjoint at this expansion stage.

`block_count.cpp` separately enumerates every labelled cross word. For each it
tests all degree-eligible single-block words on the **physical all-crossed
lift**, leaving the other block empty internally. Every triangle has two
vertices in one block and occurs in one of these tests. Rotation and the free
involution let the tester inspect the neighborhood of the first vertex of the
tested block; reversing the cross word for the other block is isomorphic by
negating indices. Thus legal A and B words combine by ordinary multiplication.
The raw labelled counts match the expanded, structurally checked cover exactly:

| Degree pair | Labelled full two-block profiles |
|---|---:|
| 8,9 | 118,536 |
| 9,8 | 118,536 |
| 9,9 | 150,651 |
| **Total** | **387,723** |

7,726 affine two-block rows map to 6,765 new terminal inputs or to previously
treated ones (6,816 new-side maps, 910 inherited-side maps). The nested
dihedral source has 28,305 labelled profiles, 903 affine rows and 623 new
terminal inputs; it also maps to all 99 F-011 inputs (frozen, not searched).
`block_audit.py` checks the 99 source hashes against the critic's confirmed
F-011 receipt. We require a cover, not a claim of pairwise nonisomorphism.

## Why one support can rule out every signing

Use a bit on each single edge, `1=parallel`. Triangle-free signings annihilate
every single-edge triangle boundary over GF(2). Fix a candidate independent
support using fibers D twice and S once, `2|D|+|S|=10`. There may be no
vertical in D, no occupied weight incident to D inside the support, and no
double among S. On the single-edge graph H induced by S, independence amounts
to `label(i) XOR label(j) = sign(ij)`. Exactly `2^components(H)` labelings
exist if the signing annihilates every cycle of H, and none otherwise.

In particular, if every cycle of H lies in the span T of the quotient's
single-edge triangle boundaries, the count is forced for **every** triangle-
free signing. Different `(D,S)` describe disjoint sets of physical ten-sets.
`forced_support.cpp` finds distinct such supports up to a bound of 25 using
path voltages after Gaussian elimination. Independent `block_audit.py` uses no
forest gauge or path voltages: it checks support legality and verifies
`rank(T) - rank(T projected outside H) = dim cycle(H)`. The intersection of T
with the edge space of H is already inside its cycle space, so this dimension
test is sufficient. It checks multiplicities and rejects duplicate supports.

| New source | Rows | Bound ≥25 | Bound >0 | Extra dual LRATs |
|---|---:|---:|---:|---:|
| Equal within-block words, after F-011 | 623 | 619 | 620 | 4 |
| General two-block source, after the preceding cases | 6,765 | 6,657 | 6,707 | 58 |

The 62 LRATs include the 61 zero-bound rows and one redundant bound-20 row.
All use the R8 projected-supported-cut semantics, with only genuine quotient
automorphisms used to propose extra cuts, **never** imposed on the signs.
All 62 got semantic replay and `lrat-check` + CakeML `cake_lpr`; a second
full replay gave byte-identical receipts. Thus no target input is inferred
from a cap. For the separate I10≤24 question only, the old search capped on
dihedral row 347; we do **not** claim a universal lower bound of 25.

## Controls, comparisons, and replay

- Direct oracle on all 65,536 labelled free-involution order-eight graphs:
  112 legal two-block profiles, 40 reduced inputs, every zero decision and all
  40 unconditional lower bounds matched exact minima for I4. The dihedral
  subcontrol has 11 reduced inputs with exact bounds. Seven adverse mutations
  were rejected, including a non-forced square cycle and a crossed LRAT.
- Order-16 positive control: 41 rotation-only quotient inputs; three recovered
  triangle-free graphs with no independent six-set passed the gate, including
  an irregular degree-(4,5) lift. The special eight-fiber dihedral control is
  two single K4s with a double perfect matching between them: it is not a
  cyclic quotient (its automorphisms act by the same permutation on the two
  cliques, optionally swapping them, so none has order 8).
- Nearness (enum, sampled): compare the best lift with **orbit-constant signs
  in the specified labels** to descent in unrestricted triangle-preserving sign
  directions on that same quotient. We do not identify all switching-equivalent
  symmetric lifts. Dihedral: 7/24 strict gains, minimum observed I10=80/e180.
  Additional general rows: 11/21 strict gains, e.g. 42,110→6,868; minimum sampled
  I10=2,180/e170. All 45 resulting graph6 witnesses were independently recounted
  and checked for quotient, involution and triangle-freeness. F's overall
  24/e178,e179 is unchanged. No candidate or submission.
- Matched cost: on the 20+21 systematically spaced pilot inputs old relift
  settled score ≤24 on all 41; the forced bound alone settled 20/20 and
  20/21 (the remaining row has a positive bound of only two). In 16 repeats
  the two pilot batches took 0.16/0.06 CPU-s respectively with the old solver,
  0.08/0.13 CPU-s with the new test. **No general speedup claim**; the gain is
  a short auditable obstruction without enumerating signings. Full general
  source estimated ~13 CPU-s, actual 3.61; lower-bound scan estimated ~3 s,
  actual 2.47; 58 residual proofs estimated ~15 s, actual 11.46.
- Data and integrity manifest: `scratch/F/r9/round9.sha256` (paths relative to
  `scratch/F/r9/`). From that directory `sha256sum -c round9.sha256`. Main
  receipts: `hardproof.receipt`, `bizproof.receipt`, `frozen_audit.stdout`.
  Source and bound audit commands: `python3 -B ../../../ralph/lanes/F/block_audit.py source`
  and `python3 -B ../../../ralph/lanes/F/block_audit.py bounds`, with solver
  limits as in `STATE.md`. The latter rewrites receipts; for independent review
  use an audit workdir with the same relative inputs. Independent raw count:
  `block_count 10 8 9 17`. Calibration: `final_controls.stdout`, `bictl.gate`;
  matched-target logs: `speed_pilot.stdout`, `witness_replay.stdout`.
