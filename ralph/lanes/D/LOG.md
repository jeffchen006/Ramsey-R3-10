# Lane D — round 3, 2026-11-21

## Historical round 5 handoff (jobs ended)

- Max-root, not min-root: 111 kernels independently counted by genbg
  across max12..16 as 35/39/26/8/3. Max12 has codegrees 2..3, 19
  isolate keys ruled out by hand and cyclic 19/20/22 ruled out by
  exact transport Farkas (`enum`, critic round 005 confirmed).
  After these exclusions every edge kernel in max12 is a forest.
- Round 5 star fixed point on all 16 no-isolate keys: only 20/22
  refuted by projection; 14 feasible relaxations. Their earlier
  composite Farkas and 24/31 CakeLRAT checks are superseded by the
  unfiltered LP, not Sec. 7 certificates. `TRANSPORT.md` and
  `scratch/D/round5_evidence.sha256` retain these results.
- Key34 (`k=6`) checked by exact Farkas with/without forest;
  k=7..14 feasible LPs. Key21 filtered IPM feasible. Integer-mask
  MILP hit cap; no claim. No change to 110 min-root keys.
- Completed supervisors 30557 (star 24,26,27,28,29,30,31,32),
  136533 (transport 19..34), 479273 (key34 k=6..14), all gone.

## Historical round 4 handoff (no jobs carried)

- `TRIPLE_U.md`: all 67,730 marked K3,4 U rows pass one T-group
  locally: 8,669 C15 only / 40,008 C6+C9 only / 19,053 both. All
  witnesses and 30 smaller rows checked. No R(4) exclusion. Do not
  rerun one-group filters or repeat fixed-cycle attempts.
- `PIN_BOUND.md`: C16 relaxed pin counts exactly agree across 26
  sides. The whole-family bounds on minimum-root R(3) sum to at most
  6.916e18, too loose for a sweep. Matching cut removes 5/501 pins.
- `OPPOSITE_SHADOW.md`: hand 2-slot obstruction on 88 side 1 and
  5-slot transversal on 149. Widths 2/3 reject 27/32 of 48 sampled
  profiles. Matched blockers remove 44/501 (39/47 on 88); transversal
  removes 104/200 on 149. Opposite incidence pin test on 149 rejects
  200/200, but unpinned 32 CPU-s cap; no whole kernel refuted.
- `FIXED_CYCLES.md`: exact C16 filtered output calibration; matched
  eight target variants cost 9.57/27.87/13.02 CPU-s (baseline/direct/
  deficit), so do not scale. The 110 minimum-root representatives
  remain a cover and no round-4 jobs remained.

**Open:** R(3) still has 110 surviving root-swap kernel representatives
(cover only); the R(4) K3,4 stratum remains open. No graph candidate.
Lane share 6; peak four concurrent workers, no jobs remain.

