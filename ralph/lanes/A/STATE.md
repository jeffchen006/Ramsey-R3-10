# Lane A state

Round 24, November 22, 2026. Allocation 2. Named residual h5 audits done;
A23 transport and physical v2 untouched and hashes verified. No h5 or h6
production SAT by critic directive. R(7) remains closed by C's accepted
finite certificates, independently replayed by A; case R remains open.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start / expected end |
|---|---|---|---:|---|
| — | No detached or stopped jobs | — | 0 | — |

Bounded foreground workers only, `nice -n 5`, `timeout`, `prlimit --cpu`,
512 MiB VM. Initial unoptimized target audit hit its CPU limit at 40.03
CPU-s; no result from that attempt. Approx. 0.023 core-h including development
and clean replay, max timed RSS 262,044 KiB (initial attempt). Net scratch
addition about 9.5 MB. Clean replay measured 11.27 CPU-s, 82,128 KiB peak.

## Results and claims

| Label | Scope / result | Evidence | Core-h per clean replay |
|---|---|---|---:|
| hand + enum (controls; submitted) | One-shore projection: a physical forbidden set can use slot activity rather than exact mates; include all possible physical edges on that shore and positive mate selectors hitting opposite boundary anchors. Both shores checked on 1,960 valid order-17 placements and 48,956 distinct one-edge seven-subsets, with four lost-positive contact/occupancy deletion fixtures. | `ROUND24_SHORE.md`, `SHORE24.sha256`, `scratch/A/r24/controls.json` | 0.00139 |
| hand + enum (saved relaxations; submitted) | `d175_1 d185_1 d246_1 d252_1 d275_1 d281_1`: verify all 367,934 CNF rows, 12,974 physical I10s, six new mate-free seven-literal clauses with explicit alternate matchings; exact witness rows absent from formula and then-current seed inventories. Both source channels bound. Same-occupancy matching counts are local, not full SAT models or excluded keys. No new target proof, candidate or board debit. | `ROUND24_SHORE.md`, `SHORE24.sha256`, `scratch/A/r24/targets.json`, `scratch/A/r24/replay.log` | 0.00174 |

## Next

- Replay: `bash ralph/lanes/A/replay_shore24.sh r24-review`. Passes both
  frozen A23 manifests and reproduces A24 receipts byte for byte.
- G owns the production queue. If it pilots the cut, regenerate using
  `(side,boundary,coords)`, bind both shore channel numberings, and measure
  same-leaf impact before expanding. Do not add parallel SAT from A. If
  asked, audit G's precise branch cover or deltas, not solver performance.
- Old A23 `physical.v2.json` is final, v1 preview only. Versioned h6 inventory
  already accepted; no h6 proof rerun or h7 revival, no h4 extrapolation.
- R19 card interface and held-out roster: `ROUND19_DELETION_CARDS.md`,
  `ROUND19_FREEZE.sha256`, `scratch/A/r19`. C owns fifth-row/join work.
