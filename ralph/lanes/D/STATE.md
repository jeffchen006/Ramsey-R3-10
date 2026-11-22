# Lane D — round 10, November 22, 2026

**R(3), R(4), R(3,10) open; no candidate.** Submitted for review: every
R(3) graph has **two vertex-disjoint nonedge pairs of codegree one**.
In particular it does not belong to the formerly open max-square-12
stratum. Two independent ways to root remain available: the previously
confirmed induced kernel P8 (D-019), or a new four-star cover with 117
generally live keys. The marked roots are not a disjoint partition of
unmarked graphs. No Section 7 end-to-end certificate or general C6/C8 ban.
Round-9 state moved to `LOG.md`; D-015 through D-019 were confirmed by
the critic. The new theorem uses D-015 but not the R9 L=6/7 closures.

## Jobs

| PID | Command | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| none | All bounded foreground producers/checkers finished. | `scratch/D/ind10/` | 0 | — | — |

Share 8; no detached/stopped jobs. No increase requested.

## Results and evidence

`S=scratch/D/ind10`; CPU-h are measured for the specified main stages,
not a claim that pipeline overhead or every pilot was included.

| Label | Result / scope | Evidence | Core-h |
|---|---|---|---:|
| estimate / open | General induced-P8 join, two seeds in all 1,829 fingerprints: 21,948 and 43,896 actual parent pairs, estimated 20.00M and 20.29M canonical children (~16.2M after basic screen). Estimated 2.37–2.40 GB emitted. 44/70 held-out live roots hit 150 nodes. No full unrestricted join. | `JOIN_ROUND10.md`; `S/{pilot-summary.log,held/search.out,model-check.log}` | 0.0073 |
| hand + enum | Deficient-pair graph cannot be a star: 27,289 marked hub positions → 1,917 → 622 → 137 → 6 → 0. All capped rows carried forward; last six also fail **independently** by induced-P8 end deletions: 14 marked P7s, one matched parent pair, one unmarked P8, zero common hub placements. No hypothesis that the hub has only one partner. | `DEFECT_MATCHING.md`; `S/{bindings.log,terminal.tsv,hub4/join8.log,match-cal.log}` | 0.1126 graph search |
| hand + enum | If all deficient pairs intersect but lack a common hub, their entire graph is a triangle. Six frozen stars have 136 labelled profiles / 44 S3 orbits by two exhaustive constructions. All 44 terminal (30+14), without library. Together these two alternatives prove the disjoint-pair reduction. | `DEFECT_MATCHING.md`; `S/{tri.log,tri-all.out,tri-tail.out,bindings.log}` | 0.0090 |
| hand + enum; two checked local CNFs | Redundant no-defect test (also excludes max12): two exact graph searches on 2,434 P6 roots, one with AH=HA and no flat quota, one graph-only / 28,005 nodes. Redundant exactly-one check: 4,741 → 533 → 6 → 0 two-mark P6s, after the first 1,917 single-hub library. No need for either result as a premise of the disjoint-pair theorem. | `S/{audit6.out,bindings.log,proofs/binding.log,jointpair-cal.log}` | 0.0059 no-defect + 0.0267 exact-one; LRAT pilot 0.0093 solver |
| hand + enum; cert for 78 local formulas | Unrestricted marked four-star source: 1,164 labelled / 195 orbits. **78** have an explicit independent ten with a frozen witness for every free nonedge; **78/78** local LRATs accepted by both checkers. **117 generally live**. Two independent source constructors agree exactly. Full C22 control recovers all 349 individually coloured classes across 54 occupied / 172 possible profiles, 2,264 physical marks. | `FOUR_DEFECT_STARS.md`; `S/{four-direct.log,four-check.log,four-certs/witnesses.tsv,four-certs/certificates.tsv,four-open-live.in}` | 0.0024 target graph pilot; 0.0028 complete control |
| estimate / open | Exactly two deficient pairs in the entire graph: 134/195 terminal at 5,000; 61 node-capped. Of nine tails, one closes by 32,756 nodes and eight cap at 40,000. Signed `AH−HA=AL−LA` on same tails at 5,000 closes only the same one. **60 remaining** in this subcase; cannot apply its bounds to the 117 general roots. | `S/{four2.out,four2-tail-sample.out,four2signed.out,signed-cal.log}` | 0.0147 |

## Next round

1. H/critic: audit star-cover scope and both marks in the matching lookup
   (`DEFECT_MATCHING.md`); independent terminal shortcut in
   `JOIN_ROUND10.md`. Triangle does not use a P6 or P8 library. Check the
   direct witness-first four-root census and 78 I10 certificates separately.
   Do not label the global matching theorem `cert`.
2. Focus on the **117 generally live four-star keys**. Freeze the one or
   two unique common witnesses before choosing an arbitrary free row;
   witnesses can coincide, or be among the four anchors. Stratify by
   cross shape (66/36/6/6/3 live). Price actual additional-star counts
   and use the coloured C22 census first. Consider reusing the four-star
   deck only on a pair whose codegree is proved one, not one with a single
   *current* common neighbor and additional possible witnesses.
3. Do not launch a general 20M P8 materialization, a 238-kernel batch, the
   old max12 SAT jobs, or uniform deeper K=2 search. The signed nine-tail
   pilot is a measured negative, not evidence that the tail is empty.
4. Source, logs, per-root terminal bindings and local proofs indexed by
   `scratch/D/round10_evidence.sha256`; disk for this round is modest.