## Round 3 results and claims

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| hand | One triangle-free graph for shared singleton/support edges per side gives necessary local restrictions. One-sided count-multiset pins are an exact split for a fixed labelled kernel up to outside relabelling. | `ralph/lanes/D/PINNED_SIDE.md` | — |
| enum | Both shared widths preserve all labelled C16 outputs. Of 800 matched R(3) profiles, 501 pass the old baseline with the unique-triple rule; shared singles reject none of these, width 3 rejects one. Do not scale shared joined encoding. | `scratch/D/factor_cal16_shared/check.log`, `scratch/D/shared_sample.tsv` | 0.0082 |
| enum | Pinned C16 exact control: 241 side profiles (100 with symmetry lex); both recover the same graph sets independently canonicalized per kernel across all 13 kernels (5 classes). All 5 independently checked. | `scratch/D/{pinned_cal16,lex_cal16}/check.log`, `scratch/D/lex_cal16/graph_check.log` | 0.0018 |
| enum | All 48 sampled R(3) pins exhausted with zero independent cuts, total 23.73 CPU-s, max 0.92 incl. startup, 0 cap hits. First profile from each of eight buckets also refutes bare triangle/degree/codegree cap without min-edge, diameter, private, or IS rows. | `scratch/D/pinned_r3/{manifest.tsv,k*.log,ablation/}` | 0.0117 incl. first ablation |
| open | Second pin ablation: bare degree+triangle or degree+coordinate caps separately feasible in all eight; combined coordinate caps/triangle hit 8/8 CPU caps; full caps minus outer triangles had 1 feasible and 7 capped. | `scratch/D/pinned_r3/ablation2/` | 0.0142 |
| enum | Bare fixed-profile DIMACS for kernel 149, side 0, line 1 checked with DRAT trim and CakeLPR. **Not** a section 7 encoding/cover chain, and not closure of kernel 149. | `scratch/D/pinned_r3/proof/k149-0-1.{lrat-check,sha256}` | ~0.001 |
| enum | Assumption-core calibration agrees on all 241 C16 outcomes with bare substituted model. On kernel 149 side 0, 3/4 requested cores finish; each uses 21–22 of 22 slots and generalizes to no other sampled projection. Symmetry lex on the same bucket yields 160 vs 159 orbits per 160 outputs, but 11.04 vs 7.22 CPU-s. Do not scale either unmodified. | `scratch/D/{core_cal16,core_r3,lex_r3}/`, `ralph/lanes/D/PINNED_SIDE.md` | 0.011 plus C16 core calibration |
| hand | In the R(4) K3,4 equality branch, the U attachments span either C15 or C6+C9 via the three selected perfect matchings. Each three-vertex singleton group at the other side must hit at least seven U vertices; `e(V)=e(U)+9`. These are conditional necessary structure only. | `ralph/lanes/D/BICLIQUE_R4.md` | — |
| enum | Full B order-15 (3,6) input (64,732 distinct, pinned): 48,322 balanced, 36,039 viable under U-only anchor codegrees (67,730 partitions). Calibrated by exact 30-partition replay on the 12-vertex class. No K3,4 exclusion. | `scratch/D/balanced{12.replay,15.log,15.canon.log}`, `ralph/lanes/D/BICLIQUE_R4.md` | <0.001 |

## Round 3 job ledger (all ended)

Smoke 0.73 CPU-s gave a linear estimate of 35 CPU-s for the 48 requested
pins (not a catalogue forecast); bounded at 384 CPU-s overall. Four
timeout supervisors reconciled, each with 12 clean child exits; none
stopped. Foreground comparison/smoke/replay runs finished as well.

| Timeout PID | Command | Log in scratch/D | Cores | Start | Hard end | Status |
|---:|---|---|---:|---|---|---|
| 1557463 | `pinned_probe.sh 149 pinned_r3 8` | `pinned_r3/worker-149.log` | 1 | 19:01:14 | 19:07:14 | done |
| 1557464 | `pinned_probe.sh 151 pinned_r3 8` | `pinned_r3/worker-151.log` | 1 | 19:01:14 | 19:07:14 | done |
| 1557465 | `pinned_probe.sh 88 pinned_r3 8` | `pinned_r3/worker-88.log` | 1 | 19:01:14 | 19:07:14 | done |
| 1557466 | `pinned_probe.sh 227 pinned_r3 8` | `pinned_r3/worker-227.log` | 1 | 19:01:14 | 19:07:14 | done |

## Next round

- Prefer cutting the one-side marginal universe before enumerating more
  profiles. Test a necessary obstruction on substantially fewer than 21
  pinned slots, or look for an exact small orbit-count estimate on one
  kernel. Cheap per-pin refutation alone is not an economic sweep.
- H/critic: review the matching-witness and seven-neighbor K3,4 lemma in
  `BICLIQUE_R4.md`; R(4) residual cross attachment is not yet encoded.
- A: the pinned CNF proof is evidence for one conditional pilot only;
  no request to certify all pins until there is a tractable cover.

## Prior handoff (round 2)

**Open:** No R(3) kernel closure or 40-vertex candidate. Lane share 8;
at most four simultaneous children used this round.

