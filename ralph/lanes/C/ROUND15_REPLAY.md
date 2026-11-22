# Round 15 — marked cap-five `K4,4` with two neutral vertices

**Result (`hand + enum`, pending critic): no cap-five 9-regular
40-vertex target can have a `K4,4` with two neutral vertices (order
17/17).** Thus any `K4,4` in such a target dominates all but at most one
vertex. This excludes neither all cap-five `K4,4` marks nor R(5).
The structural margin is that the two antineighbourhoods have size
at most 17, and their union has size 32. Their intersection has size
two exactly when both orders are 17 (`proofs/panel17_census.md`).
The pair can use two copies of the same frame. Do not collapse the
two neutral-map bits or require a diagonal crossing matrix to be symmetric.

## Mathematical and computational paths

- `proofs/panel17_census.md` and `proofs/reciprocal_panel17.md` prove the
  frame, header, local, panel and terminal cover. The seven complete
  order-17 `(3,6)` classes are a published dependency (D-G3).
- Lane A's `../A/ROUND15_EXCHANGE.md` gives a physical permutation
  exchanging shores at fixed neutral map bit. Lane A binds the old
  ordered receipts, tests both planted orientations, and checks exact
  swap membership of the full independent header roster, including
  rejected input mutations. Only the existence of a physical completion
  is transferred, not scanner depths, terminal reasons or run times.
- From the frozen round-14 sources, `panel17_triangle_C.cpp` skips
  right IDs strictly below the current left in its ordered header
  bucket; `panel17_triangle_A.cpp` instead begins raw right-ID scans at
  the left ID. Both still test both bits. Every direct shard's stage
  stream is compared byte by byte and its normalized roster digest and
  bit counts checked against A's independently reconstructed census.
  The original C++ terminal is unchanged. The separate Python terminal
  retains the scout's literal package domain and join, with exact
  independent-set witness reuse proved in `proofs/panel17_cache.md`.
  Both enumerate and compare full terminal reason vectors for every
  direct panel ID. No terminal disposition or rejection is sampled.

## Calibration and gates

In `scratch/C/r15/price`, the six fixed old expensive IDs agree per
reason and all 785 old easy-shard panel vectors match. The smaller
checks retain 2,118 `(3,7,22)` positive partial instances, 3,278 exact
regular graph instances (not distinct graph classes), and reject one
inconsistent fixed edge per partial instance. The separately compiled
panel test retains 3,448 true rectangles and rejects all 31,032
one-entry mutations. Roster calibration regenerates the 366 smaller
atlas entries and tests a nonempty repeated-row package.

| Key | Old Python ms | Round-15 Python ms | Fills |
|---|---:|---:|---:|
| `22778 40124 1` | 1070.876 | 433.689 | 1224 |
| `22778 44562 1` | 1071.947 | 417.673 | 1224 |
| `23155 23155 1` | 3149.392 | 2149.802 | 7059 |
| `23155 24435 1` | 1662.585 | 763.644 | 2122 |
| `23155 26567 1` | 1659.915 | 759.889 | 2122 |
| `23155 26938 1` | 3859.940 | 2131.898 | 7059 |

All 20,810 tail fills reject by independent ten-set. No single witness
was found in any of the six package-union upper graphs. Within fillings,
checking cached concrete witnesses replaced 20,797 fresh searches, with
13 searches left; the whole per-ID runtime improves by much less, since
the reason-priority checks and package enumeration are unchanged. The
scanned terminal-call reduction below means `local/panel`, not an
end-to-end runtime ratio.

Before scanning, the new per-ID gates were fixed at **180 ms C++ /
7,000 ms Python CPU**, 300 aggregate CPU-s per shard, 7,200 CPU-s total
including a 120 s setup allowance, under 1 GiB retained. No new shard on
a live/disagreeing terminal result or an expensive tail. Each stage
uses at most two scanner/terminal workers; the comparison controller
also uses a small amount of CPU. Per-process VM cap 16 GiB. The first
shard `[24576,25600)` had 2,647,995 representatives (541 diagonal),
376,236 local → 722 panel → 244 joint → 0 unresolved, ratio 521×.
Its 12,175 filling dispositions agree. First shard cost 29.516 CPU-s,
maximum Python ID 883.647 ms, projected end 1,034.821 CPU-s with a 3×
reserve (largest normalized prior/new cost times remaining headers).

## Completed coverage

| Domain | Physically screened | Covered by exchange | Unresolved |
|---|---:|---:|---:|
| Low/low | 27,198,813 | 0 | 0 |
| Low/high | 40,218,398 | 0 | 0 |
| High/low | 0 | 40,218,398 | 0 |
| High/high | 24,924,719 | 24,911,673 | 0 |
| **Total ordered** | **92,341,930** | **65,130,071** | **0** |

All 30 HH shards completed. The 24,924,719 representatives include
13,046 diagonal IDs: 2,982 bit zero and 10,064 bit one. HH direct
stage counts were 9,005,045 forward → 3,621,977 reciprocal →
3,620,522 local → 6,027 panel, a terminal-call reduction of 601×.
Exactly 1,617 panel IDs had at least one joint filling. Both terminals
agree on **74,632 fillings**: 2,876 degree, 0 triangle, 11,940 codegree,
59,816 independent-ten-set, 0 live. Together with the old prefix, this
is 18,621 direct panel IDs and 222,863 matched fillings across 5,081
direct IDs. No counts of fillings or screen depths are inferred for
orientations covered by exchange.

The HH terminal SHA-256 over all ordered `left right bit degree triangle
codegree I10 open\n` lines is
`bf5587676c1e8f9d473f2411eca08afe105183cd49e4c7d10e4edf41b43c8ecd`.
Both coverage audits accept the full partition: `scratch/C/r15/audit.log`
and `scratch/A/r15/{receipts.final.log,coverage.final.tsv}`. The C audit
rejects a stopped snapshot in full mode. The clean first-shard replay
matches all non-timing receipt fields, panel IDs and terminal lines.
HH production used 270.204 CPU-s (138.522 screening); the scheduler
charged 390.415 CPU-s with setup allowance. Highest direct per-ID
cost was 79.963 ms C++ / 2,123.519 ms Python. Retention was about 3 MiB
including first replay; no workers remain. `ROUND15_{INPUTS,RESULTS}.sha256`
bind the evidence used to infer the marked-case exclusion.

## Replay

From the repo root, use
`bash ralph/lanes/C/replay_panel17_r15.sh OWNED_EMPTY_WORKDIR scratch/A/r15/census.tsv first`
for build, smaller controls, tail and easy repricing and first-shard
replay; replace `first` with `full` for all high/high representatives.
The round-14 ordered prefix is not rescanned by the script; use
`ROUND14_REPLAY.md` to check that receipt. The independent A census
rebuild uses `../A/ROUND15_EXCHANGE.md`. Fast coverage check from root:
`python3 -B ralph/lanes/C/audit_panel17_r15.py scratch/C/r15 --require-full`.
Full mode rejects any absent representative shard. A prefix-only run
can be reported by omitting `--require-full`.
