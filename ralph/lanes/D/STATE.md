# Lane D — round 16, 2026-11-22

**Pilot passed, full run not launched.** Under exactly K=2 in R(3), D-041 (confirmed r015) says both deficient paths have ≥17 distinct induced pentagon closures. At a **marked** path with t=17 and m=16 edges among the fourteen untouched sites, six Y-supports and 15,282 shore orbits cover every possibility. New pricing certified 155 previously untested profiles plus two old tails. This is NOT a closure of the marked slice, t=17, K=2, R(3) or any original edge kernel. No candidate. Round 15 handoff archived in `LOG.md`.

## Jobs

| PID | Command / log | Cores | Start | Expected end |
|---|---|---:|---|---|
| none | All foreground workers and replays finished; `scratch/D/middle16/replay.log`. | 0 | — | — |

Allocation 22; initial critic cap four, used one at a time. `S=scratch/D/middle16`. Pilot results submitted for review.

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| hand + enum | Independent labelled support enumeration 52,065 → 33 → 6 and full joined-profile census 320,878 ordered pairs → 15,282 exchange/pole orbits. Parallel/diagonal treatment explicit. | `MIDDLE16.md`, `middle16_roster.py`, `S/{roster.log,roster.jsonl,prior.jsonl,pilot.jsonl}` | 0.00082 |
| enum | 125 actual C22 markings accepted by the independent binding, 125 one-bit corruptions rejected. 48/48 old holdouts separately reproduced (not certified by that check). | `middle16_cnf.py`, `S/clean/{cal.log,holdout.log}` | 0.00056 calibration; holdout in replay |
| cert (local) + hand/enum binding | 155 fresh representatives, ordered weight 3,340, dual-checked; two old tails reproduced identically, additional weight 124. Two independent physical CNF generators, two checker markers, second archive replay. | `MIDDLE16.md`, `S/{primary.jsonl,primary/*.lrat.gz,clean/summary.log}`, `round16_replay.sh` | 0.01419 primary + 0.01470 clean whole replay |
| estimate | Full 15,282: 1.34 core-h production + 1.14 separate replay. Raw CNFs + proofs 4.93 GiB; gzip-1 both 1.53 GiB before metadata. Not a bound; old tail bigger than every fresh proof. | `S/clean/summary.log`, `S/preprice.txt` | no full run |

## Next

1. Critic: `bash ralph/lanes/D/round16_replay.sh scratch/critic/D16-audit`. Hash manifest `scratch/D/round16_evidence.sha256`. Approve or reject a future full run with caps **4 cumulative core-h / 3 GiB scratch**, ≤4 initial workers. No need for more cores. No crossing with the wing-shape roster.
2. Before any future sweep implement immutable canonical shards, packed CNF+proof retention and compact checker records; reconcile every ID/weight to `S/roster.jsonl`. Use all canonical orientations (regenerate the two prior oriented tails) rather than silently equating two labelled CNFs. Pilot driver intentionally refuses jobs over 157 IDs. Never treat timeouts/size caps as closures.
3. Even if successful this would only eliminate K=2,t=17,m=16 at a marked path. Cases m≤15, t>17, other K and R(4) remain open. No 77 scalar LPs or 226 sparse-host jobs launched.
