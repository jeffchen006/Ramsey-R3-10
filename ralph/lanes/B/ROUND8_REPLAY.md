# Lane B, round 8 replay — November 22, 2026

Run from `scratch/B` with `ulimit -v 16777216`, `LC_ALL=C` and
`PYTHONDONTWRITEBYTECODE=1`. Command paths below are relative to that
directory. `ROUND8_E108.sha256` is relative to the workspace root.

## e108 scout import (enum, partial census)

`timeout 3m bash ../../ralph/lanes/B/src/import_e108_r8.sh work/e108_r8_import.replay`
preserves the original 2,102,885-key baseline. It checks the frozen scout
file's SHA-256, direct validity (order 32, e108, triangle-free, no I9), and
all 123,336 edge-deletion witnesses using both `irreducible` and the
independent `critical_witness.py` generator/checker. It checks that the old
baseline's set difference from the reducible partition is exactly the 614
old proof inputs, once those are converted to the baseline's canon form.
The 1,142 scout keys have empty intersection with the old baseline; Traces
independently confirms the combined 1,756 critical classes are distinct.
Thus 2,102,271 reducible + 1,756 critical = **2,104,027 of 2,104,151**, leaving
**124 missing**. Import evidence: `logs/e108_r8_import.log`, 21.94 CPU-s.

## Dispersed host pilot (enum / estimate)

`timeout 6m bash ../../ralph/lanes/B/src/e108_hosts_r8.sh work/e108_r8_hosts.replay 128`
reuses the scout's sorted edge-deletion DFS after rechecking exact recovery
of the published single order-7/e6 (3,4) class from three order-8 hosts.
The pilot canonicalizes each order-33 source, subtracts the scout's sampled
33-host sets, and takes 128 mid-quantile indices from each remaining family.
It drops each host vertex, explores all valid sorted edge-deletion chains
to e108 within each card, and keeps only edge-critical leaves. This is
exact for the sampled cards, not for all e108 inputs.

| Host family | Unseen pool | Sample | Unique critical outputs | Novel vs imported union |
|---|---:|---:|---:|---:|
| G e120 frozen | 1,223 | 128 | 77 | 0 |
| G e121 frozen | 12,797 | 128 | 103 | 0 |
| G e122 latest | 89,932 | 128 | 121 | 0 |
| G e123 up from critical e122 | 32,140 | 128 | 98 | 0 |

Cards are counted separately by family in `logs/e108_r8_hosts.log`:
4,224 in each, **16,896** total. The pilot including controls and setup used
2.48 CPU-s, of which about 0.70 s was descent. The measured novel yield is
**0 keys/CPU-h**. No exchange wave starts from this empty delta; no scale-up.

## Scout tranche proofs (cert, supplied 1,142 keys only)

`timeout 4m bash ../../ralph/lanes/B/src/e108_scout_proofs_r8.sh replay work/e108_r8_scout_proofs`
binds the separately imported tranche to 761 independently checked
eight-demand cliques and 381 regenerated pinned/unpinned CNFs with LRATs
accepted by both `lrat-check` and `cake_lpr`. Production used 291 one-line
RUPs and 90 CaDiCaL LRATs; 368 of the 381 inputs have seven-demand pins.
The verifier requires exact equality of the clique complement against the
381 indexed inputs, checks the pins as in `FLOOR7_108.md`, regenerates each
CNF, and matches the input index, CNF digest and proof digest to production.
The replay also checks exact per-index proof coverage. Production's first
replay setup encountered an EXDEV hard-link error, after all production
LRATs had been written and checked. `finish` with a copy into a private
replay directory completed the checks. Logs: `logs/e108_r8_scout_proofs.log`
and `logs/e108_r8_scout_replay.log`; production plus replay used 53.40 CPU-s.

Scope: these 1,142 *specified* residues cannot be dual neighbourhoods of
a degree-seven vertex in an MTF (3,10,40)-graph. No t8/t9 floors or global
distribution premise. The old 614-certificate bundle is unmodified. This
does **not** establish floor 109 or exclude any new degree distribution.

## e88 prefix replay

`src/replay_prefix_generation_r8.sh prepare` independently extracts the
three ordered seed sets, checks the exact chunk indices, counts and logs,
and stream-merges the canonical chunk outputs. Its control regenerates
the known order-16 (3,7) levels 20/21/22 as 2/15/201, matching the prior
canonical set exactly (six chunks with three degrees, 0.92 CPU-s). The
control verifies all input digests and rejects a two-record reorder.
The prefix worker was started before digests were added: the initial
strict audit stopped on the first absent digest. None of the 3,886 legacy
generation chunks has such a digest, so this is a full count/output-union
audit, **not** a retrospective digest binding of each generation chunk.
`src/replay_prefix_sample_r8.sh` regenerated d5/0, d6/1423 and the entire
21-host d7/e42 branch from freshly extracted seeds: all three canonical
outputs agree byte-for-byte (371.76 CPU-s). See `logs/prefix_r8_generation_*`.

The independent merge took 53.55 CPU-s (58.95 wall s) for 49,067,554
canonical chunk records. This measures aggregation only, not a faster
gluer. The merge matches `val/r39_30_le88_mixed_prefix.g6` byte-for-byte.
Levels 86 and 87 match the checkpoint byte-for-byte (1,800 and 147,335).
The partial e88 prefix has **5,873,187** keys: 5,719,575 reducible and
**153,612 critical**. The full reducible census has exactly one key outside
the prefix, covered by the round-6 scan. Direct validity and all 13,517,856
critical edge deletions were checked on the new partition. Evidence:
`logs/prefix_r8_{supervisor_lower,independent_lower,independent_partition}.log`.

`src/sat_prefix_r8.sh` finds the positive C35 control and independently
rejects 24/24 fixed-seed sampled critical keys (6.90 CPU-s; see
`logs/prefix_r8_sat_sample.log`). This SAT sample is enum, not LRAT and
not a full-prefix rejection.

### Terminal result (enum, prefix only)

PID 1180084 completed at approximately 01:06 CET with exit status 0.
The MTF scan produced zero outputs on all 5,873,187 e88 prefix inputs
in 5,736 chunks (6,552.95 gluer CPU-s, about 1.82 CPU-h). Unlike the
legacy generation logs, these scan logs have ordered input SHA-256
digests. Replay `timeout 5m bash ../../ralph/lanes/B/src/replay_prefix_r7.sh terminal`.
It freshly extracts e88, verifies the exact scan input file and all
ordered digests/counts/empty outputs, then independently reconstructs
the reducible/critical partition. Both files match the independent
merge's e88 and critical subsets (including the SAT sample population).
See `logs/prefix_r8_terminal.log` and `ralph/lanes/B/ROUND8_PREFIX.sha256`.

The union of independently scanned prefix and deletion-reducible keys
has 5,873,188 distinct classes, **not** the full e88 census. The outside
d7/e43 lift remains empty; the uncovered critical complement still needs
the d6/e52 or d7/e44 branch. No t9 floor 89, U88 key, distribution, or
Ramsey verdict follows from this result.
