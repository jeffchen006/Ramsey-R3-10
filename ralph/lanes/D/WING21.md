# Nine further marked Y supports excluded by the one-shore bound

**Hand + enum, pending critic.** At `K=2,t=17,m=15` in marked R(3), 150 of the 159 D-048 survivors retain an ordered wing assignment under D-049. Every host still admits each shore separately. The nine new exclusions require the pole-pair join; neither an empty short nor an empty long margin caused any exclusion. Including the three old zero hosts, 12 of the original 162 supports are excluded. This does not close the layer, an edge kernel, or R(3). The surviving assignments are not graphs.

| Exceptional pole | Supports | Ordered on fixed representatives | Marked orbits | Stabilizer actions checked |
|---|---:|---:|---:|---:|
| In triple | 96 → 91 | 1,168,799 → 226,695 | 652,035 → 134,140 | 158 |
| Outside triple | 63 → 59 | 1,127,403 → 216,689 | 682,942 → 132,360 | 106 |
| **Total** | **159 → 150** | **2,296,202 → 443,384** | **1,334,977 → 266,500** | **264** |

The ordered count decreases on every host. Removed: **1,852,818 ordered assignments, 1,068,477 marked orbits**. Each host's fixed counts are summed and divided by *that host's* stabilizer order. No tip-exchange quotient or comparison to a count of unmarked graphs.

| New zero: one-based line of `scratch/D/triple18/roster.jsonl` | Old ordered / orbits | New short / long marginal sizes |
|---:|---:|---:|
| 128 | 3 / 3 | 3 / 2 |
| 140 | 3 / 3 | 3 / 5 |
| 232 | 5 / 5 | 2 / 7 |
| 299 | 1 / 1 | 2 / 6 |
| 488 | 25 / 14 | 4 / 47 |
| 614 | 36 / 18 | 4 / 14 |
| 1009 | 2 / 2 | 4 / 8 |
| 1011 | 1 / 1 | 1 / 4 |
| 1068 | 42 / 21 | 6 / 8 |

## What was checked

For any intersecting family F of physical Y rows and any pole set U containing their union, all same-shore sites supported in U and meeting each row of F are forced independent with F, the poles outside U and the opposite tip. Consequently there are at most `1+|U|−|F|` such shore sites. This includes empty F, repeated physical sites and proper supersets U. It is only a test for this form of independent set. The original D-049 argument was confirmed in `ralph/critic/round_020.md`.

- **Calibration first.** All 250 planted shores from the three cap-three regular C22 graphs pass both the incidence formula and literal independent-set check. The calibration includes all 190 zero-mask shore occurrences; it does not impose the target's support distribution on the plants. All 210 small profiles agree with literal enumeration, including 198 rejections. On three poles, F=`[01,01]` and shore `[02,02,12]` require testing a strict superset of the union (`U=012`); deleting one repeated row or one shore site restores feasibility. Empty-family and three-site controls pass.
- **Producer.** `wing21.py` compiles minimum capacities by a bitset of eligible shore types, applies binary counters to all physical profiles, and checks that each stabilizer preserves the full capacity table. The short-first compatibility count uses the inherited coordinate constraint `1 ≤ J+P+Q ≤ 2`. It skips the three D-048 zero rows *before* computing host masks. `scratch/D/wing21/counts.tsv` contains each host ID, word, margins, assignment/orbit counts, reason for a zero, every new fixed count keyed by permutation, and the associated delta from D-048.
- **Separate audit.** `wing21_literal.cc` enumerates independent subsets of an explicit background graph of poles and physical Y sites, treating every unspecified disjoint Y pair as an allowed edge. For each set of compatible wing types retain the largest background cardinality. A physical profile with `c` compatible sites must have `c + background ≤ 8`. D-048 is reconstructed separately: a background of at least seven cannot coexist with two compatible sites. This is its exact two-site test on the pre-Hall hosts: a seven-site background forces the union of its Y masks to be exactly the complementary pole set. Raw profile counts are obtained by two scalar popcounts (present types plus repeated types), not the producer's bit-sliced counters. `wing21_audit.py` independently constructs physical profiles and group actions, iterates long profiles first, and streams the compatible short bitset. All old and new marginal cardinalities, fixed counts and deltas, orbit sums and reasons match, not merely the totals. Nonidentity fixed-count sums 16,086 → 1,722 are diagnostics only.
- **Resources.** One foreground worker; count 7.43 CPU-s, 20,720 KiB peak RSS; independent verification 4.11 CPU-s, 16,580 KiB. The respective CPU limits were 30 and 60 seconds, both under 64 MiB virtual-memory limits. Compilation was a separate 0.37 CPU-s build (74,056 KiB peak RSS). Including calibration, synthetic pricing and build: **13.91 CPU-s = 0.00386 core-h**. No wing-pair list, solver, SAT proof or candidate. Rebuild and compare using `bash ralph/lanes/D/round21_replay.sh scratch/critic/D21-audit` (fresh directory); `ROUND21_FREEZE.sha256` binds inputs, code, evidence and measurements.

## Next: force individual Y edges without listing wing pairs

Consider two **disjoint** Y rows y,z. Suppose they are nonadjacent. In a one-shore witness containing both, the other Y rows D must hit each of y,z and be pairwise intersecting; the wing sites must hit each of y,z and all of D. Since every wing mask has size at most two, it bridges y to z and lies entirely inside `y∪z`. Thus choosing U to be exactly `y∪z∪⋃D` is optimal; supersets bring no additional sites. If the number of compatible shore sites exceeds `|U|−1−|D|`, a forbidden independent set follows with the opposite tip and poles outside U. The edge yz is then compulsory for this marginal. The argument is conditional on the incidence profile, not a universal edge claim for the host. Multiple occurrences of the same Y row are distinct vertices.

On four poles, rows `01,23` and the four wing bridges `02,03,12,13` force the Y edge; three bridges do not. The test also counts physical doubles correctly. On 250 C22 planted shores it forces 27 edge occurrences on 27 shores, **all present** in the planted graphs. The program `wing21_nextprice.py` reads no target support. On a synthetic 14-row shape: 43 disjoint pairs with tests, 270 compiled limits. Setup + 150 such compilations + 52,969 single-profile calls prices at **2.54 CPU-s**, *excluding* D-049 reconstruction, join and verification. The 52,969 is the measured sum of individual surviving margin sizes (23,965 short + 29,004 long) across today's 150 nonzero hosts; it is not a count of joined pairs. No claim about the target yield.

**Requested next step:** test each marginal alone for incompatible mandatory edges (triangle, more than 15 edges, or excess degree). A Y vertex has at least two neighbors on each wing, since its nonedge with each marked tip is not deficient and shares no middle h. Hence its Y-degree is at most `9−|row|−4`, i.e. 3 on ordinary rows and 2 on the triple. Count the surviving fixed assignments with the inherited bitset join; **do not** test the union of two marginals' edges, enumerate paired profiles or launch SAT. Request one worker at 64 MiB, 30 CPU-s count + 60 CPU-s separate audit, after literal missing-edge/deletion controls. The present round has not applied this proposed test to any target host.
