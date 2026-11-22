# Round 17 — freeze the named e108 evidence

**Confirmed scope inherited from B-036/B-037:** 2,104,146 named 32/e108
keys cannot be exteriors of an MTF degree-seven root. This is 2,102,271
named reducibles and 1,875 named criticals, with 2,017,637 accepted
eight-demand clique receipts and 86,509 accepted dual LRAT receipts.
**Five deletion-critical classes are absent** from the named union. The
MTF d7 floor remains **108**, not 109. No distribution cut, U88 change,
or candidate graph. Round 17 did not generate target inputs or replay or
produce any proof.

## Archive audit

`scratch/B/work/e108_r17/archive.sha256` lists the exact data files to
retain together, with paths relative to the repository root. This is a
manifest, not a backup or a new certificate. It includes the original
labelled input and rank maps, witnesses, pins, checked receipts, packed
payloads and index for all 257 round-15 shards, and the critical
crosswalk. In particular:

- Reducible rank disposition is separate from union rank. For adopted
  ranks, `adopted.tsv` maps back to round 6 or 14; `pilot-overlap.tsv`
  retains the original overlap. Otherwise use 0-based ordinal in
  `residual.u32` modulo 257 for the shard and the quotient plus one for
  its local rank. In `proofs.tsv` the identifier is the **source rank**,
  with a byte offset/length, CNF/proof hashes, method and ordered pins.
- For each critical key, the round-16 crosswalk gives the original
  graph6 label, cohort and local rank (definitions in
  `src/e108_r16_crosswalk.py`), receipt row and actual pins row. A zero
  LRAT pins row means **unpinned**, not missing: there are **430 pinned
  and 14 unpinned** critical LRATs. Keep both logs and all pins tables.
- The 173 round-6 reducible LRAT payloads include all three with
  overlapping later evidence, not an extra three blocked keys. Their
  payload list comes from the frozen replay log. The 1,361 round-14
  reducible LRAT hashes agree between the frozen receipt and LRAT list.
  For the 381 round-8 critical LRATs, the frozen round-16 crosswalk
  provides the per-file hash (the earlier freeze anchors the two logs,
  not each file). Checked semantics are inherited from prior rounds.

**Measured archive integrity only:** Python verified all **3,066 files**
(774,404,922 bytes) against inherited hashes. GNU `sha256sum` independently
verified the same manifest. A fresh rebuild matched byte for byte. The
tiny labelled fixture passes intact and rejects a missing or swapped pin
file. Successful checks used 6.83 CPU-s total (~0.0019 core-h), peak
24,188 KiB RSS. Only foreground work; no PIDs.

From the repo root (no solver):

```bash
ulimit -v 16777216; ulimit -t 45
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
nice -n 5 timeout 60s sha256sum --strict -c ralph/lanes/B/ROUND17.sha256
nice -n 5 timeout 60s sha256sum --quiet --strict -c scratch/B/work/e108_r17/archive.sha256
```

To rebuild the manifest from prior evidence, run
`python3 ralph/lanes/B/src/e108_r17_archive.py prepare OUTPUT` with a fresh
lane-owned `OUTPUT`; `cmp` with the frozen manifest. Logs are
`scratch/B/logs/e108_r17_{control,archive,sha256sum,rebuild}.log`.

## Reopen condition — open

The missing input is an independently generated graph6 catalogue for
order 32, 108 edges, triangle-free with independence number at most
eight (or an independently supplied critical complement containing the
five absent classes). Canonicalize and validate the inputs; audit
distinctness, exact difference and the published total before crediting
coverage, then check a root obstruction for each newly bound key. An
independent complete e109 catalogue is an alternate source **only for
addable e108 keys**; it cannot discover a saturated missing class by
one-edge deletion. Round 16 did not locate that source, and this round
did not rescreen it. No new target generation, e88 wave or repeats of
known-key ascent/descent. An alternative reopening requires an exact
coverage argument, smaller withheld-key calibration and a cost for the
whole missing slice.
