# Core shares (busy solver processes; sum <= 80). Set by the critic each round.

| lane | cores | reason |
|---|---|---|
| A | 2 | Compact dual-checker replay is done; two slots suffice for audit and new cover bindings. |
| B | 18 | Unchanged: protect the 16-worker prefix and serialized e43/tail, not full e52/e44. |
| C | 8 | Unchanged: finish the live producer/replay cover, then use bounded upper-layer pilots. |
| D | 2 | Measured filters close no kernel and the whole-family bounds are too loose; retain a two-slot exact pilot budget. |
| E | 21 | Reward the all-graphs a=6 exclusion; scale only an exact, calibrated involution stratum. |
| F | 4 | Reward two nonisomorphic 24-score seeds; bound disjoint unseen-core pilots and independent recounts. |
| G | 23 | Reward eight independent e168 cuts; prioritize the missing residue classes or an e168 obstruction. |
| H | 2 | Unchanged: ledger, hypothesis audit and scoped Lean work fit two slots. |
