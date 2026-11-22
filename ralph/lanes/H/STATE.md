# Lane H — round 12 handoff, November 22, 2026

Share two. No H candidate or whole-distribution subtraction. Confirmed
through round 011: **278 near-regular MTF distributions plus Case R**,
10 conditional U88 and 20 open e168 d6 (11 single, nine paired). There
are nine confirmed remaining conditional E cores (eight if E-032 is
accepted). B's five absent classes persist after the named 7,954-parent
wave. Floor 109 has two distinct remaining gates (census and extension
cover); see `ROUND12_REVIEW.md`.

## Jobs

| PID | Command | Log | Cores | Start / end CET |
|---|---|---|---:|---|
| — | No live, detached or stopped H jobs. | — | 0 | — |
| foreground, finished | Pinned `build_private_signature.sh`: three single-file checks, `build --old R310`, targeted and integrated axioms | `scratch/H/round12-{witness-first,window-first,window-second,window-cap,build,targeted,project}.log` | 1 | ~06:08–06:15 |
| foreground, finished | `python3 -SB check_round12_controls.py` and separately `check_round12_b.py` under time and RAM limits | `scratch/H/round12-{controls,b-audit}.log` | 1 each | <4 s each |

No solver, LRAT checker or large source generation in H. Pinned
Lean/Mathlib v4.35.0 existing cache only; no source build of Mathlib.

## Results and claims

| Label | Result | Evidence | H core-h |
|---|---|---|---:|
| Lean, H-024 pending | D's distinct witness cannot meet two endpoint-disjoint same-witness pairs; given external disjointness and diversity, root-choice conclusion. Not a disjoint-P3 or solver theorem. | `lean/R310/DeficientWitness.lean`, `scratch/H/round12-{targeted,controls}.log` | shared below |
| Lean, H-025 pending | C's `10+p−h` and cap-five max 22 with equality criteria. Three pairs with codegree five and a supplied window `≤20` give `h=5` and order 20. Four targeted / 310 integrated axioms approved. Local orders 22/20/21/21 all planted; no 22/21 or 22/22 certified in Lean. | `lean/R310/ReciprocalWindow.lean`, `scratch/H/round12-{project,controls}.log`, `ROUND12_REVIEW.md` | ~0.05 combined Lean checks and build |
| enum provenance only | Exact completed B queue (33 shards / 7,954 parents), 15,204 raw outputs and 1,724 old-only keys independently bound; frozen 2,102,271+1,875 partition and 47-key receipts re-bound. Not a semantic lift replay or closure. | `check_round12_b.py`, `scratch/H/round12-b-audit.log` | 0.0010 |
| open (dated search) | No superseding decision, bulk Angeltveit/GR file or dense order-30 count located. April 2026 double-saturation paper reports >100 order-39 examples but its linked artifact gives no graph list. | `LIT.md`, `scratch/H/round12-literature.log` | — |

## Ledger and next steps

- Imported critic round-011: C-033 completed independent replay and
  exact 32 repairs, with separate corollary C-035; D-023–026 caught
  up (111 necessary roots but no path-disjoint theorem, local 1,351
  proofs apart from mono-witness enum); full independent G-037 binding
  has 72 fresh critic dual replays, not all producer proofs freshly
  checked by the critic. A/G small pivot reductions are scopes only.
- New A/B/E/F and H round-12 rows pending. Check late C/D/G reports
  against the next critic; do not count live pilots or infer a whole
  subtraction. The paired-window and tight-triple scopes differ.
- Recommend critic price/approve only B's remaining 545 named
  provenance-unbound parents (~21 CPU-s lift estimate), not broad
  lifting. If recovery reaches five, audit the partition and
  semantic extension-cover prerequisites per `ROUND12_REVIEW.md`.
  D's internal-witness restriction and C's smaller 22/20 marked
  followup have stronger current evidence than a fresh broad search.
