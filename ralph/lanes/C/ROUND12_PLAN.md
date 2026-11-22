# Round 12 budget — bounded one-sided test

- Recount the old and new cap-five B-mask profiles on the 191 existing
  order-22 hosts. The 395 smaller planted marks passed, then two physical
  order-22 hosts took 0.42 CPU-s and 12 MiB RSS. Linear price ~40 CPU-s
  for all 191, ceiling 150 CPU-s / 240 wall-s and <100 MiB of files.
- Compare original union-13 card IDs and multiplicities to `r10/fixed22.tsv`;
  union 12 is already excluded, union 13 newly excluded (round 11), and
  unions 14–18 are locally viable only. No larger catalogue or new join.
- On the tight `14/222/2` subfamily, price consistent incidences from the
  two extra common neighbours on the same twelve labelled sites as the
  original A triple. Derive sound checks before counting removals;
  calibrate on small planted graphs and keep exact per-host/card statistics.
- `C24(1,4,6,11)` five-common-site positive passed in both label orders.
  First 24 tight parents took 4.61 CPU-s on 864 orbit reps: forecast
  251 CPU-s for 1,307 at that rate. Ceiling 420 CPU-s / 700 wall-s, one
  core and a single witness journal under 20 MiB. No SAT proof queue.
- A separate 12-key opposite-window *projection* pilot (two wings per
  e-bin) cost 10.12 CPU-s total, with four dual LRAT, eight iteration
  caps. Both e20 samples needed only seven cap cuts each, <0.03
  Python CPU-s each; LRATs <16 KiB. The e20 slice is only nine left
  marks × 36 wings; allow this one bounded 324-key replay, forecast
  <30 CPU-s / 25 MiB, wall cap 100 s, Python CPU cap 65 s. No join
  or continuation for e15–19.
