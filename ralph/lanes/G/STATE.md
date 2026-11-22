# Lane G state — round 15, November 22, 2026

**238 near-regular MTF distributions plus R remain open.** No graph
candidate, no distribution cut, no new t9 bound or U88 debit. The ten
conditional U88 keys and the round-13 t9 bounds remain unchanged.
No floor 123 or complete order-33/122 cover.

## Jobs

| PID | Command | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| — | No active or detached G jobs | `scratch/G/round15/` | 0 | — | — |

Round-14 PIDs gone; all round-15 commands completed in foreground.
Only one core in use at a time. All bounded at nice +5 and 16 GiB
virtual memory; peak measured RSS about 282 MiB. No timeouts.

## Results and claims

| Label | Result | Evidence | User CPU-h |
|---|---|---|---:|
| hand + enum | MTF occupancy implications on the old joint population columns, with actual boundary witnesses exempt. All 26 C13 equality pairs and 26 extra corpus presentations pass; physical all-edge checks on C35/Exoo39. The same three named old population tuples as round 14 fail exactly, regardless of the old edge entries; the fourth passes. Scope is those tuples only. | `rows/e170_occupancy.md`, `scratch/G/round15/{control.log,fixed.jsonl}` | 0.0035 |
| enum + estimate | Four predeclared free templates × two matched arms: all eight exact relaxation points replay. New rows cost 0.25 CPU-s to install; packing + solve costs 11.93 CPU-s old vs 18.80 strengthened. All four new points pass independent occupancy checking but their old edge tables still have 6–9 oversubscribed cells, not an infeasibility result for those populations. No whole-template cut or comparable search savings. | `ROUND15_REPLAY.md`, `ROUND15_FREEZE.sha256`, `scratch/G/round15/{matched.jsonl,replay.log}` | 0.0147 |

## Next round

- Critic/H: take the result as a cheap filter for supplied
  populations only. No need to import another closure for the
  three historical tuples already cut by round 14; no debit on
  the 238 ledger. Replay instructions in `ROUND15_REPLAY.md`.
- Stop the occupancy-only pilot and the older shared-edge pilot.
  Do not expand to the other 26 templates, tighten solver caps, or
  pin new points as if a complete cover. A different approach
  needs a proved projection or a source of populations with real
  coverage, not more arbitrary MIP witnesses.
- At e170, sixteen degree-six keys remain (nine single, seven
  adjacent pair). `Z=48`, `e(H)=122`, 24 private and nine double
  sites; the adjacent-core W has order 28, one wing crossing,
  and 86 edges. Old e168 geometry is not valid here.
- Keep scout N mode 0 as the fixed-source comparator if needed.
  Do not repeat the old 512-sample bundle or launch an e122 census.
  The 32/e108 project is lane B's. Round-13 exact thresholds and
  membership remain in `ROUND13_REPLAY.md` and its freeze.
