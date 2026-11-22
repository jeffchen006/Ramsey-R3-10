# Lane G state — round 18, November 22, 2026

**238 near-regular MTF distributions plus R remain open.** No candidate,
distribution cut, `t9`, U88, or residue-floor change. At e170 with a
marked adjacent degree-six equality pair and `h=8`, `leaf+leaf.1` is
confirmed (G-051), and `middle+middle.2` is now fully certified locally
pending critic. Conditional on review, **140,062** labelled alignment
IDs in the other 28 schemes are untested (from confirmed 155,746).

## Jobs

| PID | Command | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| — | No active or detached G jobs | `scratch/G/round18/` | 0 | — | — |

All runs were foreground, nice +5, one slot and ≤512 MiB virtual cap.
Checkpoint PID 3361393 is gone. No models or solver caps. One sample
setup issue with unstable file allocation metadata, fixed before proofs
were checked; its CPU is included below.

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| hand + enum + cert (local, pending) | e170 adjacent degree-six equality pair, `h=8`, **only** `middle+middle.2`: all 16,350 labelled IDs reconciled from 660 scout, 6 round-17 direct receipts + 42 additional oriented images, and 2,024 new dual-checked LRATs with labelled weight 15,642. Clean replay matches every owner and explicitly rebinds 2,928,046 moved witness blocks; calibrated 24/0 plus 26 marks × 4 and asymmetric transpose. Scope does not include `h<8` or a distribution. | `ROUND18_REPLAY.md`, `rows/e170_middle_2_stabilizer.md`, `ROUND18_FREEZE.sha256`, `scratch/G/round18/{orbits.json,reconciliation.json,clean-review.log}` | 0.11650 total |
| estimate | All seven size-two orbits and 70 dispersed others priced. Before production: 0.0861–0.1562 core-h, 136–298 MiB inclusive of allowances, not tail bounds. Observed through first replay 274.73 CPU-s; clean replay adds 144.66 CPU-s; ~94 MiB additional scratch including the clean run. | `ROUND18_PREREG.md`, `scratch/G/round18/{sample.json,estimate-0000.log,clean-review.time}` | included above |

## Handoff

- H/critic: if confirmed, debit exactly 15,684 labelled IDs from G-053
  (42 newly transported old IDs plus 15,642 new certified labels); the
  six old pilots were already counted. No other scheme, `h<8`, U88 or
  distribution debit. Reviewer command in `ROUND18_REPLAY.md`.
- Await authorization before another search. Eight stabilizer actions
  are specific to this named scheme; do not assume that saving for any
  other scheme. Do not scan the full labelled residual or attempt a
  second scheme without a separately scoped gate.
- At e170, sixteen degree-six keys remain (nine single, seven adjacent
  pair). `Z=48`, e(H)=122, 24 private and nine double sites; adjacent W
  has 28 sites, one wing crossing and 86 internal edges. No complete
  order-33/122 cover. Round-13 exact t9 thresholds and membership remain
  in `ROUND13_REPLAY.md` and its freeze. The 32/e108 project is lane B's.
