# Round 13 — ledger transition, exact thresholds, Lean

## Ledger capture

Imported `ralph/critic/round_012.md`, including late C/D/G and the two
successful scouts. T's requested `review/ideas/r012_T.md` does not
exist; the critic records failed T/referee runs and no GAP to adjudicate.
N-003 is an MTF d6 residue floor unpinned in total edges. The catalogue
argument uses the **published 14,395** all-graph order-33 through-e121
denominator, not completion of a particular generation route. The 11
old edge-pinned proofs are replaced, not counted as unconditional.
The e108 count **2,104,146 / 2,104,151** is a separate order-32 family;
B's remaining five plus the reducible extension-cover obligation both
matter for floor 109. E-032 closes core 16 only; eight mixed cores
remain in the reviewed ledger. No E fixed-point case is closed by it.

## Independent case and t9 binding

`check_round13_thresholds.py` independently selects the low-edge cuts
from the frozen 278 baseline and compares both sets against critic TSV
manifests and the scout delta. Exact 20+19+1, including `(170,2,7,0,31)`;
all ten inherited U88 keys unchanged, none has n6>0. The surviving e170
d6 distribution count is 9 single + 7 adjacent-pair; the adjacency is
the inherited G-021 consequence, not something the CSV proves. No
additional removals for earlier e168 strips or t9 bounds.

Exact replay independently sums integer-scaled multiplier rows and
constructs the minimizing box corner, with interval sanity checks for
zero margin, strict margin, nonzero bound contribution and negative
weight. All 39 floor, one LP parity and 12 new t9 contradictions check
(0.56 CPU-s incl. roster binding). The verifier shares the previously
reviewed LP row generator, but none of G's selection, solver, or
verification code. It does not re-prove the row semantics or certify
optimality/feasibility for unchanged rows. The thresholds retain the
inherited 108/97/88 floors and G-021 where used. Evidence:
`scratch/H/round13-thresholds.log` and `scratch/G/round13/thresholds.csv`.

## Lean scope and calibration

- `R310/RootDemand.lean`: conditional equality at e170 (`e(H)=122`,
  `Z=48`), odd finset sum lemma and even-other-neighbour necessity.
  With an adjacent d6 peer, no third d6 and no d8 this is a contradiction.
  Neither the residue floor nor d6 adjacency is imported as a Lean axiom;
  they are explicit premises. The ledger application uses N-003/G-021.
- `R310/ReciprocalWindow.lean`: exact incidence sums and handshaking on
  the two induced pieces, equal boundary contributions for equally
  sized fully joined root sets, and the specializing 22/12 size count.
  This gives C's `e(P)+45=e(F_A)` without a cap-five premise or any
  census; no Lean assertion that e(F_A)≤64 or that a case is exhausted.
- `check_round13_controls.py`: 4,215 physical root splits and 16,325
  nonempty odd arrays on the known C13/all-191 C22 hosts. Regular hosts
  give 52+26 oriented balanced marks at 13 and 1,320+2,118 at 22.
  Planted `K3,3` in a 6-regular blown-up pentagon checks the width-three
  specialization of the generic identity, and all 52 C13 boundary-
  preserving edge deletions fail the balance when regularity is lost.
- `build_private_signature.sh build --old R310` passes on pinned Lean
  and Mathlib v4.35.0 and the existing cache (no Mathlib rebuild).
  `check_axioms.py` passes nine targeted and 319 integrated reports;
  only `propext`, `Classical.choice`, `Quot.sound` are permitted.

## Next credited actions

The highest-confidence near-regular direction is now the e170 d6
equality-signature stratum; priority is exact scoped coverage rather than
another e168 run or assuming the partial e122 inventory complete. Among
regular runs, the strongest new cost evidence is the matched 17/17
reciprocal pilot (197,502 local to 327 panel calls; zero open only in the
pilot), so consider one deterministically bounded shard after critic
approval. Distinguish that throughput estimate from D's confirmed
existence of two marked pentagons and their remaining compatibility
problem. B's two named negative followups supply no new key and do not
justify a broad replay. Literature findings and the proceedings citation
are in `LIT.md`.
