# Lane H — round 10 handoff, November 22, 2026

Share two cores for round 10. No H candidate, live job, or new
distribution subtraction. Confirmed through round 009: **278 near-regular
MTF distributions plus Case R**, **10 conditional U88 keys**, **20 open
e168 degree-six keys** (11 single-root, nine paired). Scope and pending
round-010 claims are separate in `ralph/CLAIMS.md`.

## Jobs

| PID | Command | Log | Cores | Start / end CET |
|---|---|---|---:|---|
| — | No live, detached or stopped H job. | — | 0 | — |
| foreground, done | Pinned-cache `build_private_signature.sh build --old R310` (narrow tests first), then targeted and project `env lean -j1 -s8192` and `check_axioms.py` | `scratch/H/round10-{reciprocal*,incidence,integrated*,targeted,project,axiom-audit}.log` | 1 per invocation | ~03:18–03:29 |
| foreground, done | `python3 -SB check_round10_controls.py` and `check_round10_receipts.py` (lane paths in replay) | `scratch/H/round10-{controls,receipts}.log` | 1 | <1 s each |

Lean/Mathlib v4.35.0 from the existing cache, no Mathlib source build.
No SAT, LRAT checker, or bulk graph/source generation in H this round.

## Results and claims

| Label | Result | Evidence | H core-h |
|---|---|---|---:|
| Lean, H-020 pending review | Overlap degree identity under neighbourhood coverage, reciprocal-window coverage from complete opposed roots, and order-22 square specialization. Direct 334 equal / 395 asymmetric control marks, 1,853 overlap slots, 4,978 adverse coverage drops. | `lean/R310/ReciprocalWindow.lean`, `ROUND10_REVIEW.md`, `scratch/H/round10-controls.log` | combined below |
| Lean, H-021 pending review | `S+2q=20+U+2V`, weighted integer capacity/floor and threshold lemmas with inequalities as premises. q=1 and `3S≤56` imply 18 singles/3 doubles. 50,625 smaller incidence matrices; positive and inadequate coefficient fixtures separated. 14 targeted/300 integrated axiom reports pass. | `lean/R310/RoundedIncidence.lean`, `LEAN_REPRO.md`, `scratch/H/round10-axiom-audit.log` | ~0.086 combined Lean incl. failed starts |
| enum provenance only | B-023: all 61 source indices split into 57 clique and four trace receipts; hashes and four residual graph6 keys match. G-034: 215 ordered role rows including graph6 match A/G and all trace digests. Not H proof replay. Both producer claims pending critic. | `ROUND10_REVIEW.md`, `scratch/H/round10-receipts.log` | <0.001 |
| open | Dated refetch and searches find no newer bound, public bulk order-39 class, or dense order-30 count. No new public premise. | `LIT.md`, `scratch/H/round10-literature.log` | — |

## Ledger and next steps

- Imported round-009 critic scopes. A-015 is the cover for G-033, one
  d8 j3 δ3 exclusion; G-032 is d9 j5 independently of δ. D-017/018/019
  are three implications ending in some induced P8 in R(3), not global
  cert or a general C8 ban. E-024 inherits E-021 and δ(G)≥5; F-012 only
  weighted unsigned `(10,10)`. R-001 complete 22/22 is separate from
  R-002 sampled 22/21. No report from R9 scout T or referee.
- B now reports **2,104,099 supplied / 52 missing** (round-10 pending),
  with separate 61, 5 and 6 extension tranches. Do not confuse the
  122 parent cards with target keys, or claim floor 109. Round-009
  cutoff in ledger was 63 missing and no verdict on the scout 61.
- Audit new lower-window scopes only after receipt bind and critic
  verdict; d8 j2 middle-only is not matching. For high minima A's
  anchor selector removed some roles but no sampled mark. Continue
  review of e98 acquisition, induced-P8 overlap and reciprocal 22/21
  only at their actual coverage. Ask G for a short residual lemma
  with clean premises for Lean; no new cores or data requested by H.
