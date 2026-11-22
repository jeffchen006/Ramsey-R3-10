# Task: critic of one round of r310_ralph (fresh session)

You are the critic of this round. Eight lanes (A..H) just ended their turns; their reports are below.
You have NO memory of earlier rounds: read `ralph/critic/LATEST.md` (your last directives) and the last
2 files in `ralph/critic/` first. Root: `<root>`. Read `AGENTS.md` (hard rules).

## Do this
1. **Check the claims of this round against the files, not against the reports.** For each new claim
   with label cert/enum/hand: open the evidence file; re-run a small check where you can (at most 4
   cores and 15 CPU-minutes per check, under `timeout`, cwd `scratch/critic/`). For a hand proof, read it
   and look for a gap. Mark each claim CONFIRMED, REJECTED (say why) or UNCHECKED (say what is needed).
   Watch for: TIMEOUT reported as UNSAT; a calibration that cannot fail; a split that is not a
   partition; symmetry breaking that is not valid for the case's extra constraints (MTF lists vs. all
   graphs, see the report's "Scope" note); a cost estimate from too few samples; repeated dead ends.
2. **Check the rules:** cores per lane against `ralph/ALLOC.md` (the flow's verdict header has the
   counts), RAM, scratch disk (cap 150 GB), writes outside a lane's places, any `git commit`/`push`.
3. **Re-balance the cores** in `ralph/ALLOC.md` (sum at most 80; one line of reason per change).
   A lane with evidence of progress (a closed case, a faster calibration, a cost cut by a measured
   factor) gets more. A lane with no measurable step in 3 rounds loses half of its cores to the best
   lane. Theory lanes (C, H) need few cores; never set a lane below 2.
4. **Every 4th round** (round number divisible by 4): pick the most important claim of the run so far
   and audit it in depth.
5. Write `ralph/critic/round_NNN.md` (your full review) and replace `ralph/critic/LATEST.md` with the
   directives for the next round: one section per lane (`## Lane A` ... `## Lane H`), each with at most
   5 concrete directives, ordered by value. Also list duplicated work between lanes and say who stops.
6. End with a short report (at most 20 lines): confirmed and rejected claims, rule breaks, the new core
   split, and the single most promising direction now.

7. In a round with idea scouts (their reports follow the lanes' reports): check their measured claims like a lane's,
   put the ideas worth a test into the lane sections of LATEST.md, and append each dead end they measured to
   `review/ideas/TESTED.md` (one line each). Operator idea files are in `review/ideas/` (DIGEST.md first).

8. The referee (Gemini 4 Neon, another model family) reports after the lanes: re-check each GAP it names against the files;
   if it holds, mark the claim REJECTED or UNCHECKED and say so in LATEST.md; if not, say why in your review.

9. **Operator directive (2026-11-22 18:50): use the compute.** The 80-core share was almost idle for
   many rounds ("Solver processes now: 0"; most jobs 0.001-0.04 core-h), and lane turns end after
   ~10 of their 60 minutes. That is too careful for the ~22 h that remain. From now on:
   - Target: on average >= 50 of the 80 cores busy between one round and the next (check
     `uptime` first; the machine has 192 cores and other users).
   - A pilot of < 0.1 core-h is a calibration, not the step of a round. Once a pilot is calibrated and
     its cost estimate is written down, approve a scale-up to the lane's full ALLOC share, as detached
     jobs under `timeout` with CPU-time limits, that run until the next round or longer (up to 6 h).
   - Do not set per-experiment limits in LATEST.md below 25% of the lane's ALLOC share, except for a
     job that you name as unsound or a repeated dead end.
   - Give the cores to runs that can close an open case end to end (for example: the remaining
     near-regular distributions, the e88/U88 gluing, the 978 open h=7 contexts, the open (2,32)/(2,30)
     involution branches, the R3/R4 kernel survivors, the open P4 rows of R(6)), not to count-only slices.
   - The rules stay: honest labels, calibration before scale-up, certificates where possible, scratch <= 150 GB.

You may not edit the lanes' files, `opt/`, or the flow. Start no long solver job yourself.
