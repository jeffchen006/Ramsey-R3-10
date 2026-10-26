# Shared toolchain (owner: agent `tools`)

Built 2026-10-24 on this machine, user space only. gcc 11.4.0, cmake 3.22.1, Python 3.10.12.
Root: `./tools` (below: `T`).

- `T/bin`   symlinks to all binaries. `T/opt/<tool>` installed files. `T/src` sources.
- `T/tests` the test inputs used below. Build logs: `runs/tools/*.log`.
- `. T/env.sh` puts `T/bin` and Rust on PATH and sets CPATH/LIBRARY_PATH for CaDiCaL, kissat, nauty.
- Run CPU-heavy commands under your own CPUs: `taskset -c <cpus> nice -n 5 ...`.
- Ask agent `tools` for more tools or packages.

## 1. Python venv
`T/venv/bin/python` (made with uv; pip is in the venv).

| package | version |
|---|---|
| numpy | 2.2.6 |
| networkx | 3.4.2 |
| python-sat (PySAT) | 1.9.dev17 (solvers include cadical195, cadical300, kissat404, glucose4, minisat22) |
| scipy | 1.15.3 (linprog with HiGHS) |
| sympy | 1.14.0 |
| pynauty | 2.8.8.1 (has its own nauty 2.8.8) |
| sms-graph-builder (pysms) | 2024.11 (from SMS source, see 4) |

Test: `T/venv/bin/python -c "from pysat.solvers import Solver; print(Solver('cadical195').solve())"` -> `True`.

## 2. SAT solvers

| tool | version | commit | path |
|---|---|---|---|
| CaDiCaL | 3.0.1 | c60730422e758ef1cebe7aeddf2dda31c996bf04 (rel-3.0.1) | `T/bin/cadical`, `T/bin/mobical` |
| CaDiCaL lib | same, `-O3 -DNDEBUG -fPIC` | | `T/opt/cadical/lib/libcadical.a`; `T/opt/cadical/include/{cadical.hpp,tracer.hpp,ccadical.h,ipasir.h}` |
| kissat | 4.0.4 | 8af8e56f174b778aef3aa45af9f739b2a5f492c2 (rel-4.0.4) | `T/bin/kissat`; `T/opt/kissat/{lib/libkissat.a,include/kissat.h}` |

Tests (PHP(6,5), `T/tests/php6_5.cnf`, UNSAT, exit code 20):
- `cadical -q php6_5.cnf p.drat` (binary DRAT by default) then `drat-trim php6_5.cnf p.drat` -> `s VERIFIED`
- `cadical -q --lrat --binary=false php6_5.cnf p.lrat` then `lrat-check php6_5.cnf p.lrat` -> `c VERIFIED`
- `kissat -q php6_5.cnf k.drat` then `drat-trim php6_5.cnf k.drat` -> `s VERIFIED`
- IPASIR-UP (ExternalPropagator) link test `T/tests/ipasirup_test.cpp`:
  `g++ -O3 -std=c++17 -IT/opt/cadical/include X.cpp T/opt/cadical/lib/libcadical.a` -> `IPASIR-UP OK`

## 3. nauty / Traces
Version 2.9.3 (latest stable). Tarball from users.cecs.anu.edu.au/~bdm/nauty, sha256
`9fc4edae04f88a0f5883985be3b39cf7f898fd6cc96e96b9ee25452743cc1b5b`. Built `-O3 -march=native -fPIC`.

- 58 programs in `T/bin`: geng, gengL, genbg, shortg, labelg, countg, pickg, dretog, dreadnaut, showg, ranlabg, listg, ...
- Libs `T/opt/nauty/lib`: `nauty.a` (dynamic MAXN), `nautyW.a`, `nautyL.a`, `nautyW1.a`, `nautyL1.a`, ..., `libnauty.so`. Headers `T/opt/nauty/include`.

Tests:
- `geng -tu 10` -> 12172 triangle-free graphs (8, 9: 410, 1897; OEIS A006785).
- `dreadnaut < T/tests/petersen.dre` -> `grpsize=120`.
- `T/tests/nauty_link_test.c`: `gcc -O3 -IT/opt/nauty/include X.c T/opt/nauty/lib/nauty.a` -> `grpsize=120`.
- `shortg -q < T/tests/shortg_in.g6` -> 4 classes from 6 graphs (3 relabelled Petersen copies).

