# Round 16 lane H — middle-star interface and claims

## Confirmed round 15 ledger

- A-026/C-039/C-040: the same **marked** regular cap-five two-neutral
  exclusion, entered once as a closure. 92,341,930 direct headers and
  65,130,071 exchanged exhaust 157,472,001. On the direct headers
  the terminal evidence gives matching **per-header reason vectors**,
  not a separately keyed correspondence of fillings. The exchange
  maps real completions, not reasons, stage depths or times.
- B-036: all 2,102,271 supplied reducible 32/e108 keys are blocked at
  MTF degree-seven roots (2,016,206 cliques and 86,065 dual LRATs).
  The critic rechecked the full index and independent regenerated
  proofs for three stripes, not all LRATs. B's new round-16 crosswalk
  for 1,875 criticals is pending. Five criticals remain absent.
- D-041: under K=2 in R(3), **each** deficient path has at least
  17 induced pentagon closures. The 287 local CNFs exclude all three
  t=16 shapes, not a matching of 17 or all K=2. R-004 records the
  independent scout's t=17,m=16 roster, while R-005 records `m≥10`
  and the separate `m≥11` implication if the middle has at most
  one deficient partner in Y. Neither bound settles the m≤15 slice.
- E-038/039 leave five conditional mixed cores (1,6,9,15,18).
  F-029 supersedes F-028 as the cyclic ID21 exclusion **for arbitrary
  vertical choices**; it does not show anything about ID8.
- N-005 is a 10,386-ID union within 169,635 aligned h=8 assignments,
  not a 10,386-proof inventory or all equality roots. N-006/007 are
  negative free-population/source pilots. G-048/049 remain fixed
  tuple results only. No `r015_T.md` was available, in agreement
  with the critic's no-submission verdict.

## Lean scope and replay

`middle_star_at_seventeen_sixteen` takes an actual finite simple
graph, order 40, degree nine, triangle-free, a nonedge with a named
unique common neighbor, a nonedge codegree cap of three, and a
codegree floor of two from the middle to the untouched vertices.
The wing/other-neighbor/book/untouched sets are defined from the
neighborhoods. The proof derives their needed disjointness and
orders, not just formal arithmetic conditional on a presumed cut
count. It uses the literal cross-wing edge count 17 and untouched
induced edge count 16.

The book has 35 edges, and regularity gives 44 edges in its complement
by canceling the same cross cut. The other middle neighbors are
independent, so exactly 28 of those edges run from the seven such
neighbors to the fourteen untouched sites. Each middle neighbor has
its one contact to the middle and at most two contacts to each wing
(its codegree with a path endpoint already includes the middle).
Thus each sends at least four edges to the untouched set; equality
forces row contacts 2/2/4. The stated middle-to-untouched floor makes
each untouched column at least two, and the same 28 incidences make
all columns exactly two. `pathUntouched_codegree_ge_two_of_mtf`
supplies the floor from MTF plus the explicit condition that the
middle is not a deficient *endpoint*. This is distinct from being
the unique *witness* of another deficient pair. The latter condition
is not needed here, but would be needed to bind scout R's subsequent
pole-pair lower constraint. No K=2 structural existence result,
support-orbit enumeration, CNF binding, or exclusion is in this file.

```sh
bash ralph/lanes/H/build_private_signature.sh --old build R310
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 -DElab.async=false ../ralph/lanes/H/AxiomsRound16.lean
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 -DElab.async=false scripts/Axioms.lean
python3 -SB ralph/lanes/H/check_middle_star.py
sha256sum -c ralph/lanes/H/ROUND16.sha256
```

Pinned Lean/Mathlib v4.35.0: `--old build R310` rebuilt the new module
and root against the cached dependencies, not Mathlib. The strict
checker accepts all 7 targeted and 339 integrated reports with only
standard axioms. The smaller Petersen control covers 60 oriented
deficient paths and 60 broken contacts; its 19-site blow-up exercises
the separate MTF/no-deficient-endpoint implication on four untouched
sites. A literal 2×4 incidence control has six floor-preserving
matrices and 30 countercontrols if the column floor is dropped.
Total timed CPU including elaboration debugging: 249.48 s = 0.06930
core-h (control time 0.02 s CPU). No solver or detached job launched.

## Decision impact

No flow-verified graph, and **238 near-regular MTF distributions plus
Case R** and ten conditional U88 keys remain. B is only five missing
critical keys away from complete *input coverage* but found no
independent e109 source; coverage of named keys is not a floor of
109. The one-neutral A/C roster has 15,051,526,031 eligible headers,
and C's pilot rejects 544, leaving 15,051,525,487 untested. C's
fastest projected route is still thousands of core-hours: shrink the
domain before production; the old two-neutral closure does not
transfer. G's named 1,828-ID scheme replay is actual
conditional progress. D's 155 fresh dual-checked pilot proofs and
two separately bound old tails give the best case for one more bounded
regular closure, with proof and disk tail gates; even complete coverage
would settle only a marked maximal-residue slice. E's core 15 stops at
142 open IDs under the 100-ID gate. These are round-16 submissions
pending critic review, not distribution debits.
