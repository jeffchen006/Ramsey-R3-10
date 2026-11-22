# Lane G — round 24, November 22, 2026

**238 near-regular MTF distributions plus R remain open.** Marked adjacent e170
has accepted h=8,7,6; h=5 is partial. No candidate or whole-distribution debit.
Round-23 handoff preserved as `scratch/G/round24/round23.STATE.md`.

**Frozen 23:01:36 CET (hand + enum + local cert, pending critic):**
275/286 raw-complete boards and 149,356 keys on those boards. With
transport alone, 153,336 keys; with 423 distinct normalized keys,
**277/286** orbit-complete boards and **153,759/156,112** keys.
**2,353 keys on nine boards** remain; relative to the critic opening,
8,259 new unique keys. 88 new checked receipts, 2.984 timed attempt
core-h, 2.641 GB packed proofs, peak 526,972 KiB. Evidence:
`scratch/G/round24/round24-final{,-holes,-merged,-residual}.json`,
`round24-final.sha256` (relative to root), `ROUND24_FREEZE.sha256`.

## Jobs

Working directory `scratch/G/round24`; scripts in `ralph/lanes/G/`.

| timeout / worker PID | command and log | cores | CET start → hard deadline |
|---|---|---:|---|
| 878711 / 878718 | `round24_fallback.py . 755019` / `fallback.log` | ceiling 16; seven live at 23:01:36, disk-reservation limited | 22:56:54 → Nov 23 02:33:34, or queue drained |

`round24-final-jobs.json`: live timeout PIDs at audit 1056778, 1056818,
1155454, 1160222, 1160330, 1163216, 1163440 (one core each, 1050-s wall).
The supervisor appends successors to `fallback.events.jsonl` and records
process/growth samples in `fallback.samples.jsonl`; verify current PIDs
there before rescheduling. The restarted predecessor 754977/755019
and all its six workers have exited. Retained normalized scopes:
`k276_00` (117), `k260_00` (160), `k260_01` (146); no raw-board debit.

Real child timeout PID, full args, log, one-core lease, launch/deadline,
exit and timed CPU are appended to `scratch/G/round24/live.events.jsonl`;
`live.samples.jsonl` records child process trees, five-minute CPU deltas,
reserved/live bytes, and anti-joined physical keys. Both standalone pilots
(3844472/3844485 and 3844477/3844488) have already exited and checked.
First supervisor 3950454/3950485 stopped when `du` raced a D reservation
unlink; all its seven uncollected children did independently exit (five
checked, two SAT relaxations). Initial successor 256411/256436 hit the
same race before launching a child. `round24_supervise.py` now retries
that transient error and adds a 250 MB cushion to unstable partial
measurements. The successor restarted after confirming no orphan was
live; no solver was killed by this lane. It uses the same dispatch lock;
new receipt/PID logs begin with
`successor-pilot.*` and `successor.*` and never overlap `live` child
leases. It first tries up to two DP and two DN scopes, under a total
prepriced pilot budget of roughly 0.1 core-h, then scales only modes
with a checked target pilot. Stage ceiling 4.35 GB gross, global logical
ceiling 146 GB; each solve reserves binary + packed + 8 MB auxiliary.
No large ASCII is staged. Each worker sets 5 GiB VM and an independent
CPU cap per stage under a 1050-s hard wall limit.

## Results so far

- **enum + prior local cert:** opening evidence `scratch/G/round24/incoming{,-holes}.json`
  matches critic: 256/286 boards, 140,055 whole-board keys, 145,500 with
  transported partial keys. All old jobs completed; eight final exits were
  solver 20 but truncated at 100,000,000 bytes (still open); only l259_111,
  l283_100 and l283_110 shipped valid receipts in that tranche.
- **enum (cover):** `round24_plan.py`, `scratch/G/round24/complement.json`:
  10,612 exact unexcluded keys on 30 boards, 34 maximal raw prefixes; next
  planned scope list at `scratch/G/round24/queue.json` has 63 disjoint
  scopes, including both children of each split and 12 with zero new keys.
- **local cert (control only):** `scratch/G/round24/pilot-php.log`:
  both checkers accept streamed ASCII LRAT reconstructed from binary on
  PHP(5,4); byte-identical to the earlier sliced proof.
- **enum + local cert, interim, pending critic:** 22:42:37, 265/286
  raw-complete boards, 144,127 whole-board keys, 148,486 distinct keys
  with orbit transport. `scratch/G/round24/interim2{,-holes}.json`:
  39 r24 proofs, 1.355 timed core-h, 1.148 GB packed, 526,864 KiB peak
  RSS. Baseline and interim are nested; not additional counts.
- **hand + enum (controls):** A's one-shore cut independently recompiled
  and falsified on six saved target models and two sides of 16 smaller
  boards. `round24_shore{,_controls,_audit}.py`,
  `scratch/G/round24/shore-controls-fixed.log`. `DP` uses still-guarded
  occupancy and every bad opposite mate; no claim of target speedup yet.
- **hand + open:** `rows/e170_occupancy_representative.md` supports exact
  `DN` representative clauses; pilot `k276_00` checked for 117 keys at
  51.38 CPU-s, and `k240_00` was a SAT relaxation. DN receipts credit only
  explicit `(board,key)` values, never an entire raw cube. DP pilots
  `p246_11` and `p247_101` were SAT relaxations; no DP production scale-up.
- **enum (h4 controls and weak cover):** 28 width-three pigeonhole
  contradictions and 504 literal width-four placements across four
  occupancy pairs, `h4-manual-control.log`. The h4 inventory matches
  the independent scout Burnside totals: 864,087 labelled grids,
  1,099 board orbits and 712,734 decorated keys, `inventory-16.json`
  and `inventory-optimized-16.log` (66.71 CPU-s). No h4 exclusion claimed.
- **estimate + open (h4 target):** finished pilot 603627/603673, board
  549/00, emits 60,223 clauses in 5.72 CPU-s; solver SAT in 0.65 CPU-s.
  Physical decode finds an I10 (five grid sites, two selected slots and
  three boundary vertices). `scratch/G/round24/h4-price-549-00/physical.log`.
  Neither that relaxation nor a cost extrapolation is an exclusion.

## Next

1. Collect fallback jobs and rerun status → raw-hole transport → merged
   anti-join → exact residual from `ROUND24_REPLAY.md`. Do not stack the
   265/276/277 milestones or treat any DN receipt as an empty raw prefix.
2. Scope the remaining h5 SAT models by physical I10 and cap failures
   by smaller occupancy scopes. Confirm `round24-final-residual.json`
   before dispatch; the fallback changes it. `262` and `252` retain the
   largest frozen masses (753 and 513 respectively). Respect available
   simultaneous reservations; a raw-cap result does not count.
3. After h5, the h4 proof cost is not priced; exploit a saturation or
   stronger cut pilot before sweeping 1,099 boards. Do not debit h≤4,
   the single-d6 slice, or either parent distribution on h5 evidence.
