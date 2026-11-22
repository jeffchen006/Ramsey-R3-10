# Round 18 — ledger and marked middle-star deficit

## Imported verdicts (round 17)

`ralph/critic/round_017.md` is the authority. D-043 is a checkpoint
**inside** D-044: 15,282 profiles, 320,878 ordered shore pairs on six
fixed supports, 6,135 eligible labelled supports before the quotient.
Only marked R(3) `(K,t,m)=(2,17,16)` is closed. The obsolete four-worker
status was superseded by D's final empty queue; no inherited H job.

E-041 closes core 15 only, under E-021 and the stated mixed involution
premises. Core IDs 1, 6, 9, 18 remain. A-029/C-042/C-043 are exact for
the two package-existence predicates: the `(71,5)` zero stratum is
inside the marginal debit; 2,542,514,492 both-pass minus the 47 old
failed joins leaves 2,542,514,445 joint-untested at the accepted handoff.
F-033 is the independent **nine** on unchanged 14-site intervals;
F-034 is the unsigned changed-site count, not an extension exclusion.
G-052/053 leave 155,746 IDs accepted as outstanding until each physical
action is verified; arithmetic orbit planning does not take proof credit.

B-039 is archive integrity, not proof replay or a floor of 109. 2,104,146
named 32/e108 d7 roots are blocked; five absent criticals. The order-33
through-e121 family has its own 14,395/14,395 denominator. No double debit,
new referee GAP or flow candidate. **238 plus R; ten conditional U88 keys.**

## H-033 (Lean, pending)

`R310.middle_star_balance` consolidates the shared graph argument once,
without changing the statement of `middle_star_at_seventeen_sixteen`.
For the marked path in a 9-regular triangle-free 40-vertex graph,
the 19-site book has `18+t` edges and its 21-site complement `27+t`.
Seven poles are independent. With 14 untouched sites,
`starMass poles untouched + m = 27+t`. Each pole has eight contacts in
the two wings and untouched sites combined. Its tip codegrees are its
respective wing contact counts plus one; each middle/untouched codegree
is that untouched site's pole count.

At `(t,m)=(17,15)` the incidence mass is 29. Wing caps of two give a
pole outside-degree floor of four. The single surplus over 28 yields
one exceptional pole with `(1,2,5)` or `(2,1,5)` contacts and six with
`(2,2,4)`. The tip codegree floor two follows even without excluding
other pairs witnessed by the middle on this layer. Independently, with
the middle/untouched codegree floor two, there is one physical triple
row and thirteen physical double rows. No link between the exceptional
pole and the triple is asserted. `middle_star_at_seventeen_fifteen_of_mtf`
obtains the untouched floor from MTF and **no deficiency with the middle
as an endpoint**. `polePair_multiplicity_of_only_marked` instead uses
**no other pair uniquely witnessed by the middle** for the lower bound
one on exterior multiplicity; the upper bound two is from the cap.
`MiddleStarBalance.tipFloors` records the witness-based route to the tip
floor outside the single-unit arithmetic. No formal claim about how
many deficient paths exist, D's support census, or a SAT exclusion.

## Controls and replay

The smaller physical controls are Petersen (alpha 4, all 60 marked
ordered paths), its 19-site MTF blow-up, then literal 3×6 and 4×8
incidences (both shore orientations, exceptional pole inside/outside
the triple) and a mass-preserving mutation failing the column floor.
Of 729 three-pole wing arrays, exactly one is tight and six have unit
deficit; a deficit of two can have a zero wing. These are local controls,
not Ramsey completions or a duplicate D census.

```sh
bash ralph/lanes/H/build_private_signature.sh --old build R310
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 -DElab.async=false ../ralph/lanes/H/AxiomsRound18.lean
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 -DElab.async=false scripts/Axioms.lean
python3 -SB ralph/lanes/H/check_middle_deficit.py
sha256sum -c ralph/lanes/H/ROUND18.sha256
```

For the historical round-16/17 `MiddleStar.lean` freeze, use the earlier
flow version (`git show b8d5d55:lean/R310/MiddleStar.lean`): its SHA256 is
`4d4d9a32c2c549966897ef1dab6d86c4e01b5e6e21291988e432aa39ddf7e511`.
Round 18 re-audits the original tight theorem against the generalized
source. Pinned Lean 4.35.0 and Mathlib `56a005855ea17e0b0958f73ec801ae140b0a1679`;
integrated build and strict checks of 10 targeted / 353 project reports
passed (`scratch/H/round18-{build,strict}.log`). 222.62 measured CPU-s
(0.06184 core-h), peak 3,495,036 KiB including one failed source probe
before cache refresh and arity correction. No Mathlib source rebuild,
detached H job, or solver search.

## Team direction

D has the strongest checked regular-path result and a sharply defined
next counting question: 162 marked necessary support types, pending,
not permission to launch a new proof queue. A/C report two small
joint exclusions (69 new failures, one overlap), pending. E priced core
1 only; F's new unsigned reduction and G's aligned transports do not
imply a distribution exclusion. No fresh literature lead in the handoff;
the dated screen remains in `LIT.md`.
