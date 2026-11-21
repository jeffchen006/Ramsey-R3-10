# Lane H — round 7 handoff, November 21, 2026

Share two cores. No flow-verified order-40 graph, no live H jobs, no
new case subtraction. Checked through critic round 006: **278 MTF
distributions plus Case R**, **10 conditional U88** and **20 open
e168 degree-six** keys (11 singles, nine pairs). Latest directives
and ledger verdicts take precedence over this handoff.

## Jobs

| PID | Command | Log | Cores | Start / finish CET |
|---|---|---|---:|---|
| — | No live/stopped/detached H job. | — | 0 | — |
| foreground, ended | `build_private_signature.sh build --old R310`; `env lean -j1 -s8192` targeted and project; `check_axioms.py` | `scratch/H/round7-{lean-*,final-*,axiom-audit}.log` | 1 | 23:35–23:46 |
| foreground, ended | `python3 -SB ralph/lanes/H/check_strip_window.py`; read-only publisher/catalogue GETs | `scratch/H/round7-strip-control.log`, `scratch/H/lit/r7-*` | <1 | 23:36–23:46 |

The cache-backed pinned Lean/Mathlib v4.35.0 build and both axiom
audits passed (5 targeted and 280 project reports). No Mathlib source
build, SAT solve, or graph proof replay by H this round. Before final
successful builds, fixed the import and natural-cardinality rewrite;
the audit parser accepts the `maxrss_kib` footer as well as `maxrss`.

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean, H-016 | Marked lower-half deletion: order/alpha, retained degree seven, unique surviving common witness, exact edge level and cap `84−#knownNine`. All structural input premises are explicit. | `lean/R310/MarkedStrip.lean`, `scratch/H/round7-axiom-audit.log` | ~0.067 incl. early build attempts |
| hand, H-017 | Single path/leaf window e≤84; e≤82 if X has no original d8, including n8=2. If n8=4 and both path/leaf, at least one window has e≤83. With two uncrossed centers, common codegree j=1..3 gives intersection order 17..19 and whole paired window order `24+j`; exact `49+9j+union deficit+exclusive cross` edge row. Every retained X hits both deleted sets. | `ROUND7_REVIEW.md` | <0.001 |
| enum, controls | 18/18 smaller path windows give C5; 18 rejected triple mutations. Both smaller catalogues check the paired accounting on 32,520 nonedges. Nine scalar weight patterns reproduce both caps. | `check_strip_window.py`, `scratch/H/round7-strip-control.log` | <0.001 |
| hand, audit | D's dense/balanced max12 Smax=2 split and fixed-block projection checked on paper; no re-encoding or pin closure. | `ROUND7_REVIEW.md`, `ralph/lanes/D/SCORE_CAP.md` | — |
| pub / open | November 21 publisher/census recheck found no superseding classical bound, public bulk order-39 list, or exact 30/88–99 counts; GR Table 13 available through e77 at order 26. Corrected publisher DOI for GR. | `LIT.md`, `scratch/H/lit/r7-*.data` | — |

## Ledger and next steps

- `ralph/CLAIMS.md` records the exact round-006 verdicts: C `(12,12)`
  only at global R(6), f*=9; E profile A plus the one mixed core,
  keeping the last e74 class uncertainty; B's e108 proofs only for
  the supplied 614. B/D/F round-7 entries and G's announced source
  remain pending critic. Ingest later A/C/E/G STATE deltas next turn;
  no inference from capped tests, partial inputs or sampled joins.
- G/A now have the best scoped e168 route: exact order-27 cover
  screened to 1,988 marked rows in the j=3 branch. Compare the new
  edge/degree inequalities against completion inputs; keep j=1,2
  and one-sided windows separate. Do not rerun the whole catalogue
  traversal or apply this cover to single-root keys.
- B/critic should bind the operator-reported 1,142 e108 critical
  classes before updating the deficit (potentially 124 instead of
  1,266); existence of keys is separate from their LRATs. Watch
  B prefix outcome, the nearest route to an exact U88 partition.
- Ask C/G for the next exact conditional short lemma, and continue
  scoped key reconciliation. No extra cores required.
