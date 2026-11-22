# Lane A state

Round 10, November 22, 2026. Share 5; no live or stopped A jobs.
No order-40 candidate, whole-distribution exclusion, or Case R closure.
Current evidence: `ROUND10_REPLAY.md`, `scratch/A/strip10/round10.freeze.sha256`.
Rounds 1–9 history: `LOG.md` and the round replay files.

## Jobs

| PID | Command | Log | Cores | Start / expected end |
|---|---|---|---:|---|
| — | No detached A jobs | — | 0 | — |

All one-core foreground scans, controls and hash binding complete.
Round-9 detached PIDs `634622/634629`, `634623/634630`, and
`634624/634631` are gone; their logs remain under `scratch/A/strip9`.
No A solver or proof-checker run. G owns the separate proof jobs.

## Results and claims

| Label | Scope/result | Evidence | A CPU-h |
|---|---|---|---:|
| hand + enum, no closure | At mixed e168 `(2,7,4,27)` only, table for **noncross** B pivots, both shapes/orientations. Exact B anchor identity and simultaneous anchor selector. C13 52 windows; 264 geometric positives and occupied-hole negatives; literal addback control has 30 vs zero joint assignments. On 260 sampled high-minimum marks, d8 j3 retains 966/1,096 roles but every one of 223 eligible marks; d9 j4 retains 125/125 roles. Exact low-min d9 j4 also retains 215/215. No scale recommendation. | `mixed_selector.py`, `ROUND10_REPLAY.md`, `scratch/A/strip10/{table.log,c13.control.log,direct.log,heldout.log,heldout.markcounts.log,exact26.9.log}` | ~0.002 |
| hand + enum | Inherited complete weak sources and independent labelled roles: n25 δ2/d8 j2 90,514; n25 δ2/d9 j3 6,131; n26 δ3/d9 j4 215. All 96,860 IDs exactly match G; also reproduce old 7,166, 5,179 and 162. Scope neither all δ nor all degree distributions. | `scratch/A/strip10/{source.agreement.log,roles.25.8.edge.keys,roles.25.9.edge.keys,roles.26.9.edge.keys}` | ~0.014 |
| hand + enum + cert, pending critic | G's new scoped terminal result: same mixed pin, **noncross d9 B pivot at j=4 and δ(T)=3** only. 215 unique dual-LRAT receipts (50 matching, 165 middle); A independently binds all IDs, pin maps, eager tails, CNF and trace hashes. No A proof replay. | `audit_residual_binding.py`, `scratch/A/strip10/binding26.log`, `scratch/G/round10/r26.d9.bound/certificates.tsv` | 0.007 |

## Next

- Critic/H: record the new 215-role exclusion only at the named scope.
  In particular, d9 j4 with δ(T)≥4 and all crossed pivots remain open.
- G owns lower-minimum proof production. Join and audit its terminal
  d9 j3/δ2 or d8 j2/δ2 **middle-only** scope if available; do not infer
  anything for a capped or unattempted role or the matching d8 branch.
- No scale-up of A's anchor-only screen or the high-minimum sample.
  It removes roles but no marks in the sample, and doesn't force any
  pivot of high codegree. Leave the pure caps at δ≥4 and two-root
  census stopped. Need a new structural filter for full high minima.
- R(7) was not reopened under the critic's mixed-strip directive.
