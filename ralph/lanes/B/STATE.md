# Lane B — round 16, November 22, 2026

**Round 16:** exactly **1,875 critical** 32/e108 keys bind to prior
MTF d7-root receipts (1,431 cliques, 444 dual LRATs, zero unbound). The
accepted reducibles join by disjoint key to **2,104,146** named keys
(2,017,637 cliques, 86,509 dual LRATs); five criticals remain absent.
All named criticals are addable (35–48 candidate nonedges each), but no
independent e109 source found after scoped inventory. Descent passed
13/13 smaller withheld addables and the saturated C5 control. No new
proof search, e109 generation, floor 109, e88/U88, or profile change.
`ROUND16_REPLAY.md`, `ROUND16.sha256`, `work/e108_r16/critical-crosswalk.tsv`.

**Current baseline:** global degree-seven floor **108** for MTF is CONFIRMED
(B-013); it subsumes the direct e162 `(0,2,32,6)` exclusion. Neither
uses t8/t9 floors. No candidate graph. Re-read the allocation.
Work from `scratch/B` with `ulimit -v 16777216` and `PYTHONDONTWRITEBYTECODE=1`.

**Round 15 (CONFIRMED):** all **2,102,271 supplied deletion-reducible**
32/e108 keys blocked at MTF d7 roots, 2,016,206 cliques and 86,065 dual
LRATs, including 36,800 adopted ranks. ~1.99 core-h, 240 MiB; archived
jobs in `LOG.md`. See `ROUND15_REPLAY.md` and `ROUND15.sha256`.

**Round 13:** all **545** authorized set-aside e98 parents tested at d7/d8;
477 distinct critical e108 outputs, **zero novel** (22.23 CPU-s incl. audit).
The other **200** were separately rebound to N's archived two-arm replay.
All **77** proposed 33/e122 child hosts were fresh against 419 actual prior
direct hosts; descent yielded five old e108 keys, **zero novel** (0.89 CPU-s
incl. controls); stopped. Census still **2,104,146 / 2,104,151**. No floor 109,
no change to e88/U88 or to the 238 near-regular distributions plus Case R.
See `ROUND13_REPLAY.md` and `ROUND13.sha256`.

**Round 12:** all **7,954** fresh e98 deck parents tested at d7/d8;
1,724 distinct critical e108 outputs, **zero novel** by canonical merge
and Traces. Five still missing; best census remains `work/e108_r11/union.g6`.
No adaptive generation. The earlier 471 remain in their prior scope;
the then-separate 745 were subsequently handled in round 13.
See `ROUND12_REPLAY.md` and `ROUND12.sha256`.

**Round 11:** lifted the 122 e98 parents (34 novel e108), then 255 more
exact e98 deck parents (13 more). Stopped at two disjoint zero-yield
batches. All 47 independently checked and blocked at MTF d7 roots (37
cliques, 10 dual LRATs; critic review pending). Best census
`work/e108_r11/union.g6`: **2,104,146 / 2,104,151, five missing**. The
older-cohort complement gives 7,954 fresh exact e98 parents, not lifted.
e95 d4/d5 terminal zero on all 560, completing the e95 source scope with
N-001. e88/U88 and floor 108 unchanged. See `ROUND11_REPLAY.md`.

**Round 10:** imported N's 61 critical e108 keys and certified their
nonextensions (57 cliques, 4 dual LRATs). Stratified two-step lift from
128 prefix-critical e88 seeds produced 5 new critical e108 keys, all from
e98 parents; seven fresh e98 parents from those five produced 6 more.
All 11 separately certified. Best census `work/e108_r10_micro/union.g6`:
**2,104,099 / 2,104,151, 52 critical classes missing**. Round 10 exhausted
the 256-per-level pilot cap; `work/e108_r10_e98_queue/fresh.g6` holds 122
fresh e98 parents for a subsequent round only. Separate e88 price pilot
not scalable yet (no coverage proof or 10x full-cost estimate). See
`ROUND10_REPLAY.md` and `ROUND10.sha256`.

Rounds 7–9 retired the null e108 discovery pilots. The e88 prefix replay
covered 5,873,187 exact keys (including 153,612 critical) with zero completions;
the full e88 complement remains open. See the respective `ROUND*_REPLAY.md`
and freezes for old proof bundles, scopes and pilot details.