## Round 2 results

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| hand | Two-side mask-count factorization; exact local residue test; three singles plus their three pair supports force a triangle. | `ralph/lanes/D/SIDE_FACTOR.md`, `factor_sat.py` | — |
| enum | 2/18/266 minimal forbidden multisets on 2/3/4 labelled coordinates, or 1/7/22 up to coordinate permutations. DFS and exhaustive optional-edge replay on the negative orbit representatives; corrupt t=2 library rejected. | `scratch/D/side_obstructions_orbit.json`, `scratch/D/side_obstructions_verify.log`, `scratch/D/negative_width2_fake.log` | 0.014 (two generations plus replay) |
| enum | Exact C16 controls, 13/13 kernels each for base factor, local-library factor and additionally no-K3,3 factor. Same five canonical graphs as root-only SMS and exact per-kernel labelled equality among variants; independent graph checker passed. | `scratch/D/factor_cal16{,_local,_k33}/`, `scratch/D/factor_cal16_k33/labelled_check.log` | 0.0018 |
| open | Baseline joined factor: 0/10 decisions, 10 CPU-limit exits on the old stratified SMS sample; no graph models, assembly 1.8–2.2 CPU-s (per kernel). No full-run extrapolation. | `scratch/D/r3_factor75/k*.log`, `r3_survivor_sample.tsv` | 0.203 |
| enum | Four matched mask pilot IDs, 8 side instances: first 100 profiles each for shadow and local-library versions (not uniform or exhaustive). Local rows reject 47/800 shadow outputs, and no strengthened output fails direct replay. No side is refuted. | `scratch/D/marginal_pilot/replay.tsv`, `scratch/D/marginal_smoke/` | 0.029 |
| hand | Saturated biclique incidence bound: R(3) has no K3,3, so triple supports at any center are unique. Also R(4) has no K4,4, and any K3,4 in R(4) has exactly the described 15+18 outside attachment split. Equality controls checked at n=6 and n=10. | `ralph/lanes/D/SATURATED_BICLIQUE.md`, `scratch/D/biclique_equal.log` | — |
| enum | R(3) four-cycle kernel obstruction checks 65/238 oriented matches, all already excluded by C. No change to 110 root-swap representatives. Triple uniqueness rejects 284/800 shadow marginals (245/400 on IDs 88,227), numbers are sample-only. | `scratch/D/r3_biclique.log`, `scratch/D/marginal_pilot/replay.tsv` | <0.001 extra |
| open | Strengthened joined factor (local library and unique triples): still 0/4 decisions, all CPU-limit exits with zero models. The first marginal improvement did not translate into a joined verdict. | `scratch/D/r3_factor75_k33/k*.log` | 0.083 |

## Round 2 job estimates and ledger

**None active.** Reconciled all eight supervisor PIDs at 18:10 CET;
each worker log contains all expected child outcomes.

110 root-swap representatives are a cover of surviving rooted kernels,
not a partition of unrooted models. Exact C16 calibration on 13 kernels
recovered all five expected classes in 2.10 CPU-s including import. Plan:
matched 10-probe R(3) survivor sample, caps 75 CPU-s and 225 wall-s each,
at most 0.208 CPU-h on up to four cores (three probes/worker maximum).
This is a bounded comparison against round 1, not a full-run estimate.

Marginal catalogue pilot: four matched Boolean-mask probe ids (149,
151, 88, 227), both sides, 100 outputs maximum each with/without the
extra exact local rules. Smoke 149 used 32.32 CPU-s across all four
children; remaining three ids project roughly 97 CPU-s, capped at
180 CPU-s total with at most two simultaneous child processes.

Strengthened joined pilot estimate: the original 10 probes all timed
out (730.95 aggregate CPU-s). A directly replayed sample of 800
shadow marginals rejects 284/800 on repeated triples (at high-edge
IDs 88,227: 245/400). With the hand saturation inequality plus the local
library, C16 again matches. Retest the same four mask IDs only, 75 CPU-s each (0.083 CPU-h
maximum), two workers; no full sweep from the projection reduction.

| Timeout PID | Command (after timeout) | Log in scratch/D | Cores | Start | Hard end |
|---:|---|---|---:|---|---|
| 2801295 | `factor_probe.sh r3_factor75 75 149 34 88` | `r3_factor75/worker-149.log` | 1 | 17:56:44 | 18:09:14 |
| 2801296 | `factor_probe.sh r3_factor75 75 151 111 227` | `r3_factor75/worker-151.log` | 1 | 17:56:44 | 18:09:14 |
| 2801297 | `factor_probe.sh r3_factor75 75 155 51` | `r3_factor75/worker-155.log` | 1 | 17:56:44 | 18:09:14 |
| 2801298 | `factor_probe.sh r3_factor75 75 16 39` | `r3_factor75/worker-16.log` | 1 | 17:56:44 | 18:09:14 |
| 3013391 | `marginal_probe.sh marginal_pilot 151 88` | `marginal_pilot/worker-151.log` | 1 | 18:03:04 | 18:07:39 |
| 3013393 | `marginal_probe.sh marginal_pilot 227` | `marginal_pilot/worker-227.log` | 1 | 18:03:04 | 18:07:39 |
| 3184312 | `FACTOR_STRENGTHENED=1 factor_probe.sh r3_factor75_k33 75 88 149` | `r3_factor75_k33/worker-88.log` | 1 | 18:07:48 | 18:16:33 |
| 3184313 | `FACTOR_STRENGTHENED=1 factor_probe.sh r3_factor75_k33 75 227 151` | `r3_factor75_k33/worker-227.log` | 1 | 18:07:48 | 18:16:33 |

