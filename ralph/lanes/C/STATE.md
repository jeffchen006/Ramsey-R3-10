# Lane C — round 19, November 22, 2026

**No candidate. R and R(5) remain open.** On the preregistered
core-order-12 held-out marked bin, the fifth-row rule rejects zero
of 578 legal rows and fails the go criterion. The unchanged signed
baseline excludes all 12 old-positive IDs of this bin (pending
critic, `hand + enum`). No expansion; no jobs.

## Results / claims for H and critic

| Label | Scope | Evidence | CPU-h |
|---|---|---|---:|
| hand, pending | For `|H|=12`, a completion supplies one physical three-neighbor fifth row compatible with all five restored singleton cards. Outside-core neutral: all k≤3 automatically restorable by deleting neighbors of x from W; with a k=4 card, the five-card filter adds no condition. Inside-core neutral: preserve signed neutral contacts and all allowed residual images. | `proofs/panel19_fifth_row.md` | — |
| enum, negative | Frame16=42679/host97/x0/z7, matching `(66,4)/(75,5)` triple roster only. 116 raw, 928 old-margin bits match; `(00,10,01,11)=(18,86,0,12)`. 356/14 high rooted cards, 578/578 shared rows pass, 12/12 headers pass. Separate indexed and raw-catalogue checks bitwise match. | `ROUND19_REPLAY.md`, `scratch/C/r19/{binding.log,indexed.cards.tsv,indexed.rows.tsv,literal.rows.tsv}` | 0.00046 indexed+literal, first pass |
| hand + enum, scoped pending | The 12 both-old-positive IDs are all arc-empty by unmodified signed baseline, same eight domain lengths and exact zero compatible tuples in independent replay. 33,064 native literal probes, zero caps and terminals. These are new explicit signed failures, not fifth-vetoes; **2,542,514,364** signed-untested / **2,542,514,308** neither covered after separate earlier 56 structural vetoes. | `ROUND19_REPLAY.md`, `proofs/panel18_signed_join.md`, `scratch/C/r19/{pilot.tsv,baseline.stats,signed-audit.log,summary.log}` | 0.00841 baseline+audit, first pass |
| enum, calibration/replay | 105 C35 K2,4 root pairs, 420 cards, 420 shared-row plants and 210 disjoint-pair plants. 1,893 exhaustive small bindings plus per-pole-positive/common-row-negative contact corruption. 15 clean replay matches. | `ROUND19_FREEZE.sha256`, `scratch/C/r19/{controls-final.log,clean.compare.log,budget.log}` | 0.03791 total incl. runs, rebuilds and capped development |
| confirmed round 18 | C-044, marked cap-five 16/17 slices `(67,5;2333,3334)` and `(68,4;2333,3334)` only: 32,340→46→0 and 28,301→24→0; 69 new signed failures. Scout R's separate confirmed 56 at H=13 are disjoint from both. | `ROUND18_REPLAY.md`, `ralph/critic/round_018.md` | prior |
| confirmed earlier | C-042 `(71,5)`: 35,458,804 labelled raw excluded; C-043 gives 2,542,514,492 / 15,051,526,031 both marginals. C-039/40 exclude two-neutral 17/17. Cap-five K3,3 22/21 impossible, 1,298 tight e≤64 local marks open. Prior R(7), R(6) no-P4, marked `f*=9`/diagonal-four are in `ROUND{4,5,6,7,8,9,11,12,15}_REPLAY.md`. | `ROUND17_REPLAY.md` and cited past round notes | prior |

## Jobs

**None.** All capped foreground production and clean replay wrappers
have exited. At most two concurrent workers; 512 MiB VM per process;
2.7 MiB allocated scratch. The initial combinatorial independent-set
control stopped at 60 CPU-s; recursive replacement passed all
controls. The timed failed attempt is charged, not evidence.

## Next

1. Ask critic to check the narrow 12-ID signed result and separate it
   from the negative fifth benchmark. H may check/Lean-formalize the
   deletion monotonicity shortcut in `proofs/panel19_fifth_row.md`.
2. Do not expand or price other fifth bins or the deferred 159-ID
   generic join without authorization. If the fifth route is ever
   reopened, discriminate neutral position and existence of any k=4
   card *before* making a new test roster. Do not use this no-cut
   bin as a performance extrapolation or a full branch exclusion.
3. Round-18 T scout file missing, as predicted by flow. The R scout
   and critic's core-order-13 crosswalk were read, not rerun as a cut.
