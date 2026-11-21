# Lane H — round 5 handoff, November 21, 2026

Two-core share, Lean builds pinned to one CPU; a small Python control
ran briefly on the second. No detached Lane H jobs and no flow-verified
order-40 witness. The checked baseline is round 004, not any pending
round-005 exclusions. Read the next critic directives first.

## Jobs

| PID | Command | Log | Cores | Start / finish CET |
|---|---|---|---:|---|
| — | No live/detached H job. | — | 0 | — |
| foreground, ended | `build_private_signature.sh` targeted builds, `build --old R310`, targeted and full `env lean -j1 -s8192` axiom audits | `scratch/H/{private-signature-v*,complete-arms-v1,residue-degree-five-v1,round5-wings-integrated,round5-wings-axioms,round5-wings-project}.log` | 1 | 21:16–21:33 |
| foreground, ended | `python3 -SB ralph/lanes/H/check_private_signature_control.py` and a frozen CSV count | `scratch/H/{private-signature-control,d5-residue-current-scope}.log` | 1 peak | 21:22–21:28 |

All builds use the pinned Lean/Mathlib v4.35.0 cache; no Mathlib source
build, solver proof replay or SAT solve. First Lean revisions had
elaboration errors (not timeouts); final module and integrated builds
passed, as did 12 targeted and 270 project axiom reports.

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean, H-009 | At `e(G)≤e(H6)+48`, MTF order 40, alpha≤9 and a degree-six root force six private cells of four and nine distinct double signatures. Applies at e168/e120 and e169/e121; no external floor formalized. | `lean/R310/PrivateSignature.lean`, `AxiomsRound5.lean`, `scratch/H/round5-wings-axioms.log` | ~0.15 total Lean work, incl. revisions and H-010–012 |
| Lean, H-010 | In C's complete-arm path, a vertex avoiding the triple intersection avoids both wings, given the exact neighborhood identities and their maximum independent sizes. No partition/count or finite cover in Lean. | `lean/R310/CompleteArms.lean`, `ROUND5_REVIEW.md`, `scratch/H/round5-axioms-final.log` | included |
| Lean, H-011 | Nonadjacent degree-six pair yields a degree-five residue vertex. If n6≥3 through e169, some degree-six residue has order 33, min degree exactly five and e≤121, assuming R(3,8)≤28. It does not certify the finite branch. | `lean/R310/ResidueDegreeFive.lean`, `scratch/H/round5-axioms-final.log` | included |
| Lean, H-012 | Given 26 exterior vertices with nonempty common support totaling 42 and at most 12 singleton supports, the total excess over two is at most two and the singleton count is 10 plus the excess. C's graph-specific premises and window counts are not formalized. | `lean/R310/CompleteArms.lean`, `scratch/H/round5-wings-axioms-audit.log`, `ROUND5_REVIEW.md` | included |
| enum, control | C13(1,5): 13 equality roots, 52 doubles, 1,872 common-anchor family checks, 208 tight. K2,3 confirms double repeats without a full cell. | `check_private_signature_control.py`, `scratch/H/private-signature-control.log` | <0.001 |
| hand / enum, scope | Audited C full-arm hypotheses, G targeted min-degree-five reduction and A's missing-class upper/lower-edge logic, and B's e162 row-support reduction. n6≥3 branch covers 18 e168 + 21 e169 keys if excluded; 18 overlap the prospective 39 e168/e120 keys. No proof replay or new cut by H. | `ROUND5_REVIEW.md`, `scratch/H/d5-residue-current-scope.log` | <0.001 |
| pub / open | Updated primary literature recheck and AlphaEvolve v5 comparator. No located exact classical result, public GR–Angeltveit order-39 bulk census or dense order-30 count. | `LIT.md`, `scratch/H/literature-recheck-r5.log` | — |

## Ledger and next steps

Round-004 verdicts copied to `ralph/CLAIMS.md`: G's eight e168 cuts
leave 368 near-regular MTF distributions plus R; 12 U88 and 39 e168/e120
are prospective only and disjoint. C's P3 diagonal bounds do not cover
isolated pairs; separate replay confirmed by C in round 005 still needs
critic verdict. E's f=28 aggregate is mixed hand/cert/enum, F10 inherited,
and E-014 a=6 covers all graphs, not just MTF. A's round-5 frozen audit
checks all 2,890 LRATs without completing the order-33 set; 11 remain
e169-pinned. B-012 is pending and would remove one U88 key, not the layer.

Best route is G's exact minimum-degree-five residue split through 33/121:
it can bypass the six missing classes for n6≥3, but its finite output
must still be bound and any survivors excluded. No global floor follows.
Keep the e168/e120 and e169/e121 coverage distinguished; leave portable
binding to A and generation/replay to G. C's complete-arm theorem makes
the f*=9 codegree-six graph a matching (not an exclusion); watch the
remaining isolated-pair work. F's best independently counted I10=24 is
not a witness. Next round, record late round-5 claims and critic verdicts
without duplicating finite computation. Evidence and commands are in
`LEAN_REPRO.md` and `ROUND5_REVIEW.md`; earlier work has `LOG.md`.
