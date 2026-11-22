# r310_ralph: final report (run stopped by the operator, 2026-11-22 23:45 CET)

## Answer
**R(3,10) is not decided. It is still 40 or 41.** No (3,10,40)-graph was found (the flow's gate verified none;
`ralph/found/` is empty), and no proof that none exists was completed. All results below are partial results.

## The run
- hmz (humanize) flow `r310_ralph` (`.hmz/flows/r310_ralph/`), a Ralph loop: 8 lanes (A..H) + 1 critic, a fresh
  session every round; the repository files are the memory. Started 2026-11-21 16:32, stopped after round 23
  (round 24 was cut). About 31 hours, 80-core cap.
- Models: lanes on GPT-6.2-sol (SoruxGPT, `codex exec`); from round 8, lanes D, F and the critic on GPT-6.2-astra;
  from round 9, Astra idea scouts every 3 rounds (`review/ideas/`); referee on Claude Opus 5.5 / Gemini 4 Neon via
  agy (ran in rounds 15 and 19; the agy quotas were then spent).
- Every round: the flow's own gate checked `ralph/found/` with two independent algorithms, held the core/RAM caps,
  and committed the round. Round files: `ralph/rounds/round_001.md` .. `round_023.md`; critic reviews: `ralph/critic/`.

## Main results (labels as in `ralph/CLAIMS.md`)
| Block | Start of run | End of run | Key evidence |
|---|---|---|---|
| Near-regular MTF degree distributions N(e), 162 <= e <= 179 | 524 open | **238 open** | G and B lanes; CLAIMS G-*, N-* |
| Case R (9-regular), max codegree c* = 7, R(7) | 99 SAT cubes open | **excluded** (cert, custom trace) | C-003/C-004; `review/R7_CLAUDE_REVIEW.md` |
| Case R, R(6) | open | codegree-6 graph has only components of order <= 3 (C8, P5, P4 excluded); many split cases closed | C-005..C-010 and later C rows |
| Case R, R(3)..R(5) | open | many marked sub-cases excluded; not closed | C, D, A rows |
| Symmetry (prime-order automorphisms) | (5,5), (5,0), (3,f), 18 order-2 cases open | (5,5) cert; many order-2 cases and mixed cores closed; a few cores open | E rows |
| Construction (41 side) | none | none; best degree-valid 40-graph has 44 independent 10-sets | F rows |

Milestones of the N(e) count: 518 (round 1), 454 (2), 376 (3), 278 (5), 238 (12): residue floors at an MTF root of
degree 6 rose to e(G - N[v]) >= 122, at degree 7 to >= 108 (degree 8: 97, degree 9: 88, from gluing).

Ledger: 423 claims in `ralph/CLAIMS.md` (229 hand, 96 enum, 45 cert, 35 Lean, 5 pub, others); critic verdicts:
about 410 CONFIRMED (within stated scope), 3 REJECTED, 2 UNCHECKED, 4 pending.

## Independent checks (not GPT)
- R(7): Claude Opus 5.5 re-derived the hand reduction, re-ran the checker, and wrote an independent search
  (`review/r7_independent.cpp`): same 977,008 cases, no completion; seeds match McKay's published list.
- Referee (Claude Opus 5.5 via agy), rounds 15 and 19: 8 key claims checked, all SOUND, including the degree-6
  residue floor 122 (`ralph/referee/round_015.md`, `round_019.md`).

## What is open
238 near-regular distributions; Case R with c* in {3,4,5,6} (except the closed sub-cases); a few symmetry cores.
The critic's last directives (`ralph/critic/LATEST.md`) name the next targets: D's remaining m = 14 two-pole sectors
and 57 two-flap shapes in R(3); G's 30 open h = 5 boards at e = 170; the 5 missing order-32/e108 critical classes.

## Limits of this upload
- `scratch/` (about 130 GB: solver logs, proofs, LRAT/DRAT files, catalogues) and `opt/` (tool builds) are NOT in the
  repository. Many claims cite evidence files under `scratch/`; they stay on the machine at
  `<root>/scratch/` until deleted. Files over 5 MB were also kept out (`.git/info/exclude`).
- Most results are `hand` or `enum` checked by GPT models; only the items in "Independent checks" were checked by
  another model family. No human has refereed them.
