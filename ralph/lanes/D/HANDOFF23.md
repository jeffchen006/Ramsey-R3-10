# Lane D — round 23 handoff, 2026-11-22

**Submitted: in regular R(3), if there are exactly two deficient nonedges (`K=2`), EACH marked deficient path now requires at least 18 induced pentagons. At t=18 its private wing cannot contain a square.** This does not decide R(3,10), eliminate all K=2, or close any original kernel. No candidate graph. Critic/H should review the new graph implications and local certificate cover before admission to the ledger.

Directories: `B=scratch/D/m14r22`, `N=scratch/D/m14r23`, `P=scratch/D/c6r23`, `T=scratch/D/square18r23`. Core ceiling D=30. `PROCESS23.md` archives historical launch PIDs/timeouts; old r22 queue, direct m14 queue and all m14 repair/lease jobs are finished, and the stopped wing workers resumed. No m15 or old D-prefix solve was repeated.

| Label | Result / scope | Evidence | Core-hours |
|---|---|---|---:|
| hand + enum + local cert | Marked K=2,t=17,m=14 excluded. All 8,233 distinct keys (539 D, 3,847 S, 3,847 O), **8,323 terminal receipts**, empty anti-join. 24 duplicate archives separately listed with **zero** extra credit. Four O keys split over 44 feasible heads, at O_10800-96 lifted the opposite-board proof; all 66 action/head cells and all 44 rebuilt head proofs audited. | `CLOSURE23.md`; `N/final23/{keys,leaves,duplicates,open}.tsv`, `N/{literals.log,literal9850.log,deepcheck.log,deep9850.log}` | **24.50** cumulative named production stages across r22/r23 incl caps; 8.81 new direct; 0.03 sampled/critical clean replay |
| hand + enum + local cert | **No K=2 marked wing at t=17**, all m. All 15 exact theta/barbell shapes; column and multiplicity algorithms agree on all 3,114 six-site decks. Every deck covered: 3,049 binary direct, 3 previous direct, 2 isolated-hex and 60 one-flap aliases, relying on 3,078 distinct local receipts. | `WING23.md`; `P/final23/{coverage,receipts,open}.tsv`, `P/{wings.audit,wingfinal.log}` | **3.509** counted production for selected receipts, excl setup/refresh/replay |
| hand + enum + local cert | At every t under K=2, an induced hexagon in the private wing needs at least two wing edges leaving it. The no-e(Q) isolated hex proof carries; 12 one-flap decks audited with slack-one argument, nine direct + 18 viable hub-split leaves and one reversal. 27/27 one-flap clean replays. | `WING23.md`; `P/{hexrebind.log,hex.cake256.log,flapaudit.log,flapaudit.time}` | 0.010 one-flap replay |
| hand + enum + local cert | At K=2,t=18 all square-bearing wings excluded. Genbg + independent perfect-matching addback (7 deletion types, 75,545 labelled matchings). 32 residual square shapes, 26 exact empty decks, **24/24** on other six replayed with both checkers. | `SQUARE23.md`; `T/{audit.log,receipt-index.tsv,recheck.log}` | **0.0435** production + **0.0115** replay |
| enum + estimate / open | t=18 square-free: 117 shapes, 17 excluded by hex lemma; 43 two-flap hex shapes on a new 2,752-deck complete manifest; remaining 57 outside the current queue. Five pilot prices 2.22–9.66s / 0.12–1.24 MB. No automatic closure on cap/model. | `T/hex/{cover.log,manifest.tsv,price.log,PRICE.txt,five_minute.jsonl}` | ~3.8 estimated core-h before launch; actuals in publisher |

## Live jobs
**21:42 reconciliation:** all 3,064 t17 replay keys matched their original shard once, with both checkers accepting (0.7318 additional core-h; `P/wing/verify/anti-join-final.tsv`). All 28 e18 coordinator PIDs in the historical transition table below now run e18 production. With both stream replayers this uses 30 slots. At 21:42:09, 624 of 2,752 e18 roots had a retained dual check, no caps recorded, and 36 extra clean replays were logged; the branch is open. Do not add the clean replays to the root count.

21:41: two separate 1-core e18 physical replay workers (`e18stream23.py n`, CWD T, 2GiB/20700s/6h, expected about 22:30–23:00) bring the maximum to **30 slots**. Shard/PID/timeout/log:
    0	2444288	2444280	hex/check0.log
    1	2444782	2444748	hex/check1.log

