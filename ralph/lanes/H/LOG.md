# Lane H — archived round 2 handoff, November 21, 2026

## Round 22 archive

- `ROUND22_REVIEW.md` and `ROUND22.sha256`: added H-037 (physical
  selected-pair injectivity and guarded fold equivalence) and H-038
  (disjoint degree-budget inequality); 7 targeted / 369 project
  axiom reports, C13 and equal-mask controls, 0.07016 core-h.
  Both confirmed independently in critic round 022 and imported in H23.
- Round 22 H staged twelve r022 claims and imported all twelve r021 lane
  verdicts plus six scout rows. Some late submissions were not yet final;
  `ROUND23_REVIEW.md` documents the scoped reconciliation. T21 and
  referee21 had no artifact. Literature recheck in `LIT.md`.

## Round 17 archive

- `ROUND17_REVIEW.md` and `ROUND17.sha256`: imported round 016 and
  formalized pole-pair exterior multiplicity. 5/344 axiom reports;
  600 smaller MTF rows distinguish the endpoint and witness premises.
- The round-17 critic confirmed H-032, the late D-044 marked closure,
  conditional E-041, A/C's exact necessary filter and the two separate
  F results. The four-worker D snapshot was obsolete before close.
  Round 18 imports those scopes, not any additional degree distribution.

## Round 16 archive

- `ROUND16_REVIEW.md` and `ROUND16.sha256`: imported round-015
  verdicts; H-031 Lean middle-star at marked t=17,m=16 gives 2/2/4
  row contacts and two-contact columns under the explicit local floor.
  7 targeted and 339 project axiom reports, Petersen plus blow-up
  and incidence controls pass. ~0.0693 core-h, no solver jobs.
- Round-16 critic later confirmed H-031, the F family scope chain,
  and the existing 238-key balance. See `ROUND17_REVIEW.md` for the
  imported ledger and the separate H-032 middle-as-witness premise.

## Round 14 archive

- `ROUND14_REVIEW.md` and `ROUND14.sha256`: ledger through round 013;
  pinned Lean old-card pole contacts and two-term book footprints had
  8 targeted and 327 project axiom reports. Controls: 388/5,789 small
  triangle-free graphs and 7,456 C13/regular C22 footprints. No H jobs.
- Round-14 critic then accepted H-028/029 and core 5, and confirmed the
  scoped A/C ordered prefix only. See `ROUND15_REVIEW.md` for imported
  statuses and the separate new 17/17 submission.

## Round 9–10 archive pointers

- `ROUND9_REVIEW.md` and `ROUND10_REVIEW.md` contain the replay/binding
  notes for the kernel reroot, reciprocal coverage, incidence rounding,
  and B/G receipts. `LEAN_REPRO.md` has the pinned-cache commands and
  earlier axiom totals. No detached H job survived those rounds.
- Round 10 supplied H-020/021 (critic confirmed), 334 equal and 395
  asymmetric controls and 50,625 small matrices. B's 61 and G's 215
  round-10 H checks were receipt identity only; use the separate
  critic reports for fresh proof replay.

## Round 8 archive

No detached H jobs. `CompletionBridge.lean` proved arc-shrink and
paired/rooted order/alpha bridges; 4 targeted and 284 project axiom
reports pass (~0.043 CPU-h). H independently checked C-026's two P3
layouts (30/60 bound residue rows and 20 required vs 16 possible single
occurrences) and G's interrupted unique receipt counts, not final
G production proofs. `ROUND8_REVIEW.md` and `scratch/H/round8-*.log`.
Initial G/A/E ledger entries subsequently replaced by the critic's
terminal scopes in round 9. Last broad literature refetch is in `LIT.md`.

## Round 7 archive

H-016/H-017: pinned Lean/Mathlib v4.35.0 build, five targeted and
280 project reports; 18 C5 path-window controls, 18 rejected triple
mutations, all 32,520 generic pair accounts checked. Window cap 84,
or 82 with no d8 in X; at least one cap-83 window on the both-path
n8=4 branch. The common exterior must meet both pivot sets by MTF.
Reviewed D max12/smax2 dense/balanced split; no pin closure. Critic
confirmed these scopes in round 007 (`ROUND7_REVIEW.md`, `LIT.md`).

## Round 6 archive

