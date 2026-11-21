# R(7) independent trace replay

**Status: cert.** The critic accepted the custom branch certificate and hand
reduction in `ralph/critic/round_001.md` (C-004). This is not an LRAT proof of
the SMS base/cubes and does not rely on the historical 464-cube split.

From the root, choose a fresh directory with an existing parent under workspace
`scratch`:

```sh
bash ralph/lanes/A/replay_r7.sh scratch/A/r7-another-replay
```

All output (binary, compiler temporary files, and logs) stays in that new
directory; this refuses a preexisting directory. The preserved inputs are
the four McKay residues in `scratch/A/r7-proof-v1/r38_27_e85.g6`, the four
`R7_full.*.txt` pair lists and four `R7_trace.*.bin` streams in the same
directory. A second argument selects another copy of that input directory.
`R7_INPUTS.sha256` pins these nine files by name, and `R7_CODE.sha256` pins
the checker, front end, and graph checker. No Lane C scratch path, shared SAT
tool, or nauty binary is needed. Requires Bash, GNU C++ (C++20/libstdc++),
Python 3.10+, GNU coreutils, `/usr/bin/time`, and `prlimit` on the current
x86-64 host (POPCNT).

The seed check binds each labelled adjacency matrix to a graph6 line, checks
triangle-free, e=85, α≤7, and uses distinct isomorphism-invariant fingerprints
to establish pairwise nonisomorphism. A vertex signature consists of its
degree and the multiset of `(other degree, common-neighbour count)` across
all vertices; a graph fingerprint is the multiset of these signatures.
Completeness depends on the published class size four (GR Table 13; D-C8e in
`notes/DEPENDENCIES.md`).

## Soundness obligations

1. **Reduction.** Lemma R7 forces the two anchors, common side C, and exclusive
   sides A/B inducing K2,2; X is one of the four e85 graphs. The required
   column totals and A/B side filters follow as in Lane C's
   `ralph/lanes/C/proofs/pair_packing.md`. Unlabelled masks on a side suffice:
   equal X neighborhoods on a false-twin type would give codegree d > cap.
2. **Cover.** `SideCover` independently regenerates fixed-cardinality
   independent masks and enumerates each unordered pair within one side.
   It counts compatible unordered A/B pairs by a binary trie on the unions,
   where a leaf carries the opposite-side demands and their multiplicities.
   A query forces zero on the fixed side's union and one on its demands,
   and rejects a leaf demand not contained in the fixed union. The oriented
   count is twice the desired count: the two nonempty unions are disjoint.
   For each submitted tuple it checks both side packages and compatibility,
   canonicalizes all permutations within and between the sides, rejects
   duplicates, and checks that the number of accepted tuples equals the
   independent count. This does not trust the trace producer's input list.
3. **Replay.** See Lane C's `TRACE.md` for the binary format. An allowed
   C mask is an independent (d−2)-set not yet excluded. Selected masks
   consume capacities for residual degrees and the number disjoint from
   each independent (d−2)-set; they cover missing MTF pairs, and may forbid
   other choices by codegree. At a closed node a degree demand exceeds the
   number of eligible masks containing that vertex, or an MTF pair has no
   eligible mask containing both. At a branch the pivot must be covered
   by at least one eligible mask in any hypothetical extension. Each child
   tries one such mask, while ruling out earlier choices in enumeration
   order. Choosing the first eligible mask present in the hypothetical
   extension proves coverage. No heuristic cut, optional complete-selection
   rejection, or node limit is accepted by the checker. It rejects any
   unconsumed proof bytes and all early EOFs.

## Calibration

- `scratch/A/rc7/audit-control.log`: the known 6-regular (3,7,22)
  K2,2-anchor example's actual attachments belong to the regenerated cover.
- `scratch/A/rc7/audit-negative.log`: fake closure at the planted root rejected.
  `scratch/A/rc7/audit-missing.log`: one valid tuple is rejected as an incomplete cover.
- `scratch/A/rc7/replay-sample.log`: 64 trace roots / 3,641 nodes accepted
  before the full replay. Full logs: `scratch/A/rc7/replay-X{0,1,2,3}.log`.
- End-to-end `scratch/A/rc7/replay-final.log`: 977,008 trees, 49,569,079 nodes;
  approximately 55.5 CPU-seconds and peak RSS about 65 MiB. The new packaged
  replay in `scratch/A/r7-replay-round2` reproduced both counts in 57.6 CPU-s.
