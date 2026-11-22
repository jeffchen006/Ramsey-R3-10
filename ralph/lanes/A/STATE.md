# Lane A state

Round 23, November 22, 2026. Allocation 2. Both critic directives done:
transport versioned and independent physical oracle delivered to G/H. No
separate SAT queue by directive. R(7) remains closed by C's accepted finite
certificates, already replayed by A. Case R remains open. No candidate, new
target proof or case debit by A.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start / expected end |
|---|---|---|---:|---|
| — | No detached or stopped jobs | — | 0 | — |

Foreground only, one bounded Python worker at a time; `nice -n 5`,
`timeout`, `prlimit --cpu`, 512 MiB VM. Timed development and replay used
17.44 CPU-s (0.00484 core-h; excludes one untimed development assertion
test). Max timed worker RSS 81,244 KiB; `scratch/A/r23` adds ~5.3 MB.

## Results and claims

| Label | Scope / result | Evidence | Core-h per clean replay |
|---|---|---|---:|
| hand + enum (regression to A-035, not a new coverage claim) | v1 raw label→representative transport: all 22,408 forward/inverse, 49 masses and 19,651 keys bound; 19,908 stale reverse uses fail. Two fixtures include a nonswap 3-cycle and a post-transpose non-involution. | `ROUND23_BLOCKERS.md`, `TRANSPORT23_V1.sha256`, `scratch/A/r23/transport.v1.json` | 0.000225 |
| hand + enum (controls only; pending critic) | Independently decoded b201/b202 SAT relaxations, all 87,000 CNF rows satisfied, four I10s with all pair names and selector guards. Both have an I10 with equal same-shore contacts at distinct physical sites. Exact compact clauses shorten 14→9, 11→7, 13→7, 17→11; guarded-false channel rows pinned. 1,960 smaller placements decode and pass triangle-free/alpha=6; explicit short-I6, missing-option-edge and missing-selector mutations each lose a valid plant. No UNSAT. | `ROUND23_BLOCKERS.md`, `BLOCKERS23_V2.sha256`, `scratch/A/r23/physical.v2.json`, `scratch/A/r23/replay.log` | 0.000708 |

## Next

- Use `physical.v2.json`; `physical.v1.json` was preview only. G owns h5 queue
  and production proof receipts. Verify new clause inventories against
  actual site names/channels if requested; do not launch parallel SAT.
- Replay from root: `bash ralph/lanes/A/replay_blockers23.sh r23-review`.
  The versioned h6 inventory is already accepted; no h6 proof rerun or h7
  revival, no extrapolation to h4.
- R19 card interface and held-out roster: `ROUND19_DELETION_CARDS.md`,
  `ROUND19_FREEZE.sha256`, `scratch/A/r19`. C owns fifth-row/join work.
