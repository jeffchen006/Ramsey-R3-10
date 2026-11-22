# Round 14 — coverage and receipt audit of cap-five 17/17

Scope: marked `K4,4`, degree nine, cap five, exactly two physical neutral
vertices and two order-17 windows. The audit does not argue that all of Case R
admits this marking. It does not cover cap six, other window orders, or the
near-regular cases. The coverage and receipts are `enum`; the needed gluing
implications are `hand`. No LRAT is claimed.

## Independent header enumeration

For each labelled private vertex, subtract its window degree and its literal
root incidences from nine. The sum on each side counts the as-yet-unknown
cross edges once; the two sums must agree. Determine the neutral labels by
the complement of the four mark masks, not by an inferred isomorphism or a
degree sort. The neutral edge must agree. Each neutral site needs the sum of
its two private-side degrees plus that shared edge to equal nine. The two
private-side common-neighbour counts of the neutral pair add with no shared
site or root contribution. This sum is at most five.

`audit_panel_headers.cpp` indexes right frames by these measurements and
both physical bijections. A left lookup asks for the complementary neutral
degrees and an interval of admissible right common-neighbour counts. A
multiway merge emits literal `(left,right,flip)` in integer lexicographic
order; equal frame IDs are allowed and no side-exchange quotient is used.
The frame IDs are the line offsets of the round-13 independently inventoried
roster; this round does not replace those inventory or catalogue checks.

- Smaller calibration: all ten 6-regular order-22 graphs, 2,118 oriented
  `K2,2` marks, with 334 planted two-neutral 10/10 decompositions. All 334
  have nonempty physical crossings; direct counting confirms cross stubs.
  Four physical neutral relabelings per plant pass. Over the resulting
  1,336 frame IDs, literal two-map enumeration and the index produce exactly
  the same ordered list of 399,584 headers.
- Target census over 55,055 frame IDs: **157,472,001** headers, 40,301,322
  with flip zero and 117,170,679 with flip one. `[0,2048)` contains
  **4,322,749** (2,100,165 and 2,222,584). The independent census uses 27
  half-open intervals and a separate monolithic stream; no full ID
  manifest is stored.
- Packed convention: zero-based `(left,right,flip,0)`, four unsigned
  little-endian 16-bit words, hashed in order. The first hash is
  `b85ba1c25268e491de9e16e94b40acca81282293452c19482af766e28a34af62`;
  monolithic hash is
  `08b2a3b6f72fae2679a717393fff67fadd2e7e0f4c9f76615c36642a0f92c8a5`.
  Each shard hash binds the roster itself: replacing a missing ID with a
  duplicate cannot be justified by retaining its count.

## First merge and terminal receipts

One bounded replay of C's first scanner recovered the packed stage stream
whose SHA-256 matches C's already-published twin merge
(`7201da7f0a3d5511a7bd92a6bf70e8dfe4f0edafb4516a91af3e8cc6d7b9c7c1`).
This is a replay against that digest, not a second production scheduler.
The independent reader checks each record's ID range, strict order, map
bit and depth, clears the depth word and compares the roster hash to the
independent header census. All 23,100 archived left-triple intersection
IDs and 42,709 archived pilot intersection IDs are present at exactly their
old depths. Nine archived pilot terminal vectors are present and unchanged.

Stages: 4,322,749 header → 1,002,255 forward → 475,368 reciprocal →
475,228 local → 785 panel. The 785 extracted stage-5 IDs equal the
published terminal roster. Converting each terminal's output to canonical
timing-free rows gives identical reason vectors: 174 joint, 3,086 fillings
(486 degree, 0 triangle, 537 codegree, 2,063 independent ten-set, 0 open).
The audit verifies C/scout receipt identity and coverage; it does not run
a third terminal algorithm. Both physical bijections at `(0,14729)` give
a positive witness. Dropping its second row, overwriting the map bit at
constant count, a shard overlap, a right-end ID in the preceding shard,
and missing terminal input all fail. Missing graph/frame inputs and a
truncated frame source fail before any roster bytes are emitted.

## Completed prefix, not a full exclusion

The production driver stopped at its independent-terminal tail gate after
`[22528,24576)` completed. `[0,24576)` is a disjoint 12-shard partition:
67,417,211 confirmed headers → 20,960,185 forward → 8,079,434 reciprocal →
8,076,698 local → 12,594 panel → 3,464 joint → 0 unresolved. All 148,231
joint fillings were rejected (7,584 degree, 0 triangle, 36,245 codegree,
104,402 independent ten-set). Every completed C interval's ordered header
digest and per-map counts agree with the independent census. Both terminal
receipt streams agree on all 12,594 panel IDs; the digest of canonical
timing-free rows across the prefix is
`b41dddffbf00ade7f4c669b9456d5c707deda28c585bd5d2197c81a4bbd935bf`.

The tail is a real resolved ID, `(23155,26938,1)`: 7,059 fillings, all
rejected by independent ten-sets; 3.859940 CPU-s in the scout terminal.
This exceeded the 1-s scout per-ID production gate, not a logical timeout
or a failed receipt. **90,054,790** headers in `[24576,55055)` have independent
census hashes but no completed C production audit. `--require-full`
rejects the present report prefix. Do not claim the full 17/17 block.

## Replay

Run from the project root. The first command rebuilds the independent
packed census; use `text` for the canonical text variant. The second audits
C's completed contiguous prefix (add `--require-full` to require all IDs).
It verifies both terminal files, keyed digest, stage counts and unresolved
inventory in every published shard, and reconstructs terminal dispositions.

```sh
bash ralph/lanes/A/replay_panel_headers.sh
root=$PWD
cd scratch/A/r14
ulimit -v 16777216 -t 120 -c 0
nice -n 5 timeout 120 python3 -B "$root/ralph/lanes/A/audit_panel_receipts.py" \
  headers.packed.shards.tsv ../../C/r14 ../../C/r13 --first-stream first.depths.gz
```

Main outputs: `scratch/A/r14/{headers.packed.shards.tsv,headers.packed.full.tsv,first.depths.gz,receipts.final.log}`.
Run `sha256sum -c ralph/lanes/A/ROUND14_FREEZE.sha256` from the project root
to check the archived inputs and receipts.
The `.gz` file is the first shard only. C owns production under
`scratch/C/r14`; the audit never writes there.

If the first stream needs reconstruction, use the scanner bound in
`ROUND14_INPUTS.sha256` and the same target inputs. From `scratch/A/r14`
with the variables and limits above:

```sh
set -o pipefail
nice -n 5 timeout 120 "$root/scratch/C/r14/scan_C" shard \
  "$root/gluing/val/r3_6_17.g6" "$root/scratch/ideas/r012_R/liftrows.txt" \
  "$root/scratch/ideas/r012_R/frames17-5-2.txt" 0 2048 \
  | nice -n 5 timeout 120 gzip -1 > first.depths.gz.replay
```

The stage digest authenticates the decompressed bytes, independently of
the compression settings. Rename to `.gz` before passing the replay to
the receipt auditor, which selects decompression by suffix.
