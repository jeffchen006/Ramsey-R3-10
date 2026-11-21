# Lane H — round 6 handoff, November 21, 2026

Two-core share. No flow-verified order-40 graph and no detached H jobs.
Checked through critic round 005: **278 near-regular MTF distributions
plus Case R**, 10 conditional U88 keys, and 20 open e168 degree-six
keys (11 with one degree-six vertex, nine with two). None of these
prospective targets is subtracted. Read next critic directives first.

## Jobs

| PID | Command | Log | Cores | Start / finish CET |
|---|---|---|---:|---|
| — | No live/detached H job. | — | 0 | — |
| foreground, ended | `build_private_signature.sh`: targeted build, `build --old R310`, targeted and project `env lean -j1 -s8192`, final integrated repeat | `scratch/H/round6-{global-v*,profiles-v*,integrated,targeted,project,axiom-audit,final-build}.log` | 1 | 22:22–22:33 |
| foreground, ended | `python3 -SB ralph/lanes/H/check_round6_scope.py` and read-only publisher/catalogue GETs | `scratch/H/{round6-scope,literature-recheck-r6}.log` | <1 | 22:25–22:30 |

Pinned Lean/Mathlib v4.35.0 cache; no Mathlib source build, solver
proof replay or SAT solve. Early Lean elaboration errors and an audit
wrapper footer were resolved; final integrated build and 5 targeted /
275 project axiom reads passed.

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean, H-013 | Global degree-six hand bridge: the Ramsey bound and no exterior degree five give exterior min degree six; exact residue identity gives c(6,t)≤t−6, then MTF forces a degree-six clique and n6≤2. The finite G-019 premise remains external; no edge cap needed. | `lean/R310/ResidueDegreeFive.lean`, `AxiomsRound6.lean`, `scratch/H/round6-axiom-audit.log` | ~0.07 Lean total including H-014 |
| Lean, H-014 | At e168 with degree-six floor 120, an adjacent degree-six pair and no third degree-six vertex, the other five neighbours have (7,8,9) counts (0,3,2) or (1,1,3). | `lean/R310/ResidueDegreeFive.lean`, `scratch/H/round6-targeted-axioms.log` | included |
| hand, H-015 | Audit A's two legal marked additions for n6=2; original cross degree and profile distinguish three possible shape cases. For `(2,8,2,28)` both marked edge sets are P3 centred at original degree seven, cross endpoints are degree nine. No exclusion, no e122 cover. | `ROUND6_REVIEW.md`, `check_round6_scope.py`, `scratch/H/round6-scope.log` | <0.001 |
| enum, control | C13(1,5): 52 ordered adjacent equality roots, each has two blocked and one legal marked pair. Exhaustive five-label arithmetic verifies all three permitted e168 shape patterns. | `check_round6_scope.py`, `scratch/H/round6-scope.log` | included |
| hand / enum, scope | Matched frozen merge: 368→283→278, five floor-108 cuts including B-012 once, 39 surviving tighter keys, four out/four in U88. Exact ten U88 keys and twenty e168 keys recorded. No new Farkas replay. | `ROUND6_REVIEW.md`, `scratch/H/round6-scope.log` | included |
| pub / open | Live EJC/arXiv and targeted catalogue recheck found no exact result superseding classical 40–41, bulk order-39 file or exact published count for 30/88–99. | `LIT.md`, `scratch/H/literature-recheck-r6.log` | — |

## Ledger and next steps

Round-005 verdicts in `ralph/CLAIMS.md` separate G's enumerated cover
from the B-013 certificates and the named Lean lemmas. C's f*=9
matching is not an R(6) closure. E's e(W)=12 certificate is scoped to
f=32,t=4,δ(W)≥2; inherited F10 remains distinguished for f=28.

Best route: for the nine two-peer e168 cases, A/G can use the marked
addition/e122 profile to narrow the equality search; two legal edges
do not imply two nonisomorphic e121 children. A partial e122 slice
is not a cover. At the eleven e168 keys with just one degree-six vertex, the
zero-addition possibility remains; keep the six combined missing
e120/e121 classes separate from the degrees-five census. No R(3,10)
decision or new cut by H. Keep key reconciliation in H and exact
input generation/binding in G/A; ask C/G for precise new hand lemmas.
