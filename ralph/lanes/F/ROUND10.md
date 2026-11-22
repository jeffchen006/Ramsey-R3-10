# Round 10 — a score floor for the mixed unsigned quotient

**Result submitted for review.** Let a triangle-free graph on 40 vertices have
at least 161 edges, degrees in `[4,9]`, and a fixed-point-free involution. If
the quotient of its 20 fibers has a permutation of cycle type `(8,8,4)`
preserving all vertical-edge bits and all inter-fiber matching multiplicities,
**every such graph has at least 25 independent ten-sets** (hand + enum,
replayable finite GF(2) certificates). The signs need not admit any rotation.
Thus this family cannot improve or tie lane F's score of 24. Its sampled
minimum is 178 at e180, **not** a claim of optimality. A separate zero-decision
cover has checked LRATs (hand + enum + cert). Neither conclusion excludes all
free involutions, any entire edge-count case, or any entire degree distribution.

## Complete source and independent count

Write the blocks as A, B of length 8 and C of length 4. Each block has its own
vertical bit and a symmetric word of internal weights. The three cross words
are `W[B−A]` modulo 8, `U[C−A]` and `V[C−B]` modulo 4. If the physical
degrees on them are `a,b,c`, then `e=8a+8b+4c`. No maximality assumption.
A double matching with a vertical at either end or a common occupied neighbor
forces a triangle. Without such an obstruction, crossing all single matchings
gives a triangle-free lift. Thus it suffices to enumerate the unsigned words
that allow this all-crossed lift; the later signing search is unrestricted.

First, `mixed_source.py` counts without materializing any target quotient. For
each cross triple, triangles meeting all three blocks are decided. Each single
internal word then has two compatibility tests, one per incident cross word.
The remaining choices of the three internal words are independent for fixed
degrees, so the count is a product. The producer takes cross-word orbits under
simultaneous multiplication by a unit and independent changes of origin, with
the common shift removed. It does not exchange unequal blocks or identify
internal words under the remaining stabilizer. The counted source is **375,974**
profiles at the cross representatives, **21,537,080** labelled profiles.

`mixed_count.cpp` independently enumerates the *raw* three cross words, with
no orbit reduction and no generator imports. It constructs physical all-crossed
adjacency masks. Test the neighbors of the first vertex of a block for an
internal triangle in each two-block test; rotation and the sheet swap act
transitively on physical vertices of that block in the all-crossed graph.
Test the three-cross-only graph at the first A vertex for triangles using
three blocks. These cases cover every triangle. The counts agree for every
one of the 14 **ordered** degree triples, and on the order-10 and order-20
controls. Edge-bin totals (labelled):

| e | 164 | 168 | 172 | 176 | 180 |
|---|---:|---:|---:|---:|---:|
| Count | 7,275,808 | 5,447,624 | 4,724,752 | 2,216,288 | 1,872,608 |

`mixed_cover.cpp` checks the actual rotation, triangle-freeness, degrees,
declared cross-orbit sizes and every permutation from every row to its signed
proof input, including verticals. It verifies distinct input words and that
different cross-representative words have disjoint cross orbits. Within one
cross representative choose one fixed transport to each cross image: distinct
internal triples still have distinct images. Thus the sum of the verified orbit
sizes counts a disjoint subset of the physical census; equality in every bin
proves coverage. There are 3,363 cross representatives and 230,054 cross images
with at least one legal internal choice. Ten source rows map to seven old
inputs, R8 indices `3,20,35,44,96,97,98`; all ten maps are checked. The other
375,964 maps land on 132,446 new proof inputs. These are proof-input counts,
not a claim about distinct 40-vertex graphs. No prior proof is modified.

## Why the score bound holds

A support consists of full fibers D (both vertices in the set) and single
fibers S, with `2|D|+|S|=10`. D has no vertical, no edges into any occupied
fiber, and S has no double. On the single-edge graph induced on S, independent
side labels obey `label(i) XOR label(j) = x(ij)`, where `x=1` means a parallel
matching. The support contributes exactly `2^(number of components on S)`
independent sets if all cycle parities vanish, otherwise zero. Different
supports count disjoint sets. Triangle-free signs have even parity around
every triangle of singles.

**Static bound:** if all the cycles on S are in the span of the global
triangle rows, the contribution is forced for every signing. Independent
rank audit of 1,989,726 supports establishes a positive bound for 132,259 of
132,446 new inputs, with **132,068** already at 25. For the separate
zero-decision route, `mixed_sat.py` refutes all 187 zero-bound new inputs.
Each support may be translated around the **quotient**, since all translated
supports are legal, not because the signs are symmetric. `mixed_replay.py`
checks the semantic trace and replays each LRAT with `cake_lpr` and `lrat-check`,
also replaying the seven earlier inputs. No SAT decision capped at zero.

