# Lane A state

Round 1 (2026-11-21). Core share 14. No critic directives for the first round.

## Jobs

No running or detached Lane A solver jobs. PID 357158 (L300 cubing) finished at its wall cap;
PID 504661 (unfiltered X0) and the compact X0 retry finished at their CPU
limits. All trace replays and cube probes exited. Tool bootstrap complete.
Tool session 46254 (timeout PID 1165159, Python PID 1165160, CakePB PID 1272170)
completed the provisional base check, 353.78 s wall and `RESULT: OK`.

## Results

| Status | Evidence | Result | Core-h |
|---|---|---|---:|
| enum | `scratch/A/tests/nauty.log`, `nauty_link.log`, `sat-tools.log` | Shared nauty 2.9.3, CaDiCaL 3.0.1, kissat 4.0.4, drat-trim, lrat-check, cake_lpr tested; `opt/README.md`/`opt/env.sh`. | <0.001 |
| cert (calibration only) | `scratch/A/tests/{veripb-php,cakepb-php}.log` | VeriPB 3.0.2 and CakePB accepted the same PHP(6,5) proof via elaboration. | <0.001 |
| enum | `scratch/A/tests/sms-r36n13-exact.log` | Patched SMS enumerates 275,086 (3,6,13) graphs; exact canonicity (`--cutoff 0`). | 0.0065 |
| cert (calibration only) | `scratch/A/tests/sms-r36n18-check.log`, `r36n18.cert.{cnf,lrat,wit}` | SMS (3,6,18) UNSAT; 816 triangles, 749 valid lazy IS and 157 checked SB clauses, cake_lpr verified. No custom input extras or cubes. | <0.001 |
| enum | `scratch/A/rc7/r38_27_e85.g6` | Filtered 477,142 McKay (3,8;27) graphs to four e=85 graphs; all passed independent triangle and alpha tests. | <0.001 |
| open | `scratch/A/rc7/{Rc7b.cnf,base.sha256,L300.log,L300.partial.cubes}` | Regenerated PRc7 CNF (444,210 vars, 893,163 clauses). Original cubes/timeouts missing. Fresh L300 emitted 808 cubes before wall cap; not an asserted cover or match. | 0.288 |
| cert (conditional on exact provisional OPB input) | `scratch/A/rc7/base-cert.log`, `scratch/A/rc7/base-cert/` | Independent base regeneration exact; VeriPB and CakePB accepted the equisatisfiable extension of Lane H's provisional OPB + R(7) case constraints, and renamed CNF was a subset. Formal-project OPB byte/provenance check pending; no cube cover claimed. | 0.0970 |
| enum | `scratch/A/rc7/fresh-sample/` | Five freshly emitted PRc7 cubes UNSAT with LRAT, lazy-IS, and block-SB checks (median 1.13 s CPU); historical median 5.2 s is not directly comparable. Base and cover separate. | <0.02 |
| enum | `scratch/A/rc7/{C13-positive,C13-negative,C22-positive,side-C22}.log` | Unordered attachment encoding yields known C13 and a known 6-regular C22; C13 with codegree cap 1 UNSAT. Side filter preserved actual C22 attachments. | <0.001 |
| open | `scratch/A/rc7/{set-X0,compact-X0}.log` | X0 attachment SAT neither solves before 180 CPU s. Side support clauses reduce pair conflicts 6,333,526 → 11,447 and initial RSS/time, but did not close X0. | 0.100 |
| enum (trace replay verified; cert acceptance pending) | `R7_REPLAY.md`, `R7_INPUTS.sha256`, `scratch/A/rc7/replay-final.log` | Independent replay of Lane C's R(7) branch proofs: 4 bound seeds, verified exact cover of 977,008 side pairs, checked 49,569,079 nodes with no cutoff. Rejected a fake closure at a planted C22 root. | 0.0154 per full replay |

## Claims / handoff

- Main result: no R(7) extensions in the independently covered/replayed
  enumeration. The traces are a separate finite proof format, not LRAT.
  Ask critic/H to accept the reduction + checker before marking `cert`.
  No graph witness and no determination of R(3,10).
- `check_sms.py` checks block membership explicitly as well as checked IS shape,
  all triangles, SB witnesses, and cake_lpr; `--allow-input-extras` only treats
  allowed exact input clauses as assumptions. Base and cover still need checks.
- Fixed-X eager edge SAT was already tried (17 h without answer; `notes/cases_local.md`,
  `notes/duo.md`). `set_completion.py` is different: selects unordered independent
  attachment sets per false-twin outer type and separates violated cardinality
  rows. R7 pair lemma for same type implemented; other codegree rules via constraints.
  First unfiltered X0 probe uses 6,333,526 binary conflicts and 775,223 vars;
  do not scale that blindly. Large C35 cap-4 positive control failed to finish
  in 60 CPU/90 wall s despite the smaller positive/negative checks passing.
- `side_filter.py` prunes pair choices via hitting all independent (k-3)-sets,
  MTF demand, and same-side c=7 K2,2. This exploratory SAT route did not close
  X0; Lane C's side-package + common-neighbor-mask DFS is the successful route.
- Reproduce the independent graph6/cover/trace check via `bash ralph/lanes/A/replay_r7.sh`.
  Do not delete `scratch/C/R7_full.?.txt`, `scratch/C/R7_trace.?.bin`, or the
  four seed graph6s without preserving them; their hashes are pinned.
- Historical `Rc7b_L300.cubes`, 99 timeout IDs and proofs were not in this
  checkout or git history. Don't spend more CPU reconstructing the original
  split unless the manifests turn up and the critic needs the SAT route.
- Next: check the proper Lean-emitted PRc7 base with `check_base.sh` if the
  provisional H export is not yet bound. On acceptance of R(7), coordinate with C/D on
  what the corresponding finite-cover approach can do in R(6), without
  scaling the already-measured full fixed-X gluing dead ends.
