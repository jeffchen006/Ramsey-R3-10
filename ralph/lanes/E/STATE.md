# Lane E state — round 3

2026-11-21; share 18 cores, peak 15 one-core foreground jobs. All
results are for all graphs, not only MTF. No order-40 candidate or
Ramsey verdict. Historic round results and job details: `LOG.md`.

## Jobs

No detached jobs this round or left over. All bounded batches are
collected. Listed PIDs were foreground wrappers, not reusable handles.
All solver/checker commands ran in `scratch/E` under `limited.sh`,
`nice -n 5`, wall timeout and CPU cap (16 GiB virtual memory).

| Batch (one core per PID) | Local start; cap | Log/result |
|---|---|---|
| `crown_exact ... local ... 4 4 4 4`, PIDs 1055712/1055714/1055717 | 18:54; 20 CPU / 40 wall s | `crown_w6.*.local.pilot.log`: 3/3 exhausted, total 0.54 CPU s |
| W6 sorted certificates; W7/W8 static certificates, peak 15 | 18:56–18:57; 25 CPU s/stage | `crown_cert/w[678].*.log`: all 27 passed |
| `crown_exact ... full ... 3 4 4 4 4 4`, PIDs 1405129/1405140/1405158 | 18:58; 65 CPU / 100 wall s | `crown_w5.*.full.pilot.log`: 3/3 exhausted, 4.95 CPU s; preceding 5-full projected controls had 3 models |
| W5 nine full proof chains, PIDs 1529565–1529624; six simultaneous W4 pilots, PIDs 1529533–1529560 | 19:00; W4 pilot 35 CPU / 55 wall s | `crown_cert/w5.*.log`: 9/9 passed. `crown_w4.*.full.pilot.log`: 2 exhausted, 4 CPU-killed, not UNSAT |
| W4 anchor residual, PIDs 1629917–1629937 | 19:02; 30 CPU / 50 wall s | `crown_w4.*.anchor.pilot.log`: five projected models (not candidates), star excluded |
| W4 clean-group checks, PIDs 1699357–1699433 | 19:03; 65 CPU / 100 wall s | `crown_cert/w4.*.tight.log`: five exhausted, C4 CPU-killed |
| C4 anchor-sort + short pair seed pilot | 19:05; 95 CPU / 135 wall cap | `crown_cert/w4.6.strong.log`: 6 calls, 2.04 CPU s |
| W4 cold proofs, PIDs 1785258/1785264/1785269/1785281/1785292/1854133 | 19:04–19:06; 75 CPU s solve and 50 CPU s/check | `crown_cert/w4.*.log`: all 6 passed, worst solve 47.60 CPU s, worst DRAT check 48.45 CPU s |
| Retained CNF regeneration + LRAT replay, four parallel, and SHA-256 checks | 19:07; verification-only | `crown_cert/w*.regen.log` 42/42; `crown_cert/hashcheck.log`; `slim5_round3_hashcheck.log` all pass |

## Claims and results for H/critic

| Claim/result | Label | Evidence | Core-hours (decisive computations) |
|---|---|---|---:|
| Complete exclusion of `(2,28,a=4)` across every `W=4..8`; no MTF or minimum-degree-five dependency. 42 core CNFs, all DRAT+LRAT verified, all independently regenerated and LRAT replayed. | cert | `ralph/lanes/E/crown28_exact.md`, `ralph/lanes/E/replay_crown28.sh`, `scratch/E/crown_cert/{SHA256SUMS,census.log,w*.log}` | 0.111 |
| W4 crown clean-group lemma: `d_F(W)≤8` and at least `max(0,2e(W)−2)` clean attachments; each clean attachment is perfectly matched to `W`. Preserves a canonical label cover. | hand | `ralph/lanes/E/crown28_exact.md` | — |
| Order-three `a=4`: pairwise footprint/degree CSP leaves 25/64 fixed-mask layouts at `f=7`, 116/144 at `f=10`, every template survives. At `f=7`, `S:1111` and `D:111` each have the single mask multiset `(1,2,3,4,8,12)` remaining up to relabeling. This is a necessary test only. | enum (filter), cases open by this method | `ralph/lanes/E/order3_a4_pairs.md`, `scratch/E/order3_a4_pairs.full.log` | 0.0006 |
| `(5,5)` prior four proof packages remain intact; all retained hashes rechecked, not a new proof run. Keeps prior universal `δ≥5` dependency. | cert (round 1) | `ralph/lanes/E/slim5.md`, `scratch/E/slim5_round3_hashcheck.log` | 0.0006 |

## Lessons and next steps

- Notify H/critic to independently review the complete `(2,28,a=4)`
  scope. F can skip this branch. Do not claim all `f=28`: `a=6` is
  distinct and remains open. Previously `(2,28,a≤3)` and `a=5` had hand
  exclusions, and `a=7` was outside the open cover via Lemma 5.3.
- For `(2,28,a=6)`, the complete-crown premise fails. Compare a quotient
  obstruction: two unjoined independent pairs have fixed attachment
  union at least 11, and three pairwise unjoined independent pairs
  violate `R(3,4)=9` since at least ten fixed vertices avoid them.
  Handle internal edge pairs separately; no new closure claimed.
- `(2,32,t=2,3,4)` and smaller `(2,30)` windows were not touched this
  round, as directed. Retain the all-graphs scope; use pinned censuses
  before extending crown formulas. The `(2,32)` t=1 route retains
  its distinct all-graphs minimum-degree-five premise.
- For order three, test at least three outside orbits jointly before
  scaling. Pair-optimal offsets can form triangles with a third orbit;
  record exact layout scope. `(5,0)` and original open order-three
  `a=2/3` remain open; don't rescale prior capped SAT unchanged.
