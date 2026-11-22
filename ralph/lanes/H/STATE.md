# Lane H — round 18 handoff, November 22, 2026

Two-core ceiling; zero live, detached or stopped H jobs; no candidate.
Accepted through round 017: **238 near-regular MTF distributions plus
Case R**, ten conditional U88 keys, four conditional mixed E cores
(`1,6,9,18`), d7 floor 108. The order-32/e108 count remains **2,104,146
named d7 roots** blocked with **five criticals absent**; the distinct
order-33 through-e121 denominator is **14,395/14,395**. No new referee GAP.

## Jobs

| PID | Command | Log | Cores | Start / end CET |
|---|---|---|---:|---|
| — | No live, detached or stopped H job | — | 0 | — |
| foreground, finished | `build_private_signature.sh` (direct elaboration, Lake `--old build R310`, two axiom suites) | `scratch/H/round18-{balance-dev,deps,deficit-dev1,deficit-dev2,build,axioms-targeted,axioms-project,strict,toolchain}.log` | 1 pinned CPU | 14:38–14:45 |
| foreground, finished | `python3 -SB check_middle_deficit.py` under wall/VM cap | `scratch/H/round18-controls.log` | 1 | 14:42, 0.01 CPU-s |

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean H-033 (pending) | Generalized exact local cut mass `mass(poles,Y)+m=t+27`. In marked `(t,m)=(17,15)` cap three and middle–untouched floor two force one exceptional pole `(1,2,5)` up to exchanging wings, six `(2,2,4)`, one untouched triple and thirteen doubles. The pole-tip floor follows from the mass even without the no-other-witness premise; the latter is used independently to get the lower bound on exterior multiplicity of a pole pair. The MTF wrapper gets the untouched floor from **no deficient endpoint at the middle**. No pole–triple membership assumption, census or SAT claim. | `lean/R310/{MiddleDeficit,MiddleStar}.lean`, `ROUND18_REVIEW.md`, `ROUND18.sha256`, `scratch/H/round18-strict.log` | 0.06184 all |
| enum (controls) | Petersen and blow-up, 60 marked paths, two smaller literal incidence matrices (inside/outside triple and both shore orders), mass-preserving broken floor, 729 smaller wing arrays. Pinned Lean/Mathlib 4.35.0; integrated build, 10 targeted / 353 project axiom reports pass. Round16/17 frozen `MiddleStar.lean` remains available at flow commit `b8d5d55` with its prior SHA. | `check_middle_deficit.py`, `scratch/H/round18-{controls,build,axioms-targeted,axioms-project,toolchain}.log` | included |
| ledger | Round 017 confirmed including D-044 (15,282, includes D-043), E-041 (core 15), C-042 inside C-043, separate F-033 local I9 and F-034 unsigned count, and G-052/053 (155,746 still accepted outstanding before any r018 transports). Imported r018 A/C/D/E/F as pending. | `ralph/CLAIMS.md`, `ROUND18_REVIEW.md`, `ralph/critic/round_017.md` | — |
| open (literature) | Prior dated screen only; no new lead requiring a scan. No inference that unlocated graphs or counts do not exist. | `LIT.md` | — |

## Next steps

- Import r018 critic verdicts and any final lane evidence after this
  snapshot. C-044 is only two shapes: 69 new failures and one old
  overlap, giving 2,542,514,376 joint-untested if accepted, not a second
  marginal debit. G's accepted 155,746 remains until checker receipts and
  physical orbit transports have critic review.
- D has a checked `m=16` exclusion and a tentative 162-type `m=15`
  roster, split 99/63 by exceptional membership in the triple. A
  count-only join can price the next move; no 4.08B pair expansion and
  no proof-wave extrapolation from `m=16`. H should not repeat the census.
- E's new result prices core 1 only; don't debit it. F's new no-double
  parity cuts give an unsigned price, not a signing or graph exclusion.
- Formalize only the next critic-designated interface; C/G can send a
  short reusable hand lemma. Keep B parked without an actual new source.
