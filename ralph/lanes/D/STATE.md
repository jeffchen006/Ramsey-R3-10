# Lane D — round 24 handoff, 2026-11-22

**Submitted: in regular R(3) with exactly two deficient nonedges, each marked deficient path now has 19, 20 or 21 induced pentagons.** The remaining 57 shapes at 18 and the upper extremes 22/23/24 closed. Also all square flaps are independent; with three cubic square sites each flap is cubic. No candidate, unrestricted kernel, or Ramsey decision. Pending independent critic/H review. `W=scratch/D/wing24`; paths below relative to W unless indicated. Historical r23/r24 launch tables are `HANDOFF23.md` and `PROCESS24.md`.

| Label / scope | Evidence | CPU |
|---|---|---:|
| hand + enum + local cert, late t18 two-flap 43 | `../square18r23/hex/final23`, `replay23.{tsv,log}`: 2,752/2,752 exact-shard secondary replays, no extra case credit | 4.920 production + 0.739 replay core-h |
| hand + enum + local cert, t18 other 57/57 | `final18/{summary.json,shape-maps.json,cover.tsv,receipts.tsv,open-shapes.tsv}`, `ROUND24.md`: 360 parent keys; 567 unique used ordinary-LRATs, 35 bare leaders. Two capped fifth-site leaves replaced by 32 and 19 sixth-site proofs; 333 locally completed parents propagate to all shapes via whole-shape transport. | 2.488 used receipt core-h; 3.783 all named four/five/six attempts incl caps |
| hand + enum + local cert, t22/23/24 complete | `high/final22`, `high/final23`, `high/final24`: respectively 2,625/2,640/355 distinct dual-verified receipts, all archive hashes checked, all open tables empty. e22 after rowcuts + 378 bare leaders; e23/e24 direct. | 2.726 / 1.970 / 0.279 core-h |
| hand + enum, all t square collar | `generic/{roster.log,cal.log,spec.json}`, `ROUND24.md`: 14 local degree/link cells, ten empty; direct argument using disjoint square contact groups. Four real strengthened SAT relaxations on 30 sites (`generic/w*.partial.g6`), **not candidates**. | four local models only |
| enum (census, not graphs), intermediate densities | `high/audit.log`: independent labelled degree-matrix counts agree with orbit masses before paircap at all densities 18..24. `high/rowcuts*.tsv`, `physical-row-audit.log`: 2,390/1,824/456/34 physically rebound and exhaustively impossible rows at t22/21/20/19. | preparatory, not a second case debit |
| hand + enum + local cert | Every square-free K=2 private wing contains at least two induced hexagons. At t19 the entire 27-shape 0/1-hex sector closed: 168 primary roots, 109 leaders, 105 direct + 68 complementary terminal receipts. At t20/21 by two independent cycle censuses. `high/finalrare19`, `high/hexsector-final.log`. | 0.657 used proof core-h |
| estimate / open | t21: 3,828 leader keys. t19 + t20 square-bearing successors: 222+1,562 leaders. New priority: pairwise disjoint hexes, t19+20 = 109+8 keys; three measured prices. No intersection theorem yet. Other t19/t20 square-free work is NOT queued. | `high/{PRICE21,PRICE1920,PRICE-disjoint,PRICE-repairs}.txt`; current CPU via monitor |

## Current jobs

Thirty mutually exclusive one-core slots, command `opt/venv/bin/python -B ralph/lanes/D/sweep24.py SLOT`, cwd W, `nice +5`, VM 2GiB per child, CPU 20,500s / wall 6h plus child stage limits. Original sweep cohort started 22:59, timeout 04:59 CET; replacement cohort started 23:08–23:09, timeout 05:08–05:09 CET. Expected proof work into ~23:30–00:15 depending on caps, staging and I/O. After named queues drain the bounded supervisors may await a further manifest, **not busy solvers**. All r23 streams and initial four-site/fifth-site/high-22/23/24 wrappers have exited. PID 235696 was transiently stopped to price successors, resumed and subsequently exited. No stopped solver. Table below is real PID, timeout PID, log; old PIDs in PROCESS24.md are historical only.

| Slot | PID | timeout PID | log |
|---:|---:|---:|---|
| 0 | 1516262 | 1516256 | replacement0.log |
| 1 | 1516367 | 1516359 | replacement1.log |
| 2 | 1006023 | 1005978 | sweep2.log |
| 3 | 1516491 | 1516482 | replacement3.log |
| 4 | 1516591 | 1516583 | replacement4.log |
| 5 | 1516679 | 1516667 | replacement5.log |
| 6 | 1006029 | 1005982 | sweep6.log |
| 7 | 1006034 | 1005983 | sweep7.log |
| 8 | 1006032 | 1005984 | sweep8.log |
| 9 | 1516806 | 1516797 | replacement9.log |
| 10 | 1006044 | 1005986 | sweep10.log |
| 11 | 1516932 | 1516910 | replacement11.log |
| 12 | 1517037 | 1517023 | replacement12.log |
| 13 | 1517426 | 1517384 | replacement13.log |
| 14 | 1554647 | 1554636 | replacement14.log |
| 15 | 1006036 | 1005993 | sweep15.log |
| 16 | 1517905 | 1517883 | replacement16.log |
| 17 | 1518541 | 1518515 | replacement17.log |
| 18 | 1518863 | 1518854 | replacement18.log |
| 19 | 1518983 | 1518969 | replacement19.log |
| 20 | 1519248 | 1519217 | replacement20.log |
| 21 | 1519338 | 1519326 | replacement21.log |
| 22 | 1519441 | 1519428 | replacement22.log |
| 23 | 1519537 | 1519530 | replacement23.log |
| 24 | 1519689 | 1519669 | replacement24.log |
| 25 | 1519804 | 1519786 | replacement25.log |
| 26 | 1519944 | 1519929 | replacement26.log |
| 27 | 1006064 | 1006007 | sweep27.log |
| 28 | 1608011 | 1608001 | replacement28.log |
| 29 | 1520046 | 1520042 | replacement29.log |

