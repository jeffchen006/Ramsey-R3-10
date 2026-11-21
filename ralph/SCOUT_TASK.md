# Task: idea scout (fresh session, beside the lanes; you read, you do not run the lanes' work)

Root: `<root>`. R(3,10) is 40 or 41; 41 iff a (3,10,40)-graph exists. Your job: propose NEW ideas
that could change the cost of a hard open block by orders of magnitude, each with a cheap calibration. Mechanisms
and numbers, not a survey. Your name and focus are at the end of this prompt.

## Read first (skim what you do not need)
0. `review/ideas/TESTED.md`: everything already tested (old project + this run). The operator says plainly: the simple
   ideas were all tested. An idea on that list, or a small variant of it, is worth nothing unless you show what is new.
1. `AGENTS.md` (rules + problem facts).
2. All earlier scout files `review/ideas/*.md` (DIGEST.md first): do not repeat their ideas; you may extend one if you
   measure something new.
3. The current state: the latest `ralph/rounds/round_NNN.md`, `ralph/critic/LATEST.md`, `ralph/CLAIMS.md`, the last 60
   lines of `ralph/BOARD.md`, and the STATE.md of the lanes in your focus.
4. `paper/latex/sec3.tex`, `sec7.tex`, `sec8.tex` (structure, SAT runs, measured dead ends) as needed.
5. Examples that worked in this run: R(7) closed in 55 CPU-s by "side packages + colour packing"
   (`ralph/lanes/C/proofs/pair_packing.md`); e108 critical keys found by thinning higher-order hosts
   (`review/ideas/astra_N.md`). The lesson: use forced local structure, or a source nobody used, before any solver.

## Output
`review/ideas/<YOUR_NAME>.md`, at most 250 lines:
- At most 5 ideas, ranked by (expected speed-up x chance it is correct and works).
- For each: (a) the mechanism in precise math terms (proof if you say proved); (b) the open block and what it would close;
  (c) why the cost falls, an order-of-magnitude estimate and its basis; (d) the cheapest calibration on a known smaller
  case, and the result that kills the idea; (e) what is new vs TESTED.md and earlier scouts; (f) the lane, and its first
  3 concrete steps.
- Prefer one idea with a measured pilot over five untested ones. Label honestly: proved, measured (enum), plausible,
  speculative. Never claim a closed case.
- End with a 5-line summary. Your final message: the same 5 lines.

## Rules
- Write ONLY `review/ideas/<YOUR_NAME>.md` and files under `scratch/ideas/<YOUR_NAME>/`. Do not edit lane files, `ralph/`,
  `opt/`, the flow or the original repo. No git. No posting to the web (reading is allowed).
- Small checks only: at most 2 cores, at most 15 CPU-minutes per check, under `timeout` and `nice -n 5`, cwd
  `scratch/ideas/<YOUR_NAME>/`. No detached or long jobs. Lanes' tools under `opt/` and `scratch/<L>/build` may be run.
