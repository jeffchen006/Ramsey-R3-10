# Task: decide R(3,10) (r310_ralph, one round of one lane)

You are one round of one lane of a Ralph loop. You have NO memory of earlier rounds. Your memory is
your lane's `ralph/lanes/<L>/STATE.md` (root `<root>`). Read it first and leave it
correct for the next round. Eight lanes work at the same time in this folder; a critic checks each round.
Solver jobs run detached and outlive your turn.

## Every round
1. Read `AGENTS.md` (the hard rules), your `STATE.md`, your section of `ralph/critic/LATEST.md`,
   `ralph/ALLOC.md` (your core share) and the last 40 lines of `ralph/BOARD.md`.
   If your STATE.md says BOOTSTRAP: read the parts of the report and notes that your lane task names,
   set up, and replace the bootstrap text.
2. Collect the results of your lane's jobs: finished, dead, stopped (`ps -o stat` T).
3. Do the critic's directives first, unless you say in your report why not.
4. Work: think, write code, calibrate on a known case, then launch jobs within your core share.
   Before a long job, estimate its cost from a sample, and write the estimate down.
5. Update your STATE.md (under ~250 lines; move old detail to `ralph/lanes/<L>/LOG.md`):
   - jobs table: PID, command, log, cores, start, expected end;
   - results table with honest labels (pub/hand/Lean/cert/enum/estimate/open) and core-hours;
   - claims: each with its label and evidence file (lane H copies them to `ralph/CLAIMS.md`);
   - what you learned that a later round must know; next steps.
6. Post a one-line note on `ralph/BOARD.md` for anything another lane needs (a tool built, a lemma,
   a dead end, a request).
7. End with a short report (at most 25 lines): what you did, what you found (with labels), what runs
   now (PIDs, cores), what is next, and what you need from other lanes or the critic.

## Spirit
The aim of the team is to settle R(3,10). The known routes cost far more than this machine has, so
the high-value work is a new idea that cuts a case by orders of magnitude, tested cheaply first.
Prefer certified results (LRAT/DRAT checked, exact Farkas certificates, Lean) over enumeration.
Do not spend a whole round on reading: each round must leave a measurable step (a tool, a calibration,
a closed case, a measured cost, a lemma with a checked proof, or a well-founded dead end).
