# Lane G state — round 16, November 22, 2026

**238 near-regular MTF distributions plus R remain open.** No graph
candidate, no distribution cut, and no change to any t9 bound, U88 key,
or residue floor. Local exclusion only: e170 adjacent d6 equality roots,
`h=8` (all eight double sites coincide), with relative hole scheme
`leaf+leaf.1`, pending critic review.

## Jobs

| PID | Command | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| — | No active or detached G jobs | `scratch/G/round16/` | 0 | — | — |

All round-16 runs completed in the foreground; production PID 3435791
and replay PID 3497702 are gone. One core at a time, nice +5, 16 GiB
virtual cap, measured peak RSS about 100 MiB. No timeouts or models.

## Results and claims

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| hand + enum + cert (local; pending) | Coincident doubles force the 20-site off-diagonal incidence grid. Expanding scout schemes covers all 900 ordered hole pairs in 30 orbits; the 62 old dual-checked LRATs cover exactly 10,386 distinct out of 169,635 IDs (69 hits in both batches count once). Smaller canonical classes replay 24/0. | `rows/e170_aligned_grid.md`, `ROUND16_REPLAY.md`, `scratch/G/round16/{prior,replay}.log` | 0.00337 first audit, replay below |
| enum + estimate | Matched 48 uncovered IDs: direct 5.56 CPU-s, 48 new; transfer 22.33 CPU-s, 211 new covering all 48 direct IDs. Transfer adds 4.40 IDs/proof and 3.71 in the latter 24 (per-new-ID cost effectively tied with direct there). Switched to direct on the tail. | `ROUND16_REPLAY.md`, `scratch/G/round16/{direct,transfer}/price.jsonl` | 0.00778 |
| hand + enum + cert (local; pending) | Exclude the named marked `leaf+leaf.1` scheme only. 356 prior + 211 pilot + 1,261 tail = all 1,828; both checkers verify every bound receipt, exact forward/inverse rosters agree. No new h<8 work, no result for the other 29 schemes beyond the old cover. | `rows/e170_aligned_grid.md`, `ROUND16_REPLAY.md`, `ROUND16_FREEZE.sha256`, `scratch/G/round16/replay.log` | 0.06843 production + replay |

## Handoff

- Critic/H: replay and ledger only the named local result. Use
  `ROUND16_REPLAY.md`; note that `h=8` is an extra hypothesis and no
  distribution debit follows. The one wing has holes `04,34`, the
  other `04,24` in common grid coordinates, modulo the indicated actions.
- Wait for new directives before any new scheme wave. Do not project
  this tail price to untested schemes or assume the private incidence
  grid for `h≤7`. No further free-population MIP runs; N's size-four
  and nonlinear cuts are archived in `LOG.md`, not a launch plan.
- At e170, sixteen degree-six keys remain (nine single, seven adjacent
  pair). `Z=48`, e(H)=122, 24 private and nine double sites; adjacent
  W has 28 sites, one wing crossing and 86 internal edges. No complete
  order-33/122 cover. Round-13 exact t9 thresholds and membership remain
  in `ROUND13_REPLAY.md` and its freeze. The 32/e108 project is lane B's.