No detached jobs. H-013 and H-014 formalized the no-exterior-degree-
five hand bridge and the two e168 peer profiles, conditional on
G-019/the Ramsey bound and on the residue floor/adjacent peer,
respectively. H-015 classified the two marked additions into the
three shapes, checked by all five-label patterns and 52 oriented C13
controls. Five targeted/275 project reports, 0.07 CPU-h Lean total.
`ROUND6_REVIEW.md` and `check_round6_scope.py` bound the 278+R,
ten U88 and 11+9 e168 keys. Critic round 006 confirmed all at their
stated scopes. The literature recheck did not find a resolution,
public bulk order-39 file or new exact 30/88–99 count.

## Round 3 archive

No detached H jobs. Targeted `R310.PathWindow` build/axiom checks ended
at 19:05 CET on one core. H-003/004: the P4 cross-edge criterion and two
projected independence rows passed three axiom reports. H-005: independent
adjacent-swap closure matched 7+6 target pin keys and three 2×2 control
keys. `LEAN_REPRO.md`, `P4_SIDE_REVIEW.md` and `scratch/H/p4-*` retain
reproduction and controls. This did not check proof coverage or close P4
by itself; C-013 was separately accepted. Historical G-009 pending scope
was superseded by the critic's round-003 verdict.

Core share 4. No flow-verified `(3,10,40)` graph. Read the new critic
directives, allocation and BOARD. Round 1 details are in thread artifacts
and the reviews; never treat R(7) as closing all regular graphs.

## Jobs

| PID(s) | Command | Log | Cores | Start / finish |
|---|---|---|---:|---|
| — | No running H jobs | — | 0 | — |
| 2792146 / 2792150 / cache 2795221 / leantar 2803817 | `timeout 3120 taskset -c 148-149 bash ralph/lanes/H/lean_round1.sh` | `scratch/H/{cache-download,mathlib-cache-check,lake-build,axioms}.log` | 2 | 17:56:31 / 18:16 (legacy axiom read retry required) |

Old cache job 1253143/1253159/1253379 hit its fetch cap (exit 124).
Probe 2729770/2729780 downloaded all 9,031 files and hit its 100-s cap
while unpacking; the ordinary Lake job resumed successfully. Integrated
build and both single-threaded axiom checks ran in the foreground and
finished. No solver jobs were started. Do not restart old job IDs.

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean | Built pinned Lean v4.35.0 project with `lake exe cache get`, then checked all 9,045 Mathlib targets without building Mathlib from source. Integrated build succeeded. The legacy 263 reports and 15 new reports contain only standard axioms. | `LEAN_REPRO.md`, `scratch/H/{cache-download,mathlib-cache-check,lake-build,lake-integrated,axioms-one-legacy,axioms-one-new}.log` | about 0.30 for cache/verified builds/audits, excluding failed pilots |
| Lean (H-002) | C's mask/residue and biclique rows, four-root endpoint step (diagonal nonedges supplied), local overlap identities, G's typed wedge identities. Ramsey bounds are hypotheses where needed; no full path census or LP run is formalized by these lemmas. | `lean/R310/{Residue,PathWindow,Wedge}.lean`, `AxiomsRound1.lean`, `scratch/H/axioms-one-new-audit.log` | included above |
| cert (H-001, A-001 scope) | Full `R310.Files` emits 99,701 / 99,700 / 99,700 constraints, byte-identical to provisional R/S8/N. A's binder checks all 189,418 retained PB rows and proof artifact hashes. No SAT cube cover or new UNSAT claim. | `scratch/H/{project-export-direct,pb-bind}.log`, `LEAN_REPRO.md` | 0.007 |
| hand | Audited C P4/P5 overlap and port coverage, E t=1 crown no-isolate bound, D's saturated biclique bound. P5 trace checks supplied residues only, and remains `enum` pending critic acceptance of the chain. | `PATH_WINDOW_REVIEW.md`, `CROWN_REVIEW.md`, `BICLIQUE_REVIEW.md` | — |
| enum control | Independent C21 local overlap check passed all 42 P4 and 42 P5 oriented controls; corrupted nonpath rejected. No C8 replay this round. | `check_path_control.py`, `scratch/H/path-control.log` | <0.001 |
| pub / open | Literature updated; published bounds remain 40–41 in sources found through Nov 21. No public GR–Angeltveit bulk census or exact new order-30 dense level located. | `LIT.md` | — |

