# Lane H — round 14 handoff, November 22, 2026

Share two, no H solver, detached or stopped jobs; no candidate. The
accepted ledger through round 013 remains **238 near-regular MTF
distributions plus Case R**, ten conditional U88 keys; 12 improved
residue cutoffs are not removals. **Seven** conditional E mixed cores
remain after core 17; six only if pending core 5 is accepted. Do not
conflate B's **2,104,146/2,104,151** order-32/e108 supply (five missing,
reducible extension coverage separately required) and the complete
**14,395** order-33 through-e121 census used by the degree-six floor.

## Jobs

| PID | Command | Log | Cores | Start / end CET |
|---|---|---|---:|---|
| — | None live, detached or stopped | — | 0 | — |
| foreground, finished | Pinned Lean builds via `build_private_signature.sh` and targeted/project axioms checks | `scratch/H/round14-{pole-dev,pole-dev2,book-dev,build,targeted,project-first,project}.log` | 1 | ~09:04–09:11 |
| foreground, finished | `python3 -SB check_round14_controls.py` (time and RAM capped) | `scratch/H/round14-controls.log` | 1 | 09:09, <1 s |

Build `--old R310` passed pinned Lean/Mathlib v4.35.0 without rebuilding
Mathlib. Both 8 targeted and 327 integrated axioms checks passed. Initial
integrated run hit resource/thread-allocation abort, not a proof failure;
`env lean -j 1 -DElab.async=false scripts/Axioms.lean` passed on retry.

## Results and claims

| Label | Result | Evidence | H core-h |
|---|---|---|---:|
| Lean H-028 pending | On an actual old induced card with a fixed-point-free graph automorphism, an outside pole with α contacts takes two mates. Disjoint four-pole columns permit at most α−2 contacts, specializing to ≤7 under old min degree 8 and α≤9. No formal edge-count or cyclic-word exclusion. | `lean/R310/PoleContacts.lean`, `scratch/H/round14-targeted.log` | shared below |
| Lean H-029 pending | Two-term union bound, literal external degree/codegree bridge, capacity 29 off one 11-site book and 18 off two; required contacts into the opposite book count distinct sites. Explicit degree and codegree hypotheses, no type count formalized. | `lean/R310/BookFootprint.lean`, `scratch/H/round14-targeted.log` | 0.0611 combined incl. development and failed Lean run |
| enum controls | All 388/5,789 labelled triangle-free 5/6-vertex graphs, 333 maximum-contact mates, 9,171 disjoint/missed images, 1,886 disjoint + 3,903 overlapping four-column controls, 7,456 footprints on C13/regular C22. | `check_round14_controls.py`, `scratch/H/round14-controls.log` | 0.00024 |
| ledger | Imported all r013 decisions including D's 101 sufficient roots / 528 unordered internal pairs, F's five necessary words, G's 12 improvements and E's terminal-only 0.62728 core-h. New r014 submissions pending: A/C completed prefix, B's 32,768 reducible extensions, E core 5 and F word 15. | `ralph/CLAIMS.md`, `ROUND14_REVIEW.md` | — |
| open (dated search) | No new resolution, dense order-30 census or bulk order-39 data located; targeted source check only. | `LIT.md`, `scratch/H/round14-literature.log` | — |

## Next steps

- Check later D/G/F/C submissions against the next critic review; never
  promote a new count based on a live output. H confirmed none of the
  pending claims independently beyond the two Lean interfaces and controls.
- A/C’s 12-shard independently bound prefix `[0,24576)` is the best
  measured regular route, not the full marked block: 67,417,211 headers,
  12,594 matched terminal vectors, 148,231 rejected fillings, zero open
  in prefix; 90,054,790 unscanned. The 7,059-filling resolved tail cost
  3.859940 CPU-s; this is a pricing stop, not timeout. Price a replayable
  faster tail path before finishing; C/A own scan/coverage respectively.
- Near-regular: B's named extension tranche is useful on its own but
  needs the full reducible coverage and five missing keys for floor 109.
  G same-edge e170 joins explicitly not settled by the 66+30 mask-only
  integral witnesses. No e168 work, no floor 123 or new U88 debit.
- Formal work after reviewer input: prefer a remaining short graph bridge
  used by C/G, not a second terminal or proof run.
