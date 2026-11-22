# Lane H — round 15 handoff, November 22, 2026

Two-core ceiling, no H solver, detached or stopped jobs; no candidate.
Confirmed through round 014: **238 near-regular MTF distributions plus
Case R**, ten conditional U88 keys. **Six** conditional E mixed cores
remain (`1,6,8,9,15,18`); five only if pending E-038 is accepted.
The order-32/e108 supply is **2,104,146/2,104,151** (five missing);
36,800 distinct reducibles accepted through round 014. Do not conflate
that supply with the **14,395** complete order-33 through-e121 census.

## Jobs

| PID | Command | Log | Cores | Start/end CET |
|---|---|---|---:|---|
| — | None live, detached or stopped | — | 0 | — |
| foreground, finished | `build_private_signature.sh --old build R310`; targeted/project `env lean -j 1 -DElab.async=false` | `scratch/H/round15-{biclique-dev,build,targeted,project}.log` | 1 slot | ~10:29–10:32 |
| foreground, finished | `python3 -SB check_biclique_neutral.py` (CPU/VM caps) | `scratch/H/round15-controls.log` | 1 | 10:32, 1.12 s |

## Results and claims

| Label | Result | Evidence | H core-h |
|---|---|---|---:|
| Lean H-030 pending | Explicit `Ramsey3Le 6 18`; the two antineighborhoods of a marked induced `K4,4` in a triangle-free order-40 graph with α≤9 cover the 32 exterior sites, intersect in the neutral sites, each have size ≤17, and exactly two neutral sites iff orders 17/17. Regularity/cap unused in this implication. No catalogue, exchange, scan or case closure formalized. | `lean/R310/BicliqueNeutral.lean`, `scratch/H/round15-{build,targeted,project}.log`, `ROUND15.sha256` | 0.03158 incl. one dev error, Mathlib not rebuilt |
| enum controls | Smaller `R(3,3)` threshold: 12 labelled order-5 and zero order-6 survivors; 1,494 smaller cap-valid planted squares; order-9 tight/asymmetric and mixed triangle mutation. Targeted 5 and integrated 332 axiom reports passed. | `check_biclique_neutral.py`, `scratch/H/round15-controls.log` | 0.00031 controls |
| ledger | Imported all round-014 verdicts including both D quantifiers (nine local CNFs), F's old-card ≥36 bounds, G's three fixed populations, 36,800 B reducibles and six E cores. New round-015 producer reports recorded pending. | `ralph/CLAIMS.md`, `ROUND15_REVIEW.md` | — |
| open (dated check) | Current EJC DS1 PDF (rev. 18, Apr 24, 2026) gives classical 40–41. No superseding decision found; no second catalogue census ordered or attempted. Prior no-new-data findings remain qualified. | `LIT.md`, `scratch/H/round15-literature.log` | — |

## Next steps

- Import round-015 critic outcomes, checking late lane submissions: B
  campaign still live at H snapshot; D had not submitted a new result.
  F's all-vertical restriction on ID21 is not a profile exclusion.
- A/C's matched full receipts (92,341,930 direct, 65,130,071 exchanged,
  zero unresolved; hand + enum pending) are the best bounded regular
  evidence. Closure if accepted is only the two-neutral cap-five mark,
  not that such a biclique exists, all R(5), or all R. Per-ID reason
  vectors must not be treated as per-filling keys or transferred depths.
- E's new core 8 has fresh bound width-three proofs; resolution of
  `(2,32,4)` or of the full IV class does not follow. G's cheap support
  rows reject three old fixed tuples, not templates; no U88 debit.
- If the critic wants a next formal bridge, C requested the physical
  exchange implication. First bind which graph invariant and mapping
  genuinely remain unproved; no second terminal/census run by H.
