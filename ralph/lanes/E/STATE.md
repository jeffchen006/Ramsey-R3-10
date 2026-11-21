# Lane E state — round 4

2026-11-21; share 20 cores, peak 15 one-core foreground jobs. No
candidate graph submitted, no Ramsey verdict. All symmetry claims are
about all graphs, not only MTF. Prior work and PIDs: `LOG.md`.

## Jobs

No live lane-E jobs; no detached jobs this round. All listed wrapper
PIDs were foreground batch children and were collected. Solver/scan jobs
ran in `scratch/E` with `nice -n 5`, wall+CPU caps and 16 GiB `ulimit -v`.

| Command / wrapper PIDs (one core each) | Local start; cap | Evidence and final status |
|---|---|---|
| `involution_cores.py calibrate/28/32`, serial | 19:57; 60 CPU/80 wall s max | `r4_cal_cores.log`, `r4_{28,32}_profiles.log`; 85/3 projected profiles |
| `involution_sat.py --profiles r4_{28,32}_profiles.jsonl`, 727030–727059 | 20:01; 24 CPU/40 wall s | `r4_pilot/{28,32}.*.log`; 11/11 f28 unchecked UNSAT, 3/3 f32 CPU-killed |
| CaDiCaL on six f28 *base* CNFs, 840828–840837 | 20:04; 25 CPU/45 wall s | `r4_base_sat/profile.*.log`; six SAT relaxations, not candidates or proof artifacts |
| f28 six residuals, `involution_sat.py --seed 5`, 870780–870787; f32 nine pinned cores `--seed 6`, 870811–870936 | 20:04; f28 36 CPU/58 wall s, f32 24 CPU/42 wall s | `r4_pilot/28.res.*.log`: all CPU-killed; `32.*.*.log`: three unchecked UNSAT, six CPU-killed |
| `overlap_windows.py --partitions`, PIDs 999132 (naive), then optimized foreground | 20:07; 75/80 CPU and 120/125 wall s | naive killed; optimized 54.13 CPU s, zero surviving root placements; superseded by weighted replay |
| `replay_overlap28.sh`; 42 older crown proof hashes, serial | 20:11–20:12; 40 s outer for scalar replay | `r4_pilot/{overlap.replay,crown28.hashcheck}.log`, all checks pass |
| `crown32_pressure.py` with `t=2/3/4`, 1451422–1451424; raw replay 1481620–1481622 | 20:15–20:16; 15/18 CPU s and 30 wall s | `r4_pilot/{w*.pressure.log,recheck/w*.log}`, all outputs byte-identical |

## Results and claims for H/critic

| Claim/result | Label | Evidence | Decisive core-hours |
|---|---|---|---:|
| `(2,28,a=6)` excluded. Hand reduction forces a four-cycle of overlapping size-six attachments. Four order-17 windows give average fixed-degree sum ≤62 but the exact window minimum is 66. Uses D-G3's seven `(3,6;17)` classes, no δ≥5/MTF dependency. | enum, pending review | `ralph/lanes/E/overlap28.md`, `replay_overlap28.sh`, `overlap17.g6`, `scratch/E/r4_pilot/overlap.replay.log` | 0.00017 |
| Consequently all `f=28` attachment sizes now have exclusions reported, inheriting their distinct statuses; need H/critic to combine a≤3/a=5 hand, a=4 cert, a=6 enum, and a=7 F10. | pending aggregate | above; `involution.md`, `crown28_exact.md`, `notes/symsat.md` F10 | — |
| `f=32`, t=2/3/4: singleton-neighbor capacity necessary bound. Of 6657/1407/356 eligible W cores, 6196/1136/313 survive. At t=4 with min degree of W at least 3, W is cubic and every full attachment has exactly two double rows. | hand bound; enum counts; no full t closure | `ralph/lanes/E/crown32_pressure.md`, `scratch/E/r4_pilot/recheck/w*.log` | 0.0013 |
| `f=32` comparison: three unpinned CPU kills; three of nine pinned unchecked UNSAT, six CPU kills. Unpinned 207–229k base rows, pinned 136–168k. | enum for the three pins only; remaining open | `ralph/lanes/E/crown32_pressure.md`, `scratch/E/r4_pilot/32.*.log` | ~0.063 |
| Prior `(2,28,a=4)` 42 proof bindings intact; no replayed or new proof search this round. `(5,5)` is already cert from round 1. | prior cert / integrity check | `ralph/lanes/E/crown28_exact.md`, `scratch/E/r4_pilot/crown28.hashcheck.log`; `ralph/lanes/E/slim5.md` | — |

## Next steps

- H/critic: review the structural reduction and U-budget algebra
  in `overlap28.md`; `cd scratch/E && bash ../../ralph/lanes/E/replay_overlap28.sh`
  validates the complete min-66 check by two algorithms in under a
  CPU second. BOARD notified F not to repeat the f=28 a=6 branch pending review.
  The earlier 85-profile quotient census and 127,502-cycle join were
  exploratory; the closure needs neither. Never treat SAT base models
  nor CPU-killed lazy runs as candidates/exclusions.
- For `f=32`, test the two cubic W cores within `(t=4,δ(W)≥3)` with
  exact support pins: each double row uses two singleton slots of
  nonneighbors which are adjacent to each other (triangle-freeness and
  α(W+A_i)≤6). Then reuse their profiles in the four attachment
  windows. Do not scale raw pinned/unpinned SAT from the measured sample.
- `(2,30)` smaller windows, `(5,0)`, and order-three open cases untouched.
  For order three, try three-orbit joint constraints only with a matched
  pair baseline; the prior pair-footprint pilot left all templates alive.