**Round 6:** d7/e43 outside prefix returned zero and finished binding.
Both scans of the full deletion-reducible e88 partition finished with
zero completions (5,719,576 keys). The edge-critical complement
and all **10** refreshed U88 keys remain open (278 profiles plus Case R
on the round-5 accepted baseline). e108 is 1,266 classes short.
Replay guide: `ralph/lanes/B/ROUND6_REPLAY.md`.

## Jobs

No live PIDs (0 cores). Round 16 used foreground only, at most one core;
round-15 PIDs were absent. Older job transitions are in `LOG.md`.

## Results and claims for review

### Round 16

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| cert inventory, pending critic | Key-indexed 1,875 critical d7 MTF receipts, 1,431 cliques + 444 dual LRATs; no new proofs or unbound key. Exact disjoint union with accepted reducibles: 2,104,146 named keys; five criticals still missing. | `ROUND16_REPLAY.md`, `ROUND16.sha256`, `scratch/B/work/e108_r16/critical-crosswalk.tsv` | 0.0023 |
| hand + enum (control) / open (source) | Legal one-edge descent recovers the addable subfamily only; smaller complete controls 13/13 addable, 0/1 saturated. All supplied criticals have 35–48 legal single-edge additions. No independent order-32/e109 source found in scope, so stopped without target descent. | `ROUND16_REPLAY.md`, `scratch/B/logs/e108_r16_{descent,local_source,public_source}.log` | 0.0007 |

### Round 15

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| cert (named reducible list, confirmed) | All 2,102,271 supplied reducible 32/e108 keys blocked at MTF d7 roots; 2,016,206 demand cliques plus 86,065 dual LRATs. New: 1,980,937 + 84,534; exact merge with 36,800 adopted positions, zero gaps. | `ROUND15_REPLAY.md`, `ROUND15.sha256`, `scratch/B/work/e108_r15/summary.json`, `scratch/B/logs/e108_r15_rank_audit.log`, `ralph/critic/round_015.md` | ~1.99 incl. setup/replay/merge |

### Round 14

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| cert (named tranche, pending critic) | 32,768 of 2,102,271 supplied reducible 32/e108 residues blocked at d7 MTF roots, with 31,407 cliques and 1,361 rebuilt dual LRATs; exact prior-pilot overlap 64. No floor/profile effect. | `ROUND14_REPLAY.md`, `ROUND14.sha256`, `scratch/B/logs/e108_r14.log` | 0.045 incl. controls |
| estimate | At measured rate 2.85 core-h / 87,300 LRATs / 215 MB proof payload for full named reducible list; proof counts 49–186 per 2,048-key group. No full run. | `ROUND14_REPLAY.md`, `scratch/B/logs/e108_r14_metrics.log` | included |

### Round 13

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| enum | Named 545 e98 parents tested d7/d8: 1,394 raw leaves, 477 critical 32/e108 keys, zero novel; 200 separately archive-bound. Not a general e98 cover. | `ROUND13_REPLAY.md`, `ROUND13.sha256`, `scratch/B/work/e108_r13_complement_run/done.tsv` | 0.0064 incl. controls |
| enum | Critic's 77 children rebuilt (116 legal additions), all 77 fresh against named direct descents; 2,541 cards, 85 leaves, five old keys. No scale-up. | `ROUND13_REPLAY.md`, `scratch/B/work/e108_r13_hosts/{inventory.tsv,target.log,target.keys}` | 0.00025 incl. controls |

### Round 12

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| enum | Exact 7,954 order-31/e98 parents, d7/d8: 15,204 raw leaves, 1,724 distinct critical e108 outputs, zero novel. Five missing; no floor or profile subtraction. | `ROUND12_REPLAY.md`, `ROUND12.sha256`, `scratch/B/logs/e108_r12_terminal.log`, `scratch/B/work/e108_r12/{plan,done}.tsv` | 0.093 incl. controls and audit |
| enum / estimate | Among 745 set-aside parents, 200 match the archived N d7/d8 replay source; 545 to fresh-bind. Project ~21 CPU-s for 545, ~29 CPU-s for all 745, before audit. No new set-aside lifts. | `scratch/B/logs/e108_r12_provenance.log`, `scratch/B/work/e108_r12_provenance/not_deck_bound.g6` | <0.001 |

