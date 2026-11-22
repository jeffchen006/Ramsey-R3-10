# Lane A state

Round 14, November 22, 2026. Share 3; no live or stopped A jobs. No new
order-40 candidate, whole-distribution exclusion, or Case R closure.
Current coverage audit: `ROUND14_REPLAY.md`, `ROUND14_INPUTS.sha256`, and
`ROUND14_FREEZE.sha256` binding `scratch/A/r14/` and C's 12 completed receipts.
Rounds 10–13: `ROUND10_REPLAY.md`–`ROUND13_REPLAY.md`;
earlier work in `LOG.md`. R(7) was already closed by Lane C's accepted
finite certificates (round 1); A replayed them independently.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start / expected end, CET |
|---|---|---|---:|---|
| — | No detached A jobs | — | 0 | — |

Old round-11 PIDs 790867/790884, 790868/790880, 790869/790883 rechecked gone.
Round 14 only used bounded foreground tools (`nice -n 5`, CPU/wall/VM
limits), no A production scan. One bounded first-only replay of C's
scanner recovered the byte stream against the frozen twin-merge digest.
Total about 0.029 CPU-h, including both text and packed censuses, repeated
first checks, compiles and calibration. Retained A growth about 9 MiB.

## Results and claims

| Label | Scope/result | Evidence | CPU-h |
|---|---|---|---:|
| hand + enum (coverage, pending critic) | Independently bound 157,472,001 ordered headers in 27 half-open shards (40,301,322 / 117,170,679 by map); first is 4,322,749. No exchange or diagonal quotient; each shard binds its ordered packed-ID SHA-256. Smaller 10/10 control: 334 nonempty plants, four map relabelings each, grouped/direct 399,584 IDs exactly equal. | `ROUND14_REPLAY.md`, `scratch/A/r14/{headers.packed.shards.tsv,headers.packed.full.tsv,controls.log,input-negatives.log}` | 0.00699 packed census incl. build/controls; 0.01263 text variant |
| enum (first merge and receipt audit, pending critic) | `[0,2048)`: independently matched header roster and C's frozen twin stage digest by first-only replay; 23,100 former triple and 42,709 former pilot IDs retained at exact recorded stage. All 785 panel IDs bind equal C/scout terminal vectors, including nine old pilot vectors; 174 joint, 3,086 fillings, zero open. Missing inputs, dropped map row, count-preserving map overwrite, shared boundary are rejected. | `ROUND14_REPLAY.md`, `scratch/A/r14/{first.depths.gz,receipts.first.log}` | 0.00573 initially incl. first stream |
| hand + enum (coverage/receipt audit of completed prefix, pending critic) | All 12 C shards in `[0,24576)` exactly match independent header census hashes and per-map counts: 67,417,211 headers → 8,076,698 local → 12,594 panel → 3,464 joint → zero unresolved; all 148,231 fillings rejected. Independent terminal stream hash matches canonical vectors. `[24576,55055)` contains 90,054,790 headers, still open. | `ROUND14_REPLAY.md`, `scratch/A/r14/{receipts.final.log,tail-witness.tsv,incomplete.stderr}`, `ROUND14_FREEZE.sha256` | 0.00233 final receipt replay |
| archived | A-023: independent Round 13 literal package audit bound all 55,055 labelled frames and 9,959 atlas entries, replayed 498,668 left-triple headers with exact per-ID stages (17,604 local → 0 panel), and preserved 100 held panel survivors. | `ROUND13_REPLAY.md`, `scratch/A/panel13/round13.sha256` | prior |
| archived | A-021 and A-022 were confirmed on the named windows, now obsolete as strip work: the verified d6 floor kills every old e168/d6 parent. No more e168 reroot, ID maps, matching or proof binding. | `ralph/critic/round_012.md`, `ROUND12_REPLAY.md` | prior |

## Next

- C owns production; A consumes the published `result.json` intervals and
  audits only coverage/receipts. The verifier can audit a completed prefix
  or demand a full tiling with `--require-full`. A's first-stream replay
  does not recalculate terminal search.
- C stopped after completing `[22528,24576)` per the scout's tail gate
  (ID `(23155,26938,1)`, 7,059 rejected fillings, 3.859940 CPU-s). This is
  neither an unresolved terminal nor an invitation to resume without the
  critic. If asked to follow up, provision all remaining coverage hashes
  already in `headers.packed.shards.tsv`, and test any terminal optimization
  against the bound complete reason vectors before new production.
- Do not generalize the marked 17/17 result to every `K4,4` or Case R.
  Do not restart the retired e168 work or the old R(7) cube queue.