Cautions: plain `geng` accepts only n <= 32 (use `gengL` for 33..64).
`shortg FILE` with one file argument sorts FILE in place; use `shortg -q < in > out`.

## 4. SAT Modulo Symmetries (SMS)
Commit 63958bd09a871e484c59270a1d0f22d482dc5770 (v2.0.0-4). Uses its own pinned CaDiCaL fork
`cadical_sms` b023aaf059babf867a7fdfc5fb342d52ffbccb25 (CaDiCaL 2.1.3); do not link it with CaDiCaL 3.0.1.
Release build, boost 1.74 (system), no Glasgow solver.

- `T/bin/smsg`; `T/opt/sms/lib/{libsms.a,libsms.so,libsmscadical.a}`; headers `T/opt/sms/include/sms`.
- pysms in the venv. It calls `smsg` from PATH and writes a temp `.enc` file in the cwd.

CAUTION: pysms `--ramsey a w` means alpha < a and omega < w. For triangle-free graphs with
alpha < k use `--ramsey k 3`. `--ramsey 3 k` gives the COMPLEMENTS; then `--Delta-upp`, `--delta-low`,
edge bounds apply to the complement (n=22: `--ramsey 3 7 --Delta-upp 6` -> 0 graphs).

Test (run from a scratch dir, with `PATH=T/bin:$PATH`):
`T/venv/bin/python -m pysms.graph_builder --vertices 8 --ramsey 4 3 --all-graphs --hide-graphs --args-SMS ' --cutoff 0'`
-> `Number of graphs: 3`. Also (3,4,9)=0, (3,5,12)=12, (3,5,13)=1, (3,5,14)=0, (3,6,16)=2576, (3,7,22)=191.
(3,5,12) and (3,5,13) agree with `geng -tq -D4 n | pickg -q -h:4 | countg -q`.
`--vertices 22 --ramsey 7 3 -D 6 -d 6 --graph6-format` -> 10 graphs; same labelg-canonical set as
MathCheckRamsey (section 6); all pass `check_graph.py --k 7 --n 22`.

## 5. Proof checkers

| tool | version | path |
|---|---|---|
| drat-trim, lrat-check | commit 2e3b2dc0ecf938addbd779d42877b6ed69d9a985 | `T/bin/drat-trim`, `T/bin/lrat-check` |
| cake_lpr (CakeML verified LRAT/LPR) | github tanyongkiam/cake_lpr a36874a8b750b43fe4b385b8ddbf5b033e46a3fa; .S from HOL4 0ae70303, CakeML fb377b4b | `T/bin/cake_lpr` |
| VeriPB | 3.0.2 (Rust), gitlab MIAOresearch/software/VeriPB f41ce91a6bba0223b925f8277d79a531a50d925c | `T/bin/veripb` |
| CakePB (CakeML verified) | gitlab MIAOresearch/software/cakepb 438b8f835f369014578223e0dd6c674e86733682; .S from HOL4 fac52534, CakeML 14856fcf | `T/bin/cake_pb`, `cake_pb_cnf`, `cake_pb_wcnf`, `cake_pb_cp`, `cake_pb_clique`, `cake_pb_colour`, `cake_pb_iso`, `cake_pb_mcis`, `cake_pb_mccis`, `cake_pb_mclique` |
| Rust toolchain (for VeriPB) | rustc/cargo 1.99.1 | `T/opt/rust` (use `env.sh`) |

Tests:
- `cake_lpr php6_5.cnf p.lrat` -> `s VERIFIED UNSAT` (ASCII and binary LRAT both accepted).
- `veripb T/tests/veripb_php.opb T/tests/veripb_php.pbp` -> `s VERIFIED UNSATISFIABLE`.
- `veripb --elaborate e.pbp veripb_php.opb veripb_php.pbp` then `cake_pb veripb_php.opb e.pbp` -> `s VERIFIED UNSATISFIABLE`.

Cautions:
- `lrat-check` reads ASCII LRAT only: use `cadical --lrat --binary=false`.
- `cake_lpr` and `cake_pb` exit 0 also when the check FAILS. Test stdout for the exact `s VERIFIED ...` line.
  `veripb` exits 1 on failure.