Ledger mirrors critic round 001: C-004 is `cert` (custom trace + hand
reduction with published seeds, not Lean); C-007 is `enum`; G-001 retains
both gluing floors. G-002's 30 thresholds include six already conditionally
excluded, so a complete MTF e88 result removes at most the additional 24
as counted at the start of round 2. G-004 is recorded only at e(H6)=118
for e(G)=166 until the residual edge level and exact affected keys are
linked to the new certificate. See BOARD request at 18:13.

## Team status and next steps

R(7)'s accepted trace remains strongest overall. C/A's overlapping window
method gives the most convincing new regular-case evidence: P4 cover
matched independently (2,454 rows), P5 supplied-residue replay checked
all 1,156 residues, and P4 remains open after the local reduction to
1,356 rows. D still has 110 rooted R(3) orbits. E's f=32 t=1 and f=30
window exclusions retain enum, G's exact five-residue branch has a narrow
ledger row, B has not covered e88, and F has no witness.

1. Mirror new reviewer verdicts. Get G's dependency and affected-key list
   before combining e166 exclusions with gluing-dependent results. Get
   independent P5 cover verification/critic acceptance before promoting it.
2. Ask C for the next short local statement, especially the MTF forced
   cross-edge criterion. Do not rerun C8 or regenerate historic R(7) cubes.
3. Keep `scratch/H/lean-artifacts` and pinned `packages-local.json`; builds
   use `--old` and `-j1 -s8192` for direct axiom reads. No heavy
   `R310Cases` table rebuild this round. Full-cube provenance is now bound;
   no reason to revisit unless inputs change.

## Round 4–5 archive pointer

Round 4 proved the MTF demand/attachment lemmas and the degree-six total
edge-floor bridge. See `LEAN_REPRO.md`, `FLOOR6_REVIEW.md`, and H-006–008.
The historical 376+R, U88=13 and 47 e168 degree-six cases predate G's
eight cuts. Round 5 proofs and their precise scopes are in `LEAN_REPRO.md`
and `ROUND5_REVIEW.md`.

Round 5's `check_private_signature_control.py` matched 13 C13 equality
roots, 52 doubles and 208 of 1,872 tight common-anchor family checks;
K2,3 serves as the no-full-cell negative control. The 12/270 Lean
axiom checks passed. Its preliminary tracking of 368+R and 12 U88
is historical after the round-005 critic confirmed 278+R / ten U88.
# Round 13 archive note

The prior round-12 handoff is superseded for status by the critic's new
degree-six floor and 40 exact removals. Round-12 details and scripts
remain in `ROUND12_REVIEW.md` and `scratch/H/round12-*`; the 278 baseline
is a historical denominator and the e168 strip work is not additive.

## Round 19 archive

H-034 proved only the capacity `t+(4−s)` and its transpose; 216
small physical-site controls, 3/356 axiom reports, 0.04003 core-h.
See `ROUND19_REVIEW.md` and the historical round-19 freeze. The
critic confirmed the capacity implication in round 019; the lower
matching implication is the separate, new H-035. The round-18 checked
G balance 79,072 and C balance 2,542,514,376 are historical after
round-19 review. No H jobs carried forward.

## Round 20 archive

H-035 derived a physical partial matching from the two independent
shores, isolated site and local cap via Hall. Used 170 controls,
3/359 axiom reports and 0.02196 core-h. See `ROUND20_REVIEW.md` and
`ROUND20.sha256` at the round-20 snapshot; the critic confirmed it in
round 020. H-036 supplies the cap and cell geometry from graph
contacts. The open 21,125 `h=8` count was then historical after G-056.

## Round 21 archive

H-036 derives cap five and the physical Hall row margin from actual
root contacts and alpha at most nine by padding with four unused
neighbours. Equality populations and contact membership remain inputs.
78 C13 pairs plus tight and adverse contact fixtures, 3/362 strict
axiom reports, 0.04021 core-h; confirmed round 021. See
`ROUND21_REVIEW.md` and the round-21 snapshot of `ROUND21.sha256`.
No H jobs carried. G's 978 then-open `h=7` contexts are historical
after N-010; conditional mixed core 1 has also closed.
