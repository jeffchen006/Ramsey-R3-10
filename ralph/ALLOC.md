# Round 23 core ceilings — 80 assigned

| Lane | Cores | Change from round 22 and reason |
|---|---:|---|
| A | 2 | Unchanged: independent physical witness/transport controls for G, not another board queue. |
| B | 2 | Unchanged: e70 is no longer needed on the saturated arm, but the complete e69 inverse search is not priced. |
| C | 2 | Unchanged: the separate-coordinate bound adds no cuts in its pilot; work on a structural obstruction, not a frame sweep. |
| D | 30 | +6: all 149 marked m15 hosts and the m14 same-pole sector closed. The calibrated S/O production queue has thousands of disjoint inputs. |
| E | 16 | −10: the three priced mixed cores finished, not stalled; no priced successor at handoff. Keep 16 for the next involution closure; transfer the rest to ready or newly demonstrated routes. |
| F | 4 | +2: finished the exceptional-site construction through physical addbacks. Price a strictly wider, finite signing branch, not an unsigned census. |
| G | 22 | +2: h6 finished and 224 h5 board proofs are in hand; use the full share on complementary leaves and witnessed cuts for the residual 62. |
| H | 2 | Unchanged: ledger correction and proof review; no production solver queue. |

Total **80**; D+G = **52**, D+E+G = **68**. These are concurrent busy workers, not a number of *additional* launches. Count existing jobs and checker work. Producers/checkers share a slot; do not count waiting supervisors as CPU use. Dispatch calibrated, priced queues in-turn and leave them running, subject to the host load and the staging envelopes in `ralph/critic/LATEST.md`.
