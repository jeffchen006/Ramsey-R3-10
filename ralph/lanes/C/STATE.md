# Lane C — round 21, November 22, 2026

**No candidate. R and R(5) remain open.** Round 21 did the critic's
hand/toy shared-degree check only. One strict order-13 fixture, one
planted positive released by lifting a single absent pin. No target
inputs, new pairs, fifth-row or signed work, or case debits.

## Results / claims for H and critic

| Label | Scope | Evidence | CPU-h |
|---|---|---|---:|
| hand, pending | At a fixed physical core vertex, the sum of the minima over all admissible separate restorations of disjoint singleton groups cannot exceed the target degree minus **all** prescribed incidences. Count only added edges in those minima. | `proofs/panel21_shared_core_budget.md` | — |
| enum, toy only, pending | Same 13-site 4-regular scaffold, one absent-pin difference. Both strict cards have valid exact-five local restorations (2 and 18); even a degree-only triangle-free regular completion exists. At physical `6`, the local minima require (1,1) additional edges, capacity 1. Lift `4–12` prohibition and `C13(1,5)` plants a complete positive, counting the fixed `6–5` once. All 16,384 masks checked, clean replay identical. | `ROUND21_REPLAY.md`, `ROUND21_FREEZE.sha256`, `scratch/C/r21/production.log` | 0.00020 all |
| hand, pending | In the cap-five 16/17 one-neutral geometry, a degree-three triple `x` on the left gives three disjoint `N(a)−(V∪{x})` of size four, exhausting `H` and forcing `z∈N_W(x)`. The local fifth-row gate then needs just a left degree-four deletion flag and a legal right `T` with `|Q_b−T|≤3+flag` for each physical original singleton group. | `proofs/panel20_factored_card.md` | — |
| enum, negative pending | Right-only `(75,5)` triple roster: 5,390 legal masks, 3,714 at threshold 3 and 5,390 at threshold 4, all **116/116 right keys live in both**. Original shape `(3,3,3,4)`. Literal physical card constructions match each mask/flag. C35: 105 root pairs, 840 plants; extra original-size-five/cap controls 61 masks. 578/578 old row masks match, 404 under the counterfactual low flag. Five byte-identical clean artifacts; no new pairs or margin check. | `ROUND20_REPLAY.md`, `ROUND20_FREEZE.sha256`, `scratch/C/r20/{control.log,right_flags.tsv,right_flags.log,clean.compare.log}` | 0.00203 all |
| confirmed round 19 | Frozen `(42679,x=0,host97,z7)` with 116 raw right triple IDs: `(00,10,01,11)=(18,86,0,12)`. Fifth gate vetoed none; the unmodified signed join independently excluded the exact 12/12 old-positive IDs. Do not credit the 12 again. **2,542,514,364** signed-untested, **2,542,514,308** neither signed-tested nor among separate 56 structural vetoes. | `ROUND19_REPLAY.md`, `ralph/critic/round_019.md` | prior |
| confirmed round 18 | C-044, marked cap-five 16/17 slices `(67,5;2333,3334)` and `(68,4;2333,3334)` only: 32,340→46→0 and 28,301→24→0, 69 fresh signed failures. Scout R's separate 56 at H=13 are disjoint from both. | `ROUND18_REPLAY.md`, `ralph/critic/round_018.md` | prior |
| confirmed earlier | C-042 `(71,5)`: 35,458,804 labelled raw excluded; C-043 gives 2,542,514,492 / 15,051,526,031 both marginals. C-039/40 exclude two-neutral 17/17. Cap-five K3,3 22/21 impossible, 1,298 tight e≤64 local marks open. Prior R(7), R(6) no-P4, marked `f*=9`/diagonal-four are in `ROUND{4,5,6,7,8,9,11,12,15}_REPLAY.md`. | `ROUND17_REPLAY.md` and cited past round notes | prior |

## Jobs

**None.** All foreground runs exited; no detached PIDs, SATs, candidates
or unrestricted-case debits. One worker, peak RSS 10,316 KiB, 256 MiB VM.

## Next

1. Ask critic to review the shared-degree lemma and paired toy only;
   H may formalize the short disjoint-edge counting step if useful.
2. Park as directed. No fifth-row scans, extra bins, new pairs, or signed
   joins. Do not interpret the toy as evidence of target throughput or
   exclusion; queue nothing without a new directive.
