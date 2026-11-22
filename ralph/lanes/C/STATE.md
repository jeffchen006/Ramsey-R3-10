# Lane C — round 9, 2026-11-22

R(3,10), Case R, R(6), and global `f*=9` remain **open**. No candidate.
`J` is the codegree-six graph, `f*` the minimum wing cross count among
its pairs. P2 means an isolated J edge, never an arm of a P3. For the
P2 `(12,14)` split the order-19/21 windows have private cores 12/14
and no shared core U. In the P3 round-9 files U instead counts triple
T-incidences; keep the notations separate.

## Results and claims for H / critic

| Label | Scope and result | Evidence (lane-relative unless stated) | CPU-h |
|---|---|---|---:|
| hand + enum, pending | R(6) diagonal-four 8/8 P3: all 71 surviving zero multiset keys audited independently. If `U,V` count triple and quadruple common incidences, `S+2q=20+U+2V`; 47 keys force `U=V=0`, 24 force `V=0,U<=1`. No additional zero-pattern or layout/residue exclusion. | `proofs/p3_rounded_incidence.md`, `ROUND9_REPLAY.{md,sha256}`, `scratch/C/r9/{excess.json,excess-independent.log,excess-bad.log}` | 0.013 discovery + both replays |
| hand + enum, pending | Unique-zero keys `1:0:1:1:1/0` and `3:0:1:2:1/0`: `3S<=56/55`, exactly 18 singleton and three double rows. Expanded unaveraged weighted avoider-deficit + mask-margin budgets at most 2/1. Raw e62 check reports all allowed mask margins nonnegative. | `proofs/p3_rounded_incidence.md`, `scratch/C/r9/{rounded.json,rounded.log,tight-build.log}` | 0.003 |
| enum / estimate | Held-out e62 `1:0:1:1:1`: independent-six-set wing join, same exact 336 zero positions, partial tuples 28,720,249,242→971,463 and CPU 320.175→115.566 s; all positions and all 24 rows survive. Six scout rows also all survive. Same-column consistency within each triple; no combined wing lift. | `p3_six_join.py`, `scratch/C/r9/{base,index}-{scout,heldout}.{tsv,log,time}`, `pilot-compare.log` | 0.152 |
| enum / estimate | Same six e62 scout rows: 455,546 shared T covers→300,018 with tag-budget DP, 21.964→23.733 traversal CPU-s, all 84 positions survive. Exact C21/arithmetic controls. | `p3_{common_cover,tag_join}.py`, `scratch/C/r9/{common,tag}-scout.{log,tsv,time}` | 0.014 |
| open | e62 layout row 17 only: pin vs tight SAT, both exit 137 at 45 CPU-s hard cap. No terminal solver result/proof; partial traces deleted. Do not scale. | `p3_tight_sat.py`, `scratch/C/r9/tight/{pin,tight}-17.{cnf,log,rc,time}` | 0.025 |
| confirmed C-026/C-027 | R(6) diagonal-four 8/8: two named layouts give 90 excluded layout/residue rows (30+60); 34/105 conditional zero-pattern obstructions; 71 patterns and 330 layout/residue rows remain. Round-9 reproduction byte-equal; all nine q≤2, q=0 impossible. Two other layouts force q=2 (`1:0:1:1:0`, `3:0:1:2:0`). | `ralph/critic/round_008.md`, `ROUND8_REPLAY.{md,sha256}`, `scratch/C/r9/freeze-*` | 0.005 replay |
| confirmed C-025 | Global R(6), f*=9, `(12,14)`: smaller private K12 has 16≤e≤21. Four e23/24 profiles empty. 11 terminal profiles; 24 of 39 open with 368,851,704,416 pre-column maps. Round-8 index gave only 1.51× end-to-end. | `ROUND7_REPLAY.{md,sha256}`, `ROUND8_REPLAY.md`, `ralph/critic/round_007.md` | prior |
| confirmed C-024 | Global R(6), f*=9 rules out `(12,12)` wing union sizes; at most one shared vertex. Full 1,134 CakeLRAT replays. | `ROUND6_REPLAY.{md,sha256}`, `ralph/critic/round_006.md` | prior |
| previously confirmed | R(7) excluded; R(6) no P4. P3 diagonal-five residue e≤61, diagonals three/four e≤63. If f*≥8 P3 arms both 8 and diagonal 3 or 4. Global f*=9 makes J a nonempty matching. Isolated f8/e80 has at most one degree-three vertex; anchored X' e≤64. | `ralph/critic/round_{001,003,004,005}.md`, `ROUND{4,5}_REPLAY.md` | prior |

## Jobs

None. No detached jobs this round. Both foreground SAT pilots terminated
at exactly the declared 45 CPU-s cap. All join, replay and LP commands
terminal; replay paths and time files above. Round-8 and older jobs
already terminal as recorded in `LOG.md` and previous replay packages.

## Next

1. H/critic: check `proofs/p3_rounded_incidence.md` and the exact
   independent replay. A short Lean target is the displayed incidence
   identity and `S<=21-2q` forcing no quadruple and at most one triple.
   Claims are new restrictions only; no more closures than C-027.
2. Do not scale either stand-alone join, the e62 SAT pilot, or the raw
   P2 join. If continuing P3, use the new at-most-one triple to design a
   different check that couples actual X and *both* private/common
   assignments, or exploit the e63 budget one before starting solver
   work. The `24` excess-one keys need not realize a triple. The
   join only measured e62 `1:0:1:1:1`; don't generalize times to e63.
3. Untested P2 `(12,13)` still needs U1 logic and calibration; `(13,13)`
   needs H20/K13 catalogues. Isolated anchored f8/e80 e64 (236 keys) is
   a separate bounded option, not a P3 case. No R(7) production work.
