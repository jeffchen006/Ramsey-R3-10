# Lane H — round 20 handoff, November 22, 2026

Two-core ceiling; used one pinned foreground worker, no solver jobs,
no detached/stopped PIDs, no candidate. Checked through round 019:
**238 near-regular MTF distributions plus Case R**, **ten conditional
U88 keys**, **four conditional mixed cores** (`1,6,9,18`) remain.
Floor 108: 2,104,146 named order-32/e108 d7 roots blocked, five
missing criticals; distinct order-33 through-e121 census 14,395/14,395.

## Jobs

| PID | Command | Log | Cores | Start / end CET |
|---|---|---|---:|---|
| — | No live, detached or stopped H job | — | 0 | — |
| foreground, finished | `build_private_signature.sh` (two elaborations, `--old build R310`, targeted/project axioms and version) | `scratch/H/round20-{dev1,dev2,build,axioms-targeted,axioms-project,toolchain,strict}.log` | 1 pinned CPU | ~17:24–17:28 |
| foreground, finished | `python3 -SB check_private_matching.py` under wall/VM cap | `scratch/H/round20-controls.log` | 1 pinned CPU | ~17:26 |

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean H-035 (pending) | On two disjoint independent physical shores plus an isolated set, a local independence cap implies a Hall deficiency bound. A partial matching exists at the desired lower size; four-plus-four at cap 5 yields `3+[cross]`, producing H-034's margin without assuming a matching. Local graph inputs, not global graph reduction or target SAT. | `lean/R310/PrivateMatching.lean`, `ROUND20_REVIEW.md`, `ROUND20.sha256` | 0.02196 all |
| enum (controls) | 170 literal small graphs; tight small and target-size toy matches; isolated-cap adverse case and cloned physical-site mutation. Lean/Mathlib pinned 4.35.0, cached `R310` build and strict 3/359 axiom reports pass. | `check_private_matching.py`, `scratch/H/round20-{controls,build,strict,toolchain}.log` | included |
| ledger (confirmed r019) | C-045 hand necessity/shortcut, C-046 zero fifth-row cuts, C-047 twelve *signed* fresh exclusions. 2,542,514,364 signed-untested, 2,542,514,308 untouched after separate R vetoes. G-055: 57,947 fresh leaves 21,125 marked h=8 ranks; h=7 is 51/1,213. F unsigned, E old proofs, D counts, H-034 conditional. Referee process failed but left report; no GAP and D=7 **0/220 survived**, all rejected. | `ralph/CLAIMS.md`, `ralph/critic/round_019.md`, `ralph/referee/round_019.md` | — |
| ledger (pending r020) | A-033 independently matches G-019 middle 118→984 (985 rooted); not prefilter or outer. G-056 reports 21,125→0 *marked aligned h=8 only*. E-044: 16 then-fresh local proofs → 115/147 unresolved; E-045 timing/forecast. D-048 cuts 3/162 supports, 1,334,977 marked orbits remain; D-049 proposed filter only. C-048/049 factored gate leaves all 116 right keys live, no debit. F-037/038 exact 435 scoped one-double opens and distinct 1,979,210 unsigned joints. B-040 saturation restriction cannot classify five missing keys. | `ralph/CLAIMS.md`, A–G round-20 `STATE.md` | — |
| open (literature) | No fresh screen per critic. `LIT.md` remains a dated search, not a completeness claim. | `LIT.md` | — |

## Next steps

- Import critic's round-20 scope decisions; do not debit the pending
  G, D or E counts until accepted. For G, a zero `h=8` ledger is only
  marked aligned equality, not the whole equality case; preserve
  `h=7` 51/1,213 separately. Verify the scope of the G-019 deep audit.
- Request independent critic build and axiom checks for H-035. If
  asked, bind its local cap to actual graph padding or formalize
  C-048's three-four-set finite exhaustion; no rerun of the fifth gate.
- G's one-receipt many-ID transfer has the strongest cost evidence;
  E's 115 residual physical IDs are a separate, exactly sized target
  if accepted. B remains parked without an independent source.