## Round 1 results (historical)

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| enum | Regenerated 238 R(3) kernels; independent colored path/cycle signatures agree one-to-one; 166 modulo global side exchange. Formula calibrated on smaller -D2 catalogue (12 oriented, 10 up to exchange). | `scratch/D/catalogues/component_check.log`, `ralph/lanes/D/catalogue_m3.py` | <0.001 |
| enum | All 55 pinned controls extend to satisfying auxiliary assignments: 5 modes × (ten known C22 plus C35), relabeled at globally min-C4 edge. Pin test is not complete enumeration. | `scratch/D/pinned/pinned.log` | 0.0092 |
| estimate | C22 calibration expected ~2–5 minutes wall per variant (repo old 93–116 CPU-s across 474; local first kernel 0.22 CPU-s); both batches cap each solve at 8 CPU-s. | `scratch/D/smoke/results.tsv`, sec8.tex | — |
| enum | Both `local` and `minedge` give only C13(1,5) across 12/12 kernels under M=3; exact canonical comparison. | `scratch/D/cal13_{local,minedge}/canonical.g6` | <0.001 |
| estimate | R3 paired probe: 10 nonduplicate survivor orbits stratified by e(F), seed 3401, at most 75 CPU-s each on base and minedge (0.42 CPU-h worst case across both). Previous first-15 timings 0.6–33s or >3600s; survivor sample deliberately emphasizes unsolved classes, not a uniform whole-catalogue predictor. | `scratch/D/r3_survivor_sample.tsv`, sec8.tex | — |
| enum | Boolean-mask projection: C13 pinned projection accepted (with endpoint minimum-edge rows and all lazy cut families enabled); n=14 control kernel rejected. Both <0.1 CPU-s after import. | `scratch/D/projection_cal{13,14}.log` | <0.001 |
| estimate | Boolean-mask R3 pilot: four matched C LP survivors (two low e and two high e), hard caps 4×60 CPU-s, 0.067 CPU-h; R3 assembly cost unknown (C linear LP builds of same rows take seconds). | `ralph/lanes/D/mask_probe.sh` | — |
| estimate | Efficient totalizer orientation retest, same selected four kernels: original first two exhausted 60 CPU-s during construction (4.5–4.7 GiB RSS). On the n14 control clauses decreased 5991 → 4615; one-sided limits now use the cheaper polarity. New upper budget 4×60 CPU-s. | `scratch/D/r3_mask/`, `scratch/D/projection_cal14_leanTotalizer.log` | — |
| estimate | Lazy Boolean-mask retest on same four: eager v2 still exhausted 60 CPU-s in assembly. Lazy cuts replace large families of totalizers and add independent sets of the possible-edge supergraph. Clauses on n14 control now 2640 vs 5991 originally. Cap remains 4×60 CPU-s. | `scratch/D/r3_mask_v2/`, `scratch/D/projection_cal14_supergraph.log` | — |
| estimate | MiniCard native projection: C13/n14 controls matched, and repeated-literal native cardinality semantics truth-table checked. No CNF auxiliaries: n14 uses 19 selectors and 88 native bounds. Same four probes capped at 4×60 CPU-s; avoid full sweep unless a meaningful fraction resolves quickly. | `scratch/D/projection_cal{13,14}_native.log` | — |
| enum | C22 full root catalogue: base recovered exactly the ten canonical graphs (474/474, 177.01 CPU-s); local recovered same ten (212.78 CPU-s including one 8-s timeout and 8.89-s retry). Minedge had 6 timeouts, 468/474 complete in its 8-s-cap test; not a complete C22 calibration. | `scratch/D/cal22_{base,local_complete,minedge}/results.tsv` and canonical files | 0.184 |
| enum | C16 saturated M=3 calibration: `minedge` across 13/13 kernels recovered the same five canonical 5-regular (3,6,16) graphs as root-only SMS; pinned C16(1,3,8) also accepted by MiniCard projection. | `scratch/D/calibration16/` | <0.001 |
| enum | Lane C's 78 already checked oriented exclusions cover 56 of the 166 side-exchange orbits. Our independent mapping gives **110 representative kernels left**: 1/1/11/23/35/39 for 8/9/10/11/12/13 edges. This does not independently re-certify C's exclusions. | `scratch/D/survivor_orbits.log`, `scratch/D/survivor_orbits/orbits.tsv` | <0.001 |
| open | Paired R3 survivor probe: base 0/10 and minedge 0/10 within bounds, no models. Base 745.10 CPU-s; minedge 696.09 CPU-s (four wall caps censored at 56.85–67.33 CPU-s). Negative bounded experiment, not an extrapolated runtime or closure. | `scratch/D/r3_{base,min}75/results.tsv` | 0.400 |
| open | Boolean-mask projection on the same four survivors, 0/4 decisions in each of original eager, optimized eager, sparse lazy, and native-cardinality runs. All child outcomes 124/152 (timeouts). Sparse eager CNF while delaying residual rows uses ~1.0–1.75M clauses; native uses ~1.7–3.1k selectors and ~9.5–24.7k native rows. Both finished assembly; neither logged a 10-model checkpoint or a verdict. | `scratch/D/r3_mask{,_v2,_lazy,_native}/k*.log` | 0.263 |
| enum | R(3) kernel 0: SMS UNSAT, Lean checked 249 SB clauses, 812 lazy IS clauses passed shape check, all 9,880 TRI present, CakeLPR verified. Lean rejected a complement-flipped witness in the C22 trace control. Lane C already excludes kernel 0. Link (a) (verified base encoding) missing; no new `cert` claim. | `scratch/D/r3_proof/k0000.checked/{sym-lean,cnf,cake}.log`, `scratch/D/cal22_proof/k0000.checked/bad-lean.log` | 0.0018 solver only |

