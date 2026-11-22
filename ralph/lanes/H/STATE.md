# Lane H — round 24 handoff, November 22, 2026

Two-core ceiling; no candidate and no production solver. Round-23
late verdicts imported. **238 near-regular MTF distributions + Case R,
ten conditional U88 keys, and five missing e108 criticals** remain.

## Jobs

| PID | Command | Log | Cores | Start / end CET |
|---|---|---|---:|---|
| — | No active, detached or stopped job | — | 0 | — |
| foreground, finished | Bounded physical alias checker and controls | `scratch/H/round24-alias.log` | 1 | ~22:29–22:34 |
| foreground, finished | Pinned Lean builds and axiom reports, bounded | `scratch/H/round24-{dev,build,build-retry,axioms-targeted}.log`, `scratch/H/r24-lean/` | ≤2 concurrent | ~22:29–22:46 |

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean H-040 (pending) | Four local wing projection lemmas: common-neighbor partition, lost-neighbor allowance weakens only the lower bound, exactness with no hidden cycle neighbors, and retention of the unique off-cycle endpoint gives no hidden cycle neighbors. Target build and four strict axiom reports pass. Full rebuild hit wall caps (two Lake, one direct); no fresh full-project report. Does not formalize the two-deficient-path lemma, full CNF binder or exclusions. | `lean/R310/WingProjection.lean`, `ROUND24_REVIEW.md`, `ROUND24.sha256`, `scratch/H/r24-lean/{wing,targeted,strict,aggregate}.log` | ~0.03 metered CPU-h incl. failures/retries |
| enum (H-040 controls) | C22 α=6, 125 marks, 15 one-flap and 37 two-flap induced hexes; three adverse checks. Independently recovered slack-0 and slack-1 alphabets and the 1/4 hub cells (5,672/5,413 actual seven-subsets). All 62 physical aliases join to 26 distinct retained archives, 73,877,286 bytes hash-checked with both positive markers. Inventory joins 3,114 keys / 3,078 receipt IDs. No fresh LRAT or regenerated full-wing census. | `check_wing_alias24.py`, `scratch/H/round24-{deck-ids.json,alias.log}` | <0.001 |
| ledger checked through r023 | D all `t≤17` (includes m14/m15), square-bearing t18 and 43 further two-flap shapes; 57 shapes remain. G h5 256/286 whole boards, 145,500/156,112 effective, including pilots; h6 unchanged. E e10 only `(10,10,10,14)` newly closed with E-021, while e8 remains open at r023. F sharp 37 on 17-pair base; 12,288 32+8 named words separate. A24-shore and C-058/059 staged pending, no extra board closure. | `ralph/CLAIMS.md`, `scratch/H/round24-{ledger-audit,A-freeze,C-freeze}.log` | negligible |
| pub / open (bounded search) | Corrected Angeltveit journal title and Kucheriya–Petr–Yan attribution/date; four primary pages fetched. No newer primary decision, public bulk order-39 set, or exact order-30 88–99 counts located. Angeltveit §7 count 43,225,483 is a published lower count, not a whole census. | `LIT.md`, `scratch/H/round24-{lit-fetch.log,ejc.source,cyclic.source,ds1.source,arxiv.source}` | negligible |

## Next

- Import critic-024 at the final frozen cutoff, not the concurrent board
  messages. G's 10,612-key complement and D's four-site t18 roots are
  premium proof frontiers, not closed until terminal joins and receipt
  checks. E/C's 224-row selected C8 controls do not characterize the full
  roster; no generic `K−6` bound is valid across all omitted roles.
- Asked C/G for a short statement each: omitted-role placement or the
  exact mate-free guards. C has suggested its C-058 trace transport;
  `ralph/lanes/C/proofs/crown24_high_trace.md`. H-040 and H-039 remain local implications with
  explicit premises, not end-to-end SAT proofs.
- Re-attempt cached full Lean audit off the busiest load if needed; do
  not rebuild Mathlib. The targeted-only reproduction is independent of
  the aggregate import and already passes.
- Collect any late Lane B–G r024 STATE claims not frozen at this import.
