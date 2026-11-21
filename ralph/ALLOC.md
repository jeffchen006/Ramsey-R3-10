# Core shares (busy solver processes; sum <= 80). Set by the critic each round.

| lane | cores | reason |
|---|---|---|
| A | 6 | R(7) packaging and PB binding are done; reserve a bounded independent P5 replay, not more cubes. |
| B | 18 | Unchanged: protect the live 16-worker prefix plus the staged partial scans; no full e88 launch. |
| C | 6 | Unchanged: P5 is excluded; use bounded structural P4 pilots rather than scaling capped SAT. |
| D | 6 | The biclique cut is sound but closes no new kernel; preserve only a matched pilot budget. |
| E | 18 | Reward the checked (2,32) t=1 closure and give exact small-core triangle tests room to run. |
| F | 6 | Rewire and repair audits are finite negative results; retain a bounded budget for a new escape move. |
| G | 18 | Reward 64 checked cuts; budget bounded calibrated experiments for the six missing e119 residues. |
| H | 2 | Full Lean/PB provenance is bound; ledger and scoped follow-up checks fit two cores. |
