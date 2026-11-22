# Lane G state — round 17, November 22, 2026

**238 near-regular MTF distributions plus R remain open.** No candidate,
distribution cut, `t9`, U88, or residue-floor change. `leaf+leaf.1` for
the marked e170 adjacent degree-six pair at `h=8` is confirmed from
round 16 (G-051), retired. The other 29 aligned schemes still have
**155,746** untested labelled alignment IDs after round 17.

## Jobs

| PID | Command | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| — | No active or detached G jobs | `scratch/G/round17/` | 0 | — | — |

All runs foreground, nice +5; one slot, virtual cap 384 MiB and actual
peak RSS ~100 MiB. Coverage PID 825700 is gone. Two setup errors before
coverage/sample certificates were fixed (CakeML heap cap and oracle link).
No models, solver caps or timeouts on the successful run.

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| hand + enum + cert (local; pending) | All 30 forward/inverse rosters identical, all 900 hole pairs in the inherited scheme orbits; 24/0 canonical controls, 26 physical marks × 4 actions. Rebound the 62 scout and all 1,357 round-16 proofs. Proper-subset support reuse adds 1,935 distinct outside `leaf+leaf.1` across 27/29 schemes; full supports add zero outside their own scheme. 155,842 IDs uncovered before the sample; no other scheme excluded. | `ROUND17_REPLAY.md`, `ROUND17_FREEZE.sha256`, `scratch/G/round17/{coverage.json,coverage.log}` | 0.0294 |
| cert (local; pending) + estimate | 96 preregistered fresh IDs across the 29 schemes, exact roster and both checker passes on independently rebound archive. No models/caps. 24.98 CPU-s producer + replay, 155,746 left. Weighted mean/max prices 7.53–8.65 core-h and 16.22–22.05 GiB raw, not tail bounds. | `ROUND17_PREREG.md`, `ROUND17_REPLAY.md`, `scratch/G/round17/{sample.freeze.sha256,prices.tsv,archive.log}` | 0.00694 |

Total round-17 use including setup and summary: **0.0389 core-h**.

## Handoff

- H/critic: ledger only the cross-scheme bookkeeping (1,935 newly
  attributed to old checked receipts), the 96 fresh IDs and the direct
  price. Do not debit any full scheme, distribution or U88 key. Use
  `ROUND17_REPLAY.md` for exact reproduction and per-scheme prices.
- Await authorization before any production. The smallest raw residual
  is `leaf+leaf.0` (1,406 after the sample, estimate 0.081–0.133 core-h,
  only six sample calls). Full direct aligned coverage is nontrivial on
  shared scratch and would not handle `h<8`. The cross credit above is
  retrospective and does not price a new transfer discovery arm.
- At e170, sixteen degree-six keys remain (nine single, seven adjacent
  pair). `Z=48`, e(H)=122, 24 private and nine double sites; adjacent W
  has 28 sites, one wing crossing and 86 internal edges. No complete
  order-33/122 cover. Round-13 exact t9 thresholds and membership remain
  in `ROUND13_REPLAY.md` and its freeze. The 32/e108 project is lane B's.
