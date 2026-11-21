# Lane A state

Round 5 (2026-11-21), core share 2. No candidate graph and no new case
closure. Followed the critic's frozen residue audit directive; no new
solving for R(7), floor-120/107, or P4/P5.

## Round 5 jobs

| PID | Command / log | Cores | Start | End |
|---:|---|---:|---|---|
| 3504835 | Foreground frozen proof-binding pilot, `scratch/A/residue5/proof-sample.log` | 1 | 21:14 | finished |
| 3512117 | Foreground exact residue incidence, `scratch/A/residue5/moves-full.log` | 1 | 21:15 | finished |
| 3570486 | Foreground independent full dual LRAT replay, `scratch/A/residue5/proof-full.log` | 1 | 21:17 | finished 21:25 |

All ended normally; no live jobs or detached solvers. The other short
foreground calibration and adversarial checks finished as well.

## Round 5 results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| cert (audit of G, supplied rows only) | Bound 14,315 e120/e121 labelled residues. All 11,425 clique witnesses checked. All 2,890 independent DIMACS rebuilds and dual LRAT replays passed, including 66 unpinned e120, 2,813 unpinned e121 and 11 e121 exact total-e169 proofs. Each of the last 11 has a valid SAT model for its much weaker unpinned core; mismatching one pinned LRAT against that core was rejected by both checkers. No e>169 claim for those 11. | `HIGH_RESIDUE_AUDIT.md`, `HIGH_RESIDUE_AUDIT.sha256`, `scratch/A/residue5/{index-full.tsv,proof-full.log,proof-cal.log,partition-negatives.log}` | 0.082 |
| enum (exact incidence for supplied rows) + hand | 1,523 e119/e120 and 24,794 e120/e121 canonical incidences agree in both directions. 230 e120 and 803 e121 supplied classes are deletion-critical. All supplied e120 have legal additions. Any omitted e120 is deletion-critical with at most `6-m` distinct upper neighbors, where `m` is the missing e120 count. Zero additions is not ruled out. Supplied row 789 has 20 labelled additions but only five nonisomorphic children; the other e120 rows have at least ten. | `HIGH_RESIDUE_AUDIT.md`, `scratch/A/residue5/{moves-cal.log,moves-full.log,five-children.log}` | 0.012 |
| open (census) | 14,389 of 14,395 still supplied. Bind-delta rejects this as complete, with no output. On the complete 191-graph C22 calibration, relabelled duplicates, omitted classes, insufficient counts and duplicate/omitted/bad proof-partition controls fail as expected. | `audit_residue_moves.py`, `scratch/A/residue5/{delta-negative.log,moves-cal.log,partition-negatives.log}` | 0.010 |
| cert provenance | Compact R(7) and existing floor hashes still pass; no copies of bulk higher-level proof artifacts needed. | `scratch/A/residue5/preserved-{r7,floors}.log` | <0.001 |

Pilot overhead ~0.016 core-h, including a 50-LRAT spread sample.
Full proof replay estimate ~309 CPU-s and ~535 wall s; actual 294.63 CPU-s,
440.45 wall s, 104 MiB RSS. Exact incidence estimate ≤90 CPU-s; actual
40.07 CPU-s. Commands, wall/CPU limits and sampling in
`scratch/A/residue5/estimates.txt` and `replay_high_residues.sh`.

## Next

- If G returns new e120/e121 rows, run `audit_residue_moves.py ... bind-delta`
  against the original frozen raw hashes; use independent CNF bindings and
  proof scopes for the new rows only. No complete new catalogue had been
  announced by the handoff. A partial degree-five decomposition is not a
  cover of all e120 types, nor is the zero-addition branch alone.
- Retain `scratch/A/residue5/index-full.tsv`, the compact `complete-v2`
  and `r7-proof-v1`. No need for a repeat replay without a defect or a delta.

## Round 4 archive

Round 4 (2026-11-21), core share 4. R(3,10) remains unresolved. No candidate
graph and no fresh solving. The old R(7) SAT cubes are not needed; the
critic accepted the independent finite proof in round 1.

## Round 4 jobs

No live or detached solver jobs. The foreground floor audits, packing,
and rational arithmetic replay used at most two cores in total and ended.