- CakeML heap/stack default 4 GB; set with `--CML_HEAP_SIZE=<MB> --CML_STACK_SIZE=<MB>`.
- cake_lpr repo `cake_lpr.sha256`: `cake_lpr.S` matches; `basis_ffi.c` does not, because commit a36874a changed it
  (heap/stack flags) and did not update the sha file. `basis_ffi.c` is the unverified C wrapper.
- VeriPB 2 (Python) is not installed; VeriPB 3 (Rust) replaces it.

## 6. (3,k)-graph generators and the R(3,8)/R(3,9) SAT+CAS pipeline
Added 2026-10-24 (online-materials rule). Code read before build; no sudo, no installs outside tools/.

| tool | source (fetched 2026-10-24) | path |
|---|---|---|
| triangleramsey 1.1 (Brinkmann, Goedgebeur, Schlage-Puchta): maximal triangle-free (MTF) graphs and triangle Ramsey graphs R(K3,H) | http://caagt.ugent.be/triangleramsey/triangleramsey-1.1.zip, sha256 6d16c21b...f548a; built with nauty 2.9.3 files | `T/bin/triangleramsey` (n <= 32), `T/bin/triangleramsey-64` (n <= 64) |
| MTF (Brandt, Brinkmann, Harmuth 1998): MTF graphs, `ramsey_kn x` | http://caagt.ugent.be/mtf/mtf.c, sha256 4fc06111...a648; `cc -DMAXN=1024 -DWORDSIZE=32 -O3 nauty.c nautil.c naugraph.c schreier.c naurng.c mtf.c` | `T/bin/mtf` |
| mc2g6 (own, tools): multicode (triangleramsey output) -> graph6 | `T/bin/mc2g6` | |
| MathCheckRamsey (Li, Duggan, Bright, Ganesh, IJCAI 2025, arXiv 2502.06055): SAT+CAS orderly generation, DRAT + permutation certificates | github.com/ConDug/MathCheckRamsey commit 84b2aefccb61d2eeea3fd9607a3de82a438a69d1 (2025-04-14); cadical-ks = CaDiCaL 1.9.4 fork | `T/src/MathCheckRamsey`; `T/bin/cadical-ks`, `T/bin/maplesat-ks`, `T/bin/march_cu` |

Tests:
- `triangleramsey N outputlevel N | mc2g6 | labelg -q`: MTF graphs n=9..12 = 16, 31, 61, 147; the SAME
  labelg-canonical sets as `geng -t N` filtered for maximality in Python. `mtf n 12` gives the same counts
  and the same n=12 count.
- Ramsey mode (testgraph must have >= 6 vertices; `T/tests/K6.mc`, `K7.mc`):
  `triangleramsey 17 ramsey K6.mc` -> one (3,6,17)-graph (passes check_graph); `18` -> none.
  `triangleramsey 22 ramsey K7.mc` -> one (3,7,22)-graph (0.6 s); `23` -> none (26 s). Add
  `write_all_ramseygraphs` for all MTF Ramsey graphs (written to a file in the cwd).
  "None found" is written as the 4 bytes 01 00 00 00; `mc2g6` then exits 3 with a message.
- `mtf n 18 ramsey_kn 6 no_save no_recover` -> 0 graphs at n=18 (R(3,6)=18).
- MathCheckRamsey (copy the repo to your own run dir; scripts use relative paths and write there; put
  `T/venv/bin/python` first in PATH as `python3`): `./main.sh -n -d 5 -D 6 23 3 7` -> UNSAT, DRAT
  `s VERIFIED`, "All 1064 blocking clauses verified" (27 s, 4 CPUs). `./main.sh -n -d 6 -D 6 22 3 7` -> 10
  solutions = the 10 six-regular (3,7,22)-graphs; same labelg set as SMS; all pass check_graph.
  Edge variable order: (i,j), i<j, column-wise: j = 2..n, i = 1..j-1, var = 1, 2, ...

Cautions:
- Do not run MathCheckRamsey `dependency-setup.sh`: it runs `pip3 install` outside the venv (not needed; all is built).
- MathCheck proofs contain trusted clauses ("t" lines, the CAS blocking clauses). Its own drat-trim fork
  (2020 base) skips them; `drat-trim/check-perm.py` checks them separately against the `.perm` file.
  Not tested: whether standard drat-trim / cake_lpr accept these proofs ("t" lines are not standard DRAT).
