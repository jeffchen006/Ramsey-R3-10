/-
Mathlib-free definitions of the SB checker, used by the executable `sbcheck`.
The soundness proof is `R310.SB.checkSB_sound` (in `R310.SBCheck`).
-/
import R310.Core

namespace R310.SB

open R310.Files

/-- Pairs `i < j` in colex order: `(0,1), (0,2), (1,2), (0,3), ...` (index = colex id - 1). -/
def colexPairs : List (Fin 40 × Fin 40) :=
  (List.finRange 40).flatMap fun j => (List.finRange 40).filterMap fun i =>
    if i < j then some (i, j) else none

/-- Pairs `i < j` in row-major order: `(0,1), ..., (0,39), (1,2), ...`. -/
def rowPairs : List (Fin 40 × Fin 40) :=
  (List.finRange 40).flatMap fun i => (List.finRange 40).filterMap fun j =>
    if i < j then some (i, j) else none

def colexArr : Array (Fin 40 × Fin 40) := colexPairs.toArray

/-- The pair with colex index `t`. -/
def pairOf (t : Nat) : Fin 40 × Fin 40 := colexArr.getD t (0, 1)

/-- Colex index of an unordered pair. -/
def eidx (p : Fin 40 × Fin 40) : Nat := xid (min p.1 p.2 : Fin 40) (max p.1 p.2 : Fin 40) - 1

/-- `σ p = (π⁻¹ p.1, π⁻¹ p.2)`. -/
def sig (pinv : Fin 40 → Fin 40) (p : Fin 40 × Fin 40) : Fin 40 × Fin 40 := (pinv p.1, pinv p.2)

/-- Contributions `(c, p)` with `D(x) = val x - val (π x) = ∑ c · x_p`. -/
def contribs (pinv : Fin 40 → Fin 40) : List (Fin 40 × Fin 40) → List (Int × (Fin 40 × Fin 40))
  | [] => []
  | p :: ps =>
    if sig pinv p = p then contribs pinv ps
    else ((2 ^ ps.length : Nat), p) :: (-((2 ^ ps.length : Nat) : Int), sig pinv p) :: contribs pinv ps

/-- Fast version of `contribs`: `k = ps.length` is passed down, `2^k` is a shift
(`contribsFast_eq`: equal to `contribs`). -/
def contribsFast (pinv : Fin 40 → Fin 40) : Nat → List (Fin 40 × Fin 40) → List (Int × (Fin 40 × Fin 40))
  | _, [] => []
  | k, p :: ps =>
    if sig pinv p = p then contribsFast pinv (k - 1) ps
    else ((1 <<< (k - 1) : Nat), p) :: (-((1 <<< (k - 1) : Nat) : Int), sig pinv p) ::
      contribsFast pinv (k - 1) ps

/-- Aggregate contributions into the coefficient array indexed by colex index. -/
def aggregate (cs : List (Int × (Fin 40 × Fin 40))) (W : Array Int) : Array Int :=
  cs.foldl (fun W c => W.modify (eidx c.2) (· + c.1)) W

/-- Fix the bits that make every literal false; `none` on a conflict (tautological clause).
Literal `l` (colex id `l.id ∈ 1..780`) fixes bit `l.id - 1` to `!l.pos`. -/
def fixedOf (lits : List Lit) : Option (Array (Option Bool)) :=
  lits.foldlM (fun A l => match A.getD (l.id - 1) none with
    | some b => if b = !l.pos then some A else none
    | none => some (A.set! (l.id - 1) (some (!l.pos)))) (Array.replicate 780 none)

/-- Lower bound of `∑ W[t] x_t` over the bits consistent with `F`. -/
def lowSum (W : Array Int) (F : Array (Option Bool)) : Int :=
  ((List.range 780).map fun t => match F.getD t none with
    | some b => if b then W.getD t 0 else 0
    | none => min 0 (W.getD t 0)).sum

/-- Upper bound of `∑ W[t] x_t` over the bits consistent with `F`. -/
def highSum (W : Array Int) (F : Array (Option Bool)) : Int :=
  ((List.range 780).map fun t => match F.getD t none with
    | some b => if b then W.getD t 0 else 0
    | none => max 0 (W.getD t 0)).sum

/-- Check one SB clause: witness `p` with inverse `pinv`, in `Γ_d`, and the clause is valid
for the order (`minOrder`: smaller value is better) on the positions `pos`. -/
def checkSB (minOrder : Bool) (pos : List (Fin 40 × Fin 40)) (d : Nat) (lits : List Lit)
    (p pinv : Fin 40 → Fin 40) : Bool :=
  (List.finRange 40).all (fun v => pinv (p v) == v && p (pinv v) == v) &&
  p 0 == 0 &&
  (List.finRange 40).all (fun u =>
    decide (1 ≤ u.val ∧ u.val ≤ d) == decide (1 ≤ (p u).val ∧ (p u).val ≤ d)) &&
  pos.all (fun e => e.1 != e.2) &&
  lits.all (fun l => decide (1 ≤ l.id ∧ l.id ≤ 780)) &&
  match fixedOf lits with
  | none => true
  | some F =>
    let W := aggregate (contribsFast pinv pos.length pos) (Array.replicate 780 0)
    if minOrder then decide (0 < lowSum W F) else decide (highSum W F < 0)

end R310.SB