**New weighted parity certificates:** work inside any affine cell of signing
space. A rank-one support contributes its weight exactly when one affine
character `h(x)` is zero. If a collection of such supports cannot all have
`h(x)=1`, at least one contributes. An easily checked witness of this is an
XOR of the selected characters equal to a constant *different* from the
parity of the number of selected supports. At the root all constants are zero,
so this is an odd linear dependence. To claim `g` sets from such a conflict,
charge `g` against **each** participating support; cumulative charges to a
support may not exceed its exact multiplicity. For any signing each conflict
has an active support that can pay its charge, proving that the sum of the
claimed gains is a lower bound. A forced rank-zero support pays directly.
If this does not reach 25, split on a nonconstant character, cover both
values, and take the smaller child bound.

The producer is `odd_support.cpp`. The independent `odd_check.py` reconstructs
the original, **ungauged** edge variables, triangle row space, actual cell
restrictions, support cycles and component weights; it verifies every
capacity and XOR conflict. `split_check.py` consumes both children of each
split and requires a consistent nonconstant decision on each path. The
starting queue and all subsequent row joins are checked by `mixed_final.py`:

| Stage | Rows | Reach 25 | Next | Witness leaves checked |
|---|---:|---:|---:|---:|
| Static on new inputs | 132,446 | 132,068 | 378 new + 7 old | — |
| Unconditioned rank-one packing | 385 | 337 | 48 | — |
| Two-sided trees capped at depth 8 | 48 | 44 | 4 | 403 |
| Two-sided trees capped at depth 15 | 4 | 2 | 2 | 200 |
| Final two trees | 2 | 2 | **0** | 54; greatest actual depth 23 |

The low values in *intermediate* capped leaves are not graph witnesses. No
cap or unexamined row remains in the combined threshold cover. The score-25
result uses the numerical certificates, not the LRATs that only decide zero.

## Calibration, nearness and cost

- Order 10: independent physical exhaustive enumeration over all signed
  realizations, 24 raw cubic quotients, 14 source rows. All 14 score lower
  bounds agree with the exact minima at k=4 **and** k=5. The 14 order-10
  positives passed the gate. Order 20: 3,640 raw, 335 proof inputs; all four
  positive `(3,7,20)` graphs passed the gate. On **each** of these four, even
  the optimal rotation-constant signing in the specified labels was not a
  solution (I7=20,24,8,8); unrestricted sign descent reached zero. We do not
  identify signings that become symmetric only after changing fiber labels.
- An invalid square-span certificate with a missing spoke was rejected. Six
  other corruptions detected overdrawn capacity, a missing conflict member,
  truncated cover, zero split, false leaf total, and swapped roots. On an
  actual n38 positive and the e178/e179 score-24 witnesses, shallow trees did
  **not** assert 25; independent recounts gave 0,24,24 respectively.
- Systematic 385-input target pilot (source ranks 269 modulo 977): 384 had a
  static bound ≥25; the remaining zero case was dual-checked. On those same
  inputs the old score-24 decision search returned 383 no, two node caps.
  Cost 0.08 vs 0.49 CPU-s on this batch only. For the later, harder six-row
  pilot the old 100k-node method settled 4/6 vs 5/6 depth-eight trees;
  respective measured costs 2.34 and 2.72 CPU-s. No general speedup claimed.
- Nearness: both the exact orbit-constant baseline witness and the unrestricted
  descent witness were recounted for every sampled row. 10/26 strict gains
  on the broad pilot, minimum 1,780/e168; 40/48 strict gains on the hard queue,
  minimum **178/e180** (from 1,768 on that row). No 40-vertex candidate. Lane
  best remains 24/e178,e179 in a different family.
- Estimates were recorded before expansion in `production_estimate.txt`.
  31 completed supervisors, peak three of four slots; **595.16 CPU-s**
  (0.16532 core-h), including builds, controls and replays.

## Replay

Artifacts are in `scratch/F/r10/`, scripts in `ralph/lanes/F/`. From the
artifact directory check `sha256sum -c round10.sha256`; its source-code
and older dependency paths are relative to this directory. For independent
review, copy/symlink read-only inputs into a reviewer-owned equivalent layout
before executing tools that write receipts. Keep the usual solver limits.

1. Build `mixed_count.cpp` and `mixed_cover.cpp` with `g++ -O3 -std=c++20`
   **without** `-DNDEBUG`. Run `./count 8 4 9 161` and compare to `target.raw`;
   `./cover target 8 4 9 161 1` checks every row and map against those totals.
2. Set `PYTHONPATH` to the lane directory. `python3 -B -c 'from block_audit
   import verify_bounds; verify_bounds("target",10)'` (one shell line) checks
   the static lower bounds. `python3 -B ../../../ralph/lanes/F/mixed_final.py`
   verifies the full score-25 queue, every stage join and leaf, mutations and
   actual sampled scores. Compare `threshold.receipt` to the manifest.
3. Independently of step 2's threshold trees, `python3 -B
   ../../../ralph/lanes/F/mixed_replay.py` regenerates `fresh.receipt` and
   `old.receipt` for the zero decision (187+7 dual replays). Main logs:
   `full_cover.stdout`, `full_bounds.stdout`, `lrat_replay.stdout`,
   `final_bind.stdout`; controls: `signed_control.stdout`, `mid_signed.stdout`,
   `checker_controls.stdout`, `outside_controls.stdout`, `control_cover_replay.stdout`.
