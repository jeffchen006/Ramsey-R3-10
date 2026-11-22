# Round 24 — marked adjacent degree-six, e=170, h=5

**Scope.** The old closed `h=8,7,6` slices are unchanged. Excluding this
marked structure would still not exclude `h≤4`, the single-degree-six
structure, or any entire distribution. No candidate has been handed to
the flow. G's accepted starting ledger remains 238 near-regular MTF
distributions plus R.

## Independent cover and receipts

Opening snapshots `scratch/G/round24/incoming{,-holes}.json` reproduce
the critic's 22:05 totals exactly: 256 full board representatives and
140,055 keys from them; 145,500 including 5,445 transported partial-board
keys. Eight late capped binary files had solver exit 20 but exactly hit
their byte cap; they shipped no proof credit. From the same inventory,
`round24_plan.py` writes an exact complement: 30 boards, 34 maximal raw
prefixes, 10,612 physical keys. `complement.json` lists *all* labelled
words of each such key, grouped by their new scopes. The 63 planned
scopes partition all raw prefixes; 12 have no new physical keys but
do have admissible labelled words. Generation-one and generation-two
queues retain both bit polarities when splitting a failed scope. The
upstream labelled action fixes each crossed anchor and may exchange
the two roots. This is a transport of labels, not a graph automorphism.

`round24_status.py` binds every retained CNF and packed proof digest,
witness file (if any), board manifest and exact occupancy scope. When
provided its snapshot, `round23_h5_hole_cover.py` separately recomputes
all prefix coverage and the transport to physical keys. That second
count omits any normalized `DN` scopes. A `DN` proof can exclude only
its explicit `(board,key)` IDs, and must be anti-joined against the raw
and transported cover before counting an increment. No `DN` proof
can be entered as if it were an unrestricted empty prefix. See
`rows/e170_occupancy_representative.md` for the graph-to-formula map.

For fresh stream replay from `scratch/G/round24`:

```sh
../../../ralph/lanes/G/round24_replay.sh UNIQUE_TAG RECEIPT_ID ...
```

The script regenerates the CNF and exact semantic delta; matches both
the packed and unpacked SHA-256, then feeds the unpacked stream to each
checker separately. Pipe exits are checked and any unread tail is
drained. No large ASCII file is written. In the low-risk PHP(5,4)
control, the ASCII stream is byte-identical to the earlier stored
reference and both checkers accept. The first two actual h5 pilots
also check: board 234 prefix `1110` produced a 35.33 MB binary / 17.04 MB
packed proof; board 174 prefix `10` with guarded physical witnesses used
47.39 MB binary / 23.22 MB packed. Read each `work/ID/*.time` to recover
all stages' CPU; timing does not include queue wait.

## Dispatch and alternative rows

`live.events.jsonl` is the immutable-by-append child lease ledger and
`live.samples.jsonl` contains five-minute actual process trees, CPU
deltas and new-key anti-joins. A task reserves the sum of its maximum
binary proof, packed output and 8 MB auxiliary budget before launch.
The 4.35 GB stage envelope is conservative: the queue adds the entire
reservation to currently measured stage bytes, even where this double
counts part of an active temporary. The supervisor also observes the
146 GB workspace bound; on a storage or resource stop the scope remains
open. Packed archives already generated are never discarded to make
room. Fresh successor budgets and actual exits are in
`successor-pilot.*`, `successor.*` and `successor.log`.

The `DP` successor emits A's mate-independent shore row, from a literal
ten-vertex witness. Each slot has its occupancy guard; every conflicting
opposite mate has a positive filter; possible same-coordinate exterior
edges are retained irrespective of the saved model's particular mate.
The six frozen model rows and two rows apiece on 16 width-three boards
match A's independent layout (`shore-controls-fixed.log`). These are
semantic controls, not production proofs or speedup claims. Production
audits reconstruct all added rows independently and match the guarded
formula delta. Only a checked target pilot enables broader DP or DN
use. The h4 preparations reuse the eight-deficit budget, with independent
small positional controls and the h5 184,488/286/156,112 inventory
regression before pricing target `h=4`; no h4 target claim is made.

## Measured continuation

At the intermediate 22:57:56 census, 133 completed D/DM attempts had
median total CPU 64.73 s (D) and 81.61 s (DM); among the checked DM
receipts, medians were 89.65 CPU-s and 33.48 MB retained. The fallback
draft of 46 exact narrower scopes therefore prices to a rough 1.04
core-h and at most 2.03 GB retained (44 MB per successful receipt),
but the remaining stage headroom is smaller, so its disk guard may
defer part of that roster. Time at this hard residual is not predicted
by the easy-board median; costs and coverage counts are measured
separately. Both DP pilots returned SAT; a DN pilot on board 276 checked
at 51.38 CPU-s for 117 explicit keys. Its fresh replay matches the CNF
and both proof digests and rechecks both proof tools. The other DN
pilot was a SAT relaxation. A transient cross-lane file unlink caused
an initial `du` failure; both affected supervisors exited, all orphan
workers finished, and the successor restarted with retrying size checks.

The h4 weak inventory matches `scratch/ideas/r018_N/burnside.tsv` at
864,087 labelled grids, 1,099 board orbits and 712,734 decorated keys.
The small four-defect calibrations match 28 forced pigeonhole failures
and 504 independently counted positive width-four placements. The h4
board 549/00 trial generated 60,223 clauses (5.72 CPU-s) and a SAT
relaxation (0.65 CPU-s) with an explicit physical I10. The target proof
cost is still unknown. Do not extrapolate this SAT time to h4 closure.

## Frozen Handoff

23:01:36 CET: 275 raw-complete boards and 149,356 keys on them;
153,336 distinct keys including prefix transport; another 423 from
three disjoint DN receipts yield 277 orbit-complete boards and
153,759/156,112 keys. This adds 8,259 keys to the critic opening,
leaving 2,353 on nine boards. The 88 new retained proofs and 56
terminal open attempts cost 10,742.60 recorded CPU-s, not including
independent replays, inventories or pending attempts. Archive hashes
are in `scratch/G/round24/round24-final.sha256` and can be checked
with `sha256sum -c` at repo root. `round24-final-residual.json` has
all remaining physical representatives and maximal raw prefixes.
The live fallback was still solving disjoint narrower scopes; later
receipts supersede rather than add to these totals.
