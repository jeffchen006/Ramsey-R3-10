/-
Mathlib-free definitions of the general-`n` SB checker (`sbcheck` with header field `n=`).
Soundness: `R310.Gen.checkG_sound` (in `R310.GenCheck`).

Vertices `Fin n`, edge variables `x(i,j)`, `i < j`, colex ids `xid i j = j(j-1)/2 + i + 1`,
`1..N`, `N = n(n-1)/2`.
-/
import R310.Core

namespace R310.Gen

open R310.Files

/-- `N = n(n-1)/2`, the number of edge variables. -/
def numE (n : Nat) : Nat := n * (n - 1) / 2

/-- Pairs `i < j` in colex order. -/
def colexPairsG (n : Nat) : List (Fin n × Fin n) :=
  (List.finRange n).flatMap fun j => (List.finRange n).filterMap fun i =>
    if i < j then some (i, j) else none

/-- Pairs `i < j` in row-major order. -/
def rowPairsG (n : Nat) : List (Fin n × Fin n) :=
  (List.finRange n).flatMap fun i => (List.finRange n).filterMap fun j =>
    if i < j then some (i, j) else none

/-- Colex index (`= id - 1`) of an unordered pair. -/
def eidxG {n : Nat} (p : Fin n × Fin n) : Nat :=
  xid (min p.1 p.2 : Fin n) (max p.1 p.2 : Fin n) - 1

/-- `σ p = (π⁻¹ p.1, π⁻¹ p.2)`. -/
def sigG {n : Nat} (pinv : Fin n → Fin n) (p : Fin n × Fin n) : Fin n × Fin n :=
  (pinv p.1, pinv p.2)

/-- Contributions `(c, p)` with `D(x) = val x - val (π x) = ∑ c · x_p`; `k = ps.length`. -/
def contribsG {n : Nat} (pinv : Fin n → Fin n) : Nat → List (Fin n × Fin n) →
    List (Int × (Fin n × Fin n))
  | _, [] => []
  | k, p :: ps =>
    if sigG pinv p = p then contribsG pinv (k - 1) ps
    else ((1 <<< (k - 1) : Nat), p) :: (-((1 <<< (k - 1) : Nat) : Int), sigG pinv p) ::
      contribsG pinv (k - 1) ps

def aggregateG {n : Nat} (cs : List (Int × (Fin n × Fin n))) (W : Array Int) : Array Int :=
  cs.foldl (fun W c => W.modify (eidxG c.2) (· + c.1)) W

/-- Fixed bits (index `id - 1`, value `!pos`); `none` on a conflict (tautological clause). -/
def fixedOfG (N : Nat) (lits : List Lit) : Option (Array (Option Bool)) :=
  lits.foldlM (fun A l => match A.getD (l.id - 1) none with
    | some b => if b = !l.pos then some A else none
    | none => some (A.set! (l.id - 1) (some (!l.pos)))) (Array.replicate N none)

def lowSumG (N : Nat) (W : Array Int) (F : Array (Option Bool)) : Int :=
  ((List.range N).map fun t => match F.getD t none with
    | some b => if b then W.getD t 0 else 0
    | none => min 0 (W.getD t 0)).sum

def highSumG (N : Nat) (W : Array Int) (F : Array (Option Bool)) : Int :=
  ((List.range N).map fun t => match F.getD t none with
    | some b => if b then W.getD t 0 else 0
    | none => max 0 (W.getD t 0)).sum

/-- `π` is in `Γ_d`: `d = 0` (all permutations), or `π` fixes vertex 0 and maps `{1..d}` onto
itself. -/
def gammaOK {n : Nat} (d : Nat) (p : Fin n → Fin n) : Bool :=
  d == 0 ||
  ((List.finRange n).all (fun v => v.val != 0 || (p v).val == 0) &&
   (List.finRange n).all (fun u =>
     decide (1 ≤ u.val ∧ u.val ≤ d) == decide (1 ≤ (p u).val ∧ (p u).val ≤ d)))

/-- The general checker. -/
def checkG (n : Nat) (minOrder : Bool) (pos : List (Fin n × Fin n)) (d : Nat) (lits : List Lit)
    (p pinv : Fin n → Fin n) : Bool :=
  (List.finRange n).all (fun v => pinv (p v) == v && p (pinv v) == v) &&
  gammaOK d p &&
  pos.all (fun e => e.1 != e.2) &&
  lits.all (fun l => decide (1 ≤ l.id ∧ l.id ≤ numE n)) &&
  match fixedOfG (numE n) lits with
  | none => true
  | some F =>
    let W := aggregateG (contribsG pinv pos.length pos) (Array.replicate (numE n) 0)
    if minOrder then decide (0 < lowSumG (numE n) W F) else decide (highSumG (numE n) W F < 0)

end R310.Gen

namespace R310.Gen

open R310.Files

/-- Index of the block of vertex `v` for block sizes `sizes` (blocks are consecutive). -/
def blockOf : List Nat → Nat → Nat
  | [], _ => 0
  | s :: ss, v => if v < s then 0 else blockOf ss (v - s) + 1

/-- Every vertex is mapped into its own block, and the sizes add up to `n`. -/
def blocksOK {n : Nat} (sizes : List Nat) (p : Fin n → Fin n) : Bool :=
  sizes.sum == n && (List.finRange n).all fun v => blockOf sizes (p v).val == blockOf sizes v.val

/-- Checker with a block partition (header `blocks=`): `checkG` with `d = 0` plus `blocksOK`. -/
def checkGB (n : Nat) (minOrder : Bool) (pos : List (Fin n × Fin n)) (sizes : List Nat)
    (lits : List Lit) (p pinv : Fin n → Fin n) : Bool :=
  blocksOK sizes p && checkG n minOrder pos 0 lits p pinv

end R310.Gen
