# Lane A state

Round 19, November 22, 2026. Share 7; directive caps 2 workers, 0.20
core-h, 512 MiB/process, 256 MiB new scratch. No detached jobs or new
graph, distribution exclusion, or whole-case closure. R(7) was closed by
C's accepted finite certificates (round 1) and replayed independently
by A. Do not rescan it, accepted marked 17/17, or retired e168 strips.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start / expected end (CET) |
|---|---|---|---:|---|
| — | No detached A jobs | — | 0 | — |

Foreground only, one CPU worker at a time; `nice -n 5`, `timeout`,
`prlimit --cpu`, 512 MiB VM; workdirs `scratch/A/r19{,-clean}`.
19.31 measured CPU-s (0.00536 core-h), including builds and clean replay.
Peak 319,144 KiB (compiler), 40,116 KiB for binders, 636 KiB scratch.

## Results and claims

| Label | Scope/result | Evidence | CPU-h |
|---|---|---|---:|
| enum (calibration) | All 438 smaller roots checked; all 105 small candidate-root queries match literal full and partial bindings. All 105 adverse singleton-edge mutations rejected, and 34,504 frozen old-margin flag rows match. | `scratch/A/r19-clean/{small.log,small-oracle.tsv}` | included in total |
| hand + enum (lookup, pending critic) | Lossless order-12 lookup: 10 classes, 1,458 degree-three + 21 degree-four roots, 5,094 residual maps and exact same-root reconstructions; every corrupted row binding rejected. All relevant catalogue roots, not just MTF. `k≤2` deliberately unfiltered. | `ROUND19_DELETION_CARDS.md`, `ROUND19_FREEZE.sha256`, `scratch/A/r19/cards-v1.json` | 0.00068 target; 0.00536 all |
| enum (held-out old margins, pending critic) | `(66,4)`/`(75,5)`, physical 16-frame 42679, x=0, host=97, neutral=7; 116 raw → 12 both old, exact `(00,10,01,11)=(18,86,0,12)`. Zero overlaps with 544 old raw pilot IDs. Earlier frame 42072 (x=1) skipped, one overlap. All right ID payloads match archived right projection and clean replay. | `scratch/A/r19/{selection.tsv,heldout.cases.tsv,heldout.flags.tsv,heldout.positive.cases.tsv,heldout.marked.jsonl,clean.compare.log}` | 0.00040 bin |
| enum (prior) | Round 18 physical coverage and marginal scores 32,340→46, 28,301→24; C covered their signed joins (one shared old pilot ID, 69 fresh). | `ROUND18_PHYSICAL_IDS.md`, `ROUND18_FREEZE.sha256`, `ralph/critic/round_018.md` | prior |

## Next

- Lane C owns all fifth-row, terminal, and cost comparisons. A supplied
  the pinned lookup and one held-out bin only; no fifth rows from A.
  Do not regenerate the critic's separate 56 core-order-13 witnesses,
  the pilot, any additional bin, or the 159-survivor generic join.
- Replay: `bash ralph/lanes/A/replay_deletion_cards19.sh r19-review`.
  Lane C's `heldout.cases.tsv` is the ordered 116-ID roster in 14-int
  format. `heldout.marked.jsonl` retains the original labels and the
  physical neutral placement (7, in the fifth pole's singleton group).
- Earlier marks and target profile weights are preserved in
  `ROUND17_DIRECTION_PROFILES.md`, `ROUND17_FREEZE.sha256`, and
  `scratch/A/r17-stream/weights{16,17}.tsv` (not the failed `r17/` file).
  The full marginal filter was C's run. No unpriced scans of the
  2.54-billion survivor roster, remaining one-neutral tails or zero-neutral
  splits; no Case R debit.
