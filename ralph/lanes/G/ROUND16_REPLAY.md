# Round 16: e170, adjacent d6 equality roots, aligned doubles only

## Predeclared price and production decision

Independent recount: all 900 ordered legal hole pairs have a unique one of
30 representative schemes. Across all schemes the 62 existing support
proofs cover 10,386 distinct of 169,635 alignment IDs (2,803 by the starter
proofs, 7,652 by the extra proofs, with 69 counted in both). For the target
`leaf+leaf.1`, that is 356/1,828 covered before the pilot.

Use the midpoint in each of 48 equal-rank intervals of the sorted list of
1,472 uncovered alignment IDs, not the old seed or the old covered IDs.
Solve and bind the same 48 IDs both ways; timings include generating the
ordinary CNF, making the proof, rebuilding the clauses, both LRAT checks,
and, for transfer, discovery/shrinking and posting expansion. Repeated
coverage of an ID has zero credit.

| Arm | Verified starting IDs | Fresh ID union | CPU-s total | CPU-s per fresh ID | Receipt payload |
|---|---:|---:|---:|---:|---:|
| Direct full aligned pattern | 48 | 48 | 5.56 | 0.116 | 4.57 MiB |
| Shrunk aligned pattern | 48 | 211 | 22.33 | 0.106 | 15.72 MiB |

Transfer initially has a modest per-new-ID gain, but averages only 4.40
new IDs/proof. In the last 24, it falls to 3.71 and costs 0.1178 CPU-s per
new ID vs 0.1176 for direct on those same 24 (effectively tied); direct is
4.0x cheaper on the identical 48 requested proof inputs and uses much
less disk per receipt. Retain all pilot transfers (these cover all 48
direct ranks as well) and switch to direct for the 1,261 IDs still
uncovered. Forecast recorded **before** the production command: 146 CPU-s
and 120 MiB raw nominal; using the largest measured proof CPU/payload,
adding 0.13 CPU-s/ID for replay and a further 36 CPU-s / 20 MiB for fixed
costs and pilot receipts, about **379 CPU-s (0.1053 core-h) / 199 MiB**.
These are sample estimates, not upper bounds. Guard production at 540
aggregate CPU-s or 450 MiB allocated for new receipts, stop immediately on
a local model, and do not work on any other scheme or on `h<8`.

## Result and reviewer replay

**Hand + enum + cert (local; pending critic):** no e170 MTF target
with an adjacent degree-six equality pair in `h=8`, `leaf+leaf.1`.
That representative has holes `L0L4,L3L4` and `R0R4,R2R4`, up to
simultaneous noncross permutations and wing exchange. See
`rows/e170_aligned_grid.md` for the proof of the incidence grid,
the complete alignment roster and the clause/transfer implications.
No other aligned scheme was extended, and no distribution is closed.

- Rebuilt order-15 and order-16 scan and grid-first outputs: exact
  canonical set equality, 24 and 0 classes respectively, 26 marked
  physical order-15 root pairs. All 26 positive C13 projections and
  the duplicated-support adverse control also passed.
- Audited both LRAT checkers and rebound all 62 scout proofs in
  the aligned block. The target's forward and inverse bijection
  enumerators agree on the full set of 1,828 IDs. Counts after each
  replay stage: 356 prior, 404 with direct pilot, 567 with both pilot
  arms (48 direct IDs are all in the 211 fresh transferred IDs),
  1,828 with 1,261 direct production proofs.
- Both `cake_lpr` and `lrat-check` verified every new ordinary CNF.
  The checker rebuilds every clause from the concrete support masks,
  triangles, or witnessed independent tens; the final union must equal
  the complete roster. It does not rely on the discovery engine's
  UNSAT status or its ability to find all independent tens.
- Production: 144.60 aggregate CPU-s, 127.27 MiB raw output (99 MiB
  allocated on this filesystem); final replay: 101.73 CPU-s. Total
  instrumented CPU including pilot and first audit: 286.45 s / 0.0796
  core-h; full scratch footprint about 113 MiB allocated. No models,
  timeouts, or active jobs.

From the repository root:

```bash
sha256sum -c ralph/lanes/G/ROUND16_FREEZE.sha256
(cd scratch/G/round16 && sha256sum -c --quiet prior.freeze.sha256 && sha256sum -c --quiet proof.freeze.sha256)
bash ralph/lanes/G/round16_replay.sh
```

Expected final line: `local scheme PASS {'direct': 48, 'transfer': 48, 'finish': 1261} 1828`.
