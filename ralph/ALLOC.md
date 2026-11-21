# Core shares (busy solver processes; sum <= 80). Set by the critic each round.

| lane | cores | reason |
|---|---|---|
| A | 14 | toolchain first, then R(7) certified SAT |
| B | 20 | gluing t9 <= 88 is the cheapest known closure (15 distributions) |
| C | 4 | theory; small checks only |
| D | 12 | R(3), R(4) kernels, new splits |
| E | 10 | automorphism cases |
| F | 12 | construction search |
| G | 4 | LP rows, exact certificates |
| H | 4 | literature, ledger, Lean |