### Round 11

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| enum + scoped cert | 377 d7/d8 e98 parent lifts supply 47 novel validated critical e108 keys; 37 demand cliques and 10 regenerated dual LRATs cover these keys only. 2,104,146 supplied, five absent. Fresh generation replay byte-identical. | `ROUND11_REPLAY.md`, `ROUND11.sha256`, `scratch/B/work/e108_r11/` | 0.021 incl. both replays |
| enum / estimate | Four-origin exact e98 deck inventory: 9,170 known-target parents with 7,954 fresh outside old records. Estimated ~310 CPU-s lift-only (no yield forecast); not lifted. e96: 33,312 reducible and only 24 of 1,842 critical supplied. | `scratch/B/work/e108_r11_complement/`, `scratch/B/logs/e108_r11_complement_replay.log` | 0.020 incl. inventory replay |
| enum | All 560 critical 31/e95 parents lifted at d4/d5: zero critical 32/e108 outputs. Together with N-001's d6–8 results, none of the missing targets has a legal e95-thinned puncture. | `ROUND11_REPLAY.md`, `scratch/B/logs/e108_r11_e95_low.log` | 0.024 |

### Round 10

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| enum + cert | N's 61 critical e108 keys independently validated, distinct from baseline; 57 verified demand cliques and 4 dual LRATs cover this tranche only, 63 missing at this handoff. | `ROUND10_REPLAY.md`, `scratch/B/work/e108_r10_import/`, `scratch/B/logs/e108_r10_replay_scout.log` | 0.002 incl. replay |
| enum + cert | Two-step critical-card lift at e98 yields 5 new critical e108 keys, and a seven-parent e98 repuncture yields 6 more; 7 checked cliques and 4 dual LRATs across those two separate tranches. Final census 2,104,099 (52 missing), not floor 109. | `ROUND10_REPLAY.md`, `scratch/B/work/{e108_r10_new,e108_r10_micro}/`, `scratch/B/logs/e108_r10_target_replay.log` | 0.081 incl. full generation replay |
| enum | Exact e98 deck of the eleven new keys: 135 classes, 122 fresh vs recorded pools/parents. No new wave in round 10. | `scratch/B/work/e108_r10_e98_queue/fresh.g6`, `scratch/B/logs/e108_r10_e98_queue.log` | 0.0006 |
| estimate / open | e88 parent pricing: one withheld marked positive recovered on smaller control. At e78, 397/34,122 critical parents supplied; 640 sampled parents across e78–82 give no critical marked lift. Costs do not justify full scaling. | `ROUND10_REPLAY.md`, `scratch/B/logs/e88_deck_r10_{control,probe}.log` | 0.008 |

### Round 9

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| enum / estimate | Pair-union repartition: exact labelled control (12 cases, 72 emissions), 33/42 withheld critical e22 reconstructions. Target 96 parents, 40 distinct old e108 keys, zero scout or novel keys; stopped. | `ROUND9_REPLAY.md`, `scratch/B/logs/e108_r9_pair_{control_replay,probe}.log` | 0.0032 |
| enum / estimate | Nonadjacent stem e92/e93 unrestricted row-pair lift: 324 matched oracle cases, 38/42 withheld e22. Held-out 1,024 stems give zero novel keys in 3.59 CPU-s. No broader census claim; stopped. | `ROUND9_REPLAY.md`, `scratch/B/logs/e108_r9_nonadjacent_{control,heldout}.log` | 0.0025 incl. cost probe |
| enum, diagnostic | Supplied 1,756 critical e108 graphs: 23 with a d8/e51 card, 1,246 with a d8/e52 card, none with d8/e49 or d8/e50. No necessary bound for the missing keys. | `scratch/B/logs/e108_r9_d8_{profile,bind}.log` | <0.001 |

