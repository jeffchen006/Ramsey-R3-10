# R310-hmz: rules for agents

This folder is a copy of github.com/jeffchen006/Ramsey-R3-10 (a progress report on R(3,10)), made
2026-11-21 for the hmz flow `r310_ralph`: 8 lanes (A..H) + 1 critic, a fresh session each round.
Read `README.md` and `paper/latex/sec1.tex`..`sec10.tex` for what was done before. Large files of that
project (graph classes, cubes, proofs, run logs `runs/`) are NOT here; rebuild what you need.

## The question
R(3,10) is 40 or 41 (Exoo 1989; Angeltveit 2024). R(3,10) = 41 if and only if a (3,10,40)-graph exists:
40 vertices, no triangle, no independent set of 10 vertices. Two ways to answer:
- **41:** find such a graph. Put it as graph6 in `ralph/found/<lane>_<tag>.g6`. The flow checks it with
  two independent algorithms. Only the flow's verdict counts. Never claim R(3,10) = 41 yourself.
- **40:** prove that no such graph exists. This needs every case closed with a certificate
  (or an accepted proof). Each closed case is a partial result with a status label.

The earlier project measured every known route for the open cases at 10^2..10^7 times a budget of
180 CPU-years (`paper/latex/sec8.tex`). Brute force on this machine will not do it. Look for an idea
that changes the cost by orders of magnitude, test it cheaply on a known smaller case, and only then
use cores. A clean negative result with measurements is also a result.

## Hard rules
1. **Write only in this folder** (`<root>`), and only in your own places:
   `ralph/lanes/<L>/`, `scratch/<L>/` (large files), `ralph/found/` (candidate graphs), and one-line
   appends to `ralph/BOARD.md`. Lane A also owns `opt/` (shared builds). The critic owns
   `ralph/critic/`, `ralph/ALLOC.md` and `scratch/critic/`, and may append lines to `review/ideas/TESTED.md`.
   Lane H owns `ralph/CLAIMS.md` and may edit `lean/`. Idea scouts (every few rounds, beside the lanes) write only
   `review/ideas/<name>.md` and `scratch/ideas/<name>/`; `review/` is otherwise the operator's (read only).
   The referee (Gemini 4 Neon, every round, beside the lanes) writes only `ralph/referee/` and `scratch/referee/`.
   Models: lanes D and F and the critic run on GPT-6.2-astra; the other lanes on GPT-6.2-sol; the referee and the
   theory scout (T) on Gemini 4 Neon (another model family: its GAP reports are an independent check, still claims).
   A Landlock write fence holds every turn and job to this folder, /tmp, /var/tmp, ~/.cache and
   ~/.elan (so put CARGO_HOME, PIP caches, builds under `opt/` or `scratch/<L>/`).
   Do not edit the files of the original repo in place (`cases/`, `sms/`, `gluing/`, ...): copy a file to
   your lane folder first. Every other folder on this machine is read only (other users and projects
   run jobs there).
2. **Never `git push`, never `git commit`, never open issues or pull requests, never send mail.**
   The flow commits each round. Reading the web is allowed; posting to it is not.
3. **Core cap: 80 busy solver processes for the whole workspace.** Your lane's share is in
   `ralph/ALLOC.md`. The flow counts every 5 minutes and kills the newest processes beyond 100. Check
   `uptime` before a large launch (192 cores, other users). Wrap every solver in `timeout`; prefer
   CPU-time limits (`prlimit --cpu=SECONDS` or `ulimit -t`). Use `nice -n 5`.
4. **RAM:** run each solver under `ulimit -v` (default 16 GB per process; ask the critic in your report
   for more). The flow kills the newest processes while the workspace RSS sum is over 300 GB. An earlier
   run reached 480 GB with one SMS batch.
5. **Disk:** large files go in `scratch/<L>/` only. Cap for all of `scratch/`: 150 GB (the filesystem is
   94 % full). Delete what you do not need. Never write large files in `ralph/`.
6. **Detached jobs:** `cd scratch/<L> && setsid nohup nice -n 5 timeout ... CMD > LOG 2>&1 &`. The
   job's working directory must be `scratch/<L>/...`, so that the flow counts it for your lane. Write
   its PID, command, log, cores and expected end in your STATE.md at once. `$!` is the PID of setsid;
   find the real PID with `ps`.
