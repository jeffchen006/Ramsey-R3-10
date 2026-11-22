# Round 18 preflight: two physical slices only

The critic authorizes exact joint tests on A's 46+24 physical IDs,
at most 0.30 core-hours, two workers, 512 MiB/process. One foreground
worker suffices. No target ID generation or joint test outside these
slices. Use the round-16 native and independent package enumerators.

Price before launch: round 16 used 2.60 CPU-s native for 544 mixed IDs
with capped literal paths, and the maximum measured Python tail on
its 47 both-pass IDs was 2.638 CPU-s. Multiplying that tail by 70
gives 184.66 CPU-s, a crude price, **not** a bound. Use stage caps:
native target 60 CPU-s; independent target 300 CPU-s and its inherited
per-ID branch cap; the 6/7 control and labelled binder target add only
small work. On a cap, leave the affected coverage open. Recompute the
two marginal filters with independent hitting predicates on the
restricted weighted cells, not expanded header pairs; the small 6/7
weighted run took 0.45 total CPU-s and checked all 29,220 host products.
