# Lane H: literature scout, claim ledger, Lean

Start share: 4 cores.

## Do
1. **Literature** (web reading only): every result on R(3,10) and on (3,k)-graph enumeration since
   2024: Angeltveit (arXiv:2401.00392, later versions), Angeltveit-McKay, Goedgebeur-Radziszowski,
   SAT+CAS (Li, Duggan, Bright, Ganesh 2025), SMS (Kirchweger-Szeider), anything from 2025-2026.
   Is R(3,10) still open today (2026-11)? Is the GR/Angeltveit set of (3,10,39)-graphs public now?
   Are there new class counts for R(3,9;30,e), e >= 88? Write `ralph/lanes/H/LIT.md` with exact
   citations and what each means for lanes A..G; post the important ones on the BOARD.
2. **Claim ledger** `ralph/CLAIMS.md`: one row per claim of this run (id, lane, statement, label,
   evidence file, critic verdict). Copy new claims from the lanes' STATE files each round; never
   upgrade a label yourself.
3. **Lean**: make the `lean/` project build here (Lean 4 v4.35.0, Mathlib v4.35.0; elan is in
   ~/.elan; `lake exe cache get`, do not build Mathlib from source; check the axioms script). Then
   formalize the short new hand lemmas of lanes C and G (ask them on the BOARD for the statements).
4. Each round: one paragraph in your report on what the whole team has found so far, and which
   direction has the best evidence (the critic reads it).
