# Lane G state — round 11, November 22, 2026

**278 near-regular distributions plus R remain open.** No order-40
candidate. The exact baseline (`round6_baseline.csv`), ten U88 keys
(`round6_u88.csv`), twenty e168 d6 keys (`round6_e168_d6.csv`), six
missing e120/e121 classes, and eleven single-root zero-addition cases
are unchanged. No new class-LP or Farkas elimination this round.
The d8 j2 middle minimum-degree-two bundle is now terminal and bound;
this does not close the parent distribution `(2,7,4,27)`. This round's
direct order-21 addback pilot is summarized below.

## Jobs

No active or detached jobs after round 11. Foreground proof pilots
and dual replays have terminated; no production sweep launched.

Round 10 (CET), cwd `scratch/G/round10`: all jobs retired. PID 3097303
was absent at round-11 collection; terminal master status at 04:00:44
was 21,236 CERT, no other status. All twelve shards and trace digests
bound in round 11 and passed to A for separate replay. No matching arm.

| PID | Command | Log | Slots | Start | End / hard limit |
|---|---|---|---:|---|---|
| 3020265 | `bash ../../../ralph/lanes/G/run_mixed_residual.sh r26.d9.production 4 225s 100000 18` | `r26.d9.production.master.log` | 4 | 03:22:11 | retired 03:22:49, 187/187 |
| 3020266 | `bash ../../../ralph/lanes/G/run_mixed_residual.sh r25.d9.pilot 3 225s 100000 18` | `r25.d9.pilot.master.log` | 3 | 03:22:11 | retired 03:22:39, 48/48 |
| 3020267 | `bash ../../../ralph/lanes/G/run_mixed_residual.sh r25.d8.pilot 3 225s 100000 18` | `r25.d8.pilot.master.log` | 3 | 03:22:11 | retired 03:22:35, 48/48 |
| 3044396 | `bash ../../../ralph/lanes/G/run_mixed_residual.sh r25.d9.production 8 1470s 100000 18` | `r25.d9.production.master.log` | 8 | 03:23:12 | retired 03:37:41, 6,083/6,083 |
| 3097303 | `bash ../../../ralph/lanes/G/run_mixed_residual.sh r25.d8.middle 12 3150s 100000 18` | `r25.d8.middle.master.log` | 12 | 03:25:03 | retired 04:00:44, 21,236/21,236 |

Round 9 jobs, both retired, in `scratch/G/round9` (CET):

| PID | Command | Log | Slots | Start | End / hard limit |
|---|---|---|---:|---|---|
| 231913 | `bash ../../../ralph/lanes/G/run_mixed26.sh mixed26.pilot 3 250s 100000 18` | `mixed26.pilot.master.log` | 3 | 01:50:11 | retired 01:50:27, 96/96 dual LRAT, 40.57 CPU-s |
| 304605 | `bash ../../../ralph/lanes/G/run_mixed26.sh mixed26.production 8 1800s 100000 18` | `mixed26.production.master.log` | 8 | 01:51:27 | retired 01:59:18, 7,070/7,070 dual LRAT, 2,970.90 CPU-s |

Round 8 jobs confirmed retired by `ps` in round 9:

| PID | Command and cwd | Log | Cores | Start | End |
|---|---|---|---:|---|---|
| 360479 | `bash ../../../ralph/lanes/G/run_low25.sh` in `scratch/G/round7` | `scratch/G/round7/proof-low25.master.log` | 16 | Nov 22 00:04:11 CET | 00:44:12 CET, partial at worker wall cap |
| 2015131 | `bash ../../../ralph/lanes/G/run_low25_resume.sh` in `scratch/G/round8` | `scratch/G/round8/proof-c1retry.master.log` | 16 | 00:45:53 CET | 00:57:50 CET, 3,826 certs, all remaining keys |
| 2694969 | `bash ../../../ralph/lanes/G/run_pure_pivot.sh` in `scratch/G/round8` | `scratch/G/round8/proof-pure.master.log` | 6 | 01:02:24 CET | 01:05:49 CET, 1,484 certs, all remaining keys |
| 710384 | `bash ../../../ralph/lanes/G/run_mixed_strip.sh` in `scratch/G/round7` | `scratch/G/round7/proof-mixed.master.log` | 2 | 00:12:22 CET | 01:06:51 CET, 5,155 certs, all remaining keys |