## Round 4 results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| cert (audit of accepted G-008/G-009; MTF only) | Degree-six residue floor 120: all 74 validated, canonically distinct `5+69` rows; exact old 68 overlap, six disjoint new e119 rows at full positions 3, 6, 14, 15, 16, 29. Old and new graph6/CNF/LRAT bindings agree with the original hashes. Both checkers passed every independent CNF. Portable `complete-v2` is 3.8 MiB. | `FLOOR_AUDIT.md`, `FLOOR_AUDIT.sha256`, `scratch/A/root-residue/complete-v2`, `scratch/A/floor-audit4/{root6.tsv,pack6.log,replay6.log}` | 0.003 |
| cert (audit of accepted degree-seven floor 107; MTF only) | Verified all 19,589 graph6 seeds directly for alpha <=8, triangle-freeness and exact canonical classes, 19,521 explicitly bound incompatibility traces, and both checkers on all 68 independently regenerated exceptional CNFs. Negative masks and wrong exception rejected. | `FLOOR_AUDIT.md`, `scratch/A/floor-audit4/{e104,e105,e106,controls,negative_demand,negative_exception}.log` | 0.019 |
| cert / conditional cert (audit only) | Independent reconstruction of baseline (545 → 524 → 454) and delta byte-matches G's CSV. All 463 supplied rational certificates passed G's read-only checks. 55 incremental e167 cuts; 8+6+9 conditional on previous gluing floors; 376 near-regular + R remain; 13 more if e88 MTF gluing is excluded. No new closures from this audit. | `audit_floor_delta.py`, `scratch/A/floor-audit4/{delta.csv,farkas.log}` | 0.004 |
| cert provenance (no fresh solving) | Read-only R(7) and retained PB hash checks match. No P4/P5 reprise; no new PB or R(7) proofs. | `scratch/A/floor-audit4/preserved-*.log`, `R7_REPLAY.md`, `PB_BINDING.md` | <0.001 |

Estimate and runtime evidence: `scratch/A/floor-audit4/estimate.txt`.
Whole e106 pilot 1.95 CPU-s, even naively scaled ~283 CPU-s; full
three levels 65.2 CPU-s, 266 MiB RSS. Farkas pilot 1.98 CPU-s/36;
463 rows actually took ~12 CPU-s. The combined script passed in 89.6
CPU-s (0.025 core-h additional; `end-to-end.log`). G's frozen index
matches all 91 keys and 78 witness locators (`frozen-compare.log`).

## Next

- Preserve `scratch/A/root-residue/{retained-v1,complete-v2}` and
  `scratch/A/floor-audit4`; use `FLOOR_AUDIT.md` and its replay script.
  Complete-v2 supersedes v1 as the degree-six coverage bundle.
- If G announces an exact e120 or e107 cover (or a proof for the omitted
  part), audit that new coverage and its CNF/proof order before claiming
  the next floor. Partial supplied residues do not suffice.
- Keep R(7)/PB proof snapshots available. No SAT or P4/P5 reiteration
  absent a specific binding defect; no extra request to another lane.

## Round 3 archive

Round 3 core share 6. No candidate graph and no new SAT run.

## Round 3 jobs

No live or detached jobs. P5 comparison, proof packing/replay and hash checks
ran in the foreground (one core each) and finished normally.

## Round 3 results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| enum (coverage only, supports C-009) | Independent full-row overlay matches the exact labelled P5 set modulo path reversal: 2,454 P4 rows, 177 windows, 47,031 pairs, 1,156 P5 rows. C21 42 spans/672 exact marked alignments; reverse P4/P5 accepted, deleted/mismarked P5 rejected. Not a separate extension search or claim of closure. | `P5_REPLAY.md`, `P5_REPLAY.sha256`, `scratch/A/p5/{control,reversed,reversed-p4,missing,wrong-mark,full}.log` | 0.0033 |
| cert (existing fixed-residue proofs; supports G-004/G-007) | Preserved and replayed five e118 and 63 e119 graphs with independently reconstructed DIMACS and both LRAT checkers. Catalogue is 68 distinct classes but six e119 classes are still missing. 220 planted roots satisfy all clauses; crossed proof and forged matching digest both fail. | `RESIDUE_BUNDLE.md`, `RESIDUE_BUNDLE.sha256`, `scratch/A/root-residue/{retained-pack,retained-replay,crossed,forged,positive,uniqueness}.log` | 0.0024 |
| cert provenance / no new coverage | C and A R(7) pair lists and traces byte-identical; input/code hashes match. Retained PB artifacts and H's full export match the named inputs. No SAT or PB reruns. | `R7_REPLAY.md`, `PB_BINDING.md`, `scratch/A/round3-preserve.log`, `scratch/H/pb-bind.log` | <0.003 |

P5 estimate from 430 smaller pairs: 18.6 CPU-s plus larger-row overhead;
actual full 10.87 CPU-s, 10.88 wall, 33 MiB peak RSS, cap 240 CPU/300 wall.
Six-residue pilot pack + replay 0.68 CPU-s, extrapolated ~8 CPU-s; actual
7.03 CPU-s for 68, cap 60 CPU/90 wall. Both used 16 GiB virtual limits.

