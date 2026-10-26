/-
Mathlib-free core definitions shared by the Lean proofs and the executable `sbcheck`.
-/

namespace R310.Files

/-- A literal: variable id and sign (`true` = positive). -/
structure Lit where
  id : Nat
  pos : Bool
deriving Repr, DecidableEq

/-- Edge variable id of `x(i,j)`, `i < j` (colex): `j(j-1)/2 + i + 1`. -/
def xid (i j : Nat) : Nat := j * (j - 1) / 2 + i + 1

end R310.Files
