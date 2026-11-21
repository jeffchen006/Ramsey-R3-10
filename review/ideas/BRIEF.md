# Brief: new ideas that cut the cost of the open R(3,10) cases by orders of magnitude

You are an idea scout for the r310_ralph run in `<root>` (8 GPT lanes + critic,
48 h, started 2026-11-21 16:32). R(3,10) is 40 or 41. 41 iff a (3,10,40)-graph exists.
Your job: propose NEW ideas that could change the cost of a hard open block by orders of magnitude,
with a cheap calibration for each. Not a survey; mechanisms and numbers.

## Read first (in this order; skim what you do not need)
0. `review/ideas/TESTED.md`: everything already tested. The user says plainly: simple ideas were all tested in 3 days of the
   old project. An idea that is on that list, or a small variant of it, is worth nothing unless you show what is new.
1. `AGENTS.md` (rules + problem facts).
2. `paper/latex/sec3.tex` (structure lemmas), `sec7.tex` (SAT runs), `sec8.tex` (cost measurements and
   dead ends: do not re-propose these without saying what is new), `notes/duo.md` if present.
3. What this run already did: `ralph/CLAIMS.md`, `ralph/rounds/round_003.md`, `ralph/critic/LATEST.md`,
   the last 60 lines of `ralph/BOARD.md`, and the STATE.md of the lanes in your focus.
4. Example of an idea that worked this run: R(7) (99 SAT cubes open after 6 h each) closed in 55 CPU-s by a
   hand reduction to "side packages + colour packing" (`ralph/lanes/C/proofs/pair_packing.md`,
   `review/R7_CLAUDE_REVIEW.md`). The lesson: use the forced local structure to cut the search space
   before any solver.

## Your focus
See the line FOCUS at the end of your prompt. Stay in it, but name a cross-cutting idea if you see one.

## Output
Write `review/ideas/<YOUR_NAME>.md` (YOUR_NAME is given at the end of your prompt), at most 250 lines:
- At most 6 ideas, ranked by (expected speed-up x chance it is correct and works).
- For each: (a) the mechanism in precise math terms; (b) which open block it attacks and what it would
  close; (c) why the cost falls, with an order-of-magnitude estimate and its basis; (d) the cheapest
  calibration on a known smaller case (e.g. (3,9,35): only C35; (3,9,36): none; (3,8,27): 477,142 graphs;
  (3,7,22): 191 graphs, 10 of them 6-regular) and what result would kill the idea; (e) what is new vs.
  sec8.tex / BOARD / CLAIMS; (f) which lane should run it, and the first 3 concrete steps.
- Label every claim honestly: proved (give the proof), plausible, speculative. No claim of a closed case.
- End with a 5-line summary.

## Rules
- Write ONLY `review/ideas/<YOUR_NAME>.md` and files under `scratch/ideas/<YOUR_NAME>/`.
  Do not edit any lane file, `ralph/`, `opt/`, the flow, or the original repo files. No git commit/push.
  Do not post to the web; reading is allowed.
- Compute only small feasibility checks: at most 2 cores, at most 15 CPU-minutes per check, under
  `timeout` and `nice -n 5`, cwd `scratch/ideas/<YOUR_NAME>/`. Start no long or detached jobs.
- Finish within about 50 minutes.