### Round 8

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| enum, partial census | Frozen scout tranche is exactly 1,142 distinct valid critical e108 keys disjoint from the old set, independently valid and critical. Combined critical count 1,756; catalogue 2,104,027 with 124 absent. | `ROUND8_REPLAY.md`, `ROUND8_E108.sha256`, `scratch/B/logs/e108_r8_import.log` | 0.0061 |
| cert, supplied tranche only; pending critic | All 1,142 imported e108 keys excluded as degree-seven MTF duals: 761 checked demand cliques + 381 regenerated and dual-verified LRATs (291 one-line RUP, 90 CaDiCaL). Old 614 proofs unaffected. No global floor 109 or new distribution exclusion. | `ROUND8_REPLAY.md`, `ROUND8_E108.sha256`, `scratch/B/work/e108_r8_scout_proofs/` | 0.0148 |
| enum / estimate | Bounded e120/121/122/123 order-33 host pilot, 512 fresh spaced hosts, 16,896 cards, 0 novel keys (0/CPU-h); control exactly matches known order-7/e6. Stopped, no exchange or scale-up. | `ROUND8_REPLAY.md`, `scratch/B/logs/e108_r8_hosts.log` | 0.0007 |
| enum; pending critic | Prefix e88: 5,873,187 digest-bound MTF inputs, 0 completions, including 153,612 directly audited critical keys; SAT 24/24 negative on that critical partition. Full e86/e87 exactly matches checkpoint. Legacy generation counts/output union audited in full, input replay sampled. Prefix and reducible union have 5,873,188 keys but do not cover all e88. | `ROUND8_REPLAY.md`, `ROUND8_PREFIX.sha256`, `scratch/B/logs/prefix_r8_terminal.log` | 108.68 generation gluer; 1.82 scan gluer; ~0.16 audits |

### Round 7

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| enum / estimate | Adjacent-pair critical reconstruction checks 374 labelled smaller cases, reconstructs all 42 e22 critical control keys from all e22 stems, and 18/42 from e21 stems. On 2,700 critical-e108 stems it finds 32 known keys; 2,549 e107 stems give none. Zero novel key; do not scale. | `ROUND7_REPLAY.md`, `scratch/B/logs/e108_r7_{adjacent_control,adjacent_sample,final_retest}.log` | ~0.001 including calibration |
| enum / estimate | Degree-six/e65 pilot from exact 396-key source: 25 seeds, 45,192 labelled outputs, 21/21 planted critical keys, zero new. Root-edge screen matches exact smaller controls but retains all 268,617 candidates on the target shard; paired core times 16.71 vs 16.40 s. | `ROUND7_REPLAY.md`, `scratch/B/logs/e108_r7_d6_{control,pilot,binding}.log` | ~0.01 pilot |
| open | Prefix still running at 16 slots. New replay script checks exact byte equality at ≤87 and isolates prefix-critical e88 after terminal chunk binding. Calibrated 201→159+42 split; no target replay yet. | `src/replay_prefix_r7.sh`, `scratch/B/logs/prefix_r7_replay_control.log` | <0.001 |

