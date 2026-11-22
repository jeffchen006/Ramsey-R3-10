# Lane A state

Round 15, November 22, 2026. Share 3; no live or stopped A jobs. No new
order-40 candidate, distribution exclusion, or whole Case R closure.
R(7) was already closed by Lane C's accepted finite certificates (round
1); A replayed them independently. Do not restart the old R(7) cube queue
or the retired e168 strips.

Current hand+enum audit of the marked cap-five 17/17 block:
`ROUND15_EXCHANGE.md`, `replay_panel_exchange.sh`, `ROUND15_FREEZE.sha256`,
`scratch/A/r15/`. Complete 12+30 shard coverage, pending critic.
Lane C owned production; A consumed receipts and did not launch solvers.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start / expected end, CET |
|---|---|---|---:|---|
| — | No detached A jobs | — | 0 | — |

Uses bounded foreground tools (`nice -n 5`, 120/150-s CPU/wall and
16-GiB VM limits), at most two census pipe workers and no solvers.
Round aggregate about 0.011 A CPU-h including repeated validation and
compiles; peak recorded RSS under 400 MiB, retained A data under 1 MiB.

## Results and claims

| Label | Scope/result | Evidence | CPU-h |
|---|---|---|---:|
| hand (pending critic) | Shore swap `(i,j,b) -> (j,i,b)` on separate copies, physical neutral `k -> k xor b`, private crossing matrix transposes. Both bits remain, fixed diagonals are counted once, one-sided premises and stage/timing data do not transfer. | `ROUND15_EXCHANGE.md` | — |
| enum (coverage, pending critic) | All 157,472,001 ordered headers bound to the original 12 receipt rosters or 30 disjoint HH shards. Exact bitwise transpose membership over all off-diagonal IDs; 67,417,211 original direct, 40,218,398 inferred HL, 49,836,392 HH orientations requiring 24,924,719 representatives (13,046 diagonals). First HH shard 2,647,995 reps, 541 diagonals. | `scratch/A/r15/{census.tsv,first.tsv,coverage.initial.tsv,receipts.initial.log}`, `ROUND15_EXCHANGE.md` | 0.004 full rebuild/replay |
| enum (controls) | 2,672 smaller physical orientation checks, both fixed bits and asymmetric fixed-header crossings. Missing diagonal, wrong bit and dropped LH reference rejected. Actual first-receipt copies reject transferred diagonal, count-preserving map mutation, and one live/disagreeing terminal. Incomplete `--require-full` output is not published. | `scratch/A/r15/{controls.log,receipt-negatives.log,incomplete.stderr}` | 0.001 controls incl negative receipt checks |
| hand + enum (marked two-neutral block only, pending critic) | All 30 HH receipts independently bound and checked: 24,924,719 reps → 3,620,522 local → 6,027 panel → 1,617 joint, 74,632 matching rejected fillings, none live. With the 12 frozen ordered negatives and exchange proof: 92,341,930 direct, 65,130,071 transferred, 0 ordered unresolved. | `ROUND15_EXCHANGE.md`, `ROUND15_FREEZE.sha256`, `scratch/A/r15/{coverage.final.tsv,receipts.final.log,totals.final.log}` | <0.001 final A binding; 0.0751 C production |
| archived | Round 14 exact independent header census and C prefix audit: original 12 ordered shards through left ID 24,575, 67,417,211 headers, 12,594 panel IDs, 3,464 joint, full matched reasons on 148,231 fillings, none live. A separate first read recovers first twin stream digest and former pilot/triple IDs. | `ROUND14_REPLAY.md`, `ROUND14_FREEZE.sha256` | prior |
| archived | A-023: independent Round 13 literal package audit bound 55,055 labelled frames and 9,959 atlas entries, replayed 498,668 left-triple IDs (17,604 local → 0 panel), preserved all 100 held panel survivors. | `ROUND13_REPLAY.md`, `scratch/A/panel13/round13.sha256` | prior |

## Next

- H/critic to review the complete `--require-full` receipt audit and
  C's structural cover and search. No more A production or replay wave
  unless the critic finds a gap. Never copy stages or reason vectors
  to exchanged IDs.
- Even full closure is only the marked cap-five 17/17 block, i.e. the
  two-neutral-site case of a `K4,4` in a cap-five regular target. The
  zero-/one-neutral-site cases, cap six, and whole Case R do not follow.
