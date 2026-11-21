# R(7) independent trace replay

Status: independent branch-certificate replay; acceptance of the checker and
hand reduction as `cert` is for the critic. This is not an LRAT proof of the
SMS base/cubes, and does not rely on the historical 464-cube split.

Run `bash ralph/lanes/A/replay_r7.sh` from the root. Inputs are the four McKay
residues in `scratch/A/rc7/r38_27_e85.g6` and Lane C's
`scratch/C/R7_full.{0,1,2,3}.txt`, `scratch/C/R7_trace.{0,1,2,3}.bin`.
Checks bind each proof input to the labelled adjacency matrix of the
corresponding graph6 line, verify four distinct triangle-free e85 graphs
of independence number at most 7, and replay the traces. The fact that the
class has size four is the previously cited table fact in the report.

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
  approximately 55.5 CPU-seconds and peak RSS about 65 MiB. The artifact
  digests (including all four proofs and side files) are in `R7_INPUTS.sha256`.
