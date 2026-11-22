# Lane C — round 17, November 22, 2026

**No candidate. R, R(5), and one-neutral 16/17 remain open.** An exact
weighted filter for the marked one-neutral cap-five K4,4 16/17 roster
leaves **2,542,514,492 / 15,051,526,031** labelled headers. Of those, 47
already have incompatible joint packages (round 16); exact untested
joint frontier **2,542,514,445**. The `(D16,d16)=(71,5)` subcase alone
has no survivor and has a complete independent first-direction check.
No production header expansion, no new joint or terminal scan, no SAT.

## Results / claims for H and critic

| Label | Scope | Evidence | CPU-h |
|---|---|---|---:|
| hand, pending | Exact individual group existence depends on full labelled destination adjacency + neutral and on source row-size/neutral-demand multiset. Sizes 2/3/4; full-profile conjunction. At fixed host pair the intersection is the product of the two filtered weight sums. No identification of complete physical headers or terminals. | `proofs/panel17_weighted.md` | — |
| hand + enum, pending | 582,982 compatible host pairs, 549,727 with positive intersection. Native counts 10,171,596,865 forward, 3,748,552,858 reverse, 2,542,514,492 both. Raw mass 15,051,526,031 independently bound for all 34 shapes; every host-product calculation and 440 deterministic group receipts independently checked. Largest host-pair raw/both weights 148,356/60,480, largest one-sided cells 84/66. This is not exhaustive independent replay of each target predicate. | `ROUND17_REPLAY.md`, `scratch/C/r17/{target.count.log,target.arith.log,target.receipts.log,target.buckets.tsv}` | 0.0542 native + independent target audits only |
| hand + enum, pending scoped exclusion | `(71,5)` zero forward: covers 35,458,804 labelled headers; complete independent hitting recheck of all 76 group predicates for 1,238 profiles across the two possible destination host/neutrals. No reliance on reverse results. Other five zero shape strata lack this complete extra predicate audit. | `scratch/C/r17/{stratum.count.log,stratum.arith.log,forward-zero.log}`, `ROUND17_REPLAY.md` | 0.0056 including arithmetic / receipt / forward checks |
| enum, calibration | All 34,504 smaller literal IDs in both directions, 29,220 host pairs, all 153 physical plants (A); 31,495 both pass. All 544 bound target pilot IDs match both existing uncompressed literal domains and independent hitting (47 both/140 forward-only/96 reverse-only/261 neither). | `scratch/C/r17/{small.check.log,pilot.audit.log}`, `scratch/A/r17-stream/{small.log,small-xcheck.log,pilot.log}` | 0.0396 native + independent small/pilot (excluding builds) |
| enum, clean replay | 17 deterministic files matched byte for byte, including the full host-pair table. C charged CPU (both passes, all builds and checks) is below the 0.25 core-h cap. | `ROUND17_FREEZE.sha256`, `scratch/C/r17/{clean.compare.log,budget.log}` | 0.21802 cumulative |
| prior confirmed, round 15 | C-039/40: 17/17 two-neutral marked case excluded; 92,341,930 direct + 65,130,071 by exchange, both bits/all diagonals. | `ROUND15_REPLAY.md`, `ralph/critic/round_015.md` | prior |
| prior confirmed, rounds 11–12 | Cap-five K3,3 22/21 impossible; tight window e≤64, 1,298 tight marks open. | `ROUND{11,12}_REPLAY.md`, `ralph/critic/round_{011,012}.md` | prior |
| prior frozen, rounds 1–9 | R(7) excluded; R(6) no P4; f*=9 (12,12) impossible with 1,134 CakeLRAT; (12,14) K12 has 16≤e≤21, 24/39 profiles open. Diagonal-four P3 8/8: 34/105 patterns contradicted; 71 patterns and 330 rows open. | `ROUND{4,5,6,7,8,9}_REPLAY.md` | prior |

## Jobs

**No active or detached jobs.** Main count (foreground PID 979439,
one core) finished normally. Complete clean replay foreground wrapper
1065369, one core, ran c. 13:27:25–13:34:55 host time (wall cap 780 s).
Command `nice -n 5 timeout 780 bash ralph/lanes/C/replay_panel17_weighted.sh full <root>/scratch/C/r17-clean <root>/scratch/A/r17-stream`.
Logs in `scratch/C/r17-clean/`; each stage `prlimit` and 512 MiB VM.

## Next

1. Critic: review and ledger the exact first filter and the scoped
   `(71,5)` exclusion separately. H may formalize the finite-product
   identity or the row/group permutation lemma. The count is not cert.
2. Do not scan the 2.54B survivors. If authorized, first recover all
   physical IDs for the smallest nonzero shape strata `(67,5;2333,3334)`
   and `(68,4;2333,3334)` (46 and 24 labelled survivors). Keep original
   marks, actual physical singleton labels, neutral, and transpose
   orientation when binding both directions. The quotient does not
   identify full headers.
3. For larger frontiers, seek a stronger sparse gate; do not infer a
   runtime from the 544 pilots. No effect on 17/17, 15/17, 16/16, cap
   six, or any unmarked case.
