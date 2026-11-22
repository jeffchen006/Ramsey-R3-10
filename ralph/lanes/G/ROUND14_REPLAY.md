# Round 14: e170 shared-edge price (November 22, 2026)

The predeclared four rows in `round14_pilot.json` cover the three
templates for `(e,n6,n7,n8,n9)=(170,2,0,14,24)` and the only template
for `(170,2,6,2,30)`. This is four rows of the 30-row pair roster;
no unrestricted template was excluded. The model and hand validity
are in `round14_shared_edges.py` and `rows/e170_shared_edges.md`.

## Results

| Row | Exact old masks **and** old tables pinned | Exact old masks pinned, **both tables free** | Free-population LP | Free-population MIP | Free-population with windows |
|---|---|---|---|---|---|
| matching+matching at n7=0 | 9 supply failures | 3-row rational contradiction | numerical feasible | cap | LP cap |
| matching+middle at n7=0 | 6 supply failures | exact integer shared-edge point | numerical feasible | cap | LP cap |
| middle+middle at n7=0 | 5 supply failures | 3-row rational contradiction | cap | cap | LP cap |
| leaf+leaf at n7=6 | 10 supply failures | 3-row rational contradiction | numerical feasible | cap | LP cap |

`scratch/G/round14/recomplete-0.jsonl` contains the exact three
weighted-box/Farkas receipts and the positive integer point. Each
negative receipt can be understood as a missing compatible common
neighbor for a W type and an anchor. The independent support check
recognizes exactly these three of the four old population patterns.
In matching+middle the new edge point satisfies all unrestricted
plain rows and every actual population product bound. Its 28 types
are singletons and its W has **22 triangles**, so this is not a graph
candidate. It fails 38 mixed-window edge inequalities. A two-switch
of one projected table from this compatible point keeps every old
integer row, but demands four edges in side-0 cells `(5,8)` where
identifying the two masks leaves capacity three. Independently,
each of the four original old points admits a coarse-passing switch
creating a new oversubscribed marginal. These are adverse controls,
not branch-cover arguments. Certification applies only to named
population patterns, not all possible populations of the template.

The plain models have 13,294–16,380 columns and 37,917–45,109 rows;
windows have the same columns and 44,564–51,756 rows. The capped
plain IPM+MIP pass used 76.09 user CPU-s. The window-only pass used
66.52 CPU-s and four LP caps. The initial uncapped-internal dual
simplex and the window+MIP passes exhausted their outer CPU limits
(139.69 and 158.53 user CPU-s respectively); this is not infeasibility.
The latter produced three capped rows before it was terminated.
The pinned-population passes used 18.28 user CPU-s to produce all
four exact outcomes, plus replay. This is cheaper only on named
inputs and not a target search speed-up.

Controls: all 26 literal C13(1,5) equality pairs with actual W edges;
97 unary population quota checks; 52 smaller rooted literal support
controls; C35 (15,006 windows / 26,880 codegrees) and saturated
Exoo39 (17,528 windows / 41,692 codegrees). The latter two use the
literal order analogue of the codegree bound, not the target `-11`.
No new distribution debit or U88 change. Do not expand this pilot to
the 26 untested rows or price tighter caps without a new algorithm.

## Replay from repository root

```sh
ROOT=$PWD
G=$ROOT/ralph/lanes/G
P=$ROOT/opt/venv/bin/python
cd "$ROOT/scratch/G/round14"
ulimit -v 16777216
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
nice -n 5 timeout 30s "$P" -B "$G/round14_shared_edges.py" control .
nice -n 5 timeout 65s "$P" -B "$G/round14_edge_control.py" control .
nice -n 5 timeout 65s "$P" -B "$G/round14_edge_control.py" recomplete . --verify
nice -n 5 timeout 65s "$P" -B "$G/round14_shared_edges.py" plain . --verify
nice -n 5 timeout 75s "$P" -B "$G/round14_shared_edges.py" windows . --verify
```

The `--verify` modes build all rows, check key identities and replay
exact rational arithmetic or integer points without an LP solver.
They check no theorem for cap records; these records carry no artifact.
Use the hashes in `ROUND14_FREEZE.sha256` from the repository root.
