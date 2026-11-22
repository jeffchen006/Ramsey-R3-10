# Three marked Y supports excluded by the two-site test

**Hand + enum, pending critic review.** In marked R(3), `K=2,t=17,m=15`, the two-site filter D-047 removes **3 of 162** Y supports. The other 159 admit wing assignments under the tested conditions. They are not demonstrated graphs. This does not close the marked layer, any original edge kernel, or R(3).

| Exceptional pole relative to the triple | Supports before → after | Ordered on fixed representatives before → after | Ordered removed | Marked orbits before → after | Orbits removed |
|---|---:|---:|---:|---:|---:|
| Inside (`T=012`) | 99 → 96 | 2,378,983 → 1,168,799 | 1,210,184 | 1,549,150 → 652,035 | 897,115 |
| Outside (`T=123`) | 63 → 63 | 2,438,798 → 1,127,403 | 1,313,395 | 1,579,324 → 682,942 | 896,382 |
| **Total** | **162 → 159** | **4,817,781 → 2,296,202** | **2,521,579** | **3,128,474 → 1,334,977** | **1,793,497** |

| Excluded one-based line in `scratch/D/triple18/roster.jsonl` | Ordinary Y word | Fixed-shore ordered count before | Short / long individually surviving after |
|---:|---|---:|---:|
| 255 | `010012002101100021010` | 1,704 | 27 / 16 |
| 345 | `010012102000010121010` | 472 | 2 / 6 |
| 350 | `010012102001000021110` | 435 | 4 / 9 |

All three have trivial marked stabilizer and `e∈T`. Neither shore by itself eliminates **any** of the 162 supports: the three exclusions require combining the marginal test with the `1 ≤ J+P+Q ≤ 2` pole-pair constraints. The ordered count decreases strictly on every host. No tip-exchange quotient is taken. The separate `m=16` exclusion is unchanged.

## Verification

- For a tight intersecting family F of physical Y sites whose union is U, two sites on the same shore each hitting every member of F and contained in U would give an independent ten: the two sites, F, the poles outside U, and the opposite tip. Equal masks require separate sites. See `WING19.md` for the marked action and D-047. The producer (`wing20.py`) compiles forbidden pairs of types and indexes occurrence on actual sites, intersects the two legal marginal sets with the prior join, and asserts that every marked stabilizer permutation preserves the set of forbidden pairs. Changed fixed counts are combined by Burnside **per host**, not divided by a common order.
- `scratch/D/wing20/counts.tsv` records all 162 fixed-host results: roster ID and word, forbidden pairs of types, marginal survivor counts, identity and orbit counts and their positive removal deltas, and **all 267** new and removed fixed counts keyed by permutation. Summed over nonidentity elements only, 30,207 prior fixed assignments fall to 16,086 (14,121 removed). These action-sums are diagnostic, not extra orbits.
- Smaller checks ran first: on three poles, all 32 pre-Hall-admissible multisets of at most five two-/three-pole Y rows agreed with literal independent-set witnesses on all 672 type-pair tests (243 positive). The 94 other multisets already violate the pre-Hall condition. Two equal physical copies can fail where one cannot. All 250 physical planted C22 shores pass. Two four-pole fixed-count toys give old `10,0` → `0,0` and `60,4,4,0,0,4` → `48,2,2,0,0,2`, checked by literal shore enumeration.
- `wing20_audit.py` imports no producer code. It enumerates physical singleton/pair multisets by settling the lowest pole; enumerates possible independent background sets of exactly seven sites by first choosing the unused-by-rows poles, then filling the rest with distinct intersecting Y sites. For each background it forbids two compatible physical sites, testing both repeated types and distinct types by counts. This background procedure is equivalent to the tight-family test on pre-Hall-admissible hosts: seven independent background sites force the Y sites' union to be exactly the complement of the chosen poles. It independently reconstructs the stabilizer, iterates long rather than short words, intersects eligible shorts using the sums `J+Q` and accumulates fixed-popcounts. Both the old and new counts, every fixed delta, two margins, forbidden-pair cardinality and orbit counts match for every host. No target pairs are enumerated or written. The final checker streams one compatibility mask per long word. Its output is byte-identical to the first independent check which temporarily retained the masks per host.
- One worker, 64 MiB virtual limit. Production 1.59 CPU-s (peak 16,968 KiB RSS); both independent checks together 14.46 CPU-s (6.14 + 8.32), within the separate 60-s cap. Entire round incl. controls and prices 17.86 CPU-s, **0.00496 core-h**. All jobs finished in foreground. `round20_replay.sh` reproduces the comparison and `ROUND20_FREEZE.sha256` binds code, incoming evidence and results. No SAT or certificate production.

## Proposed next count — no target test yet

There is a stronger one-shore test that need not enumerate ordered wing pairs. Let F be *any* intersecting family of physical Y rows (including empty) and U *any* superset of their pole union. Count the physical sites on the given shore whose mask is contained in U and intersects every row of F; write this number as c. The opposite tip, F, these c sites and all poles outside U form an independent set. Thus

`c ≤ |U| + 1 − |F|`.

This is exact for witnesses consisting of that tip, poles and sites which are forced independent by these local incidence rules only: conversely choose U to be the complement of the poles in such a witness. It is not an independence oracle for the actual graph. The `|U|=|F|` instance includes D-047. A strict improvement is possible: on three poles, `F=[01]`, a shore `[0,1,01,2]` forces an independent six (the three sites covered by `01`, Y, pole 2, opposite tip) although there is no nonempty tight F. Deleting shore site `1` removes this witness; literal enumeration finds no other six.

`wing20_nextprice.py` compiles minimum bounds per allowed type set and uses bitwise counters across marginal words. All 210 small literal graph/shore tests agreed (198 excluded). **Synthetic only:** setup + 159 host filters projects to 5.54 or 7.44 CPU-s on two different shapes, before stabilizers and joining. Not a bound or a target rejection measurement. Request one count-only run on the 159 remaining hosts, 30 CPU-s / 64 MiB, one worker, after C22 calibration of the stronger rule; independent audit up to 60 CPU-s if feasible. No further target work before approval.