Round-24 observers: PID 3985471 timeout 3985407 (`watch24.py`, `five_minute.jsonl`, 22:32–04:32), PID 1684565 timeout 1684553 (`measure24.py`, `campaign2.jsonl`, 23:12–05:12); source `campaign.jsonl` holds 23:00–23:10 history, previous observer 1080054 stopped. Zero solver leases. Stage CPU counts exclude replay unless separately reported. Some old sweep coordinators exited on a disappearing *replay reservation file before claiming a new job*; changes made lease deletion atomic under the lock, new workers skip completed replays and verified-dead slots alone were restarted (`replacement.tsv`, `activepids.tsv`). This is not timeout/UNSAT and invalidates no retained proofs.

Space: `W/{lock,charged,reserve.*}` total work envelope **5.55 GB net** (plus <0.45GB metadata/census margin within D's 6GB). Standard 110MB slots incl 19MB CNF / 32MB binary / 55MB trimmed / 25MB packed; easy six-site square 60MB incl 12/14/27/15MB. Actual peak is less than the sum of consecutive stage caps. `global2301.tmp` = 136.355GB logical all scratch; respects joint ceiling with other lanes' budget. Keep every unique proof. For the new h19/20/21 and b repairs, redundant deletion lines can be omitted for RUP-only additions; **both** ordinary LRAT checkers still required. No rewrite of archived old proofs. Monitor keys by density, not the older watcher's generic `subleaves` bucket.

## Next

Late addendum: at t=20 **two of the hexagons must intersect** in a square-free wing. Of 352 such shapes, 351 already contain an intersecting pair; shape 1489 has eight decks, all directly dual-checked and indexed in `high/finaldisjoint20/receipts.tsv`. At t=21 an intersecting pair is automatic by the independent cycle census. This does not yet establish intersection at t=19. The other 109 disjoint-hex t19 leader keys are queued; reprice/repair cap leaves before counting the sector. At 23:17 the logical all-scratch sample was 138.038GB, lane archive/metadata ledger ~3.15 GB (not reserved bytes). Slot 28's last race replacement started 23:10, PID 1608011, timeout 1608001, wall deadline 05:10. The stage accounting meter restarted at 23:12:51 with replacement process sessions included. The original two-flap and final18 integrity streams are ALL finished.

1. Critic/H: check `ROUND24.md`, `ROUND24_FREEZE.sha256` and four frozen complete scope indexes. Rebind e.g. `z280_4-0-4`, an h22 square and an h22 bare transport via `index24.py replay` (in a reserved slot). The e18 transport is whole-bare-shape only after all leader roots close. These are local CNF certificates plus a hand/enumerated cover, NOT the original Section 7 edge-kernel chain.
2. All 567 used t18 proofs have now been freshly rebound, unpacked and run through both checkers, each on its original hash-shard and exactly once across original and replacement logs (1,710.30 stage CPU-s; `final18/replays.tsv`). Integrity only; never count a replay as a new root.
3. T19 rare is already final. Collect the **next** t19 sector against `high/disjoint19`, t21 against `high/plan21`, square-bearing t19/t20 against `high/square19` and `high/square20`. The 23:18 snapshot is `handoff-counts.json`; the latest two priority transitions are `sweeps/batch.00-a19-latest` and `sweeps/batch.00-b21-latest` with complete five-site manifests derived at that cutoff (no credit until checked). Before subtracting a case, match all sources including zero census, impossible extension, bare transport, retained checker markers and archive SHA. For a capped four-site root, `repair24.py DENSITY` builds the exact fifth-site candidates with a separate multiplicity recheck. The standard complementary row is priced (`high/PRICE-repairs.txt`); capping a replacement or a six-site root needs a separately priced further split, never a blind retry. `highcover24.py freeze DENSITY NEWDIR` supports completed direct, cut and full five-site replacement rows only.
4. If budget insufficient for all 2,703 remaining square-free leader roots at 19/20 (inc. nested rare sector), finish a named full min-hex-exits sector. `high/{rings*,hexsector.log,minexit*}`. After a priced disjoint tranche, publish `W/sweeps/batch.*` atomically: `.00` priority is checked within an ongoing tranche; complete receipts are skipped. Do not publish `sweeps/no_more` until already-queued batches are done. The 5.55GB reservation is shared and does not reset. Under K=2 both paths have to survive; no kernel debit and no assumption of a second clean vertex or a symmetry of the whole target.
