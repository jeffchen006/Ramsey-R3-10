# Round 17: cross-scheme credit and bounded h=8 pricing

## Scope and exact cover

**Hand + enum + cert (local; pending review).** This is the marked e170
adjacent-degree-six equality case with all eight double sites coincident
(`h=8`). The `leaf+leaf.1` closure was already confirmed in round 16.
There is no other scheme closure, no `h<8` inference, no residue-floor or
`t9` change, and no distribution/U88 debit.

- Rebuilt the smaller canonical sets, 24 at order 15 and 0 at order 16.
  Re-extracted 26 physical marks and checked all 104 action images and
  an asymmetric shore-transpose fixture. A separate half-mask action
  matched the original bit action on all 48 × 1,024 inputs. Forward and
  inverse bijection loops give exact roster equality for all 30 schemes.
- Rebound 62 scout and 1,357 round-16 receipts: exact clause multisets,
  both LRAT checkers with exact success lines. The scout index agrees as
  a set (10,386 IDs). Proper-subset certificates from the old `leaf+leaf.1`
  pilot add **1,935 distinct IDs across 27 other schemes**, already-covered
  IDs counted zero. Core lengths among those 48 pilot receipts: one 5,
  42 of size 6, five 7. All full eight-double proofs fix the hole scheme
  (`ROUND17_PREREG.md`); their outside-scheme gain is exactly zero.
- Excluding the retired scheme, the count moves **157,777 → 155,842**
  before the round-17 sample. `scratch/G/round17/coverage.json` has the
  entire ordered residual ID list per scheme, not just counts. With 96
  freshly checked direct IDs counted once, **155,746 remain untested**.

## Direct sample and forecast

**Cert (96 local IDs) + estimate.** The hash-frozen queue spans all 29
still-open schemes, with six each from the smallest, median and largest
queues. 96/96 archived ordinary CNFs were rebound and dual-checked in a
separate pass, with no models, capped IDs or missing receipts. The sample
used **24.98 CPU-s** producer + archive including repeated queue setup
(16.97 CPU-s summed in per-ID timers). The table
`scratch/G/round17/prices.tsv` gives each scheme's CPU sum, min/mean/max
including clause reconstruction, both checker runs in each pass, and hash
work, plus LRAT and total receipt byte tails.

| Item | Median | p90 | p95 | Max |
|---|---:|---:|---:|---:|
| LRAT bytes | 34,288 | 69,070 | 116,638 | 377,351 |
| Raw total receipt bytes | 103,661 | 145,699 | 188,949 | 467,974 |

Weighted by the **post-sample** residual counts and each scheme's sample
mean/max, the direct route prices at **7.53–8.65 core-h** and **16.22–22.05
GiB raw** for receipts, before staging or unobserved tails. The 3–6 calls
per scheme do not bound future tails, either in CPU or disk. The estimates
price labelled IDs without stabilizer savings. The measured cross credit
is a reuse audit, not an end-to-end price for discovering new transfers
in open schemes. No matched transfer campaign was run or is authorized.

**Resource use:** 139.90 CPU-s / 0.0389 core-h including coverage, sample,
replay and two setup failures (8.72 s default CakeML reservation, 0.21 s
missing oracle link before the first receipt; no coverage from failures).
One slot, 384 MiB virtual cap, ~100 MiB peak RSS, ~8.7 MiB allocated in
round-17 scratch, no active jobs. CakeML used explicit 128/32 MiB heap/
stack settings; the producer retried the unchanged preregistered queue.

## Replay from the repository root

```bash
sha256sum -c ralph/lanes/G/ROUND17_FREEZE.sha256
sha256sum -c scratch/G/round17/sample.freeze.sha256
timeout 310s bash ralph/lanes/G/round17_replay.sh coverage
sha256sum -c --quiet scratch/G/round17/sample.freeze.sha256
bash ralph/lanes/G/round17_replay.sh replay --audit
bash ralph/lanes/G/round17_replay.sh summary
```

The audit writes separate replay timings and preserves the frozen timings.
It verifies the SHA-256 and size of each receipt file before reconstructing
the necessary CNF, and requires exact equality with the preregistered
ordered sample. To reproduce proof generation (not necessary for audit),
use the `sample` phase in a clean round-17 scratch directory prepared with
the frozen queue and a local `oracle.so` symlink to `../round16/oracle.so`.