### Round 6

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| enum | Outside-prefix d7/e43: exact GR T13 1,521 small seeds, 48 audited chunks, zero raw order-30 e88 outputs and no outer roots to glue. Fresh pickg/input equality, independent direct validity and Traces. Not the e44 branch and not full U88. | `ROUND6_REPLAY.md`, `scratch/B/logs/e43_r6_full_binding.log` | 2.63 generation |
| enum | No degree-nine MTF root with a deletion-reducible e88 residue. Complete 133,434 + 13,901 exact e87 parents; independently replayed 1,052,247 raw tail children and exact 11,524 overlaps + 967,613 novel keys. Ordered scans of 4,751,963 + 967,613 keys returned zero; all 4,641 + 945 chunks bound. Dispersed tail SAT sample 64/64 nonextending. Does not cover e88 critical. | `ROUND6_REPLAY.md`, `scratch/B/logs/{up87tail_checkpoint,up87_r6_terminal_audit,up87_r6_sat64}.log` | ~0.32 new; 1.71 total solver hours incl. up86 |
| enum / open | e108 partial: separate validity/Traces both give 2,102,885; 2,102,271 reducible + 614 critical. New critical deltas 479, 68, 40, 20, 0; now 1,266 short of GR. | `scratch/B/logs/{e108_r6_pass1,e108_r6_follow,e108_r6_partial_audit}.log` | ~0.26 new swap and replay |
| cert (supplied keys; pending critic) | 614 known critical e108 residues excluded at d7 MTF roots: 569 checked demand cliques, 45 pinned LRATs (43 single-line RUP, 2 CaDiCaL), regenerated CNF digests and both proof checkers. No t8/t9 or global distribution premise; no floor 109. | `ROUND6_REPLAY.md`, `scratch/B/logs/e108_r6_critical_proof.log` | <0.01 |
| estimate | 4,096 dispersed reducible inputs: 3,923 checked cliques + 173 dual LRATs. Compact proof/replay 14.81 CPU-s for 173, 149 unit-refutable; discards redundant CNFs/logs. ~2.3 CPU-h for whole e108 proof campaign *if exact cover acquired*, 4 slots ~35 min at full speed; allow ~1 GB allocated. Maximal-row cliques reject 0/173 more after 220 actual roots and 30 exhaustive row-domain controls. | `scratch/B/logs/e108_r6_{pilot,unit,maxrow}.log` | ~0.011 calibration/pilot |
| estimate / open | No new e108 critical keys in calibrated local pilots: exact star rewires (8,192 e107 + 614 critical e108 parents, 38.5s), critical-only 2→3 from 512 e107 (39.1s; 170 distinct already known), 2→2 from 4,096 reducible e108 (110.7s; 202 already known), random excursions +3/+5/+8 edges on 614 critical anchors (64 trials each; all outputs known), or direct d7/e58 gluing (48 inputs, no critical outputs, 51.6s). Critical-only edits passed 24 brute controls and an exact paired 8-parent multiset. Full direct e58 branch alone estimates 38.6 CPU-h, no coverage guarantee. | `scratch/B/logs/e108_r6_{rewire_pilot,edit107_opt,edit108_opt,edit_pairbind,excursions,direct}.log` | ~0.071 |
| estimate | Explicit size plans did not speed the d7/e58 critical gluer: baseline 97.83 CPU-s on 24 seeds, recovering all 12 planted keys and 286 total known canonical classes; first planned order TIMEOUT 180 wall seconds. Positive controls are not a proof of census coverage. | `scratch/B/logs/e108_r6_sizeplans.log` | ~0.076 |

### Round 5

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| cert (MTF; CONFIRMED) | d7 residue floor **108**, no t8/t9 or profile premise. Complete 234,681 GR classes at e107; 231,455 checked eight-demand cliques plus 3,226 necessary CNFs pinned by seven-demand row normalization. All 3,226 LRATs pass both checkers and byte-identical CNF/hash replay. Combine with G-011. | `FLOOR7_108.md`, `FLOOR7_108.sha256`, `src/replay_floor7_108.sh`, `scratch/B/logs/e107_floor108_replay.log` | ~0.14 new proof and replay, excluding census/gluer |
| enum / open | Exact e108 reducible slice 2,102,271 of 2,104,151 GR classes (9,185,929 raw children of all e107s). Audited edge/order/alpha and sorted canonical distinctness. Of 1,880 deletion-critical types, an 8,192-parent swap pilot recovered 7, independently validated as critical; 1,873 missing. No e108 closure. | `scratch/B/logs/{e108_r5_reducible,e108_r5_followup,e108_r5_critical_audit}.log` | ~0.04 |
| estimate | e108 pilot: 0/1,024 MTF glues, 979 checked demand cliques, 45/45 pinned dual LRATs. Project ~0.82 CPU-h whole e108 gluer or ~1.7 CPU-h pinned production plus clique checks/replay, biased toward reducible inputs; a full first critical-swap pass projects ~13 min on one busy slot before final audit, with no reachability guarantee. | `scratch/B/logs/{e108_r5_pilot,e108_r5_followup}.log` | <0.01 pilot |
| enum | Complete untuned independent gluing at e107: 234,681 inputs, zero completions in 355.18 CPU-s. Independent SAT gluer agreed on 64/64 dispersed inputs after positive D5/K6 control. No broader e level inference. | `scratch/B/logs/{e107_fullglue,e107_sat_control,e107_sat64}.log` | ~0.103 |
| cert (conditional; pending critic) | e162 `(0,2,32,6)` impossible in MTF, using accepted G-011 (floor 107) and GR T14; neither gluing floor is a premise. Complete, valid, pairwise nonisomorphic census of 234,681 e107 roots, one checked distance-3 pair per root incompatible with both attachment sizes 6 and 7. Independent SAT verifies 64/64 pairs. | `E162_E107.md`, `E162_E107.sha256`, `src/replay_e162_e107.sh`, `scratch/B/logs/e162_r5_complete_replay.log` | ~0.05 including catalogue |
| enum | Reused G's 234,352 e107 roots, added 305 by critical one-edge swap and 24 by applying the same operation to the 305. Exhaustive small labelled calibration (12 cases). Exact count, graph-validity audit, and independent Traces distinctness; move reachability not assumed. | `scratch/B/logs/{e107_lateral_cal,e107_lateral_full,e107_lateral2}.log` | ~0.027 |
| enum | Profile-pinned gluer passed 12 order-22 controls plus a forged histogram, rejected 234,352 original e107 inputs in 54.54 CPU-s. The independent pair proof covers the strict complete catalogue instead. | `scratch/B/logs/{profile_r5_cal,row_support_cal,e162_r5_known}.log` | ~0.018 |

