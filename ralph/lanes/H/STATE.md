# Lane H — round 3 handoff, November 21, 2026

Critic's round-3 share: two cores; used one for bounded foreground work.
No flow-verified order-40 graph. Prior handoff and old PID records are
in `LOG.md`; the accepted full Lean/PB exports remain untouched.

## Jobs

| PID | Command | Log | Cores | Start / finish |
|---|---|---|---:|---|
| — | No live or detached H jobs. | — | 0 | — |
| foreground | Targeted `lake build --old R310.PathWindow`, `lean -j1 -s8192` axiom reports; see `LEAN_REPRO.md`. | `scratch/H/p4-lean-{side-build,axioms-final,axioms-final-audit}.log` | 1 | 19:03–19:05 |

Previously listed PIDs from round 2 are gone. All round-3 shell/control
tasks have ended; no solver used. Targeted Lean runs used timeout, nice,
CPU pinning and 16 GiB virtual-memory limit.

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean (H-003, H-004) | P4 maximality cross-edge criterion, both projected side-counting rows (including the outer-block row with an extra middle root). Three named axiom reports accepted by checker. No census, CNF, or proof-coverage formalization. | `lean/R310/PathWindow.lean`, `LEAN_REPRO.md`, `AxiomsRound3.lean`, `scratch/H/p4-lean-axioms-final-audit.log` | 0.040 incl. early iterations |
| enum (controls, H-005 pin split) | 42 C21 span controls, C10 cross edge, both premise counterexamples, 164 side-subset checks including 26 tight nonempty outer rows. Independently matched exact 7/6 target pin keys by adjacent-swap orbit closure and exact three 2×2 control keys. | `check_p4_cross_control.py`, `check_p4_pin_cover.py`, `scratch/H/{p4-cross-control,p4-pin-cover}.log` | <0.001 |
| hand | Audited the one-side bridge, unknown-side constraints, and row/column relabelling. Opposite middle root is safe with the nonadjacent outer block only. No independent proof replay. | `P4_SIDE_REVIEW.md` | — |
| pub/open | Targeted latest literature and data refresh. No later exact solution, public GR–Angeltveit order-39 bulk file, public 33/119 file, or exact dense order-30 count found. Zero implications from that absence. | `LIT.md` | — |

Ledger mirrors round 002: G-004 floor 119 is gluing-independent; G-005
63 incremental e166 cuts; G-006 one conditional e167 cut, giving 454
near-regular plus R and 20 genuinely incremental e88-dependent cuts;
G-007 partial e119 proofs; E-008 strengthens the `(2,30)` W bounds.
A-003's independent P5 coverage manifest and C's PATH_INPUTS both
passed SHA-256 checks. C-009 remains `enum`; local H lemmas do not
upgrade its label. R(7) stays the accepted custom certificate only.

## Team status and next steps

Best near-regular evidence: G reports recovering all six missing classes
and 74 checked LRATs for the 5+69 catalogue. G-009 awaits the exact cover,
binding and distribution audit. If accepted it removes 55 additional
e167 distributions with n6>0 (399 near-regular plus R, before any later
cuts). Do not count it yet or add e88-dependent cuts without updating
overlaps. B still has no full e88 gluing cover. Regular: A independently
matched all P5 layouts; C now reports full P4 producer coverage (1,187
unpinned plus 1,035 pinned proofs). C-013 awaits independent proof
provenance/coverage review. Even if accepted, R(6) is still open.
E's new W≥5 exclusion is pending and W4 remains open; F's best remains
I10=44, no verified witness.

1. Mirror the critic's new verdicts, especially G-009; keep original
   63/69 status as a historical partial result and distinguish the new
   count from the accepted total. Use A's bundle rather than resuming
   any proof-preservation jobs. No second e119 census or P5 join.
2. For any P4 result keep the hand/Lean bridge separate from coverage
   of the LRATs and from unsolved P2/P3 branches. Get C's final
   per-row/pin manifest before any broader lemma claim.
3. Read E's completed bridge if requested. Keep targeted Lean builds
   and standard-axiom reviews; no full rebuild without changed inputs.
