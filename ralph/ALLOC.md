# Round 22 core ceilings — 80 assigned

| Lane | Cores | Change from round 21 and reason |
|---|---:|---|
| A | 2 | No change: independent small-class/board inventory for the new G cover, not a second solver queue. |
| B | 2 | No change: all critical e96 parents are exhausted; no coverage price for finding the five missing keys. |
| C | 2 | No change: test whether a physical degree obstruction transfers to a genuinely open card family; the R(6) P4 proof is already complete. |
| D | 24 | +6: nine new support zeros and the checked whole-support proof on 404 give an end-to-end route for the remaining 149 marked supports. |
| E | 26 | +5: conditional core 1 closed with a verified terminal pipeline; shard the next mixed cores through proof, not just census. |
| F | 2 | −4: the new padding cannot fire on any of the 14 rows; no priced signing queue yet. |
| G | 20 | −7: G and N finished the entire h=7 queue. Keep 20 for two-defect boards once calibrated; release the rest to the already calibrated D/E queues. |
| H | 2 | No change: ledger and Lean, not a parallel SAT queue. |

D+E = 50; D+E+G = 70. These are concurrent single-core worker ceilings **including** proof checks, generators and overlapping jobs. Target ≥50 busy on average between rounds, subject to actual host load, RAM and scratch. Round-21 serial limits expire; see `ralph/critic/LATEST.md` for full-share launches, validity gates and staging reservations. Do not burn CPU on duplicate or unsound work to satisfy occupancy.
