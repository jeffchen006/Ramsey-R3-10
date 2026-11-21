# Lane G state — round 6, 2026-11-21

## Baseline and open work

**278 near-regular distributions + R**, unchanged this round. No
order-40 candidate. Exact `round6_baseline.csv` includes the five
floor-108 cuts; the direct e162 cut is not additional. Send B/H the
ten conditional keys in `round6_u88.csv`. The 20 remaining e168
degree-six pins are in `round6_e168_d6.csv` (11 one-root, nine two-root).

The six order-33 e120/e121 classes are still missing at unknown levels.
All 1,223 supplied e120 and 13,092 supplied e121 rows retain their prior
gluing scopes. The 11 e169-pinned proofs are not unpinned. No floor
121/122 for all degree-six MTF residues was proved.

## Results and claims

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| hand + enum | Equality-root private pairs admit matchings of size `3+1_{ij∈J}`. Label a perfect matching on every edge of a signature spanning tree, fixing 20 exterior edges. A independently binds 3,700 labelled signature graphs, 14 orbits and all 112 orbit/pin pairs. | `rows/signature_matchings.md`, `equality_template.py`, `scratch/{G/round6/template.cover.log,A/pair6/g-template-audit.log}` | <0.001 |
| cert | In the exact induced three-anchor window with 12 privates and `q=0..3` distinct doubles, the minimum **exterior** edge counts are 9,11,15,18. Four lower-cap proofs pass both LRAT checkers; four independent positive controls attain each bound. No claim of a completion to 40. | `local_signature_budget.py`, `scratch/G/round6/localproof/`, `rows/signature_matchings.md` | <0.002 |
| hand + estimate | Retained-anchor edge floors, independent-double contact and even-cycle rows, exact local floors, and adjacent-root strip inequalities. All 112 base and all 112 strengthened projected LPs numerically feasible; **zero cuts**. Actual C13 and n9/p3 equality substitutions pass; Hall analogues pass C35 and saturated Exoo39. | `signature_rows.py`, `scratch/G/round6/signature{.control-final,-final.lp}.log` | 0.032 total, 0.010 final |
| enum | No structural inverse mark among all 13,092 supplied e121 rows and 90,223 supplied e122 rows. Independent n12 controls agree on all 104 partial and 52 full upper marks and lower alpha verdicts. Not an upper-class census. | `mark_inverse.cc`, `test_mark_inverse.py`, `scratch/G/round6/{inverse.control,e121.full.inverse,e122.full.inverse}.log` | <0.001 |
| hand | Two adjacent d6 equality roots give a residue half with a five-column strip, `X` of order 28/84 edges, and exactly two uncovered pairs. Cross role path/leaf is necessary on both halves when n8=2, on at least one when n8=4. Lane A proved the two-root zero-addition branch impossible; this does not prove any missing level complete. | `rows/signature_matchings.md`, `ralph/lanes/A/ADJACENT_DEG6.md` | — |
| estimate/open | Direct normalized 40-vertex CNF pilots: 4 cap5k + 8 cap20k + 4 cap100k, zero models, all capped. Two unmarked and three cross-role-marked exact 33-vertex half-pilots cap100k also have zero models. Neither route has an estimate to UNSAT. | `scratch/G/round6/{template*,half*}.log`, `half_template.py` | 0.074 |
| hand + exact arithmetic (replay of accepted prior results) | 984-class round-5 cover and 85+5 cut keys frozen with exact refreshed identities. No new assertion of completeness for e120/e121. | `ROUND6_FREEZE.sha256`, `freeze_round6.py`, `scratch/G/round6/freeze.replay.log` | <0.01 |

## Jobs

No live jobs, no detached launches. Foreground runs all completed
within their limits; peak eight concurrent pilot solvers, share 25.

## Handoff

- H/critic: local exact triple edge rows and the hand matching-tree
  normalization are suitable separate claims. Do not change the
  distribution baseline. A independently checked the mask cover.
- If new e121/e122 keys appear, `mark_inverse` is a fast exact delta
  scan; verify alpha after the deletion and canonically bind newly
  recovered e120 rows before any LRAT run. The 90,223 e122 rows are
  only a supplied set. Missing e120 cases with a single degree-six
  root may have zero additions and need a different exact source.
- Strongest narrow target: path/leaf strip alone would close the two
  two-root pins with n8=2,4, subject to a checked refutation. The other
  half roles are path/center and matching/incident. Look for a narrow
  **complete** smaller window source or a contact inequality that
  correlates overlapping triples. Do not scale the capped flat SAT
  pilots or repeat broad replacements without a new selector.
- Only perfect matching pins are valid. The first local q=0 pilot
  used weak pins and was discarded; the final proofs use forest
  perfect pins only. All order-40 and 33-vertex shape runs were on
  connected signature graphs, so this correction changes none of
  those pilot scopes. Replay recipes are in `REPRO.md`.
- Prior accepted floors: degree-six 120 (`rows/floor120.md`),
  degree-seven 108 (Lane B `FLOOR7_108.md`). No order-32 d4 expansion:
  237/520 pilot survivors, no new cap. More history in `LOG.md`.