## Results and claims

Round 11:

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| hand + enum + cert, A audit pending | Mixed `(2,7,4,27)`, path/middle only, noncross d8 j2 and `δ(T)=2`: 21,236/21,236 dual LRAT receipts bound in all 12 shards, zero missing; independent A role identities agree. The 69,278 matching roles are separate. | `scratch/G/round10/r25.d8.middle.bound/certificates.tsv`, `scratch/G/round11/middle.bind.log` | 3.113 proofs, 0.002 binding |
| hand + enum + inherited cert, pending review | At mixed `(2,7,4,27)`, d8 B-side noncross equality anchor gives a d8 B pivot exchange `j'=5−j+τ`. The order-21 singleton deficit census and A-013 exclude B-small at order24 j1 (30,800 of 49,597 roles). Any remaining d8 B equality transfers to j3 and `δ(T)=4` by G-033. No exclusion of that slice or A-small. | `rows/pinned_anchor_swap.md`, `scratch/A/strip11/short.cnf.log`, `scratch/G/round11/role.d8.log` | 0.001 count; inherited proofs |
| enum + measured pilot cert/open | Direct order24 pin on four dispersed cores: 100,569 literal weak lifts vs 28 direct roles; small controls match 2,235 lifts. Eager sorted slots gives 4/27 unchecked UNSAT at 16k vs 0/27 baseline. At 50k, seven d8 replayed dual proofs (three A-small), 20 CAP; d9 0/12, all CAP. No production. | `ROUND11_REPLAY.md`, `scratch/G/round11/{controls.final,literal4,direct.d8.slots,proof.d8.0,replay.d8.0}.log` | 0.089 solve/verify pilots |

Round 10, see `ROUND10_REPLAY.md` and `rows/residual_mixed_windows.md`.
Proof variants use `--mixed --residual --eager 10000` only; the
budget, structural and joint pilots are not producer sources.

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| hand + enum + cert | Mixed `(2,7,4,27)` only, noncross d9 j4, δ(T)=3. 50 matching +165 middle, 215/215 dual LRAT and source-bound, independently replayed A. | `scratch/G/round10/r26.d9.bound/certificates.tsv`, `ralph/lanes/A/ROUND10_REPLAY.md` | 0.023 |
| hand + enum + cert, accepted | Same mixed scope, noncross d9 j3, δ(T)=2. 2,134 matching +3,997 middle, 6,131/6,131 dual LRAT and bound; A source/role match and critic sampled fresh replay. No higher minimum. | `scratch/G/round10/r25.d9.bound/certificates.tsv`, `scratch/critic/r10/G/r25.d9.replay` | 0.980 |
| hand; enum cross-check | Any noncross retained anchor in a weak paired `(3,8)` window has degree ≥`|T|−22`; saturated 3+4 cut would force degree seven in an α≤6 core. Mixed d9 j1 excludes isolate; d8 j1 and d9 j2 exclude leaf. Computation unneeded; 191 isolates and 513,438 rooted leaf glues independently give no weak marks. | `rows/residual_mixed_windows.md`, `scratch/G/round10/{leaf_window_core,r23.plain,r24.plain,r24.rooted}.log` | <0.03 |
| enum + estimate, open | Equality root leaves order21, 6,160 marked cores on 6,056/1,118,436 parents; exact unpruned agreement, 42/42 smaller controls. Raw order24 graft capped 100 wall s after 1,194,099 weak marks from 256-parent pilot. Direction is partial-window pinned completion, not raw gluing or full higher-minimum scope. | `scratch/G/round10/short-anchor.{full,unpruned,graft24.sample}.log` | 0.002 core scan; graft capped |
| hand + measured enum | Joint support test retains 215/215 and 639/640 sampled lower-minimum roles; planted support witness and independent 210-placement incompatible oracle pass. Joint/budget variants do not reduce proof time on the 48-role sample; no further matching or high-minimum launch. | `scratch/G/round10/{r26.d9.joint,r25.project,joint.control}.log`, `ROUND10_REPLAY.md` | 0.04 |

