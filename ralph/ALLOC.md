# Round 20 core ceilings — 80 assigned (global limit 80)

| Lane | Cores | Reason relative to round 19 |
|---|---:|---|
| A | 8 | +1. Lossless physical-card index verified; use the audit slot for the independent G-019 expansion check, not another frame scan. |
| B | 2 | Unchanged at the floor; five missing criticals and no new source. Parked. |
| C | 4 | −2. The signed baseline disposed of the bin, but the new test removed zero rows. Only a factored, one-shore test is warranted. |
| D | 17 | −12. Exact counting succeeded, but no support was removed. The next filter is explicitly a one-worker count, not millions of proof jobs. |
| E | 19 | +2. Exact terminal roster and full receipt replay beat the time estimate. Fund the preregistered proof pilot only. |
| F | 5 | +2. Measured, independently replayed footprint exclusions justify the inexpensive remaining marginal census. |
| G | 23 | +10. One checked formula removed 57,947 outstanding alignments; prioritize the last shape over per-ID proofs. |
| H | 2 | Unchanged. Lean interfaces, ledger and scope checks need few cores. |

Ceilings are not launch authorizations. The worker, CPU, RAM and staging limits in `ralph/critic/LATEST.md` take precedence. Keep unused capacity idle.
