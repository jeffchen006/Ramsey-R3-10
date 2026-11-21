# Lane A state

Round 7 (2026-11-21 to 2026-11-22), share 2. No graph candidate or whole
distribution closure. Replayed the c=3 both-path/leaf subcase in full.
Followed the critic: independently checked G's new path/leaf cover,
sampled the new proof bindings, did not repeat the old residue sweeps or
R(7). No new e120/e121/e122 delta was supplied. Round 1–6 history is in
`LOG.md`; earlier freeze manifests are unchanged.

## Round 7 jobs

All foreground; no live or stopped A jobs. Logs under `scratch/A/path7/`.

| PID | Command / log | Cores | Start | End |
|---:|---|---:|---|---|
| 3788147 | bounded `replay_strip_marks 4 4 3`, `pair27.A.log` | 1 | 23:38:51 | 23:39:08 |
| 3940949 | bounded `filter_strip_supports.py pair27.A.keys`, `supports.full.{log,time}` | 1 | 23:44:10 | 23:46:17 |
| 4157781 | `audit_strip_proofs.py --shard 0 2`, `replay.0.{log,time}` | 1 | Nov 21 23:51:19 | Nov 22 00:00:15, complete |
| 4157799 | `audit_strip_proofs.py --shard 1 2`, `replay.1.{log,time}` | 1 | Nov 21 23:51:19 | Nov 22 00:00:07, complete |

The short calibration, window runs, class normalization and sample
checks also finished. G owns its separate proof jobs.

## Round 7 results / claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| hand | Exact one-centre H26 projection has four independent d7 anchors with four privates each and six distinct doubles; lower alpha rechecked for upper marks. Exact pair cover at c=3 by independent 7-set plus cross-endpoint construction. | `PAIRED_WINDOWS.md` | — |
| enum / open | Positive and negative alpha/mark controls pass; checked mark at n26 e82, so the weakened cap82 standalone window does not suffice. No supplied e73/e74 marks; e74 incomplete. Cap74 and cap78 hit CPU limits. | `scratch/A/path7/{calibrate.log,n12.log,n22.log,e82.model.log,e73.tsv,e74.tsv,e74.time,e78.time}` | ~0.010 |
| enum, cover only | Independently canonicalize both class sources (477,142 distinct), reproduce 1,988 exact paired keys/1,980 classes, reject omitted and duplicated receipts; smaller n8 agreement 21 marks, 10/410 positive rows. | `PAIRED_WINDOWS.md`, `scratch/A/path7/{lineage27.log,pair27.A.log,pair27.A.keys,control8.A.log}` | 0.006 |
| hand + enum, necessary prefilter | Full exact c=3 support-only filter leaves 633/1,988 for `(2,7,4,27)` and 591 for `(2,8,2,28)`, union 633. Checks all cross contacts, potential MTF, degree ranges/edge identity, Hall on forced-independent cliques. Positive C7 controls and two negatives pass. No c=1,2 or mixed roles. | `filter_strip_supports.py`, `PAIRED_WINDOWS.md`, `scratch/A/path7/{supports.full.log,support-survivor.keys}` | 0.032 final |
| cert, pending critic | The 1,988 terminal receipts join one-to-one to the exact cover. Every independently reconstructed fixed-edge map and rebuilt CNF digest matches. Both LRAT checkers accepted all 1,988; crossed, incomplete and duplicate controls fail. Scope: e168, c=3, both path/leaf on the two low-n8 pins only. | `audit_strip_proofs.py`, `PAIRED_WINDOWS.md`, `scratch/A/path7/{proof-receipts.tsv,replay.0.log,replay.1.log,freeze.sha256}` | 0.1604 full |

## Next

- c=3 proof campaign is terminal and fully replayed; no repeat proof
  production or replay unless hashes or binding change. H/critic can
  record only the both-path/leaf c=3 split, not a distribution cut.
- For c=1,2 bind G's new low-degree source or obstruction only at its
  covered scope. Any broader move needs its own complete source.
  Keep mixed-role windows separate.
- If new e120/e121/e122 rows appear, bind only their deltas; use
  `inspect-upper` to replay lower alpha after deleting marked edges.
  Keep future e169-pinned and unpinned proofs separate. No repeated
  full-catalogue inverse scan or old proof production.
