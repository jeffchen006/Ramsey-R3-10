# Lane H — round 22 handoff, November 22, 2026

Two-core ceiling; one pinned foreground worker, no SAT, candidate,
live/detached/stopped PID. Checked through round 021: **238 near-regular
MTF distributions plus Case R**, **ten conditional U88 keys**, and
**three conditional mixed cores** (`6,9,18`) remain. No distribution
debit or flow graph. The marked aligned `h=8` and marked `h=7` e170
slices are closed separately; they do not exclude the whole equality
case. B's five critical keys are absent and host floor is still 108.

## Jobs

| PID | Command | Log | Cores | Start / actual end CET |
|---|---|---|---:|---|
| — | No live, detached or stopped job | — | 0 | — |
| foreground, finished | `bash build_private_signature.sh` (development, cached `--old build R310`, targeted and project axioms, version) | `scratch/H/round22-{build-final,combined-build,axioms-targeted-final,budget-axioms,combined-axioms,combined-strict,toolchain}.log` | 1 pinned CPU | ~19:24–19:36 |
| foreground, finished | `python3 -SB check_folded_slot.py` and `check_card_degree_budget.py` (wall/VM caps) | `scratch/H/round22-{controls-final,budget-controls}.log` | 1 pinned CPU | ~19:29–19:35 |
| foreground, finished | Primary source fetch and focused arXiv/Crossref discovery | `scratch/H/round22-{literature,extra-sources}.log` | negligible | ~19:28–19:30 |

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean H-037 (pending) | One physical vertex per selected slot pair, with distinct vertices for distinct selected pairs independently of masks. Actual contact overlap forces a nonedge in a triangle-free graph. Proves guarded equality of two slot/grid descriptions and two slot/slot descriptions. Does not derive populations, label extraction/exhaustion, MTF/padding rows, or bind a CNF. | `lean/R310/FoldedSlot.lean`, `ROUND22_REVIEW.md`, `ROUND22.sha256` | 0.04944 timed all |
| enum (controls) | C13(1,5) alpha=4; 52 oriented marks, 312 selected grid edges checked (104 true, 104 asymmetric clashes), and 624 mismatches under unselected guards. Duplicate full masks distinguish two grid rows; 24 labellings and both reuse mutations. Optional/optional plant: 36 labellings, one true edge and two asymmetric clashes each. Lean/Mathlib v4.35.0 final build and strict 5/367 axioms pass. | `check_folded_slot.py`, `scratch/H/round22-{controls-final,build-final,strict-final,toolchain}.log` | included |
| Lean H-038 (pending) | C-050's generic disjoint-set count and graph wrapper: sum of additions into disjoint physical groups bounded by actual degree minus every prescribed incidence. Card-specific lower bounds remain premises. 3,328 C13 allocations, 1,053 tight, both overlap and prescribed double-count mutations fail. Combined Lean/Mathlib v4.35.0 build and 2 extra targeted / 369 project reports pass. No target replay or exclusion. | `lean/R310/CardDegreeBudget.lean`, `ROUND22_REVIEW.md`, `ROUND22.sha256`, `scratch/H/round22-combined-strict.log` | 0.02072 additional, 0.07016 total |
| ledger (confirmed 021) | Confirmed all twelve lane claims as scoped. N-010/011: 51→235→1,213 keys, six local proofs add 978 beyond G, separate estimates. E-046: conditional core 1 565,384 inherited weighted negatives +32 prior +115 fresh. D-050/R-007: 159→150→149 supports, 250,440 wing orbits, not kernels. N-012/013: complete e96 parent source, puncture floor ≥97 not e108 host floor; conditional e86 overlap and negative pilots. T21/referee21 absent. | `ralph/CLAIMS.md`, `ralph/critic/round_021.md` | — |
| ledger (pending 022) | Staged A-035/036, B-042, C-052/053/054, D-052, E-048, F-040, G-059 and H-037/038. D's 149 local replay IDs match the manifest; E's terminal counts 277/630/255 and F's first 405 rows have provisional audit evidence, not confirmed case debits. G is running the balance of its calibrated `h=6` queue. | `ralph/CLAIMS.md`, lane STATE files and named evidence in each row | — |
| pub / open (limited search) | DS1 rev. 18 unchanged at 40–41; journal §7 is partial lower count 43,225,483. McKay unchanged. No newer decision, public bulk order-39 data, or exact 30/88–99 count located. Screen includes three constructive papers, no reusable finite target. | `LIT.md`, `scratch/H/round22-{literature,extra-sources}.log` | negligible |

## Next steps

- Import critic round-22 verdicts and referee report if produced. Keep
  claimed marked slices distinct from any original kernel/distribution.
  Reconcile any final receipts posted by D/E/F/G after H's cutoff with
  the provisional rows before importing critic decisions. D's 149/149
  matched replays give the strongest scoped regular evidence; E's
  residual check archives and G's two-defect board splits are next.
- H-037 and H-038 need independent re-elaboration and strict axiom check against
  frozen artifacts. G can cite physical semantics; the SAT binder and
  global board cover remain separate. C's shared-budget target gate
  remains parked after the negative pilot; its Lean counting step
  does not justify a new campaign. No duplicate solver or binder.