### Round 4

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| enum (SAT sample cross-check) | Exact up86 two-addition slice: 133,434 e87 parents, 4,751,963 distinct e88 duals, 4,641 completed chunks, 0 MTF completions. Independent SAT agrees 32/32 on a fresh uniform sample. Every up86 e88 dual has a d5/e<=58 or d6/e<=51 root, so the entire slice is in intended prefix scope. Neither all e88 duals nor all-graphs order-40 gluing. | `scratch/B/logs/{edgeup2_full86,up86_audit_r4,up86_r4_sat_sample,profile_census_r4}.log` | ~1.46 |
| enum | Early prefix checkpoint matches HoG e86 canonically (1,800). Its 147,334 e87 graphs plus one from up86 give exactly the reference 147,335 e87 count. Direct branch-and-bound checked triangle-freeness and alpha<=8 for all, independent Python checker passed 64/64, and the union is strictly sorted and hash-bound. The disjoint tail is ready without waiting for full prefix. No e88 closure. | `scratch/B/logs/{prefix_checkpoint_r4,prefix_checkpoint_r4_full_valid,prefix_checkpoint_r4_valid}.log`, `scratch/B/logs/prefix_checkpoint_r4.sha256` | 0.020 |
| enum | Disjoint tail pipeline calibrated exactly: 11 prior + 4 tail order-16/e21 parents, 130 prior + 29 novel order-16/e22 descendants, exact complement of 42 edge-critical graphs. Bound chunk hashes pass 7-input positive and reject reordered input. | `scratch/B/logs/{tail_accounting_control,chunk_bind_r4}.log`, `ralph/lanes/B/src/edgeup_tail87.sh` | <0.001 |
| hand | For e162 `(0,0,36,4)` the four degree-nine vertices induce C4. For e162 `(0,2,32,6)`, the degree-seven pair is adjacent, both degree-seven residues have e107, and the degree-nine induced subgraph is one of four explicit shapes. Neither is a distribution exclusion. | `ralph/lanes/B/CYCLE162.md`, `scratch/B/logs/cycle162_shape.log` | — |
| estimate | All 13 U88 distributions retain a viable relaxed degree-nine root profile, even imposing outer floors, MTF private-cell counts and no prefix/e43 roots in the residue. C35 control has exact feasible row substitution. Incidence LP and signature grouping do not reduce the e52/e44 cover. | `scratch/B/logs/{root_projection_r4,anchor_profiles,signature_r4}.log` | <0.01 |
| enum / estimate | Best e52 holdout is 0.298 vs 0.379 CPU-s/parent (128 held-out parents; `-DCOLMIN=99`); best e44 pilot is 1.852 vs 3.628 (32 parents; also `-DBITPLANE_ATTACHMENTS`). All controls match, but generation alone projects ~893 CPU-h or 49.6 h on 18 cores, before final sort/scan. No full launch and no 10x gain. | `scratch/B/logs/{coloring52_r4,coloring44_r4,holdout_r4}.log`, `ralph/lanes/B/LOG.md` | ~0.5 all pilots |

