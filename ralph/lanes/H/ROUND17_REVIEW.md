# Round 17 — Pole-pair multiplicity and round-16 ledger

## Imported verdicts

The critic's round-16 fourth-round depth audit reconfirmed the same
`368 → 283 → 278 → 238` distribution balance, including the same
forty-key debit under the inherited gluing floors. It did not reopen
or duplicate those cuts. The d6 floor's separate denominator is
14,395 complete order-33 through-e121 classes. Ten U88 keys remain
conditional. No new referee report.

- A-027/028: labelled 16/17 one-neutral roster, 15,051,526,031 headers,
  no side-exchange factor; 544 physical pilot IDs. C-041 has 497 exact
  empty domains and 47 headers with incompatible joins, not 544
  target terminal calls; 15,051,525,487 untested at end of round 16.
- B-037 is a named-key crosswalk: 1,875 criticals join 2,102,271
  reducibles once, making 2,104,146 named keys and leaving five absent.
  d7 floor stays 108. B-038 licenses descent only for addable keys
  from a complete independent e109 source; it says nothing about
  saturation of any missing key. B's round-17 archive checks are
  integrity evidence, not new graph or proof work.
- D-042 covers 155 fresh and two old tail profiles only. The 48
  holdouts with no proofs are enum, not included in those 157. The
  round-17 checkpoint and remaining campaign use canonical labels;
  do not add the old pilot counts to the checkpoint.
- E-040 is an ordered diagnostic cover, not a core exclusion. E-041
  resolves the resulting 142 IDs for core 15 only, pending critic;
  leave all five conditional cores in the accepted baseline until
  review. G-051 closes exactly the 1,828 `h=8` aligned `leaf+leaf.1`
  IDs, not other aligned schemes, h<8, a distribution, or U88.
- F's late accepted submission is split into F-032 (seven-window
  bridge with the pole present), F-030 (ID8 cannot extend to 37 at
  arbitrary verticals/signings), and F-031 (inherited four-deletion
  cyclic unsigned family consequence). No assertion that the original
  verticals were present, the bare card impossible, or unrestricted
  involutions excluded. F-031 additionally depends on the separate
  ID15 no-missing-vertical implication before F-025.
- H-031 is a conditional structural Lean result, not a support orbit
  or SAT completeness theorem. Its distinct column-floor premise
  addresses middle-as-endpoint, not middle-as-witness.

## H-032: Lean interface and controls

`polePair_multiplicity` starts with a marked unique-witness nonedge
`left—middle—right`, triangle-freeness and two distinct poles in
`pathStar`. The poles are nonadjacent (they share `middle`). Their
other common-neighbor set excludes the entire neighborhood of `middle`
by triangle-freeness. In particular it excludes the two tips; the
remaining locations are the two private wings and `pathUntouched`.
The wings do not overlap because the marked tips have no second
common neighbor. `pathUntouched` avoids both wings. Thus the three
physical cardinalities add exactly, with no identification of sites
having the same pole support. Adding back `middle` gives the codegree.

At cap three, the sum is at most two unconditionally under those
hypotheses, and it is at least one **iff** this pole pair is not uniquely
witnessed by `middle`. The application under D's K=2/disjoint marked
paths uses the separate no-other-witness implication. This Lean module
does not prove that premise, the K=2 split, the profile roster or a
solver result. The theorem does not require regularity, total order,
t or m. It refines the already known hand argument in `D/MIDDLE16.md`
and `review/ideas/r015_R.md`; it is not a new enumeration method.

The literal control checks Petersen's 15 edges and independence number
four, then clones just the three neighbors of one chosen middle at a
time. The resulting 13-site graphs are MTF and have codegree cap three.
The middle has codegree exactly two with every nonneighbor (so it is
not a deficient endpoint), but there are 600 marked pole-pair rows
with zero exterior multiplicity across the ten labelled constructions.
They positively distinguish the two premises. There are also 120
upper-tight rows and nine smaller positive configurations realizing
every nonnegative wing/untouched triple with sum one or two.

```sh
bash ralph/lanes/H/build_private_signature.sh --old build R310
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 -DElab.async=false ../ralph/lanes/H/AxiomsRound17.lean
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 -DElab.async=false scripts/Axioms.lean
python3 -SB ralph/lanes/H/check_pole_multiplicity.py
sha256sum -c ralph/lanes/H/ROUND17.sha256
```

Cached Mathlib and pinned Lean 4.35.0: successful project build,
five targeted and 344 integrated axiom reports, accepted by the
strict checker. No Mathlib source rebuild. Elaboration development,
proof build, both audits, binder-name rebuilds and controls took about
329.35 CPU-s (0.09149 core-h), peak ~3.31 GiB. Final logs have prefix
`scratch/H/round17-verified-`. No H solver or detached jobs.

## Decision impact at handoff

No flow-verified graph; the denominator remains **238 near-regular MTF
distributions plus Case R**. D's bounded canonical proof campaign has
the strongest evidence for another marked regular closure; exact
completed/open reconciliation matters more than multiplying pilot
timings. E's finished conditional queue is ready for critic review.
F's family is retired, G's named scheme is closed, and B must wait
for independent coverage of its missing five. A/C report 12,509,011,539
of 15,051,526,031 headers rejected by a necessary package-emptiness
filter, leaving 2,542,514,492 passing in both directions before
terminal joins. The (71,5) key is independently checked as entirely
rejected, included in the total, not another debit. Other passes
are not compatibility claims. The literature screen added no input.