- MTF writes log, dump and output files into the cwd; run it in a scratch dir. Its output format
  ("multi code2 s old") is not multicode; mc2g6 does not read it. Prefer triangleramsey.

Public code NOT found (searched 2026-10-24): Goedgebeur-Radziszowski 2013 (R(3,10) <= 42) programs and
Angeltveit 2024/25 (R(3,10) <= 41) programs. Angeltveit's paper (arXiv 2401.00392v2, EJC 32(4) P4.30) has
no code/data statement; it names nauty only. The EJC pages list no supplementary files.

## 7. tools/check_graph.py (independent graph checker)
`python3 T/check_graph.py --k 10 --n 40 FILE` (graph6 lines, ">>graph6<<" header allowed, or one 0/1 matrix).
Exit 0: at least one graph read and all pass; 1: a graph fails; 2: bad input/arguments.
Fixed 2026-10-24 for critic review 1 (C1-C6): header line keeps its graph, strict graph6 (length, chars,
padding), `--n`, clear errors on 0 graphs / n=0, strict arguments, no asserts in parsing.
Also (critic C7, 2026-10-24): selftest uses explicit checks (works under `python3 -O`) and tests that bad
graph6 strings are rejected; long size field for n < 63 rejected; `--k`/`--n` must be positive; binary file -> exit 2.
Older versions: `runs/tools/check_graph.v1.py`, `v2.py`. `python3 T/check_graph.py --selftest` -> `selftest ok`.