## Round 3 handoff (superseded)

- H/critic: use the exact P5 join comparison with C's trace and the hand
  reduction; keep the overall C-009 result at enum until critic action.
- G will announce any new e119 residue. Independently replay its proof with
  `RESIDUE_BUNDLE.md` and keep a separate versioned bundle; G owns the census.
  Preserve `scratch/A/root-residue/retained-v1` (3.5 MiB), no bulk copies.
- Preserve `scratch/A/r7-proof-v1` and the PB links; rerun neither absent an
  input/checker change. `PB_BINDING.md` documents H's byte binding (not
  cube coverage or the hand/Lean encoding provenance itself).

## Round 2 archive

Core share 10. Critic directives: preserve R(7), replay
Lane C's path-window cover independently, help bind the retained PB chain.

### Jobs

None running or detached. The R(7) replay, P4 controls/full replay and PB
binding each used a single foreground worker and finished. No SAT was launched.

### Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| cert (C-004; already accepted) | Preserved four R(7) seeds, pair lists and traces independently from Lane C's scratch. Portable replay checked all 977,008 roots and 49,569,079 nodes in 57.6 CPU-s. | `R7_REPLAY.md`, `R7_INPUTS.sha256`, `R7_CODE.sha256`, `scratch/A/r7-proof-v1`, `scratch/A/r7-replay-round2/replay-X*.log`; critic `round_001.md` | 0.0160 |
| enum (coverage only) | Independent P4 window replay exactly matches 2,454 labelled rows, 31,994 placements, 13,613 core classes. All 42 shorter-case planted paths recovered; deleted row, forged empty cover, forged triangle row rejected. Does not close any R(6) path branch. | `P4_REPLAY.md`, `check_path_cover.py`, `scratch/A/path/{control,missing,forged-closed,forged-triangle,sample,full}.log` | 0.0176 incl. sample |
| open (PB provenance only) | Verified exact composition of retained PB input: 99,701 provisional cube rows + 89,717 independent case rows; altered augmentation and altered PB input both rejected. Proof/input/output artifacts pinned and checked. Full-project `cube_R.opb` not yet available at handoff. | `PB_BINDING.md`, `PB_ROUND1.sha256`, `scratch/A/rc7/{bind-provisional.log,pb-manifest.log,bind-control/*log}` | <0.003 |

P4 full replay calibrated before launch: sample 96 classes/18 rows, 13.28
CPU-s including global setup, and C's production scan 72.85 CPU-s. Expected
few CPU-minutes, bounded to 600 CPU/900 wall seconds and 16 GiB virtual memory;
actual 49.82 CPU-s, 58.26 wall, 247 MiB peak RSS.

### Round 2 handoff (superseded)

- H: when actual `R310.Files` export is available, follow `PB_BINDING.md`.
  Byte equality and exact composition reuse the old PB chain without solving
  any SAT cubes. A binder pass alone does not establish Lean provenance.
- Coordinate with C for an independent replay of its next path-window
  reduction or certificate, first on an exact planted control. Do not treat
  the 2,454 survivors as actual completions.
- Preserve `scratch/A/r7-proof-v1` (21 MB on disk). Other lanes can choose
  scratch output with `bash ralph/lanes/A/replay_r7.sh NEW_SCRATCH_OUTPUT_DIR`.

## Round 1 archive

Core share was 14. No critic directives for the first round.

### Jobs

No running or detached Lane A solver jobs. PID 357158 (L300 cubing) finished at its wall cap;
PID 504661 (unfiltered X0) and the compact X0 retry finished at their CPU
limits. All trace replays and cube probes exited. Tool bootstrap complete.
Tool session 46254 (timeout PID 1165159, Python PID 1165160, CakePB PID 1272170)
completed the provisional base check, 353.78 s wall and `RESULT: OK`.

### Results

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
| cert (now accepted) | `R7_REPLAY.md`, `R7_INPUTS.sha256`, `scratch/A/rc7/replay-final.log` | Independent replay of Lane C's R(7) branch proofs: 4 bound seeds, verified exact cover of 977,008 side pairs, checked 49,569,079 nodes with no cutoff. Rejected a fake closure at a planted C22 root. | 0.0154 per full replay |

### Notes

- No R(7) extensions in the independently covered/replayed enumeration.
  The traces are a separate finite proof format, not LRAT; accepted by critic.
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
- Historical `Rc7b_L300.cubes`, 99 timeout IDs and proofs were not in this
  checkout or git history. Don't spend more CPU reconstructing the original
  split unless the manifests turn up and the critic needs the SAT route.
