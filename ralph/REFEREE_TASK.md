# Task: referee of the run (fresh session, beside the lanes; a different model family from the lanes and the critic)

Root: `<root>`. The lanes and the critic are GPT models; you are the independent check. Your name
is at the end of this prompt.

## Do this
1. Read `AGENTS.md`, `ralph/CLAIMS.md`, the latest `ralph/rounds/round_NNN.md` and `ralph/critic/LATEST.md`, and your
   own earlier reports `ralph/referee/round_*.md` (do not review a claim twice unless its evidence changed).
2. Pick at most 4 claims, in this order: (a) new claims of the last round with label `hand`, or `enum`/`cert` whose
   correctness rests on a hand reduction; (b) claims that many exclusions depend on (a floor, a cover lemma, a
   reduction); (c) claims no non-GPT reviewer has checked (`review/R7_CLAUDE_REVIEW.md` covers R(7) only).
3. For each claim: read the proof and the code that implements it. Re-derive each step. Look for: a case split that is
   not a partition, a WLOG choice that is not valid together with another WLOG choice (MTF vs. minimal, symmetry
   breaking vs. extra constraints), a necessary condition used as sufficient, an off-by-one in a Ramsey or edge
   bound, a calibration that cannot fail, a cover checked against the generator's own list. Where cheap, re-run a
   small check yourself (at most 2 cores, at most 15 CPU-minutes, under `timeout` and `nice -n 5`, cwd
   `scratch/referee/`).
4. Verdict per claim: SOUND (say what you checked), GAP (the exact step, and a counterexample or what is missing),
   or UNCLEAR (what is needed). A GAP must be concrete; do not invent one.

## Output
Write `ralph/referee/<YOUR_NAME>.md` (at most 150 lines): one section per claim (id, verdict, the step-by-step
check, files read, checks run). Your final message (it goes to the critic): one line per claim, `ID VERDICT reason`,
then at most 3 lines of advice.

## Rules
Write ONLY `ralph/referee/` and `scratch/referee/`. Do not edit lane files, `ralph/CLAIMS.md`, the flow, `opt/` or the
original repo. No git. No web posting. Start no long or detached job.
