# Round 19 — fixed middle, any right at h=8

**Hand + enum + local cert, pending critic.** One shared-grid formula
excludes precisely the scoped `h=8` slice with a middle hole shape on
at least one shore of the marked adjacent degree-six equality pair at
`e=170`. Proof of necessity and the label action:
`rows/e170_shared_middle.md`. The local UNSAT checks do not settle
`R(3,10)` or close any of the seven adjacent-pair distributions.

## Exact accounting

`scratch/G/round19/physical.tsv` lists all 169,635 historical original
`(scheme,rank)` keys, round-17 open flags, accepted round-18 owner and
applicable selector IDs. The independently forward-enumerated physical
pairings are sorted by their existing support-mask rank convention.
The crosswalk partitions the 900 physical hole-list pairs under the
simultaneous action with shore swap, checks every mapped grid and
slot, and reconciles round-17 uncovered rank lists minus the 96 direct
receipts, all 16,350 `middle+middle.2` owner ranks from round 18, and
the accepted 17 leaf scheme maps. Eight of the 11 middle scheme maps
require shore swap, including all four new matching+middle schemes.

The middle formula touches 107,772 historical IDs: 30,203 in four
already-excluded leaf schemes, 16,350 in the accepted `middle+middle.2`
scheme, and 61,219 in six otherwise open schemes. The last six include
3,272 already counted in round 17. Only the **57,947** below are new:

| Scheme | New |
|---|---:|
| `matching+middle.0` | 7,332 |
| `matching+middle.1` | 8,351 |
| `matching+middle.2` | 7,771 |
| `matching+middle.3` | 8,822 |
| `middle+middle.0` | 11,941 |
| `middle+middle.1` | 13,730 |

**79,072 − 57,947 = 21,125** labelled IDs remain in the marked `h=8`
slice: `matching+matching.0..5` contain 2,942 / 3,072 / 3,553 / 3,901 /
3,790 / 3,867 respectively. Exact remaining rank lists are in
`scratch/G/round19/outstanding-if-verified.json`. Until critic review,
79,072 is the accepted count and 21,125 is the post-receipt count.

## Receipt and clean replay

`scratch/G/round19/middle.cnf` has 724 variables and 23,733 clauses:
12 positive selector rows (8 compulsory slots, 4 MTF disjunctions),
528 exclusivity rows, 1,172 triangles, and 22,021 padded blockers.
The scout's frozen edge/blocker generator was compiled in lane-local
scratch. The separate literal binder accepted every clause and rejected
a bogus edge unit, unguarded optional-edge row, fake slot mutex and
shortened MTF row. Both `lrat-check` and `cake_lpr` accepted the bound
formula/proof; the accepted leaf proof was also fully rebound and
dual-checked. The full-model any-right control recovered smaller
catalogue canonical sets exactly: aligned **24/0**, one-defect
**129/11** at orders 15/16. Its reconstructed positive graphs satisfy
all clauses of the separate one-site projection on the same board:
86 aligned and 269 one-defect labelled plants, 208 with changed right
double lists. The clean directory regenerated the same CNF, all three
rank/crosswalk artifacts and the `h=7` pilot plan byte-for-byte and
rechecked the original LRAT, without solving the target again.

From repo root, using a fresh lane-owned directory and no solve:

```sh
sha256sum -c ralph/lanes/G/ROUND19_FREEZE.sha256
mkdir -p scratch/G/round19-audit
timeout 150 bash ralph/lanes/G/round19_shared.sh review "$PWD/scratch/G/round19-audit"
```

Baseline / target including checks / clean replay: 13.10 / 4.03 /
13.60 CPU-s, **30.73 CPU-s total (0.00854 core-h)**. Solver alone
1.44 CPU-s; CNF+LRAT 10,058,455 bytes. Peak RSS 134,516 KiB; peak
additional scratch ~29.5 MiB apparent, ~19.3 MiB retained. No jobs
remain. The small tests did not launch the matching shape, any per-ID
proof, or any `h=7` target solve. The 51 checked `h=7` two-sided orbits
are unchanged; eight pilots are frozen in `ROUND19_PREREG.md` and
`scratch/G/round19/h7-prereg.json` for later authorization.
