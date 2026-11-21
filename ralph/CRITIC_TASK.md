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

You may not edit the lanes' files, `opt/`, or the flow. Start no long solver job.
