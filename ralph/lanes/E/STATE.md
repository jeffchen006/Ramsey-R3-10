# Lane E — round 23 handoff (2026-11-22 CET)

Scope of new work: involution `(2,32)`, crown `t=4`, `δ(W)≥2`,
universal `δ(G)≥5`, no maximality assumption. See `ROUND23.md`.
No flow candidate or Ramsey verdict. `(5,5)` remains certified.

## Jobs

All round-22 wrappers absent at first check. Completed round-23 groups
are frozen in `scratch/E/r23_deck/{jobs.closed.tsv,exits.closed.tsv}`;
`jobs.tsv` records every detached wrapper and exact command, start,
deadline, one core and log; `exits.tsv` records real exit statuses.
Live at 21:22:48 CET (all `SNs`, verified PIDs):

| Real timeout wrappers | Command / log | Cores | Start / wall deadline |
|---|---|---:|---|
| 1519023, 1519047, 1519076, 1519150, 1519174, 1519191, 1519228, 1519358, 1519384, 1519413, 1519443, 1519486, 1519515, 1519561, 1519592, 1519610 | `project_deck23.py run e8ext.first.plan e8ext.final --offset SLOT --stride 16 --lazy 8 --proof 14 --skip 0 225 5115 7355 9922 15349`; slot 0 first regenerates independent cover; `e8ext.SLOT.log` | 16 × 1 | 21:21:10–11 / 21:57:55–56 |

This is only the `2C4` core (graph6 ``G?r@`_``), both `b_max=16`
profiles. 15,350 IDs total, six dual-checked pilot IDs are skipped by
production. At 21:22:48 there were 4,263 new CHECKED, zero open in
processed prefix; not terminal coverage. Expected ~0.60 core-h,
~200 MiB typical archive, 32 MiB per-worker archive gate. 2 GiB VM,
CPU and wall caps and bounded proof files; cap/open is not UNSAT.
Whole e8 extreme roster 258,512; second (`C8`) core's 243,162 IDs
are **not assigned**. Initial naive census terminated by signal 9
at its CPU limit; use completed indexed census, not its partial file.

## Claims for H and critic

Evidence `ralph/lanes/E/ROUND23.md` and `scratch/E/r23_deck/`.
All labels are pending new critic review.

| Result | Label | Measured core-h | Evidence |
|---|---|---:|---|
| e8/P0, any omitted b=13..18, known-card arm excluded: 351,794 masks, 134 unordered marks on 49 cards, all 134 addbacks byte-rebound and dual-checked twice. Combined with confirmed r22 b≤12 fact, all four H_i must be the single E-021 missing class. **Not an e8/P0 closure.** | hand + enum + cert | ≈0.16 | `known8.plan.jsonl`, `audit.8.*`, `rebind8/` |
| e10, `(10,10,10,14)`, large omission known-card arm excluded: 420,492 masks, 126 marks on 86 cards, 126 bound addbacks dual-checked twice; each small omission already forces missing by six d7 W sites. | hand + enum + cert | ≈0.17 | `known.plan.jsonl`, `audit.10.*`, `rebind10/` |
| e10 **entire profile `(10,10,10,14)`** excluded under the E-021 all-graph catalogue premise, by preceding known-card closure and conditional all-missing projection. 20 cores (7,740 normalized labelled); exact 8,157 rows, K=6:3,390 / K=7:4,767. 13 mapped pilots + 8,144 production, 8,157 independent byte/CakeLRAT/lrat-check replays, 13,247 valid lazy cuts, zero remaining. **No other e10 profile excluded.** | hand + enum + cert | ≈0.54 beyond known-card arm | `projected.plan.jsonl`, `projected.pilots.tsv`, `projection.rebind/`, `freeze.e10_known.sha256` |
| e8/P0 with bmax=17 or 18 excluded conditional on all-missing: K≥6 by a b10 omission, but K≤10−ceil((bmax−8)/2)≤5. bmax=16 forces K=6 and four triple rows, only `(10,10,12,16)` or `(10,11,11,16)`; ongoing. | hand conditional | negligible for inequality | `ROUND23.md`, `e8.extreme.index.log` |

Measured 3,293.81 completed CPU-s = **0.91495 core-h** at checkpoint,
including census/replay, bounded failed attempts and calibration, not
active e8ext workers. Brief initial audit dispatch overlapped up to
three finishing known8 wrappers; every later dispatch verified slots
free first. ~159 MB logical staging including in-flight e8 receipts.
Freeze contains 25,617 digests and passes `sha256sum --quiet -c`.

## Next

- Reconcile e8ext slots exactly: zero discarded/capped IDs, six pilot
  IDs plus modulo shards, independent `cmp` in slot 0, and rebind
  formulas with group-specific zero-contact budgets. The e10 binder
  hardcodes `K−6`; generalize to `K−#singleton_rows(role)` before e8
  replay, checking old e10 pilot hashes retain exact bytes.
- Price front/interior/tail on the disjoint C8 core before committing
  the 243,162 IDs. Try a cheap witnessed upper-graph propagation gate
  to shrink that tranche, or use the C-055/056 physical overlap and
  matching necessities. Never claim capped leaves. Other e8/P0
  profiles and `(2,32)` overall remain open.
- No concrete missing-card source yet. The two-copy physical deck
  join is calibrated on all six smaller omission pairs (and adverse
  mutations), but has no priced target producer. Do not assume a
  marked isomorphism or treat known cards as a complete catalogue.
- Bank prior round: e8/P2 closed and e11 subcase closed, confirmed
  in `ralph/critic/round_022.md`. Do not repeat those jobs.
