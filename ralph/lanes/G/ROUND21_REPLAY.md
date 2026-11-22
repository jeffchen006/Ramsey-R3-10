# Round 21 — eight frozen one-defect shared-grid pilots

**Hand + enum + local cert, pending critic.** All eight preregistered
`h=7` formulas for marked `e=170` adjacent degree-six equality are
UNSAT, with their clauses bound to the physical boards and their LRATs
accepted by `lrat-check` and `cake_lpr` in production and clean replay.
Their 192 scope incidences collapse to 191 keys, seven of which were
already checked in N-009. This adds **184 distinct two-sided contexts**
and takes the local account from **51/1,213 to 235/1,213**, leaving
**978**. The only fresh overlap is between pilots 6 and 8. The marked
aligned `h=8` slice was already confirmed in G-056 and is not rerun.
No distribution, `t9`, U88, or floor changes; no candidate.

## Validation and pricing

- `rows/e170_shared_one_defect.md` describes the physical projection.
  The independent binder rebuilds the variable layout, identifies the
  exact multiset of structural rows, and verifies every remaining
  blocker by reconstructing the forced nonedges and the available
  padding. All eight reject three targeted mutations: clipped MTF
  witness list, deleted optional-site guard, and a complete three-site
  nonedge clause lacking independent padding. The latter starts with
  three disjoint grid rows and columns and cannot gain any jointly
  forced additional site.
- Controls recover the **exact** 129 and 11 one-defect canonical class
  sets of orders 15 and 16. All 269 labelled plants bind both required
  singleton incidences on distinct physical sites and satisfy the
  projected formula; 128 have a different right double list. Each of
  the 22 order-16 plants also has one double/double site. A rejected
  preflight (no target solve) corrected the binder's assumption that
  small-control slot existence rows are always nonempty and distinct.
- Independent stabilizer enumeration agrees exactly with the frozen
  baseline and every pilot's key set. It uses a set of physical cell
  copies, including multiplicities, to test the anchor permutations
  and checks transportation of the deficient coordinates. Boards 2
  and 3 have zero transposing stabilizers. `presolve-sets.json`
  retains the stabilizers and full scope, baseline overlaps, prior
  pilot overlaps and new key set per pilot; `checked-union.json` is
  the checked prefix debit.

CPU-seconds below are measured. Generate and prebind are separate;
replay includes regeneration, semantic binding and both LRAT checkers.
Clean replay starts from an empty scratch folder and never solves a
target. `pricing.tsv` joins the exact key sets (not just totals) to
lane A's independent alignment table.

| Pilot | Board | Fresh keys | Fresh labelled alignments | Generate | Prebind | Solve | Replay | Clean replay | LRAT bytes |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 15 | 118,702 | 0.09 | 0.34 | 0.07 | 0.50 | 0.63 | 331,090 |
| 2 | 1 | 30 | 166,255 | 0.07 | 0.34 | 0.02 | 0.58 | 0.63 | 24,863 |
| 3 | 2 | 18 | 745,140 | 0.07 | 0.42 | 8.63 | 5.52 | 5.59 | 48,183,272 |
| 4 | 3 | 29 | 532,658 | 0.08 | 0.40 | 0.85 | 1.13 | 1.22 | 6,301,615 |
| 5 | 4 | 30 | 1,285,530 | 0.07 | 0.29 | 2.34 | 2.17 | 2.22 | 15,872,916 |
| 6 | 5 | 17 | 1,537,822 | 0.05 | 0.44 | 2.25 | 1.59 | 2.23 | 17,494,557 |
| 7 | 2 | 29 | 495,097 | 0.08 | 0.37 | 5.86 | 2.99 | 3.85 | 36,909,535 |
| 8 | 5 | 16 | 711,446 | 0.08 | 0.41 | 1.84 | 1.97 | 1.76 | 13,247,045 |

**Measured:** 71.94 CPU-s (0.01998 core-h), including failed setup
2.25, preflight 7.84, production 39.06, clean review 22.70, and
debit/pricing 0.09. Target solves took 21.86 CPU-s in total. LRATs
total 138,364,893 bytes and reported RSS peaks at 134,708 KiB; about
142 MiB peak apparent staging. Pilot 3 came within 2,148,376 bytes of
the 48 MiB proof cap. There were no target stops or caps. This is
not a tail bound, even on the other `h=7` boards.

**Comparison, not measured speedup:** The byte-pinned lane A table
gives **5,592,650** labelled alignments, counted on one representative
of each of the 184 new two-sided keys, never weighted by stabilizer.
To achieve a 10× advantage against a route producing one certificate
per such alignment, its mean all-in cost would need to exceed about
**129 microseconds per alignment** on this queue (`10×71.94/5,592,650`).
This is a conditional threshold, not a cost forecast for the direct
route. Round 17 prices `h=8` fixed alignments, while N-009 prices whole
`h=7` fixed hole-list contexts with thousands of alignments per input.
Neither measures a matched `h=7` fixed-alignment route. No new batch
requested; ask the critic to check coverage and decide how to measure
a matched comparator first. No extrapolation to `h≤6`.

## Replay

From the root, with a fresh lane-owned scratch folder and no target
solve (retained receipts are read-only):

```sh
sha256sum -c ralph/lanes/G/ROUND21_FREEZE.sha256
mkdir -p scratch/G/round21-audit-new
timeout --kill-after=2 120 bash ralph/lanes/G/round21_h7.sh review "$PWD/scratch/G/round21-audit-new"
```