## 8. Tools owned by other agents (not built or tested by `tools`; ask the owner)
| tool | owner | location | notes |
|---|---|---|---|
| ls: SA/VR local search for (3,k,n)-graphs | anneal | `anneal/ls.cpp` | build `g++ -O3 -march=native -std=c++17 -o ls ls.cpp`; usage in `notes/anneal.md`. anneal reports (web review, 2026-10-24): no public R(3,k) local-search code exists (Exoo's site, AlphaEvolve repo = constructions only, GitHub). |

## 9. Job tools: jobctl, cuberun, teamstat (stdlib Python, `/usr/bin/python3`; `--help` on each)
Goal: one monitor per agent, wake only on events (TEAM_RULES "Token budget").

### jobctl
```
jobctl start AGENT NAME [--expect 6h] [--fail REGEX] [--found GLOB] [--cpus SUBSET] [--ok-rc 0,10] [--cwd DIR] -- CMD ARGS
jobctl status [AGENT]        # state, CPU%, RSS (whole process tree), runtime, last log line
jobctl stop AGENT NAME       # TERM to the job's process tree, KILL after 10 s
jobctl log AGENT NAME [-n N] | jobctl forget AGENT NAME
jobctl wait-event AGENT [--poll 30] [--timeout 8h]   # blocks; prints events; exit 0 (3 = timeout)
```
- Always runs `taskset -c <AGENT's CPUs from TEAM_RULES> nice -n 5 CMD`, with OMP_NUM_THREADS = CPU count.
  A detached supervisor records the exit (rc, runtime, CPU s, max RSS); the job survives the agent.
- Registry `runs/jobs/AGENT/NAME.json` (+ `.exit.json`); log `runs/AGENT/NAME.log`.
- Events (each reported once): EXIT, CRASH (rc != 0 / signal), STOPPED, LOST (no process, no exit record),
  FAIL (new log line matches a pattern: default Traceback, segfault, bad_alloc/out of memory,
  NOT VERIFIED, FATAL; add `--fail`), DEADLINE (`--expect` passed, still running),
  FOUND / ALERT (new file `FOUND*` / `ALERT*` anywhere under `runs/AGENT/`, any new file in `graphs/found/`,
  or new match of `--found GLOB`). Files that exist at the first wait-event are not news.
- Only one wait-event per agent (lock). Recommended agent pattern: after starting jobs, run ONE background
  `jobctl wait-event AGENT --timeout 8h`, end the turn, act when it returns, start it again.

### cuberun
```
jobctl start sms cc1 --expect 2d --ok-rc 0,10 -- cuberun run runs/sms/cc1 --cnf base.cnf --cubes cubes.icnf \
   --timeout 2h --proof-ext .lrat --cmd 'cadical -q --lrat --binary=false {cubecnf} {proof}' \
   --check 'cake_lpr {cubecnf} {proof}' --after-check zstd
cuberun summary runs/sms/cc1          # counts, cpu mean/median/p90/p99/max, extrapolated total
```
- INPUT: `--cubes FILE` (+ `--cnf BASE`), or `--cnfs LIST` (one CNF per line), or `--jobs LIST` (one job per
  line, `TAG<TAB>ARGS` or `ARGS`; `{args}` is inserted unquoted, `{tag}` is recorded).
- Placeholders: `{cnf} {cubecnf} {cube} {units} {lits} {lineno} {cubefile} {args} {tag} {id} {proof} {model}
  {dir} {log}`. `{units}` = file of unit clauses "lit 0"; `{cube}` = "a lits 0"; `{cubecnf}` = base + units
  (deleted after the job unless `--keep-cubecnf`, then `cnf/ID.cnf`, hashed). `{lineno}` = line number in
  the cube file (e.g. smsg `--cube-file {cubefile} --cube-line {lineno}`). Other braces stay as they are.
- Workers = CPUs of the process / `--threads-per-job`; each worker pinned to its own CPUs.
- Status: exit 10 SAT / 20 UNSAT, else `s SATISFIABLE`/`s UNSATISFIABLE` line, else exit 0 = UNKNOWN,
  else ERROR. TIMEOUT kills the job's process group.
- `results.jsonl`: one line per finished job (id, tag, status, rc, wall_s, cpu_s, maxrss_mb, cpus, cube,
  lineno, args, last log line, files {path: bytes, sha256}, check, check_s, check_maxrss_mb, check_last).
  Re-running the same command resumes; `--retry timeout,error,unknown` re-runs those.
- Proofs: `--proof-files '{proof}*'` (templates, globs allowed) = files hashed and, after a VERIFIED check,
  handled by `--after-check keep|delete|zstd`; `--keep-files LIST` = hashed and always kept.
- `--check TEMPLATE`: verdict ONLY from stdout regex `--check-ok` (default `^s VERIFIED`); FAILED, TIMEOUT
  or NO_PROOF -> `ALERT_errors.txt`, all files kept. `--check-parallel K` limits checks at once (cake_lpr
  needs 4-10 GB each).
- SAT: full solver output kept in `sat/ID.out`; `--on-sat TEMPLATE` runs after each SAT (`{log}` = that
  output), e.g. decode + `check_graph.py`; result goes into `FOUND_SAT_ID.txt`. `--stop-on-sat` stops all;
  `--sat-expected` writes no FOUND files. ERROR -> `ALERT_errors.txt`. Put OUTDIR under `runs/AGENT/`, so
  FOUND/ALERT files are jobctl events.
- Logs: kept for every status except UNSAT (unless `--keep-logs`); the last log line is always recorded.
- `cuberun summary OUTDIR` (counts, cpu mean/median/p90/p99/max, check cpu, max RSS, stored MB, estimated
  total cpu, LOWER BOUND if timeouts), `--tsv` (one row per job), `--timeouts FILE` (writes the TIMEOUT
  cubes as "a lits 0" lines, or job lines, for re-cubing), `--json`.
- `--sample K [--seed S]` runs K random cubes; the summary extrapolates to all input cubes.
- jobctl: use `--ok-rc 0,10` for cuberun (10 = stopped on SAT) so that the end is EXIT, not CRASH.
- Tests (2026-10-25, tools CPUs): R(3,5) n=14, 32 march_cu cubes (depth 5), CaDiCaL LRAT + cake_lpr per cube:
  32 UNSAT, 32 "s VERIFIED UNSAT", 4 min wall on 4 CPUs (= R(3,5) <= 14). n=13: SAT at once; `--on-sat`
  decodes the model and check_graph.py passes it as a (3,5,13)-graph. Job-list mode: UNKNOWN / ERROR /
  TIMEOUT / SAT / UNSAT all classified right; stop + restart resumes without repeating finished cubes.

### teamstat
`teamstat` (about 2 s): per agent CPU busy on its CPU list (all users) vs allotted, CPU% and RSS of this
user's processes pinned inside that list vs memory cap, jobctl jobs running/ended/bad, age of the status
file; newest files in `graphs/found/`; newest `ALERT*`/`FAIL*`/`FOUND*` files under `runs/`.

## 10. Working while the desktop app sleeps: jobctl queue, watchd, mbox, night lead
Agent sessions run only while the app's bridge is up. These tools need no app and no LLM (except the
optional night lead).

