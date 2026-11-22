# Round 17: preregistered h=8 direct price

Retire `leaf+leaf.1`. Start from all 30 `h=8` hole-scheme rosters. The unit
is the same labelled alignment ID `(scheme, sorted double supports)` as in
round 16, **not** the number of occurrences of a transferred pattern or the
number of stabilizer orbits of alignments. The inherited local argument and
proof bindings are in `rows/e170_aligned_grid.md` and `ROUND16_REPLAY.md`.

Rebind the 62 scout proofs and all 1,357 round-16 receipts before taking
any cross-scheme credit. Compare the scout union as a set, not just a
count. Expand all checked masks with the 48 simultaneous relabelings and
whole-shore transpositions. A full eight-double mask fixes **both** hole
sets, by projecting the eight masks onto each shore and complementing in
`E(K5)`. It therefore cannot hit a different relative hole scheme under
these actions. Only a proper-subset proof can add cross-scheme IDs.

Sort the remaining 29 schemes by uncovered count (ties by scheme name).
Within each scheme sort the uncovered IDs and let `m` be the final offset.
For zero-based scheme rank `i` take offsets `floor(m/32)`,
`floor(m*(12+(5*i mod 9))/32)`, and `m-floor(m/32)`. In rank 0, 14 and 28
(smallest, median and largest) also take `0`, `floor(m/4)`, `m`.
This gives 96 distinct IDs across all 29 schemes, with both near-tail
offsets in every scheme and the actual endpoints in three. This is a
dispersed diagnostic, not a probability sample of runtimes. Freeze the
actual queue (`sample.json` plus its hash) before running any of its IDs.

Use direct certificates for these IDs only. One slot, nice +5,
384 MiB process virtual limit. Sequential phase wall caps are 310 s
(coverage/control wrapper), 15 s (preregister), 100 s (sample), 85 s
(archive replay) and 15 s (summary); the sum is below 540 s. The sample
also has internal aggregate gates at 80 CPU-s or 72 MiB allocated, checked
before each ID. After the smaller controls pass, the round-16 direct
0.116 CPU-s/ID and 4.57 MiB/48 suggest 11.2 CPU-s and 9.1 MiB for the
96-ID producer at the old price, plus at least a second binding pass.
These are planning estimates only. Stop without a price for any missing
receipt or checker mismatch, and stop at a checked local projection model.

Archive by byte hashes; a separate pass must check exact queue equality,
reconstruct the clauses and run both LRAT checkers. Report per-scheme
producer + reconstruction + hash + replay CPU and LRAT/payload sizes.
For the remaining IDs report a weighted direct mean-price projection
and a cautious sample-max-price projection, neither a guaranteed bound.
Credit exactly the explicitly checked fresh IDs from this sample, not
new stabilizer postings. No second wave, no h<8, no production on any of
the other 29 schemes, and no new transfer discovery.