Previous rounds:

Use `ROUND9_REPLAY.md` and `ROUND8_REPLAY.md` for exact scope. Indexes retain
each key, regenerated-CNF digest from the proof receipt, stored proof
digest and size. Producer dual checks are CakeLRAT and lrat-check;
the index is not itself a proof replay. No pending solver caps in
the final sets. Claims await the flow's ledger/critic review.

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| hand + enum + cert, pending critic | Mixed path/leaf plus matching/incident or path/middle at `(2,7,4,27)`, **noncross d8 pivot** with codegree 3 to A's centre, **order 26 and δ(T)=3 only**. 191 → 2,712,471 glues → 2,111 marks → 1,767 mark orbits → 5,438 matching +1,728 middle roles. All 7,166 bound and dual checked; A independently regenerated the source and replayed 16 pilot hashes/proofs. 0.420 vs 0.279 CPU-s per production key for prior d8/codegree-four. | `rows/mixed_pivot_windows.md`, `scratch/G/round9/mixed26.bound/{cert.keys,certificates.tsv}`, `scratch/A/strip9/mixed.j3.source.log` | 0.837 proofs |
| hand + enum + cert, pending independent cover audit | Same mixed profile, **noncross d9 pivot** with codegree 5 to A's centre, any δ(T) at order 27. Both holes retained; 1,988 weak marks →162 matching and zero middle roles, 162/162 structural addbacks and 162/162 dual LRAT proofs bound. | `rows/mixed_pivot_windows.md`, `scratch/G/round9/mixedfull.bound/{cert.keys,certificates.tsv}`, `scratch/G/round9/mixedfull.addback.log` | 0.012 proofs |
| hand + enum sample | Pure both-direction caps joint in one attachment CNF, 52 dispersed marks: old structural rows 14 unchecked UNSAT +38 CAP; among the latter joint variant one additional unchecked UNSAT +37 CAP at 2,500 conflicts. No demonstrated proof reduction; Lane A proves redundancy for δ≥4. Separate exact projected degree-choice relaxation rejects 0/52 and neither exterior profile in any mark. Controls C13/C35/Exoo39 and A's positive/overflow lifts pass. | `rows/joint_projected_caps.md`, `scratch/G/round9/{joint.dispersed.log,projected.dispersed.log}`, `scratch/A/strip9/joint.audit.log` | 0.005 |
| hand + enum + cert | Both path/leaf at `(2,8,2,28)` and `(2,7,4,27)`, centre codegree `j=1` and paired window `δ(T)=2`: all 17,194 representative LRATs checked and terminally bound. 191 order-22 cores → 18,333,381 raw → 20,181 marks → 17,194 exact marked orbits; A independently regenerated this source and binds/replays separately. | `scratch/G/round8/c1.final/{cert.keys,certificates.tsv}`, `scratch/G/round8/c1.final.log`, `scratch/A/strip8/lower.terminal.tsv` | 4.33 proofs, 0.095 cover |
| hand + enum + cert | Mixed path/leaf with matching/incident or path/middle at `(2,7,4,27)` only; there exists an opposite uncrossed d8 pivot with codegree 4. All 3,688 matching +1,491 middle roles certified. No lower mixed pivot codegree scope. | `scratch/G/round8/mixed.bound/certificates.tsv`, `scratch/G/round8/mixed.bound.log`, `rows/path_leaf_windows.md` | 0.401 proof |
| hand + enum + cert, pending independent cover/semantics review | Both path/leaf at the same two pins; codegree 4 with opposite noncross d8 leaf (1,491 keys), or 5 with opposite noncross d9 full anchor (6 keys). All 1,497 dual LRATs passed. Does not require or exclude any particular codegree between the two **centres**. | `rows/alternate_pure_pivots.md`, `scratch/G/round8/pure.bound/certificates.tsv`, `scratch/G/round8/pure.bound.log` | 0.132 proof, 0.002 cover |
| hand | Paired pure windows have `δ(T)≤6`, `e(T)≤83,88,92` for `j=1,2,3`; cap tighter by half the degree gap when the root is exterior. Cross compatibility for each exclusive deleted vertex is necessary by MTF. Generic rows hold on 21 exact small marked windows and all exclusive vertices of C13/C35/Exoo39. No full profile closure. | `rows/paired_window_budget.md`, `scratch/G/round8/window-budget.control.log` | <0.001 |
| enum / estimate | Exact next source is the full order-21 `(3,7)` catalogue for `(j,δ)=(1,3),(2,4)` only. Fast exact mark scan matches 205 and 260 pilot keys byte-for-byte (and 21/44 smaller controls); combined gluing/scan 6.02→1.77 and 16.63→10.22 CPU-s. Projects to ~110 and ~12.4 CPU-h census, before proofs; `j=2,δ=4` gives 33/33 pilot LRATs in 19.49 CPU-s (~187 CPU-h extrapolated proofs). No broad launch. | `strip_window_fast.cc`, `ROUND8_REPLAY.md`, `scratch/G/round8/{source21*,scanner.*,proof-q4-pilot.log}` | ~0.015 pilots |
| enum / measured dead end | Centre-only integer overlay prefixes, 60 complete first-prefix subtrees each at `j=1,2`. After initial Hall: 335,539 / 79,242 centre tables. Hall edge forcing rejects zero; MTF cross rejects 4,000 / 3,388; edge-budget check rejects zero more; 330,893 / 72,112 retain high-min marked degrees. This is not a full overlay. 54 exact smaller edge-subset oracles plus C35/Exoo literal controls pass. | `center_prefix.cc`, `ROUND8_REPLAY.md`, `scratch/G/round8/{center.control.log,center.*.mtf.log}` | <0.002 |

