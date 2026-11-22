# Round 18 production gate (November 22, 2026)

Only marked e170 `h=8`, `middle+middle.2`. The rebuilt orbit roster is
16,350 labelled IDs. It attributes 660 to old scout proofs and 48 to the
six already checked full direct receipts (42 new transports), leaving
15,642 IDs in 2,024 orbits. No cross-scheme discovery. The registered
sample is 77 orbits: all seven of size two, 22 of size four, 48 of size
eight, with ordered-rank tails and extreme compatible site-pair counts.
There are no singleton orbits; the nonidentity fixed points are audited.

The sample used the same producer, compression, unpacking, semantic
binding and two proof checkers as production, with additional literal
block transports. Initial allocation metadata was rejected before the
first replay check (filesystem `st_blocks` changed after the file was
flushed); no proof bytes or roster changed. Replaying after using file
length with a page allowance gave 77/77. The sample's price includes
that failed setup attempt.

At 16.17 CPU-s already used, the extrapolated total including coverage,
packing, independent replay and allowances is 309.88 CPU-s (0.0861
core-h) at the stratified mean or 562.22 CPU-s (0.1562 core-h) at 1.2
times the stratum maxima, both with 38 CPU-s reserve. Disk including
38 MiB overhead/staging reserve: 136.06 MiB or 297.88 MiB respectively;
largest observed simultaneous raw and packed receipt charge 0.922 MiB.
These are estimates, not tail bounds. `estimate-0000.log` is the frozen
gate calculation. Run one foreground worker in paired generate/replay
checkpoints of at most 160, then independently reconcile every original
labelled ID. Reprice after each checkpoint, stop on any failure, model,
cap or over-budget forecast, and preserve all checked and open IDs.
