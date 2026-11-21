# Core shares (busy solver processes; sum <= 80). Set by the critic each round.

| lane | cores | reason |
|---|---|---|
| A | 2 | Unchanged: independent binding of new marked-strip source and delta keys. |
| B | 24 | +2: terminal reducible e88/e43 scans and new e108 critical certificates; reserve 16 for the live prefix and up to eight for bounded new deltas. |
| C | 10 | +2: checked (12,12) closure; reserve extra slots only for a selective asymmetric pre-join pilot. |
| D | 3 | +1: max12 shrank from 13 to nine rooted keys; use a matched score-cap pilot, not broad strengthening retries. |
| E | 19 | +2: checked profile-A and one-core mixed exclusions; keep 16 as the batch ceiling until the mixed/reverse pilot justifies a bigger run. |
| F | 2 | Unchanged: validated relift is cheap; no gain in target nearness and no request for more cores. |
| G | 18 | −7: template and local-budget gains did not make capped half-CNFs decisive; prioritize an exact path/leaf split over wide pilots. |
| H | 2 | Unchanged: ledger, hypothesis audits and scoped Lean work fit two slots. |