## Round 1 jobs (historical)

**None active**, as checked at 17:06 CET. Historical launch table below.

All are launched in `scratch/D` via `setsid nohup nice -n 5 timeout`; every solver has 16GB virtual-memory cap and its own CPU/wall timeout. `batch.py` path `../../ralph/lanes/D/batch.py`.

| Timeout / launcher PID | Command (after timeout) | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| 370312 / 370328 | `batch.py 22 6 5 catalogues/C22.g6 local cal22_local --seconds 8 --workers 4` | `scratch/D/cal22_local.log` | 4 | 16:42:42 | ~16:46; hard 1100s |
| 370316 / 370354 | `batch.py 22 6 5 catalogues/C22.g6 minedge cal22_minedge --seconds 8 --workers 4` | `scratch/D/cal22_minedge.log` | 4 | 16:42:42 | ~16:46; hard 1100s |
| 450393 / 450407 | `batch.py 22 6 5 catalogues/C22.g6 base cal22_base --seconds 8 --workers 3` | `scratch/D/cal22_base.log` | 3 | 16:45:18 | ~16:50; hard 900s |
| 554198 / 554221 | `batch.py 22 6 5 catalogues/C22.g6 local cal22_local_retry --indices cal22_local_retry.ids --seconds 100` | `scratch/D/cal22_local_retry.log` | 1 | 16:48:11 | ~16:52; hard 320s |
| 554199 / 554225 | `batch.py 40 9 3 catalogues/R3.g6 base r3_base75 --indices r3_survivor_sample.ids --seconds 75 --workers 2` | `scratch/D/r3_base75.log` | 2 | 16:48:11 | ~16:57–17:02; hard 1250s |
| 554200 / 554216 | `batch.py 40 9 3 catalogues/R3.g6 minedge r3_min75 --indices r3_survivor_sample.ids --seconds 75 --workers 2` | `scratch/D/r3_min75.log` | 2 | 16:48:11 | ~16:57–17:02; hard 1250s |
| 717958 / 718143 | `bash ../../ralph/lanes/D/mask_probe.sh 0 149 88` | `scratch/D/r3_mask/part0.log` | 1 | 16:54:25 | ~16:58; hard 360s |
| 717959 / 718144 | `bash ../../ralph/lanes/D/mask_probe.sh 1 151 227` | `scratch/D/r3_mask/part1.log` | 1 | 16:54:25 | ~16:58; hard 360s |
| 786702 / 786720 | `MASK_OUTDIR=r3_mask_v2 bash ../../ralph/lanes/D/mask_probe.sh 0 149 88` | `scratch/D/r3_mask_v2/part0.log` | 1 | 16:57:08 | ~17:01; hard 360s |
| 786703 / 786715 | `MASK_OUTDIR=r3_mask_v2 bash ../../ralph/lanes/D/mask_probe.sh 1 151 227` | `scratch/D/r3_mask_v2/part1.log` | 1 | 16:57:08 | ~17:01; hard 360s |
| 863822 / 863852 | `MASK_LAZY_ROWS=1 MASK_OUTDIR=r3_mask_lazy bash ../../ralph/lanes/D/mask_probe.sh 0 149 88` | `scratch/D/r3_mask_lazy/part0.log` | 1 | 17:00:02 | ~17:04; hard 360s |
| 863823 / 863853 | `MASK_LAZY_ROWS=1 MASK_OUTDIR=r3_mask_lazy bash ../../ralph/lanes/D/mask_probe.sh 1 151 227` | `scratch/D/r3_mask_lazy/part1.log` | 1 | 17:00:02 | ~17:04; hard 360s |
| 954519 / 954524 | `bash ../../ralph/lanes/D/mask_native_probe.sh 149 88` | `scratch/D/r3_mask_native/part0.log` | 1 | 17:03:03 | ~17:07; hard 360s |
| 954520 / 954528 | `bash ../../ralph/lanes/D/mask_native_probe.sh 151 227` | `scratch/D/r3_mask_native/part1.log` | 1 | 17:03:03 | ~17:07; hard 360s |

