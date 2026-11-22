# Lane D — round 21, 2026-11-22 (final)

**Marked R(3), `K=2,t=17,m=15`: 9 of the 159 D-048 survivors excluded, leaving 150 of the original 162 supports.** Hand + enum pending critic. Every new zero still has nonempty individual margins. These are exclusions of marked supports, not edge kernels. Prior D-048 and D-049 confirmed in `ralph/critic/round_020.md`; round 20 handoff archived in `LOG.md`. `S=scratch/D/wing21`.

## Jobs

| PID | Command / log | Cores now | Start | Actual end |
|---|---|---:|---|---|
| None | Sequential, bounded foreground `wing21.py`, `wing21_audit.py`, `wing21_nextprice.py`; `S/*.log`. No detached, live or stopped jobs. | 0 | ~17:56 | ~18:01 |

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| hand + enum | All nine new zeros require the pole-pair join: roster lines **128, 140, 232, 299, 488, 614, 1009, 1011, 1068**. Ordered assignments on fixed representatives 2,296,202 → **443,384**, marked orbits 1,334,977 → **266,500**. All 159 decrease, 150 remain positive. No original kernel, `m=15`, or R(3) closure. | `WING21.md`, `S/{counts.tsv,target.log,audit.log}`, `ROUND21_FREEZE.sha256` | 0.00206 production; 0.00114 independent audit |
| enum | All 250 planted shores and 210 small literal profiles agree; exact independent recovery of every old/new margin, all 264 old/new/delta fixed counts, all per-host Burnside sums and join reasons. | `S/{controls.log,auditprice.log,audit.log}`, `wing21_literal.cc`, `wing21_audit.py` | included; entire round **0.00386** |
| hand + enum + estimate | Hypothesizing a missing disjoint Y edge reduces one-shore witnesses to bridge sites, with no strict supersets needed. Four-pole positive and deletion control; 27 forced occurrences on 250 planted shores, all present. Synthetic 2.54 CPU-s for mandatory-edge compilation and marginal calls alone; no target tests of this extension. | `WING21.md`, `S/nextprice.log`, `wing21_nextprice.py` | 0.00010 |

## Next

1. Critic/H: `bash ralph/lanes/D/round21_replay.sh scratch/critic/D21-audit` (fresh directory). No candidate, SAT, proof or debit against an unrestricted case. R(4) not reached.
2. Request a marginal-only forced-Y-edge scan of the 150 surviving hosts: reject a shore if its mandatory Y edges contain a triangle, number >15 or exceed the site's degree cap (ordinary 3, triple 2). Preserve all fixed counts, no paired edge lists. Calibrate first with literal missing-edge/deletion tests and C22. Proposed limits one worker, 64 MiB, 30 CPU-s target + separate 60 CPU-s audit. No target run of this follow-up before authorization.
