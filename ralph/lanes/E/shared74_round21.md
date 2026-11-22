# Round 21 — exact conditional mixed core-1 residual

The critic authorized only the 115 IDs frozen in
`scratch/E/r20_shared/residual.jsonl`, one worker, 234 CPU-s all-in,
1 GiB address space and 224 MiB new staging. The round-20 paired
sample forecasts 88.00 CPU-s / 129.98 MiB without fallback and
142.95 CPU-s / 185.66 MiB with six stressed fallbacks; these are
sensitivities, not upper bounds. This run adds a complete accounting
pass over the existing frozen scan. Start no other core.

Use one CPU-affined worker and a 223 s wall limit plus 2 s kill grace
for the complete solver wrapper, an internal no-new-lift guard at 194
CPU-s, and reserve the remaining CPU allowance for external artifact
auditing and freezing. Retain the round-20 8 MiB per-file, 7 CPU-s / 15 s
per-solve and 10 CPU-s / 30 s per-check caps. Check the projected staging
size before each large write/tool invocation and do not start another
lift within 32 MiB of the 222 MiB soft staging cap.

After the three inherited hash checks, repeat the smaller SAT and checked
UNSAT controls and reject the wrong degree formula and wrong physical
lift. A target ID is accepted only after reconstruction of its omitted
group by ordinal from the whole cover and the independently bound branch
stream, fresh width-three and original width-eight reference formulae,
independent width-three clause regeneration and subset verification,
and both LRAT checkers. Solve first at width three; only on recorded SAT
or solver limit is a width-eight solve permitted. Stop on wide SAT/limit,
failed binding/check, or the resource guards. Do not solve the previous
32 IDs again.

## Result — conditional mixed core 1 only (hand + enum + cert)

Zero-based core 1 is `G?bFbo` in `scratch/E/r5_saturated/e11.g6`.
Scope: `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, attachment
profile `(10,10,11,11)`, universal `δ(G)≥5`, and the E-021
all-graph premise/consequence that all four `F\A_i` windows belong
to the sole missing order-26/e74 class under these hypotheses.
E-042 and E-043 cover all four omission roles and `K=6,7,8`.
No MTF restriction and no debit to the full involution case or to a
degree distribution. This closure is submitted for H/critic review.

| Disposition | Physical lifts |
|---|---:|
| Projection graph obstruction (weighted by omission count) | 340,949 |
| Lift graph obstruction | 202,928 |
| Fused obstruction | 19,090 |
| Marked incompatibility | 2,417 |
| Round-18 checked LRATs (distinct IDs, inherited) | 16 |
| Round-20 checked LRATs (distinct IDs, inherited) | 16 |
| Round-21 fresh width-three LRATs | 115 |
| Remaining | **0** |
| Total, 68,323 projections in 24 first branches | **565,531** |

The reconciliation traversed every frozen cover row and merged receipt.
It independently compared each branch row to the whole cover, checked
projection intervals, checked each omitted-group ordinal or the sole
projection-wide receipt, and extracted the exact 147 terminals. The
565,384 inherited negative receipts are enumeration with replay, not
individual LRAT proofs. None of the 32 old IDs was solved again; a
comparison proof never counts twice.

All **115/115** newly checked IDs (across 94 projections in 12 branches)
have a fresh width-eight reference bound to the branch physical lift,
independently regenerated width-three clauses contained in that
reference, and passing CakeLRAT and `lrat-check` logs. No wide solve,
fallback, failed check, limit or SAT on the target. The smaller positive
was SAT at both widths, the smaller negative passed both checkers at both
widths, and the wrong degree formula and wrong lift were rejected. A
separate artifact-only audit recovered all 115 actual omitted support
lists from the whole cover, checked raw CNF clause multisets, and matched
exactly 230 target checker markers.

**Measured:** 82.72 CPU-s for the main wrapper, including 66.788 s
preparing/binding, 2.641 s solving and 8.805 s checking the target
IDs. The separate artifact audit took 1.93 CPU-s; total about
0.024 core-h including the freeze. New logical staging about 132 MiB;
peak RSS 43,672 KiB for the wrapper. No candidate or active process.

**Evidence:** in `scratch/E/r21_shared/`, `checked.1.jsonl` records every
omitted group, formula and proof hash; `accepted.1.jsonl` and empty
`remaining.1.jsonl` are the exact ID lists. `target.log`, `audit.log`,
`timing.tsv` and `freeze.1.sha256` pin the accounting, checkers, proof
artifacts, code and inherited manifests. Run `sha256sum --quiet -c
freeze.1.sha256` from that directory to verify the freeze.

**Next:** conditional mixed cores `{6,9,18}` remain, and `(2,32)` is
still open. Request at most a bounded ordered-census and dispersed
pricing pilot for core 6 (`G?bav_`), not a full scan. Old round-10
front/tail samples found 16/0 terminals across 34,425/12,411 lifts;
that spread is evidence against extrapolating from a single band, not
a comparative ranking or an exclusion. Nothing was launched.
