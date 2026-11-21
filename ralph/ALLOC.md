# Core shares (busy solver processes; sum <= 80). Set by the critic each round.

| lane | cores | reason |
|---|---|---|
| A | 3 | +1: full independent paired proof replay; bind terminal lower/mixed covers and safeguard exact source generation. |
| B | 25 | +1: checked 1,142-key scout delta; reserve 16 for prefix and up to nine for bounded new-source/proof work. |
| C | 8 | −2: the 16–21 bound is checked, but 99.9% of raw maps remain; use small exact blocker and pre-join pilots, not a broad join. |
| D | 4 | +1: punctured-root cover has a fresh exact calibration; allow a matched small target pilot, not more score-cap retries. |
| E | 16 | −3: checked 785→57 queue reduction and core closure; retain the prior working batch ceiling, no need for the extra burst slots. |
| F | 2 | Unchanged: exact two-seed trade neighborhoods exhausted without gain; only a genuinely new source or selector warrants a pilot. |
| G | 20 | +2: confirmed c=3 and c=2/min-degree-three paired exclusions; preserve 18 live slots and reserve up to two for exact source or overlay controls. |
| H | 2 | Unchanged: ledger, hypothesis audits and scoped Lean work fit two slots. |