Early eager-mask launcher logs have a shell parse error **after** both
child exits were recorded; editing the shell source while live upset the
reader. Each reported child result is also in its own time log. The revised
script passes `bash -n`; avoid live edits to it.

## Claims / next

- `hand`: complete path/cycle classification of admissible rooted R(3)
  kernels and sound side exchange; `enum`: 238 ordered, 166 modulo exchange.
- `hand`: with R(3) minimum edge C4 count 13, every vertex has at least
  five singleton-codegree partners; all R(3) outside masks are distinct.
  Evidence for both hand claims: `ralph/lanes/D/ENCODING.md`.
- Round 2 hand claims: see `SIDE_FACTOR.md` for local support feasibility
  and `SATURATED_BICLIQUE.md` for the incidence bound and its consequences.
  The local catalogue and both control/measurement claims are `enum`;
  neither supplies a refutation of a new R(3) kernel.
- Do not scale the measured joined variants unchanged. A new marginal
  tightening worth testing is a single shared graph of private-singleton
  vertices: triangle-free, each present pair support forces a singleton
  edge (if both singles exist), and any present triple support on three
  private coordinates forces at least one edge among those singles.
  This couples decisions that the independent t-coordinate local
  witnesses otherwise make separately. Calibrate first and require a
  measurable improvement in the matched marginal sample.
- Keep R(4) as a later priority; its saturation equality is a hand
  reduction only. Consider overlap residues around a codegree-3 pair if
  independent singleton coupling proves too weak.
- Use `survivor_orbits.py` to rebuild the 110-orbit list from C's two
  baseline shards. If a future R(3) kernel solves, `check_trace.py`
  reproduces the R3 proof plumbing, but finish the VeriPB/CakePB encoding
  link (a) before reporting `cert`.
# Round 6 handoff archive (2026-11-21)

- Open R(3), R(4); 110 minimum-root kernels unchanged. Alternate max12 forest cover: S=2 keys 24,25,26,28,29,32, S=3 keys 21,23,27. Exact `sum S=240+2*w`. For `max q22=0`, at least 60 edges have key32, so key32 alone covers that subset. Evidence `TIGHT_FOREST.md`, `scratch/D/seed_r6/forest_score.log`; round-6 critic confirmed.
- Root-to-anchor q22 cap matches 360 C20 local decisions; seed-window and floor rows replayed 13 C16. Exact forest, signed-count and compact SAT replays repeated 144 smaller solves, matching all labelled graph and pin sets. `TIGHT_FOREST.md`, `scratch/D/seed_r6/{cal,q22-cal,sat16/check,compact16/check,no22-cal}.log`.
- Open: key34 ordinary/forest/signed probes 48 CPU-s; key32 plain compact reaches 30,001 conflicts, global q22=0 caps at 55 CPU-s. Windows feasible at key34 and inconclusive at key21; q22 and endpoint pins no demonstrated gain. Evidence `scratch/D/seed_r6/{sat40,compact40,q22,key32pins}/`.
- No jobs at handoff. Prior PIDs 30557, 136533, 479273 absent. Round 6 ~0.21 CPU-h; evidence frozen `scratch/D/round6_evidence.sha256`.
