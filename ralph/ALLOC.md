# Core shares (busy solver processes; sum <= 80). Set by the critic each round.

| lane | cores | reason |
|---|---|---|
| A | 10 | Toolchain is ready and the independent R(7) trace passed; retire duplicate R(7) SAT work. |
| B | 18 | Protect the existing 16-worker prefix; do not fund full e88 generation at the measured rate. |
| C | 6 | R(7) and the R(6) eight-cycle are closed; add room for bounded path-window experiments. |
| D | 8 | Keep the kernel reduction work, but do not scale encodings that timed out on the matched sample. |
| E | 16 | Reward checked symmetry exclusions and prioritize the small involution residue sieve. |
| F | 10 | Preserve calibrated witness search; narrow follow-ups to degree-valid scores and distinct families. |
| G | 8 | Reward six conditional closures and give exact degree-6-root experiments room to run. |
| H | 4 | Unchanged: ledger and bounded Lean/provenance checks. |