### Round 3

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| hand | An e88 dual outside prefix and d7/e43 has at least four d6/e52 or d7/e44 roots whose neighbors all have degree ≥5. This is a joint cover, not either branch separately; no global minimum-degree-5 assertion. H/critic review requested. | `ralph/lanes/B/ANCHOR88.md` | — |
| enum / estimate | `glueanchor -S 5` and optional `-P` match all 430 rooted labelled e63 controls and exact postfiltered outputs in four dispersed eight-parent blocks each at e52 and e44. 0.373 and 3.450 CPU s/input; optional overlap prefilter did not help. Estimated ~1,140 CPU-h before sort/I/O, 63 h on 18 continuously busy cores, so no full launch and 10x target unmet. | `scratch/B/logs/anchor_bench.log`, `ralph/lanes/B/LOG.md` | ~0.07 sample |
| enum | Star lift matches independent exact labelled oracle in both directions on order-22 controls; recovers 58/60 canonical e63 graphs. Independent exhaustive verifier also finds no one-star reduction of the retained edge-critical e88 dual (which is in the d5 prefix). | `scratch/B/logs/starlift_control.log`, `scratch/B/logs/starlift_critical88_ref.log` | <0.01 |
| enum | Exact star-lift slice from 133,434 up86 e87 parents: 14,454 globally edge-critical e88 duals, all MTF-negative; audited all 15 chunks and independent SAT agreed on 24/24. All 14,454 satisfy the prefix root condition, so they do not shrink the anchor complement and are not a complete e88 result. | `scratch/B/logs/starlift_stage{,_sat,_profile}.log`, `ralph/lanes/B/LOG.md` | 0.068 including SAT |
| estimate | Largest-first cost reflection (`-R`) matches canonical e63 outputs with multiplicities, but the first eight e52 inputs capped at 120 s wall (112.75 CPU s), versus 3.74 CPU s smallest-first. Do not scale. | `scratch/B/logs/order_bench.log`, `scratch/B/logs/anchor_bench.log` | 0.032 |

### Earlier rounds

