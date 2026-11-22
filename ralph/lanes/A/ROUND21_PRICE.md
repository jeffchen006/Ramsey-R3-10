# Round 21 — preflight price for the fixed-alignment denominator

Scope: the eight frozen G pilots; independently rebind their context
keys and subtract the frozen 51-key baseline. No solver work.

After literal small controls and the seven matched historical counts,
take the first and last fresh canonical key per board (12 total). Timed
in `scratch/A/r21/sample.log` and `sample.time`: 3.00 CPU-s inside the
counting loop, 3.07 CPU-s including setup; 13,580 KiB peak RSS. Mean
0.250 CPU-s/key and max 0.372 CPU-s/key give 46.0 and 68.5 CPU-s for
184 keys, respectively. These extrapolations are estimates, not runtime
bounds or historical fixed-CNF solve prices. Stage two small TSV tables.

Run the independent permanent and literal permutation counts together
with a single 100 CPU-s / 130 wall-s, 512 MiB virtual-memory worker.
Clean replay uses just the permanent algorithm to regenerate both TSVs,
via one 25 CPU-s / 35 wall-s worker. Including the pilot and all preflight
work (~13.4 CPU-s), even both caps leave headroom under 216 CPU-s. No new
proofs, no 81-context scan, and no `h<=6` extrapolation.
