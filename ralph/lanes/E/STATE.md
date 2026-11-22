# Lane E state — round 22 complete (2026-11-22 CET)

## Jobs and cost

None running, detached, or stopped. Checked every listed timeout PID
after the last exit. The finite announced work completed. Do not rerun
the original 22 EXDEV-stopped workers or any audited shard for credit.
`scratch/E/r22_shared/jobs.tsv` has every real timeout wrapper PID,
exact command, log, core (one), start and deadline. `owner.json` in
each shard also records its actual worker PID. `exits.tsv` and
`reconcile.log` account for outcomes. Important job groups:

| Job group | Slots | Start / end (CET) | Logs |
|---|---:|---|---|
| Core-6 exact cover, independent generator and price (1500791,1500804,1614700) | ≤2 | 19:22:19 / 19:26:07 | `census.6.log`, `independent.6.log`, `pilot.6.log` |
| First core-6 launch, stopped after EXDEV | 22 | 19:26:43–49 / 19:27:35 | `worker.6.{0..21}.log`, `core.6/failed-exdev/` |
| Corrected core-6 worker IDs 22–43 (first PID 1715926) | 22 | 19:27:52–19:28:21 / 19:31:02 | `worker.6.{22..43}.log` |
| Exact covers, independent generators, separate pilots, cores 9/18 | ≤4 | 19:27:12 / 19:30:28 | `{census,independent,pilot}.{9,18}.log` |
| Core-9/18 production worker IDs 0–12 / 0–10 | ≤24 | 19:30:27 / 19:34:42 | `worker.{9,18}.INDEX.log` |
| Complete artifact audits; 1,162 fresh dual replays | 25 replay slots | 19:31:25 / 19:36:59 | `audit.CORE.final.log`, `recheck.CORE.OFFSET.log` |
| Deficit-two / known-74 controls and scans (last PID 2158645) | 1 | 19:34:24 / 19:40:07 | `deficit73.*.log`, `known74.*.log` |

Peak 26 slots (observed at 19:30:50). Five-minute nominal active slot
snapshots 19:25/30/35/40: 0/24/2/0. Including measured failures,
**7,788.30 CPU-s = 2.1634 core-h** over 1,068 elapsed s (7.29 mean
measured cores); excludes unmeasured EXDEV stops (<1,100 CPU-s extra
by wallbound). ~394 MiB new logical staging. One launch toy failure
and one pre-claim file race exited 1; neither left a production gap.
No limit, solver SAT or unchecked debit on any covered terminal.

## Claims for H and critic (evidence: `ROUND22.md`)

All in involution `(2,32)` with four size-six attachments (`t=4`),
universal `δ(G)≥5`, `δ(W)≥2`, no MTF assumption.

| Result | Label | Core-h | Evidence in `scratch/E/r22_shared/` |
|---|---|---:|---|
| Conditional mixed cores 6 `G?bav_`, 9 ``G?q`v_``, 18 ``GCpb`o`` under E-021: byte-bound 157 branches, 589 shards, 677,214 projections, 5,779,378 lifts. All 1,162 width-three proofs independently rebound and dual-checked twice, zero unresolved. Combined with the other 16 core results and E-019, this closes `e(W)=11` in the stated stratum. | hand + enum + cert, pending | 2.161 rounded measured, plus EXDEV | `core.CORE/{parent.json,shards.jsonl,shards/}`, `audit.CORE.final/`, `recheck.CORE.OFFSET.log`, `reconcile.log`, `freeze.sha256` |
| `e(W)=8,P=2` excluded without E-021. Both e73 windows would need core `C8` or `2C4` containing their two d7 and six d6 vertices. 67 such W masks on 25 of the complete 62 cards, zero necessary `(10,10,14)` partitions by two exact methods. | hand + enum, pending | 0.00129 | `deficit73.final.log`, `deficit73.final.jsonl`, `freeze.sha256` |
| `e(W)=8,P=0`: every omitted group with `b_i≤12` gives the sole missing E-021 class; at least two such groups. Independent mark enumeration on all 160 eligible known e74 cards: six W masks, zero relaxed partitions, even allowing all retained support totals. Not an exclusion of `P=0`. | hand + enum filter, pending | 0.00081 | `known74.relaxed.log`, `known74.relaxed.jsonl`, `freeze.sha256` |

No entire `(2,32)` exclusion, no MTF-distribution debit, no graph
candidate and no Ramsey verdict. `(5,5)` remains certified.

## Next

- Critic: replay the three final artifact audits and certificate
  partitions or sample from their frozen ledger, check the 19-core
  join and the two new marked window arguments in `ROUND22.md`.
- Price a new disjoint next target before launch: `e(W)=8,P=0` has
  ≥2 same missing windows, all four for `(12,12,12,12)`; consider a
  missing-window deck join, not an exhaustive unpriced quartet loop.
  The `e(W)=10` profile `(10,10,10,14)` has a prospective
  three-small-group projection-first relaxation; calibrate against
  E-019 before scaling. Other 8/9/10-edge branches, `δ(W)<2`, other
  attachment sizes and involution types remain open.
- Use `r22_launch.sh` and in-place atomic outputs for later jobs.
  `queue_mixed74.py`'s manifests preserve local ordinals with a global
  projection base. Compressed proof archives are sufficient for
  `audit_mixed74.py --ledger` to regenerate the exact formulas and
  recheck the LRATs. Keep the archives, code and original cover files.
