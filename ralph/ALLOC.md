# Core shares (busy solver processes; sum <= 80). Set by the critic each round.

| lane | cores | reason |
|---|---|---|
| A | 4 | P5 coverage and root proof preservation are done; spend only on independent bindings or new coverage. |
| B | 18 | Unchanged: protect the live 16-worker prefix and staged partial scans, not either full anchor branch. |
| C | 8 | Reward checked P4 and P3/e64 exclusions; use the increment only for bounded e63/boundary pilots. |
| D | 4 | Shared pins cut only one of 501 sampled profiles and close no kernel; retain a matched pilot budget. |
| E | 20 | Reward the all-graphs crown closure; prioritize similarly small, exact involution strata. |
| F | 2 | Bounded repairs are exhausted or relabel the same seed; require a nonisomorphic baseline before scaling. |
| G | 22 | Reward 78 checked degree cuts; prioritize a calibrated complete e120 cover or direct obstruction. |
| H | 2 | Unchanged: ledger and tightly scoped Lean bridges fit two cores. |