## Handoff

- Mixed pending: d8 j1 δ≥2 **except B-side equality**, j2 δ≥2
  (middle δ2 terminal, matching δ2 unlaunched), j3 δ≥4; d9 j1 δ≥1,
  j2 δ≥2, j3 δ≥3, j4 δ≥4; and crossed pivots. Lane A's separate d9
  B-side equality exclusion also uses the singleton-deficit census.
  Reduce any surviving d8 B-side equality to j3/δ4 via pivot swap.
  Do not scale direct order24: best measured A-small d8 proofs 3/7,
  d9 0/12 at 50k. Try a new cut or price the alternative A pivot
  identity, not raw grafting, a higher cap alone, or matching sweeps.
- No high-minimum pure batch: the joint caps are automatic at δ≥4,
  and the independent-set capacity projection has no sample attrition.
  Seek a different selector rather than increasing the conflict cap
  or rerunning either test unchanged.
- c1 terminal provenance fixed in both replay files: G selects 32
  non-eager original pilots and 17,162 eager production/retry keys;
  A chooses all eager. Compare selected hashes, not only key sets.
- Round-7 `j=3` and `j=2,δ(T)=3` scopes unchanged and confirmed;
  see `ROUND7_REPLAY.md`. In the pure both-path/leaf branch the two
  centres now have exclusively `j=1,δ(T)≥3` or `j=2,δ(T)≥4` if
  these proofs are accepted. A d8-leaf or d9-full pivot on the
  opposite side then has codegree at most 3 or 4, respectively.
- Do not repeat the complete order-25 low-min or mixed-j4 batches.
  The first order-25 production timeout left 3,816 keys unwritten,
  plus 10 original pilot CAPs. The retry checks all 3,826; G does not
  count the 10 alternate pilot proofs in `proof-low25-eager` twice.
  The old serial hash index timed out; the canonical terminal index
  **is `c1.final`**, not `c1.bound`. Its streaming 4-reader binding
  took 31.89 wall seconds and passes duplicate/crossed/size/source
  and missing-receipt controls (`binder.controls.log`).
- For higher min require at least an order-of-magnitude gain before
  spending the projected ~187 CPU-h; never pad smaller windows to 27.
- No residue floor upgrade, no change to the e169-pinned scope;
  earlier 14 templates / 112 pins and exact three-anchor budgets
  remain in `LOG.md` and the round-6/7 replay files.
