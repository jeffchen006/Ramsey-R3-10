# Lane D — round 7, 2026-11-21

**Open:** R(3) and R(4). No graph candidate, no target pin exclusion,
no new Sec. 7 certification. The 110 minimum-root keys and max13–16
are unchanged. The round-6 nine-key max12 cover is critic-confirmed.
This round split its score-two stratum by the density of score-two
edges; both subcases still have a six-key cover, not a partition by
key. The three score-three keys and the `max q22=0` key32 convention
are unchanged. Total this round about 0.084 CPU-h including controls.

## Results and claims

| Label | Scope | Evidence | CPU-h |
|---|---|---|---:|
| hand | In max12 `Smax=2`, either root at a score-two edge whose endpoints have total score-two degree ≥7 (dense), or the score-two edges form a cubic graph, there are no score-zero edges, and `w=0` (balanced). This partitions unrooted graphs before choosing a root. | `SCORE_CAP.md`, section “Exact secondary split” | — |
| hand + enum | Eager score cap uses clean common pivots and counts each isolated edge once. 2,960 local selector checks on known forest/nonforest C16/C20 and 18 exact tight C16 solves match independent component counts and labelled sets. | `score_sat.py`, `check_score_sat.py`, `scratch/D/score_r7/{cal.log,cal16/}` | 0.0078 |
| open | Key24, signed `k=7`, no terminal result with or without global cap (two 100-CPU-s limits). 1,108,371 vs. 3,568,570 initial clauses and 72,530 vs. 10,001 last logged conflicts; zero intermediate SAT candidates on either arm. | `scratch/D/score_r7/key24-{base,eager}.{log,time}` | 0.0555 |
| hand + enum | Edges internal to X cannot affect the two root-star kernels. Attachment-only dense/balanced cuts validated by 27,360 forced threshold checks over every edge of 13 C16 controls and the C20 control (580 rerootings). Mixed tests accept 200/reject 380. Projection finds the known one SAT/two UNSAT tight C16 key pattern; four retained/rejected Clebsch pin controls. | `score_star.py`, `check_score_star.py`, `scratch/D/score_r7/star-cal.log` | 0.0040 |
| open | Key24 `k=7` base/dense/balanced projected CNFs have 423,461/453,857/466,305 clauses, respectively. Base and dense SAT **projections only** (7.64/4.73 CPU-s); balanced caps at ~45 CPU-s without a decision. No key or pin cut; no evidence that full solving is faster. | `scratch/D/score_r7/star24-*.{g6,log,time}`, `SCORE_CAP.md` | 0.0159 |

## Jobs

All bounded foreground jobs ended; no live or stopped Lane D PID
and no detached jobs. Global pilot wrappers 3596547/3596548 (two
slots, session 25359), projected wrappers 3831306–3831308 (three
slots after calibration, session 16804). Limits, invocations and
logs documented in `SCORE_CAP.md`, `scratch/D/score_r7/`. Hashes:
`scratch/D/round7_evidence.sha256`. No extra cores or RAM requested.

## Next

- H/C/critic: audit the dense/balanced split and two-star projection
  completeness in `SCORE_CAP.md`. It depends on max12 and `Smax=2`;
  key32 alone still applies only with `max q22=0`.
- Stop the eager-global key24 build and unchanged projected breadth
  runs; neither has demonstrated terminal attrition. A new balanced
  filter could exploit `w=0` beyond the selected roots, not just
  increase the budget. Prepare a frozen CNF and Sec. 7 replay before
  calling any eventual target UNSAT `cert`.
- Keep old exact R5 exclusions of 19/20/22 (`enum`, critic-confirmed)
  and key34 k=6 exact Farkas separate. No transfer to min-root or R(4).
  Historic details and capped runs are in `LOG.md`.
