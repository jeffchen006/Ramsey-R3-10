# Lane H — round 17 handoff, November 22, 2026

Two-core ceiling; no solver, detached or stopped H job; no candidate.
Confirmed through 016: **238 near-regular MTF distributions plus Case R**,
ten conditional U88 keys, five conditional mixed E cores (`1,6,9,15,18`),
d7 floor 108. The critic's fourth-round depth audit confirms the same
forty-key debit, not another debit. For 32/e108, **2,104,146 named keys**
are blocked and five critical keys are absent; the separate order-33
through-e121 denominator is **14,395/14,395**. See `ROUND17_REVIEW.md`.

## Jobs

| PID | Command | Log | Cores | Start/end CET |
|---|---|---|---:|---|
| — | None live, detached or stopped | — | 0 | — |
| foreground, finished | `build_private_signature.sh` for source, `--old build R310`, two axiom suites | `scratch/H/round17-verified-{build,targeted,project}.log` and earlier dev/build logs | 1 slot | 13:17–13:28 |
| foreground, finished | `python3 -SB check_pole_multiplicity.py` (wall/VM cap) | `scratch/H/round17-controls.log` | 1 | 13:19, 0.02 s CPU |

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean H-032, pending | Distinct pole pair shares the middle. Other common physical sites partition exactly into private left/right wings and untouched sites. Sum ≤2 under cap 3; sum ≥1 iff the middle is not this pair's unique witness. No-deficient-endpoint is not a substitute. No K=2 existence, roster or SAT theorem. | `lean/R310/PoleMultiplicity.lean`, `ROUND17.sha256`, `scratch/H/round17-verified-{build,targeted,project}.log` | 0.09149 including dev/controls |
| enum controls | Petersen α=4, 10 MTF cap-three blow-ups, 600 zero rows despite no deficient endpoint at the middle, 120 cap-tight rows, nine positive location controls. Pinned v4.35.0 and 5 targeted / 344 project axiom reports pass strict checker. | `check_pole_multiplicity.py`, `scratch/H/round17-controls.log` | included |
| ledger | Imported 016, including distinct F-032 bridge / F-030 ID8 non-extension / F-031 conditional cyclic four-deletion family. A/C counts 497 empty + 47 no-join, D 155 fresh + two old tails, G one named aligned scheme, B crosswalk counted once. No referee report. | `ralph/CLAIMS.md`, `ROUND17_REVIEW.md` | — |
| open (dated source screen) | DS1 rev. 18 unchanged at 40–41. No later classical decision, public bulk GR–Angeltveit order-39 file, or new dense order-30 exact count located. No second B source or frame census. | `LIT.md`, `scratch/H/round17-literature.log` | — |

## Next steps

- Import round-017 critic verdicts; compare any final A/C/F/D reports
  after this snapshot. E-041 is the full 142-ID exact queue for core 15
  only, **pending**; do not reduce the accepted balance of five before
  review. B-039 archive audit is not semantic proof replay or a new floor.
- D's canonical campaign is the best bounded regular path. Check final
  roster/weights and rebind, not overlap with old pilot counts. Even a
  success at K=2,t=17,m=16 leaves all other slices unaffected.
- One-neutral A/C weighted existence reduces 15,051,526,031 headers
  to 2,542,514,492 both-pass pending review. The zero `(71,5)` key is
  included in those rejects, not another debit. Nonempty package
  domains cannot establish terminal viability.
  G's 1,935 transferred and 96 tested h=8 IDs close no additional
  scheme; 155,746 remain. Do not repeat their searches in H.
- Ask C/G for a short usable implication if they have one next round;
  otherwise keep Lean focused on the next critic-designated seam.