| Label | Result | Evidence under `scratch/B` unless noted | CPU-hours |
|---|---|---|---:|
| enum | All 1,118,436 R(3,7;21) graphs rebuilt; all 13 GR T12 levels exact. | `logs/r37_21_final.log`, `logs/r37_21_3.log`, `logs/bootstrap.log`, `val/r3_7_21.g6` | <0.15 |
| enum | Verified 1,800 order-30 e86 and 560 order-31 e95 HoG inputs independently for graph validity, edge counts and distinct canonical labels. | `logs/hog_30_86.log`, `logs/hog_31_95.log`, `work/hog_30_86.canon`, `work/hog_31_95.canon`, `logs/bootstrap.log` | <0.01 |
| enum | `glue`, `glue2`, `glue5` rebuild C35 and Exoo from their own dual neighbourhoods (same canonical sets: 1, 18 respectively at chosen roots). | `logs/Ramseygraphs_3_9_35_e140.selftest`, `logs/exoo39.selftest` | included in bootstrap |
| enum | Exact upstream R(3,7) counts through specified e windows at n=16–19; exact R(3,8;22,<=44), (23,<=52), (24,<=58) per GR, including all 10,326,716 e52 inputs. | `logs/seed_small_retry.log`, `logs/seed_upper52.log:470` | small 0.006; upper 0.760 |
| enum | `gluetrans`, `gluepair`, `glueres` each recover exactly the canonical 191 order-22 graphs (same files, not just counts). `gluepair` and `gluetrans` match baseline on real order-30 samples. | `work/cal22_*.g6`, `logs/cal22_*.log`, `logs/real_*` | <0.1 calibration; see LOG for sample timings |
| enum | `mtfcover` passed C35 and 12 MTF order-22 re-glues against `glue2` filtered for MTF. All 1,800 e86 inputs gave no MTF completion, 2.53 CPU s; independent SAT gluer found C35 SAT and agreed on 8/8 e86 samples. Recheck of a previously closed level, not a new closure. | `logs/mtfcover_cal.log`, `logs/mtf86_full.log`, `logs/sat_control.log`, `logs/sat86_sample.log` | <0.003 |
| hand | Completeness of MTF cover branching and scope of results. | `ralph/lanes/B/LOG.md` | — |
| enum | Sampled 40 distinct e88 duals generated in the d5 calibration. No MTF completion; independent SAT agreed on 12/12. Not a full e88 result. | `logs/mtf88_sample.log`, `logs/sat88_sample.log` | <0.002 |
| estimate | Generation, not final scan, still controls e88: uniform sample of 96 from the exact n23,e52 family took 49.03 vs 63.25 CPU s (1.29x) with matching output. At 0.511 s/input, the 10,326,716-input stage alone projects ~1,465 CPU-hours = 73 h at 20 fully busy cores. No full launch; need <=0.27 s/input for practical completion. 10x target **not met** for generation. | `logs/uniform_23_52_gluetrans.log`, `logs/uniform_23_52_glue5.log`, `ralph/lanes/B/LOG.md` | sample 0.031 |
| enum | Early up86 pilot: 98,408 slice inputs, zero MTF outputs and 24/24 independent SAT agreement. Superseded for coverage by the round-4 terminal scan. | `logs/edgeup2_pilot.log`, `logs/edgeup2_pilot_sat.log` | 0.032 |
| cert | Not every e88 dual can be generated by edge addition from e87: explicit (3,9;30,88) graph has checked independent 9-set witnesses after all 88 one-edge deletions. This is a counterexample to the shortcut, not an order-40 graph. | `ralph/lanes/B/critical88.json`, `ralph/lanes/B/src/critical_witness.py`, `logs/critical88.log` | <0.001 |
| enum | `gluecheap` exactly matches all 191 canonical order-22 graphs and all 162 labelled outputs on the 96-parent e52 sample, taking 44.37 CPU s versus 49.03 (`gluetrans`) and 63.25 (`glue5`). `g84` profile filter recovers the independently filtered 24 of 60 e63 controls; early triple propagation matched small controls but was 4.15x slower on 24 e52 inputs. | `logs/cal22_*`, `logs/gluecheap_23_52.log`, `logs/triple_3_*.log`, `ralph/lanes/B/LOG.md` | sample 0.012 cheap; 0.016 triple |
| estimate | Dispersed e52 paired blocks: 0.555 CPU s/input baseline, 0.491 optimized, 0.468 outside-prefix only (ranges 0.456–0.676, 0.419–0.578, 0.383–0.541). At least ~1,340 CPU-h for e52 and ~82 CPU-h for e44 before e43 and final sorting/scanning (~79 h even at 18 saturated cores). On 32 dispersed e44 parents, exact raw equality and zero outside-prefix outputs; sample alone is not exclusion. | `logs/paired_speed_r2.log`, `ralph/lanes/B/LOG.md` | see paired log |

## Next

0. Critic/H: review the critical receipt crosswalk and disjoint named
   union in `ROUND16_REPLAY.md`; no production rerun. Reopen one-edge
   descent only with an independent e109 input; it does not cover
   saturated missing keys. No new discovery wave without a distinct
   source or coverage argument.
1. Critic/H: replay or audit the bounded prefix and scout proof tranche.
   `src/replay_prefix_r7.sh terminal` and `src/e108_scout_proofs_r8.sh replay work/e108_r8_scout_proofs`
   are ready. Do not re-launch prefix. Outside-prefix critical e88 after
   e43 still requires d6/e52 or d7/e44, ten U88 keys unchanged.
2. The complete reducible e88 zero is ready for critic review; optional
   fresh `src/replay_tail87_r6.sh terminal` independently recomputes the
   tail and binds both MTF scans. Scope is only reducible e88;
   `critical88.json` proves a critical graph exists.
3. Do not scale e52/e44, star-lift, the e108 adjacent-stem, d6/e65, pair
   repartition or unrestricted narrow nonadjacent-stem pilots, or old
   local/host pilots. Require a different source or necessary coverage
   reduction with measured value before further batches.
   t9<=89 and larger t8 floors unbudgeted.
4. Do not repeat the 545, the 7,954 or the 77-host descent. The e95 source
   is exhausted; e96 acquisition lacks 1,818 critical parents and is not
   priced by deck speed. Require a new source or necessary coverage reduction;
   do not reopen broad e99..101. Keep five missing, no floor-109 claim.
   At exact 2,104,151 require full order/e/alpha/distinctness audit and
   terminal checked proof cover including reducibles before floor 109.
