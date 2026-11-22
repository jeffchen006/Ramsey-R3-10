# Lane A state

Round 12, November 22, 2026. Share 4; no live or stopped A jobs. No order-40 candidate,
whole-distribution exclusion, or Case R closure.
Current replay: `ROUND12_REPLAY.md` and `scratch/A/strip12/round12.sha256`.
Rounds 10–11: `ROUND10_REPLAY.md`, `ROUND11_REPLAY.md`; earlier work in `LOG.md` and prior replay files.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start / expected end, CET |
|---|---|---|---:|---|
| — | No detached A jobs | — | 0 | — |

All round-12 checks ran sequentially in the foreground under per-run timeouts,
`nice -n 5`, `ulimit -v 16777216`. Total below 0.020 CPU-h, including pilots.
Round-11 PIDs 790867/790884, 790868/790880, 790869/790883 rechecked gone.
No A SAT, LRAT production, or replay in round 12.

## Results and claims

| Label | Scope/result | Evidence | A CPU-h |
|---|---|---|---:|
| hand | At mixed e168 original order24 A-small, alternate noncross pivot `s` preserves the same labelled order21 core and directed cross edge. The six `(d,s,τ)` types give orders d8 leaf 27 / full 26 or 27, d9 leaf 26 / full 25 or 26; restored centre has `d=|T'|−22`, not necessarily minimum. Relabelled marked C13 changes minimum without changing equality. No A-013 transfer. | `ROUND12_REPLAY.md`, `scratch/A/strip12/controls.final.log` | <0.001 |
| hand + enum, pending critic | Exact original-ID binding of all covered A reroot scopes, then necessary cross-pair support matching: order27 d8 899→447 rooted positions, 48→22 original IDs (one full, also leaf); order26 δ3 d8 full τ0 77 IDs, d9 0 for both pivot types; order25 δ2 d9 full τ0 16 IDs. Raw and canonical projections identical for the two smaller windows; both B shapes and orientations preserved. | `audit_a_side_reroot.py`, `audit_reroot_cross.py`, `scratch/A/strip12/cross{27.A,26.canon,25.canon}.idtags` | 0.011 final runs |
| hand + enum, scoped | Disjoint order27 and order26 δ3 surviving d8 sets give 99/18,797 old IDs with those routes. The other 18,698 require order26 δ4. d9 order26 always requires δ4; the 1,782/1,798 d9 IDs outside the order25 δ2 set need order25 δ3 or order26 δ4. These are per-route exclusions, not elimination of original IDs from all completions. | `ROUND12_REPLAY.md`, `scratch/A/strip12/{covered,needs-higher-minimum}.d[89].ids` | included above |
| enum, negative pilot | Optimistic wing-only contact screen removes 0/768 dispersed reroot branch tests; 156 positive small controls and planted I8 negative PASS; stop the screen. | `audit_reroot_wing.py`, `scratch/A/strip12/wing.pilot.{log,tsv}` | 0.001 |

## Next

- Critic/H: review the A-side table, exact mapped IDs, and conditional
  d9 no-δ3-at-order26 result. Do not extend it to non-equality windows.
- G owns pricing and solving. The order26 δ4 and order25 δ3 branches
  still lack complete sources here; do not pad order27 or treat the
  99/16 supported IDs as the whole A-small queue. A can bind a new joint
  source to the old IDs if G's separate test finds a material reduction.
- Keep the completed G-037 middle-only proof tranche archived; its
  21,236-row independent identity is in `ROUND11_REPLAY.md`. No duplicate
  SAT work, and no scale-up of the wing-only optimistic screen.
- R(7) remains untouched under the critic's mixed-strip directives.
