# Round 15: occupancy-only e170 implications

The proof in `rows/e170_occupancy.md` adds a necessary condition for
MTF domination of a missing anchor without adding W-edge variables.
The only new variables referenced are *existing* type populations.
The four templates are exactly `round14_pilot.json`. Their historical
integer points are inputs only for the fixed-tuple test and diagnostics;
the matched solve pins nothing. Stop here: no whole-template cut and
no comparable search speed-up.

## Exact controls and fixed tuples (hand + enum)

All 26 C13(1,5) adjacent equality pairs pass the whole paired model
with the new rows. The smaller corpus contributes another 26 rooted
presentations (not a claim of distinct classes). In C13 alone, 208
occupied-type anchor rows are required and 208 are exempt by a real
crossing witness. General two-wing controls on all 140 edges of C35
and all 172 edges of saturated Exoo39 separately check actual
adjacency, boundary common neighbours, and physical W suppliers.
They exercise 15,120 and 21,056 required physical site/anchor pairs
and 11,760 and 20,636 boundary-exempt ones, respectively.

With the round-13 type populations fixed, the following exact rows
have LHS 1 and RHS 0, unchanged if both old edge tables are freed:

| Key `(e,n6,n7,n8,n9)` | Template | Occupied type `(L,R,d)` | Missing wing/anchor | Eligible types, all empty |
|---|---|---|---|---:|
| `(170,2,0,14,24)` | matching+matching | `(5;1,4;8)` | left 3 | 36 |
| `(170,2,0,14,24)` | middle+middle | `(3,4;2;9)` | right 1 | 18 |
| `(170,2,6,2,30)` | leaf+leaf | `(3,4;3;9)` | right 1 | 20 |

The matching+middle tuple passes every occupancy row. The old
set-based supplier filter agrees with all the exact row evaluations.
These are the *same three* unsupported tuples as round 14, not new
whole-template exclusions. Receipts: `scratch/G/round15/fixed.jsonl`.

## Matched price (enum + estimate)

Four unpinned templates, two arms, one solver thread, 8 s LP cap and
10 s MIP cap per template/arm. All eight LP calls returned numerical
feasibility and all eight MIPs furnished integer points, replayed
against exact rows and checked separately for supplier compatibility.
Each strengthened point changes populations relative to the old
point, and every resulting old edge table still violates some shared
product capacities. Those table failures do not show that its
population cannot be completed with a different edge table.

| Template | Columns | Old → new rows | Occupancy point: population L1 change from round 13 | Occupancy point: oversubscribed old edge cells |
|---|---:|---:|---:|---:|
| matching+matching | 510 | 6,567 → 8,503 | 48 | 7 |
| matching+middle | 518 | 6,790 → 8,786 | 38 | 8 |
| middle+middle | 524 | 7,013 → 9,061 | 44 | 6 |
| leaf+leaf | 532 | 7,019 → 9,139 | 34 | 9 |

The timed old/master setup totals were 4.19 CPU-s in the baseline
arm and 7.19 CPU-s in the strengthened arm; cold builds and cached
builds are not equally apportioned in this one pass. Measured
append-only cost was **0.25 CPU-s total**. Matrix packing + LP/MIP
calls total **11.93 CPU-s old vs 18.80 CPU-s strengthened** (LP 2.11
vs 3.28; MIP 9.82 vs 15.52). Total matched run 42.66 user CPU-s,
43.24 s wall, peak 288,332 KiB RSS. This is smaller than round 14's
shared-edge job but implements a strictly weaker test, not a
speed-up for any shared-edge infeasibility objective. Controls,
fixed checks, matched price and exact replay used 65.82 user CPU-s
in total. No new Farkas proof against an unpinned template, no
change to 238+R or the ten conditional U88 keys.

## Replay

From the repository root, `sha256sum -c ralph/lanes/G/ROUND15_FREEZE.sha256`
checks the evidence. Verify existing solver outputs without invoking
an optimizer; the following does not overwrite the frozen files.

```sh
cd scratch/G/round15
ulimit -v 16777216
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
r=../../..
p=$r/opt/venv/bin/python
g=$r/ralph/lanes/G/round15_occupancy.py
nice -n 5 timeout 55s prlimit --cpu=48 "$p" -B "$g" control .
mkdir -p replay
nice -n 5 timeout 16s prlimit --cpu=13 "$p" -B "$g" fixed replay
cmp fixed.jsonl replay/fixed.jsonl
nice -n 5 timeout 35s prlimit --cpu=31 "$p" -B "$g" verify .
```

To reprice, use `nice -n 5 timeout 195s prlimit --cpu=185 "$p" -B "$g" price replay --lp-cap 8 --mip-cap 10` after making the replay directory. The fixed-tuple and exact witness checks do not depend on reproducing the timing.
