# Lane A state

Round 16, November 22, 2026. Share 4; no live or stopped A jobs. No new
candidate, distribution exclusion, or whole Case R closure. R(7) was
already closed by C's accepted finite certificates (round 1), replayed
independently by A. The round-15 17/17 marked block is accepted; do not
rescan that, the old R(7) cubes, or retired e168 strips.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start / expected end (CET) |
|---|---|---|---:|---|
| — | No detached A jobs | — | 0 | — |

Only bounded foreground compilation, counting and controls. `nice -n 5`,
up to 60-s wall / 120-s CPU and 512 MiB VM per process. Timed build,
original and clean replay total **0.0099 A CPU-h**; further failed initial
control attempts <0.001 CPU-h. Working peak 37 MiB RSS per process (164 MiB
compiler). Retained 0.75 MiB including clean duplicate and two executables.

## Results and claims

| Label | Scope/result | Evidence | CPU-h |
|---|---|---|---:|
| hand (pending critic) | One-neutral marked cap-five window order 16 then 17 by order, private sizes 15/16, same neutral matched once, transpose only when reading backwards. Literal shapes 3322/3332 and 3333/4332/4333; distinct catalogue-labelled frames cover all physical targets. No bit or half-plane. | `ROUND16_ONE_NEUTRAL.md` | — |
| enum (pending critic) | McKay catalogue bytes match both local inputs; 2,576 and 7 distinct classes checked by `shortg`, triangle-free and alpha ≤5. 2,817,701 and 59,521 exact side frames. Six `(D16,d16)` complementary header keys, 34 positive shape strata, **15,051,526,031** exact ordered eligible header IDs, all still open from A's count. | `ROUND16_FREEZE.sha256`, `scratch/A/r16/{count16.tsv,count17.tsv,strata.tsv,public.sha256,replay.log}` | 0.82 CPU-s for counting alone |
| enum (calibration) | Smaller 6/7 frame rosters exactly match literal set enumeration; 34,504 exact header IDs per read direction, 153 physical edge reconstructions each way; 306 crossed-edge deletions rejected. Swapped private size, dropped frame and false degree total diagnosed. | `scratch/A/r16/controls.log`, `one_neutral_control.py` | 0.33 CPU-s original |
| enum (pilot binding only) | Delivered 544 headers to C, 16 from every positive shape stratum including extreme and seeded ranks. Full side-frame IDs lex `(host, four increasing masks)`. No Cartesian product or terminal scan. Clean replay reproduces all 13 deterministic outputs. | `scratch/A/r16/{pilot.frames,pilot.index.tsv,pilot.bound.tsv,pilot.log,replay.log}`, `replay_one_neutral.sh` | 15.09 CPU-s original sampling |
| estimate | 112.14 GiB at eight bytes per eligible ID; 4.18 core-h at 1 µs/header, 4,181 core-h at 1 ms/header. Unit-cost sensitivities, not predicted terminal costs. | `ROUND16_ONE_NEUTRAL.md`, `scratch/A/r16/estimate.log` | — |

## Next

- C owns terminal pilot and tail, not A. Await its price before any
  production. Do not materialize the header product or treat 544 rows
  as a terminal certificate or statistically reliable tail bound.
- Critics can replay with `bash ralph/lanes/A/replay_one_neutral.sh`;
  it writes under `scratch/A/r16-replay/` without mutating C's input.
- Both zero-neutral splits and the one-neutral split are still open
  from this roster alone. Do not infer whole cap-five or Case R closure.
