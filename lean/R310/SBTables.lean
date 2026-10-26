/-
Tables for the SB checker: edge orders and the colex index, checked by the kernel.
-/
import R310.LexLeader
import R310.SBCore

namespace R310.SB

open R310 R310.Enc R310.Files

/-! ### Edge orders and the colex index -/

theorem pairOf_spec : ∀ t < 780, (pairOf t).1 < (pairOf t).2 ∧
    xid (pairOf t).1 (pairOf t).2 = t + 1 := by decide +kernel

theorem pairOf_xid : ∀ i j : Fin 40, i < j → pairOf (xid i j - 1) = (i, j) := by decide +kernel

end R310.SB
