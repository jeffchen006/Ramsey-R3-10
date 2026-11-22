# Round 22 — degree budgets on fresh physical cap-five frames

**Hand + enum, pending.** No row or frame was cut by C-050. The
unchanged signed join independently excluded **eight fresh marked
frame pairs**, including the two degree-budget pilot pairs, after
their old marginal tests had passed. The results are separate; do not
credit any signed exclusion to the new budget or to the old fifth
test. No candidate, distribution, or whole case claim.

## Frozen comparison

Fix left frame **42072**, host 97, left neutral **6**, and physical
triple **x=1** of left-window degree 3, at key `(66,4)`. Use the
matching right `(75,5)` triple roster, with its original IDs. It has
116 rows of which `(42072,16780)` was in round 16 and is removed.
The earlier fifth pilot used a different left frame, 42679; none of
its IDs are used. The 56 old structural vetoes and round-18 closed
slices do not overlap these IDs. Independently recompute old marginal
bits: 12/115 fresh are both-positive. Before any new budget test,
select the first eight both-positive IDs in ascending order:

```
27448 27790 37550 38058 38779 39167 39288 40768
```

All eight get the unchanged signed comparison; only its first two
get the new gate, exhaustively over their legal physical `T` rows.
The other four fresh old-positive frame pairs in this subroster got
neither check. There was no recount of any old fifth-gate bin.

## Calibrated labelled adapter and measured stop

`proofs/panel22_fixed_label_projection.md` gives the exact extension
obligation for these boards and proves that the adapter preserves
every physical orientation and outside fixed incidence. Each card
is enumerated by its labelled singleton columns with exact local
alpha and triangle tests; outside allowed sites bound the degree
still owed to the core. The optimized path uses existence queries
to find coordinate minima rather than counting every restoration.

- On both C13 fixture variants, the new adapter's complete sets
  agree with all 16,384 literal masks. The strict pair has local
  counts 2 and 18 and an overload at 6; releasing the prohibition
  gives counts 4 and 18 and retains the actual C13(1,5) plant. In
  particular neither path counts prescribed `6–5` as new.
- Separately, 16 small core/root tests agree on **148 labelled
  assignments** after directly enumerating every compatible physical
  labelling of the raw order-5..8 `(3,4)` catalogues. The optimized
  minimum search agrees with complete enumeration on both controls.
- The two target pilot pairs each have **48** legal physical rows.
  Each has **17** empty separate-card rows under the pins/degree
  bounds and **31** rows with all five separate domains nonempty.
  On the **62** nonempty rows, **all 60 coordinate minima per row
  are zero**, against fixed capacities
  `(5,4,4,3,4,3,3,3,3,2,3,3)`. Each distinct coordinate can avoid
  all new contacts of an individual card in some admissible physical
  restoration, although the same restoration need not avoid them
  all. Consequently the C-050 sum has no leverage in these frames.
  The exhaustive counting and focused-minimum runs agree 96/96
  on the row, domain flags and minima. No frame blocked by this gate.

Counting all restorations took **64.14 CPU-s** on two pairs; focused
minima took **23.76 CPU-s**. The original signed join on the *same*
two pairs took **0.01 CPU-s** at stopwatch precision and made zero
terminal calls. The new gate cannot improve that endpoint, and this
pilot does not price any other family. No production budget queue.

## Signed comparison: separate local exclusions

`scratch/C/r22/summary.log` binds each exact ID to the before/after
domain sizes. All eight have nonempty original domains; every one
becomes arc-empty. The unchanged literal baseline makes 45,348
probes across all eight, including 14,358 in the two pilot frames;
the arc-filtered join has zero probes, zero tuples and zero terminal
calls. Neither reaches a cap. The existing independent Python audit
reconstructs all eight physical domains and gets the same zero
solutions (at most two indexed join probes per ID). This is `enum`,
not a checked LRAT/DRAT certificate or a closure of the full bin.

If accepted, the signed-untested total falls from 2,542,514,364 to
**2,542,514,356**; subtracting the independent 56 structural vetoes
leaves **2,542,514,300** neither signed-tested nor structurally
excluded. No fifth-budget exclusion is subtracted. The evidence
contains exactly these eight pairs, not all 116 raw IDs.

## Replay

```sh
sha256sum -c ralph/lanes/C/ROUND22_FREEZE.sha256
bash ralph/lanes/C/replay_panel22.sh "$PWD/scratch/C/r22-review"
```

The clean replay rebuilds the native baseline and compares seven
deterministic artifacts byte for byte. The original exhaustive
pilot's exact inputs, raw output and normalization are pinned;
the final adapter's `--exhaustive` mode also replayed in the clean
directory (39.84 CPU-s) and produced rows and log byte-identical
to the focused mode. Neither replay needs output from another current
lane or a solver queue.

All bounded runs and replays used one worker at a time, 512 MiB VM,
and **210.52 CPU-s / 0.05848 core-h** including failed initial catalogue
calibration (accidentally imposed an exact degree in an unpinned
control; corrected and recalibrated before touching the new gate on
any target) and native rebuild. Peak RSS 291,260 KiB for the rebuild;
the main Python pilot used 35,500 KiB. No active or detached jobs.
