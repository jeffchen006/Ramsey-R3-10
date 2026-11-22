# Lane H — round 16 handoff, November 22, 2026

Two-core ceiling; no solver, detached or stopped H job; no candidate.
Confirmed through round 015: **238 near-regular MTF distributions plus
Case R**, ten conditional U88 keys, five conditional mixed E cores
(`1,6,9,15,18`), d7 floor 108. **All 2,102,271 supplied reducibles** of
order-32/e108 are covered. The supply remains **2,104,146/2,104,151**,
five missing criticals; the separate order-33 through-e121 denominator
is **14,395/14,395**. See `ROUND16_REVIEW.md` for scope and replay.

## Jobs

| PID | Command | Log | Cores | Start/end CET |
|---|---|---|---:|---|
| — | None live, detached or stopped | — | 0 | — |
| foreground, finished | `build_private_signature.sh --old build R310`; `env lean -j 1 -DElab.async=false` source and two axiom suites | `scratch/H/round16-{build,middle-dev*,targeted,project}.log` | 1 slot | 11:57–12:07 |
| foreground, finished | `python3 -SB check_middle_star.py` (wall/VM cap) | `scratch/H/round16-controls.log` | 1 | 12:08, 0.02 s |

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean H-031, pending | Actual marked-path partition at t=17,m=16 gives row contacts 2/2/4 at each of 7 middle neighbors and column size 2 at each of 14 untouched sites. Explicit ambient 9-regularity, triangle-free, cap 3, and local floor 2; MTF and no deficient pair incident to the middle imply that floor. K=2 structural existence, the roster and exclusion not formalized. | `lean/R310/MiddleStar.lean`, `ROUND16.sha256`, `scratch/H/round16-{build,targeted,project}.log` | 0.06930 including dev and controls |
| enum controls | Petersen (3,5,10) degree/α and 60 oriented marks, 60 contact deletions, 19-site MTF blow-up, 36 tight row arrays. Targeted 7 and integrated 339 axiom reports pass strict checker. | `check_middle_star.py`, `scratch/H/round16-controls.log` | included |
| ledger | Imported r015 A/C once, B full reducibles, D each-path theorem, E core 8, F all-vertical-pattern ID21, G/H and R/N scouts. New r016 lane receipts pending, not debited. | `ralph/CLAIMS.md`, `ROUND16_REVIEW.md` | — |
| open (dated literature) | DS1 rev. 18 clearly lists 40–41. No later classical result, bulk GR/Angeltveit order-39 release or new dense order-30 exact count located; no second catalogue run. Current HoG HTML is a shell, not a fresh catalogue assertion. | `LIT.md`, `scratch/H/round16-literature.log` | — |

## Next steps

- Import round-016 critic verdicts including any final F handoff
  after the snapshot. Preliminary ID8 hole restoration is not an
  exclusion and has no full receipt yet. Preserve B's 1,875-critical crosswalk as a
  named inventory; five missing are not established addable or saturated.
- D's `K=2,t=17,m=16` pilot, not the 15,282-fold whole run, is the best
  measured regular continuation. Distinguish column-floor/no-deficient
  endpoint (Lean) from the no-other-witness premise in the pole-pair
  lower row (not Lean). Do not repeat D's generator or price.
- A/C round-15 marked exclusion is confirmed; C-041 is the 544-ID
  one-neutral pilot with 15,051,525,487 untested, not a case closure.
  Zero-neutral and broader cap-five are still open. G's result is the h=8 `leaf+leaf.1`
  scheme only. E core 15 has 142 exact open IDs, not 142 UNSATs.
- Request a bounded formal bridge only after identifying the remaining
  mathematical premise; no second inventory or terminal run by H.