7. **Kill only PIDs that your STATE.md lists.** Check `ps -o args= -p PID` first. Never `pkill -f`.
8. **Honest labels.** Use the report's labels: pub, hand, Lean, cert, enum, estimate, open.
   TIMEOUT is not UNSAT; killed is not TIMEOUT; a solver UNSAT without a checked proof is `enum`.
   A claim names its evidence file. The critic re-checks claims; a claim it rejects is removed.
9. **Calibrate first.** Every new encoding, lemma or search must first give the known answer on a smaller
   case: e.g. (3,9,35): only C35(1,7,11,16), 8-regular; (3,9,36): none; (3,8,27): 477,142 graphs;
   (3,7,22): 191 graphs, 10 of them 6-regular; (3,10,39): exists (Exoo). A method that fails its
   calibration gets no more cores.
10. **Before a new idea**, grep it in `notes/`, `paper/latex/`, `ralph/BOARD.md`, `ralph/CLAIMS.md` and
    the lane STATE files. Do not repeat a measured dead end (`paper/latex/sec8.tex`, `notes/duo.md`)
    unless you can say what is new.
11. **Subagents** (if your harness has them): tell each one "start NO solver jobs", or give it an explicit
    core cap inside your lane's share.
12. Codex/GPT and Claude models may be used for second opinions; every claim still needs evidence.

## Shared places
- `ralph/BOARD.md`: append-only messages between lanes, one line each:
  `YYYY-MM-DDTHH:MM [L] text` (e.g. "opt/sms/smsg built, see opt/README.md").
- `ralph/CLAIMS.md`: the ledger of results of this run (lane H keeps it; the critic marks checks).
- `ralph/critic/LATEST.md`: the critic's directives for the next round, one section per lane.
- `ralph/ALLOC.md`: cores per lane (the critic sets it; the sum is at most 80).
- `ralph/rounds/round_NNN.md`, `ralph/STATUS.md`: written by the flow. Read only.
- `opt/`: shared tool builds (lane A). `opt/README.md` says what is there and how it was checked.

## Problem facts (from the report; do not re-derive)
- In a (3,10,40)-graph G: 4 <= d(v) <= 9, max degree 9, 161 <= e <= 180 (e >= 161 is GR Table 5).
  One may assume G is maximal triangle-free (MTF); then min degree >= 6. Non-adjacent u, w: codegree
  c(u,w) <= d(u) + d(w) - 11 <= 7. G - N[v] is a (3,9;39-d(v))-graph with e(G-N[v]) = e - Z(v).
- 545 MTF degree distributions (`cases/degseq.py`, Lean-checked). Gluing (enum): a degree-8 vertex has
  e(G-N[v]) >= 97, a degree-9 vertex >= 88. This closes cube S8 and 20 distributions. **Open: case R
  (9-regular, e = 180, every G-N[v] in R(3,9;30,99), about 1e18 graphs) and 524 distributions N(e),
  162 <= e <= 179.** A t9 <= 88 gluing with no output would close 15 more.
- Case R: split by max codegree c* in 3..7 (Lemma Mc). c* = 7 forces X = G - N[u] - N[w] to be one of the
  4 graphs of R(3,8;27,85) (Lemma R7). R(7): 365 of 464 cubes certified UNSAT, 99 open (6 h each; a
  re-split did not make them easier). Edge kernels: every graph in R(M) completes one kernel from a
  finite list (M = 3: 238, 4: 96,135, 5: 2,852,820, 6: 26,326,286 kernels).
- Symmetry: G is not a Cayley graph; no automorphism of prime order >= 7; order 5 with f = 10, 15 and
  order 3 with f >= 13 are excluded (cert). (5,5) is UNSAT without proof (enum). Open: (5,0);
  (3, f) for f in {1,4,7,10}; all 18 cases of order 2 (a = 7 subcases closed except f = 34).
- Published facts used: R(3,k) for k <= 9; e(3,k,n) tables of Goedgebeur-Radziszowski (GR); class counts
  (`notes/DEPENDENCIES.md`). Third-party tools and versions: `tools/README.md`.
- Independent graph checker: `tools/check_graph.py`. The flow's own checker:
  `.hmz/flows/r310_ralph/gate.py ROOT check FILE [N K]` (you may run it; you cannot change its verdict).