### jobctl queue (follow-up jobs)
```
jobctl queue AGENT NAME [--after AGENT/JOB]... [--when-free] [start options] -- CMD ARGS
jobctl queue-list [AGENT] | jobctl queue-cancel AGENT NAME | jobctl queue-run [AGENT]
```
- Starts by itself (when watchd runs `queue-run`, every minute) once every `--after` job has EXITED with an
  ok rc (`--ok-rc` of that job). `--after NAME` without `AGENT/` = same agent; a dependency may itself be
  queued (chains work). `--when-free`: also wait until the agent has no running job and its CPUs are
  < 25% busy (all users, 1 s sample). A failed/lost/missing dependency -> state BLOCKED + event.
- Start options are those of `jobctl start` (`--expect`, `--ok-rc`, `--cpus`, `--fail`, ...); cwd = where you
  ran `jobctl queue`.

### mbox (file mailbox, `runs/mail/AGENT/{new,cur}`)
```
mbox send TO "text" [--from NAME]     # TO = agent, lead, or all; also when SendMessage fails
mbox read AGENT [--peek] | mbox list [AGENT] | mbox tail AGENT [-n N]
```
Agents: read your mailbox at the start of each turn (`mbox read AGENT`).

### watchd (server daemon in tmux, no LLM)
```
tools/bin/watchd start     # tmux session r310, window watchd; survives logout of the app
tools/bin/watchd status | tools/bin/watchd stop | tools/bin/watchd once (one tick, for tests)
```
Every 60 s: `jobctl queue-run`; events of all agents (EXIT, CRASH, STOPPED, LOST, FAIL, DEADLINE, BLOCKED,
FOUND*/ALERT* under runs/AGENT/, QUEUE start, IDLE = agent had running/queued jobs and now has none)
-> one line in `runs/events.log` + mail to the owner; every new file in `graphs/found/` ->
`check_graph.py --k 10 --n 40`; PASS -> mail to all + `runs/watchd/VERIFIED_<file>`, FAIL -> mail to lead.
State in `runs/watchd/state.json` (restart-safe; on its first start, old events are not news, but every
graph already in graphs/found/ is checked once). One instance (flock). Heartbeat: `teamstat` shows it.
Agents' own `jobctl wait-event` keeps working (separate state).
Not covered: a server reboot (tmux dies too; then run `watchd start` again).

### Night lead (optional, headless `claude -p`)
- Tested 2026-10-25: `~/.local/bin/claude -p` (2.1.296) runs with a clean environment (no app variables)
  and uses the CLI's own login. An earlier call the same morning answered "You've hit your weekly limit
  · resets Oct 29"; a later one worked. watchd detects the limit message and pauses for 6 h.
- On only if `runs/watchd/nightlead.on` exists. Called only for MAJOR events: graph PASS, FOUND* file, FAIL,
  MEMKILL, CRASH/LOST of a job that ran >= 1 h (not SIGTERM = stopped by hand), IDLE of an agent that is not
  a support agent or a live tmux teammate (ignored: tools, tlead, sms, cases, duo, critic, gluing, symsat;
  `NL_IGNORE_IDLE` in watchd). At most 6 calls per day (counter resets at local midnight), one at a
  time, 30 min limit, 40 turns. Brief: `notes/NIGHT_LEAD.md`. Allowed tools only: Read/Grep/Glob, Bash for
  jobctl, mbox, teamstat, `cuberun summary`, tail/ls/grep/cat, Edit of `notes/night_lead_log.md`.
  Output: `runs/watchd/nightlead/<time>.log`; it mails the owner and lead and appends to night_lead_log.md.
- Test calls (2026-10-25): it read the events, saw that a test CRASH was fake (0 s job), took no action,
  mailed tools + lead, wrote 3 log lines. As the brief asks.
- It uses the account's usage quota.

### Tests (2026-10-25, test mode `WATCHD_TEST_DIR=...`: own events/state/found dir, all mail to a test box)
- Queue: q2 after q1 started after q1's EXIT; q3 after q2 + when-free started next; a dependency on a
  missing job and on a crashed job -> BLOCKED events. EXIT, CRASH, IDLE events -> events.log + mail.
- graphs/found: an empty 40-vertex graph -> GRAPH-FAIL; Exoo's (3,10,39)-graph with test n=39 -> GRAPH-PASS,
  mail to all, VERIFIED file.

