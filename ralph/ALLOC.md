# Core shares (busy solver processes; sum <= 80). Set by the critic each round.

| lane | cores | reason |
|---|---|---|
| A | 2 | Unchanged: audit new cover bindings and protect frozen artifacts. |
| B | 22 | +4 for floor 108: reserve at most 18 for the prefix/e43/tail chain and up to four for bounded e108 census deltas. |
| C | 8 | Unchanged: certified P3 reductions justify a calibrated isolated-pair join, not wide SAT sweeps. |
| D | 2 | Unchanged: exact tight max12 filters are useful, but two slots suffice for the next key-specific pilot. |
| E | 17 | −4: the 7,962-window batch is complete; retain capacity for the narrower m=11 orbit split, contingent on a measured pilot. |
| F | 2 | −2: 486,212 promotions and exact local scans did not improve score 24; pilot a different source on two slots. |
| G | 25 | +2 for 85 incremental cuts; prioritize the 20 remaining degree-six e168 cases or the exact e120 gap. |
| H | 2 | Unchanged: ledger, hypothesis audits and scoped Lean work fit two slots. |
