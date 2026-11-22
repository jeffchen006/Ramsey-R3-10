# Conditional mixed core 1: exact terminal roster

Round 19, 2026-11-22 CET. **Core 1 is still open.** This is the zero-based
core `G?bFbo` in `scratch/E/r5_saturated/e11.g6`: `(p,f,t)=(2,32,4)`,
`δ(W)≥2`, `e(W)=11`, mixed profile `(10,10,11,11)`, universal `δ(G)≥5`,
and the all-graph E-021 assumption that each of the four `F\A_i` windows
belongs to the sole missing order-26/e74 class. No MTF assumption. The
pipeline covers all four omission roles and degree-count branches
`K=6,7,8`; it can stop for a lift as soon as one valid obstruction is
replayed. No other mixed core was worked, and no target proof was run.

## Full scan and replay (enum)

`scratch/E/r19_shared/branches.tsv` assigns the 24 already independently
regenerated branches to 12 contiguous, disjoint two-branch shards. Each
plan entry binds its half-open projection and cumulative lift intervals.
Preparation checked the inherited freeze, the raw cover hash, branch
labels and counts. Scanning uses the round-18 native graph-witness
checker in the same fused-first path; separate workers replay every
receipt with the unchanged Python graph-witness checker and literal
rooted-window compatibility test. Fused verdicts are recomputed by the
existing fusion routine, not treated as SAT proof logs. The ordered
merge rechecks each branch against the frozen cover, every local lift
ID and global projection order. Positive C13 and six-site controls passed;
misbound branch/formula, dropped/duplicated/reordered lifts and wrong
fresh-proof IDs were rejected. All 3,385 pilot projections and their
12,814 receipts match byte-for-byte after translating local IDs. An
independent text check matches the merged open-ID extraction and set
difference with the old checked proof roster.

| Receipt disposition | Physical lifts |
|---|---:|
| Projection graph obstruction | 340,949 |
| Lift graph obstruction | 202,928 |
| Fused obstruction | 19,090 |
| Incompatible marked windows | 2,417 |
| Terminal | 147 |
| Total (68,323 projections) | 565,531 |

The frozen terminal roster spans 113 projections in 14 first branches;
75 IDs are in branch 6 and 20 in branch 13. All 24 round-18 pilot IDs
are present. E-042's 16 checked IDs each have two proof routes, but
count only once. Remaining: **131 distinct IDs** in 103 projections.
See `terminal.1.jsonl` and `pending.1.jsonl` in the round staging area.

Measured wrapper cost was **139.44 CPU-s scan + 175.54 CPU-s replay**
against 219.12 + 299.95 estimated. The estimates overshot in aggregate;
the scan estimate was exceeded in six branches and Python replay in two
(both branches 8 and 9). `branch_rates.tsv` and `final.audit.fixed.log`
give the complete per-branch comparison. All ten jobs were collected,
with no killed, stopped or detached process. The first supplemental
count audit had a wrong hardcoded byte total; the rerun compared
against actual `wc -c` and passed. Total measured wrapper cost including
controls, pricing and both count audit attempts: **321.01 CPU-s
(0.08917 core-h)**; **48.14 MiB** of new logical staging retained.

## Proof prices (estimate, no new proofs)

`price.strata.tsv` weights round-18 paired route measurements by exact
pending counts in each branch and projection third. For 29 pending IDs
there is a paired sample in the same branch and third, for 48 only in
the same branch, and for 54 the estimate uses the pooled sample. The
per-ID estimate includes route encoding/binding and solver/checker
CPU; common fresh-rebind and startup costs are allocated evenly.

| Pricing scenario for 131 pending | CPU-s | Retained MiB |
|---|---:|---:|
| Narrow-first, no fallbacks | 114.88 | 148.43 |
| Original wide-only | 221.70 | 138.87 |
| Narrow-first, 7 charged fallbacks | 387.06 | 156.62 |
| Narrow-first, 27 charged fallbacks | 1,164.70 | 180.02 |

A charged fallback adds the sampled maximum wide-route CPU estimate
plus a 7 s narrow solve and three 10 s checker allowances; retention
adds the maximum observed wide artifact cost. No target pilot had a
fallback. These are sensitivity estimates, not runtime or disk bounds.
As a separate planning allowance, three times both route baselines is
1,009.73 CPU-s, and twice the measured maximum paired bytes per ID
times 131 is 616 MiB; this allowance does not cover arbitrarily hard
retries. The last column of `price.strata.tsv` is wide retained bytes.

**Request next round:** permission for at most the frozen 16 new
matched IDs in `proposed_pilot.1.jsonl` only (two workers, ≤0.08 core-h,
≤96 MiB new scratch). Prioritise underrepresented strata. Stop on
binding mismatch, wide SAT, unsuccessful wide replay or resource cap;
report a narrow incomplete result separately if a wide fallback is
attempted. If authorized, check independently rebound formulas before
credit, then reprice the unresolved remainder. No bulk proof run, no
core exclusion and no debit against `(2,32)` or the Ramsey frontier.

Evidence: `scratch/E/r19_shared/freeze.1.sha256` (94 entries),
`finish.log`, `final.audit.fixed.log`, `pricing.log` and `{jobs,exits}.tsv`
in that staging folder. The narrow/wide proofs are inherited from
`scratch/E/r18_shared/freeze.1.sha256`, not new round-19 artifacts.