## 11. Memory caps (enforced, 2026-10-25)
Caps come from the "memory cap" column of the TEAM_RULES table.
- `jobctl start` runs every job in its own cgroup scope: `systemd-run --user --scope -p MemoryMax=<cap>
  -p MemorySwapMax=0`. The limit covers the whole process tree (RSS, no swap). Over the cap, the kernel kills
  the job: CRASH rc=-9, and the event says "probably over its memory cap". Default cap = the agent's cap;
  `--mem GB` sets a lower one (a higher one is refused). Fallback if systemd-run fails: `prlimit --as`
  (virtual memory; weaker). `jobctl status` / the start line show `mem<=XG(cgroup)`.
  The cgroup cap limits used memory, not address space: a 100 GB MAP_NORESERVE reservation runs under a
  1 GB cgroup cap but fails under `prlimit --as 1G` (ENOMEM). So it does not have the `prlimit --as` /
  `ulimit -v` failures (sms saw smsg segfault under `prlimit --as`). smsg (tools and sms builds) gives
  the same (3,6,16) count of 2576 under cgroup caps of 4 GB down to 64 MB.
- `cuberun`: under jobctl, the whole run has the job's cap. Outside jobctl, `--agent A` is required:
  cuberun then restarts itself under A's CPUs and cap. `--mem-per-job GB` also caps each solver/check job
  on its own (a killed job = ERROR rc=137 + ALERT).
- `watchd` memory guard, every minute: RSS per agent = its jobctl job trees + this user's processes
  pinned (taskset) inside its CPU list. > cap: MEMWARN (once per 6 h, mail to the agent).
  > 1.5 x cap: SIGKILL its biggest jobs / process groups until the total is <= cap; MEMKILL event, mail to
  the agent and the lead; a killed jobctl job ends as MEMKILL. Unpinned processes (agent sessions,
  watchd) are never touched. Jobs that already ran before this change get no cgroup, but the guard covers them.
- `tools/bin/watchd mem`: dry run (RSS per agent vs cap; kills nothing).
- Tests: a 600 MB allocation under `jobctl --mem 0.2` -> killed (rc=-9); 100 MB under 0.5 -> OK; `--mem 99`
  for tools -> refused. cuberun `--mem-per-job 0.2`: 600 MB job -> ERROR rc=137, ALERT. watchd test mode
  (tools, fake cap 0.5 GB): a 1 GB job + a 0.3 GB pinned process -> the job was killed (MEMKILL), the
  0.3 GB process kept. Scopes also work from a bare environment (XDG_RUNTIME_DIR/DBus defaults are set).

## 12. LaTeX (TinyTeX = TeX Live 2026, user space on <local disk>; 2026-10-26)
- Source: github.com/rstudio/tinytex-releases v2026.10, `TinyTeX-1-linux-x86_64-v2026.10.tar.xz`
  (sha256 4d519d62...6566), unpacked to `tools/opt/TinyTeX`; `tlmgr update --self`, then packages from the
  TinyTeX CTAN mirror (tlnet.yihui.org). pdfTeX 3.141592653-2.6-1.40.29, tlmgr r79639.
- Everything stays inside `tools/opt/TinyTeX` (TEXMFHOME = texmf-local, TEXMFVAR/CONFIG = the system
  ones of that tree). Nothing is written to <home> (tested with HOME set to an empty scratch dir).
- Wrappers in `tools/bin` (they put TinyTeX first in PATH): `pdflatex latexmk bibtex biber lualatex xelatex
  tlmgr kpsewhich`. Add packages with `tools/bin/tlmgr install NAME` (only `tools` should do this; ask).
- Packages: amsmath, amscls (amsart, amsthm), amsfonts (amssymb), mathtools, hyperref, cleveref, booktabs,
  graphics (graphicx), xcolor, pgf (tikz), algorithm2e, algorithmicx, algorithms, enumitem, geometry,
  microtype, natbib, biblatex + biber, float, caption, etoolbox, thmtools, mathrsfs, doi, url, xurl.
- Test: `tools/tests/latex/test.tex` (amsart, all packages above, BibTeX amsplain) and `testbiber.tex`
  (biblatex/biber): `latexmk -pdf test.tex` -> PDF, 0 warnings, citations and \cref resolved; same for biber.
- Not installed: tectonic (optional; ask if needed).
