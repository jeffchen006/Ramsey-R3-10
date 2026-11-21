# Lane C — round 4, 2026-11-21

**Open:** R(3,10), Case R and R(6). No candidate. In R(6), J is the
graph of codegree-six pairs. P3/P4 means consecutive distinct roots
in J, not an induced path of G. Prior critic accepted no-P4, so J
has only components of order one, two or three. P2 below always means
an *isolated edge component*, never an incident edge of a P3.

## Results and claims for H / critic

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| cert, accepted rounds 1/3 | R(7) excluded; no P4 in R(6); diagonal-five P3 has e(X)<=63. P5 and C8 enumeration are now redundant; do not rerun them. | `ralph/critic/round_001.md`, `ralph/critic/round_003.md`, `P4_REPLAY.md`, `P3_REPLAY.md`, `ROUND3_REPLAY.sha256` | prior |
| cert, composite pending critic | **P3 diagonal five e63 excluded:** 13 ordered boundary orbits, 8 under reversal, times all 60 22-vertex/e63 residues. All 480 checked CakeLPR proofs and byte-identical regenerated CNF/proof hashes on full replay, zero caps. Gives e(X)<=62 with prior accepted result. | `ROUND4_REPLAY.md`, `proofs/p3_e63_relaxation.md`, `scratch/C/p3e63-final-index.log`, `ROUND4_REPLAY.sha256` | 0.587 produce + 0.284 replay |
| cert, composite pending critic | **P3 diagonals three and four e65/e66 excluded:** each covers all 35 residue keys with a guarded variable-boundary CNF. All 70 matched regenerated hashes and replayed. Thus e(X)<=64 at these two diagonals, not e(X)<=63. | `ROUND4_REPLAY.md`, `proofs/p3_e63_relaxation.md`, `scratch/C/p3r4-upper-index.log` | 0.118 + 0.075 |
| hand | **Isolated P2** e81 residue has minimum degree >=4. At e80 at most **one** degree-three vertex (supersedes earlier general counting bound of five); all degree-three vertices share the missing-edge wing neighbour, while any two nonadjacent degree-three vertices of the 26-residue contradict R(3,6)=18. C22 controls: 7 complete and 4 one-missing. | `proofs/isolated_pair.md`, `scratch/C/p2isolated-control.log` | <0.001 |
| cert, composite pending critic | **Isolated P2 e80, with a degree-three anchor:** 22-residue X' has e(X')<=65 by hand; all-three-same-wing equality boundary has fixed codegree seven, and all 25 residues of the 2+1 boundary checked and replayed. Gives e(X')<=64, not an exclusion of e80. C21 checks 444 anchors, 23 exact equality boundaries and full SAT/corruption controls. | `proofs/isolated_pair_anchor.md`, `scratch/C/p2anchor-e65-index.log`, `scratch/C/p2anchor-control.log` | 0.024 + 0.012 |
| hand + enum cover | At diagonal five a P3 cannot have both incident cross-edge counts >=8; at diagonal four they cannot both equal nine. Under reviewed e(X)<=64 at diagonal three, the f*=9 P3 branch has exactly two boundary layouts and 119 residue/layout tests unrun. For min f>=8, counts by e(X)=61..64 are 1/4/11/22 at diagonal three, 0/4/6/5 at diagonal four, no diagonal five. Counts are covers only; no claim for isolated edges. | `proofs/high_f_paths.md`, `scratch/C/p3-high-f-layouts.log` | <0.001 |
| enum / estimate | Lite6 e63 matched 8/8 at 4.71 CPU-s each versus 39.12 for Min6; matched full baseline/root-twins plain refuted 16/16 each in 429/390 CPU-s. e62 fixed pilot 12/12, 6.11 CPU-s/key; full-selector table 1/2 checked, one cap. Flexible guarded s=3/4 capped on every tested e63/62/61/60 row; e64 passed 4/4 for each at ~11–13 CPU-s. Five fixed e61/e60 keys checked each in 56.56/80.50 CPU-s. | `ROUND4_REPLAY.md`, `scratch/C/p3e63-minpilot-*.log`, `scratch/C/p3low-pilot-*.log`, `scratch/C/p3extra-*.log` | sample |
| open; checked partial coverage | Diagonal-five P3 e62: 90 ordered -> 49 reversal orbits -> 44 passing, independent C++/Python boundary audit; 30 x 44 = 1,320 tests. At 20:32:40 CET 702 checked (690 production +12 pilot), 543 replays, no caps observed, 618 absent. Do not close until exact full replay index passes. | `scratch/C/p3r4-boundary-index.log`, `scratch/C/p3e62-active-index.log`, `ROUND4_REPLAY.md` | 1.24 prod + 0.42 replay at snapshot |

## Live jobs — all in `scratch/C`, one core and 16 GB limit each

| Wrapper PID | Command template (shard argument) | Log | Started CET | Expected end / wall cap CET |
|---:|---|---|---|---|
| 1345478 | `p3_low_trials.py --mode fixed --prove --seconds 45`, e62 residue shard 0 | `p3e62-full-0.log` | 20:13:13 | ~20:48–20:55 / 21:13:13 |
| 1345482 | same, shard 1 | `p3e62-full-1.log` | 20:13:13 | ~20:48–20:55 / 21:13:13 |
| 1345489 | same, shard 2 | `p3e62-full-2.log` | 20:13:13 | ~20:47–20:54 / 21:13:13 |
| 1345498 | same, shard 3 | `p3e62-full-3.log` | 20:13:13 | ~20:47–20:54 / 21:13:13 |
| 1752307 | `replay_p3_e62_shard.sh 0` | `p3e62-replay-0.log` | 20:20:28 | ~20:51–20:58 / 21:17:08 |
| 1752313 | `replay_p3_e62_shard.sh 1` | `p3e62-replay-1.log` | 20:20:28 | ~20:51–20:58 / 21:17:08 |
| 1810068 | `replay_p3_e62_shard.sh 2` | `p3e62-replay-2.log` | 20:21:36 | ~20:50–20:57 / 21:18:16 |
| 1946269 | P2 replay phase ended; `replay_p3_e62_shard.sh 3` | `p3e62-replay-3.log` | 20:24:09 | ~20:50–20:57 / 21:20:49 |

Production skips six already-proved layout keys on each of seeds 17
and 118; replay includes the pilots. Checker cap 165s/key. Replay waits
for full producer `TERMINAL` for each seed; a capped row is logged as
`REPLAY-SKIP` and remains open. Prelaunch estimate: 1,308 remaining keys
x 6.11 CPU-s = 7,992 CPU-s at 4 cores (~33 min ideal), ~17 GB LRAT;
headroom 8s/key = 2.91 CPU-h / 22 GB. Verification ~3 CPU-s/key streams
behind production. Job metadata, including completed wrappers, is in
`scratch/C/p3*.tsv`, `scratch/C/p2anchor*.tsv` and `LOG.md`.

## Next

1. First collect e62. Read exact job stats and logs. From `scratch/C`,
   use `../../opt/venv/bin/python -B ../../ralph/lanes/C/p3_round4_index.py ../../gluing/val/r3_7_22.g6 . --part lower --replay --output p3e62-final-index.tsv`
   under lane RAM/wall limits. Omit `--replay` and add `--partial` for
   progress only. Any cap/missing row needs precise carry-over; do not
   overwrite existing proofs or truncate retained logs.
2. For e64 diagonals 3/4, 4/4 each pilot, 55 remaining each; budget
   ~1,500–2,200 CPU-s production at measured rates. If approved, cover
   e64 first; the f*=9 P3 branch then needs only the 60 e63 keys of
   the b=0 boundary. No lower flexible full sweep at current cap rates.
3. For diagonal five after e62, e61 has 149 passing layouts x6,
   e60 320 x1. Five pilots each passed; 4.25 estimated CPU-h production
   plus replay. Ask critic based on remaining budget; no launch yet.
4. For isolated P2 e80 with a degree-three anchor, lower boundary
   enumeration has 4/12/20/23/13 passing masks at e(X')=64..60
   (`scratch/C/p2anchor-lower-control.log`). The orbit generator
   matches all 444 C21 observed anchors; no lower proofs launched.
   Start with a dispersed e64 pilot (236 keys in the full cover).
   Work on e80 without that anchor and e81 separately; the 22-census
   does not cover them. Do not generalize any of these to R(5) or
   other degree distributions.
