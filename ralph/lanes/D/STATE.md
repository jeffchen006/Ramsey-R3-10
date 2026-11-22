# Lane D — round 22 handoff, 2026-11-22

`S=scratch/D/closure22`; `T=scratch/D/m14r22`. All work is in lane-owned paths. No graph candidate and no full Case-R/kernel closure.

## Results

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| cert + enum | 404 regression rebound and double-checked; 250/250 directed C22 planted boards pass, 250/250 adverse edge mutations reject. | `scratch/D/closure22/control/control.log`, `scratch/D/closure22/recover.log` | 0.01 |
| cert + enum | Fresh unpinned R(3), K=2,t=17,m=15: **149/149** remaining support hosts have ordinary LRATs accepted by `lrat-check` and `cake_lpr`; 427,324 ordered assignments / 250,440 marked orbits. 404 is not in this fresh count. | `ralph/lanes/D/CLOSURE22.md`, `scratch/D/closure22/{cover.txt,manifest.tsv,replay*.log}`, `ROUND22_FREEZE.sha256` | 0.91 measured production+clean replay |
| enum + cert | Same-pole m=14 sector: 539/539 keys covered. 534 direct receipts; five raw LRAT-size caps replaced by all 55/55 sorted-first-double prefix receipts. Every one of 209 fixed action cells agrees independently, including zeros. | `CLOSURE22.md`, `scratch/D/m14r22/{prefix,literal.log,lease*.log}` | 0.08 prefix audit + queue ongoing |
| enum + hand | m=14 support census: 25,142 colored-nauty representatives; D 539 pass / 4,712 Hall rejects, S 3,847 pass / 16,044 rejects, O 3,847 pass / 16,044 rejects. Labelled coefficient fibers and literal Hall audit agree. | `scratch/D/m14r22/{roster.jsonl,coverage.log,dispatch.tsv}` | 0.01 |
| enum | C22 missing-edge controls: 27 forced Y-edge occurrences, all present; target tail sample 33,417→32,897 after D-051-style marginal checks, zero new host zeros. | `ralph/lanes/D/margins22.py`, `scratch/D/m14r22/{margincal.log,marginprice.jsonl}` | 0.001 |

The 149-host result is a local projection closure, not a sec7(a–e) full original-kernel certificate. Combined with D-044 it implies the marked `K=2,t=17` layer has `m≤14`; no claim that all K=2 or all Case R is closed. In m=14, D is the excluded same-pole alternative, so any remaining path must use two distinct exceptional poles (S/O). This is a hand consequence of the sector split plus its checked receipts.

## Active jobs

The 24 coordinators below are the real listed PIDs, one core each, CWD `T`, command `m14queue22.py worker N`, `nice -n 5`, `timeout -k 12 21600`, VM 2 GiB, CPU limit 20,700 s. They are allowed to continue between rounds; some may be stopped briefly by the bounded archive replay leases. Logs are `T/wN.log`; reservation count is guarded by `T/staging.lock` and the 13.5 GB logical cap.

| N | PID | timeout PID | log |
|---:|---:|---:|---|
| 0 | 2121520 | 2121518 | w0.log |
| 1 | 2121555 | 2121553 | w1.log |
| 2 | 2121603 | 2121599 | w2.log |
| 3 | 2121627 | 2121625 | w3.log |
| 4 | 2121643 | 2121641 | w4.log |
| 5 | 2121661 | 2121658 | w5.log |
| 6 | 2121686 | 2121684 | w6.log |
| 7 | 2121706 | 2121704 | w7.log |
| 8 | 2121727 | 2121725 | w8.log |
| 9 | 2121760 | 2121757 | w9.log |
| 10 | 2121783 | 2121780 | w10.log |
| 11 | 2121812 | 2121810 | w11.log |
| 12 | 2121851 | 2121843 | w12.log |
| 13 | 2122042 | 2122040 | w13.log |
| 14 | 2122072 | 2122068 | w14.log |
| 15 | 2122109 | 2122106 | w15.log |
| 16 | 2122137 | 2122127 | w16.log |
| 17 | 2122721 | 2122707 | w17.log |
| 18 | 2122828 | 2122826 | w18.log |
| 19 | 2122880 | 2122870 | w19.log |
| 20 | 2122900 | 2122897 | w20.log |
| 21 | 2122968 | 2122965 | w21.log |
| 22 | 2123008 | 2123005 | w22.log |
| 23 | 2123082 | 2123080 | w23.log |

At the latest snapshot, 2,686 distinct m14 keys have receipts: D 1,067 checked plus 10 solve-capped leaves, S 797 checked, O 812 checked; 5,547 keys remain unreported or running. Capped leaves are open, not UNSAT. The queue is intentionally still active and must not be duplicated.

Observer: PID 2841712, timeout 2841698, `T/five_minute.jsonl`, polling only and zero solver cores. Listed temporary archive replay leases have completed; `T/audit{2..5}.log` and `T/final8.log` contain sampled independent checks. Use `ralph/lanes/D/round22_m14_replay.sh NEW_DIR [workers]` for a clean replay; use `ralph/lanes/D/round22_replay.sh NEW_DIR [workers]` for the m15 layer. `ROUND22_FREEZE.sha256` binds the m15 evidence and source inputs; do not edit the freeze.

## Next

1. Let the 24-worker S/O queue run; collect statuses and proof bytes next round. Do not requeue capped keys automatically.
2. Critic/H should review `CLOSURE22.md`, the 149-host reconciliation, prefix receipts, and the D-sector implication. H may copy the claims to `ralph/CLAIMS.md`.
3. If queue cost or storage becomes excessive, use the measured marginal filter only as preprocessing; it produced no host closure in its 24-key sample.