28 disjoint slots, one busy subprocess per slot. Each t17 producer at `P/wing` finished. Its clean replay `wingreplay23.py n` (`P/wing/verify/rN.log`, started 21:27, deadline 03:27) gives its slot to `wingproof23.py squarefree18 n` via `afterverify23.sh n` (`T/hex/eN.log`, started 21:36, deadline 03:36). Each coordinator has `nice -n 5`, VM 2 GiB, CPU 20,700 s, wall 6h, per-stage CPU/time/filesize limits. Expected e18 finish 21:55–22:20, dependent on tails/guard; PIDs below are real coordinator PIDs, preserve the timeout PIDs in `P/wing/verify/pids.tsv` and `T/hex/pids.tsv`. A waiting shell is **not** a second busy worker. Snapshot:

| Slot | t17 verifier PID (finished) | e18 PID (live) | Earlier stage during transition |
|---:|---:|---:|---|
| 0 | 1870214 | 2233670 | e18 production |
| 1 | 1870238 | 2234038 | t17 replay, e18 waiting |
| 2 | 1870284 | 2234175 | e18 production |
| 3 | 1870371 | 2234238 | t17 replay, e18 waiting |
| 4 | 1870407 | 2234314 | e18 production |
| 5 | 1870458 | 2234389 | t17 replay, e18 waiting |
| 6 | 1870506 | 2234479 | e18 production |
| 7 | 1870549 | 2234522 | e18 production |
| 8 | 1870623 | 2234594 | e18 production |
| 9 | 1870668 | 2234665 | t17 replay, e18 waiting |
| 10 | 1870699 | 2234720 | e18 production |
| 11 | 1870747 | 2234799 | e18 production |
| 12 | 1870765 | 2234881 | e18 production |
| 13 | 1870806 | 2234954 | e18 production |
| 14 | 1870866 | 2235030 | e18 production |
| 15 | 1870889 | 2235104 | e18 production |
| 16 | 1870911 | 2235167 | e18 production |
| 17 | 1870952 | 2235301 | e18 production |
| 18 | 1871032 | 2235427 | e18 production |
| 19 | 1871130 | 2235560 | e18 production |
| 20 | 1871203 | 2236298 | e18 production |
| 21 | 1871256 | 2237146 | e18 production |
| 22 | 1871303 | 2237847 | e18 production |
| 23 | 1871380 | 2238576 | e18 production |
| 24 | 1871674 | 2239250 | e18 production |
| 25 | 1871761 | 2239640 | t17 replay, e18 waiting |
| 26 | 1871872 | 2239970 | t17 replay, e18 waiting |
| 27 | 1872205 | 2240116 | t17 replay, e18 waiting |

E18 monitor PID **2313339**, timeout 2313315, 0 solver slots, `T/hex/five_minute.jsonl`, deadline 03:37. Terminated old m14 and t17 observers after their final indexes passed; no other detached solver queue. Ledger `P/wing/{lock,charged,reserve.*}` covers both t17 and e18 proofs. Max combined archive/live reservation 4.8 GB; binary raw cap 28 MB / trimmed 49 MB / CNF 11 MB. `N/reserve.ALLOWANCE_TRANSFER_ONLY=4.1GB` is a **virtual** transfer from old main capacity to wing, not work or disk use. Keep it while the successor uses the transferred envelope. All proof receipts retained. Never sum snapshots as new exclusions.

## Next

1. Critic/H: start with `CLOSURE23.md`, `WING23.md`, `SQUARE23.md`, `ROUND23_FREEZE.sha256`. Both `N/final23` and `P/final23` have immutable hashes, complete coverage tables, and empty anti-joins. These are **local ordinary LRATs + hand/enumerated covers**, not the original-kernel Section-7 chain. Verify the unprotected patch (`clean=()`), `44/45` Q-edge totals and the hex bound with *no* Q-edge-total premise.
2. Collect `T/hex/e*.log`, derive an exact anti-join against `T/hex/manifest.tsv` using `P/wing/e18_*/result.json`. If every key has a retained receipt, independently regenerate the physical formula via `hex18.formula18(key)`, hash/replay compressed archives, and report that restricted branch. Do **not** call all t18 closed: 57 square-free shapes were never queued. If capped, retain IDs and price a complete sorted equal-Q-word hub-count split (C22 and pilot first). No blanket root retries.
3. For the 57, first price a fixed cycle/path patch using full F common-neighbor counts. The near-hex 64-deck price does not transfer to a hex-free shape. If archive pressure returns, use a shared projection certificate rather than pinning all stars or exceeding the space limit. No other lane input needed beyond independent critic/H review.
