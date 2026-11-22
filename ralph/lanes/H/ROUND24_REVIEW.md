# Round 24: independent wing-alias audit

**Proposed H-040: Lean (local projection lemmas) + enum (physical alias
audit).** No new target exclusion, no new LRAT replay in H, and no
formal proof of the full D pipeline.

## Graph-to-projection dependencies

Fix an R(3) graph with exactly two deficient nonedges (codegree one).
D-028 supplies two disjoint deficient paths; in exact `K=2` these use
both deficiencies. Fix either path, tips `a,b` and middle `h`. Their
private shores `A,B` have eight sites each. The remainder `Q` has 21
sites. A wing site is adjacent to exactly one anchor, its own tip;
`h`'s other seven neighbors are in `Q`. A wing site's cross degree is
its codegree with the opposite tip, hence is 2 or 3: the other
deficiency is disjoint. In the full-wing binder, the wing sends
`128−2t` edges to Q, the three anchors send seven, so from degree 9
on Q one gets `2e(Q)=189−(128−2t)−7=54+2t`. This identity justifies
the full `t=17` binder, **not** a row in either universal alias.

For each pair of selected wing sites the known contribution is the
intersection of their *full* wing neighborhoods plus one for a shared
tip. Adjacent sites cannot co-occur in a Q column (triangle). Otherwise
the cap on total codegree is 3, and the global budget for a second
deficient pair is one. A pinned site has `8−d_F(site)` Q-neighbors.
A scope that keeps only an induced cycle must not strengthen lower
codegree demands due to omitted neighbors; nor does omitting them
justify subtracting a worst-case allowance from an upper cap.

- **Isolated hex.** No hidden co-neighbor occurs in a wing–Q return
  through a cycle site. There are six distance-two capacities 1 and
  three antipodal capacities 3: total 15. With 36 contacts to 21 sites
  the slack is zero. `hex_hub.make(1,0,1,1)` skips `e(Q)` entirely
  (`hex_hub.py`, `if edges:`); it does not set `e(Q)=0`. The old
  CNF and proof are referenced by two different parent keys.
- **One flap.** With one edge out of the cycle, retain its actual
  endpoint `z` and mark the cycle from the unique apex. Among the
  selected wing pairs, at least one site is on the cycle and so
  their hidden-wing intersection is empty. For `(z,q)` at most two
  hidden wing neighbors can contribute; the two synthetic stubs are
  a bound, not physical labels adjoining the cycle. This is the
  difference between the exact known term of `patchbind23.py:30`
  and the weak lower test of `patchbind23.py:37`. `flap23.formula`
  passes `None` for `qedges`, never the full-wing edge identity.
  Any I10 row must be on actual distinct physical sites (including
  the two implicit tips when used). These statements describe the
  dependency; this audit does not verify the arbitrary-I10 binder.
- **Alphabet and hub splits.** Write slack as the sum of unused pair
  capacity and `Σ_q (1 + binom(k_q,2) − k_q)`. The independent sets
  in C6 have size at most three; terms are 1 for `k=0,3`, 0 for
  `k=1,2`. With one flap the contact sum is 35 and slack is one. The
  loss is either an empty word, one of two alternating triples, or
  one unit of capacity on one of nine pairs. The rest are forced
  singletons and doubles, yielding the 12 decks. A hub neighbor set
  has seven distinct sites, with one or two contacts in each cycle
  column (codegree with `h` includes the tip and is nondeficient).
  Sorting those sites by membership within equal-word blocks is a
  relabeling, not identification of repeated sites or a completion
  automorphism. The cycle reflection fixes the apex and maps deck
  7 to 4; it does not assert symmetry of the completion.

## Independent controls and cover join

`WingProjection.lean` proves a common-neighbor partition, the asymmetric
visible interval bound, exactness with no hidden cycle neighbors, and
that retaining the sole flap endpoint gives this no-hidden condition.
The theorems do not derive D-028, codegree capacities, the contact
catalogue, CNF soundness, or the no-wing-hex theorem from scratch.
Pinned Lean/Mathlib 4.35.0 compiled this module and passed all four
targeted standard-axiom reports. Two cached Lake aggregate invocations
and the direct aggregate retry hit their wall limits; no fresh full
build or 378-report full scan is claimed. Round 23's successful full
build and 374 reports predate this module. No Mathlib source rebuild.

`check_wing_alias24.py` does not import a producer. It exhausts the
smaller C22 positive calibration: the eligible six-regular, cap-three
graphs have α=6 and produce 125 marked paths; of 52 induced hexes in their
private wings, 15 have one flap and 37 have two. All 15 one-flap plants
retain exact cycle counts, with three explicit adverse projection checks
on a small physical graph (drop the endpoint, keep an unjustified lower
bound at `z`, or reuse cycle exactness with two flaps).

After calibration, it independently constructs the zero-/one-slack
alphabets and matches those to D's numeric binder IDs *exported* into
`scratch/H/round24-deck-ids.json`. It iterates all `binom(21,7)`
physical choices separately on decks 1 and 4, recovers 5,672 and
5,413 subsets in nine cells each, and verifies the other seven cells
are zero. Reading the physical graph6 labels, it walks both directions
around each aliased hex and matches the resulting contact words and
precise receipt list. All 62 aliases cover exactly the intended seven
shapes. The 26 distinct archive IDs selected in this freeze are one
isolated, seven direct-flap, and eighteen hub-cell archives; two more
direct-flap archives were checked by D for the universal clause but
are not selected for this cover. All 73,877,286 selected bytes match
hashes and retained checker markers. Whole inventory joins contain
3,114 keys and 3,078 receipt IDs; the non-alias receipts are index-only
in H's run. This is independent transport and accounting, not a fresh
proof replay or independent regeneration of the 15-shape census.

Replay from the root:

```bash
(cd scratch/H && PYTHONPATH=../../ralph/lanes/D ../../opt/venv/bin/python -B -c 'import json; from flap23 import masks; from hex_hub import masks as isolated; print(json.dumps(dict(one_flap=masks(),isolated=isolated())))' > round24-deck-ids.json)
python3 -BS ralph/lanes/H/check_wing_alias24.py scratch/H/round24-deck-ids.json
bash ralph/lanes/H/build_private_signature.sh --old build R310
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 ../ralph/lanes/H/WingProjectionAxioms.lean
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 scripts/Axioms.lean
bash ralph/lanes/H/replay_wing_lean24.sh --targeted
```

## Ledger notes

Round 23 confirmations were imported exactly at the late-frozen cutoff.
`D23-t17` subsumes both m14 and m15, and none of the 24 duplicates
counts. `G23-h5` subsumes the provisional pilot and both interim whole
counts. F's wider sign attempts and caps are not complete regions. E's
dominant large missing role has its own singleton count: applying the
small-role `K−6` zero-contact allowance across all roles is invalid.
Current round-24 board-only messages and work in flight are not upgraded
to critic-confirmed rows. A24-shore and C-058/059 are staged from final
STATEs; both source freezes hash-check (`scratch/H/round24-{A,C}-freeze.log`).
Remaining denominator 238 near-regular MTF
distributions plus Case R is unchanged.
