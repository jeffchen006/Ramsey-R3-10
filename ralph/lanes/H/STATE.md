# Lane H — round 19 handoff, November 22, 2026

Two-core ceiling. No live, detached or stopped H jobs; no candidate.
Checked through round 018: **238 near-regular MTF distributions plus
Case R**, **ten conditional U88 keys**, **four conditional mixed cores**
(`1,6,9,18`). Floor 108: 2,104,146 named order-32/e108 d7 roots blocked,
five missing criticals. Order-33 through-e121 denominator 14,395/14,395
is distinct. Neither referee nor T filed a round-18 report.

## Jobs

| PID | Command | Log | Cores | Start / end CET |
|---|---|---|---:|---|
| — | No live, detached or stopped H job | — | 0 | — |
| foreground, finished | `build_private_signature.sh` (direct elaboration, Lake `--old build R310`, two axiom suites, version) | `scratch/H/round19-{dev1,dev2,dev3,build-final,axioms-targeted-final,axioms-project-final,strict,toolchain}.log` | 1 pinned CPU | 16:02–16:07 |
| foreground, finished | `python3 -SB check_private_grid.py` under wall/VM cap | `scratch/H/round19-controls-final.log` | 1 pinned CPU | 16:05 |

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean H-034 (pending) | Matching from one four-site physical private cell to distinct noncross anchors has size at most `t+(4−s)`, including when multiple physical sites share a grid cell. The lower bound `3+[i=0]` implies `s−t≤1−[i=0]`; columns by transpose. General cell capacity proved, matching lower bound imported as a hypothesis; no MTF/codegree graph reduction, board enumeration or SAT work. | `lean/R310/PrivateGrid.lean`, `ROUND19_REVIEW.md`, `ROUND19.sha256`, `scratch/H/round19-strict.log` | 0.04003 all |
| enum (controls) | 216 exhaustive three-site arrays, tight small and four-site examples, literal transpose, and a mutation where counting two edges from one double-supported site fakes three size-3 matchings (actual max 2). Pinned Lean/Mathlib 4.35.0; strict 3 targeted / 356 project axiom reports pass. | `check_private_grid.py`, `scratch/H/round19-{controls-final,build-final,toolchain,strict}.log` | included |
| ledger | Round 018 confirm A-030, C-044, D-045, E-042, F-035, G-054, H-033 and scouts R-006/N-008/N-009. C's 69 fresh signed failures leave 2,542,514,376 untested; R's disjoint 56 structural vetoes leave 2,542,514,320 neither tested nor vetoed. G's 15,684 then N's 60,990 fresh debits leave 79,072 `h=8` IDs in 12 schemes. `h=7` has 51/1,213 two-sided contexts with local receipts, not 51/81. | `ralph/CLAIMS.md`, `ralph/critic/round_018.md`, `ROUND19_REVIEW.md` | — |
| pending imports | G-055: one local middle receipt, 57,947 proposed debit to 21,125, not yet accepted; F-036: 102/128 one-double pilot cuts and unsigned count only. A-031/032: lossless lookup and old-margin held-out bin. E-043: 147 terminals, 16 inherited proofs, 131 unresolved; core stays open. D-046/047: 3,128,474 necessary marked orbits and proposed filter, no closure. | `ralph/CLAIMS.md`, A/D/E/F/G round-19 `STATE.md` and freezes | — |
| open (literature) | No new screen on critic's instructions. `LIT.md` remains a dated search, not a completeness claim. | `LIT.md` | — |

## Next steps

- Import final round-19 lane evidence (other lanes in flight at H
  snapshot) and critic verdicts. Do not debit the 57,947 potential G
  middle IDs without the bound receipt and physical residual crosswalk.
- Keep A's held-out order-12 old-margin slate separate from R's order-13
  structural veto and C's older signed failures. An order-12 sample is
  not a slice exclusion. The round-19 fixed-left pilot is G's, not H's.
- Keep B parked with no new source. A D count-only nonempty join is not
  a closure; an E exact terminal roster is not a proof batch; F's
  unsigned pilot does not constrain arbitrary signing. Ask the critic
  to check H-034; await any new short reusable interface from C/G.
