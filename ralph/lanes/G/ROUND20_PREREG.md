# Round 20 — matching target gate

One target only: marked `e=170`, adjacent degree-six equality, aligned
`h=8`, fixed left matching and any right. Freeze the exact residual
intersection before solving: six lists, **21,125** labelled ranks.
The broader formula maps 80,054 ranks in 17 schemes; 58,929 are old
credit. The baseline reconstructs the outstanding set independently
and compares keyed rank lists exactly with the accepted round-19 JSON.
Both earlier proofs are reused and checked, not solved again.

Preflight passed all 24/0 aligned and 129/11 one-defect class sets, 208
changed-right plants, the guarded/MTF adverse mutations and the forged
positive all-grid blocker with its complete edge list but insufficient
padding. The 693-variable / 22,841-clause matching CNF is 571,912 bytes
versus 598,649 bytes for middle (about 4% smaller). Round 19 middle
measured 1.44 solver CPU-s, 4.03 target CPU-s including rebind/checks, and
10,058,455 bytes CNF+LRAT. Use that only as a same-method price, not a
proof-time bound. New preflight 13.87 CPU-s (plus 6.33 setup CPU-s),
134,552 KiB peak RSS, 7,127,176 apparent bytes. Forecast roughly
40 CPU-s all-in with a clean review; even a near-cap solve plus a review
fits 360 CPU-s. Budget two ~7 MB workspaces plus at most 96 MiB LRAT;
review references the original proof without copying it.

Limits: sequential nice +5; 30 solver CPU-s and 45 wall-s, single
solver, 512 MiB virtual, 128 MiB additional scratch all-in. Use both
checkers; on SAT, cap, or any failed audit do not debit anything. No
per-ID, leaf/middle re-solve, or `h=7` target. The eight `h=7` pilots
stay frozen and unrun by this lane.
