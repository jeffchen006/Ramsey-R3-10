/-
Exact checker for Farkas certificates of the class LP (Lemma L8 of `notes/cases.md`).

Variables: `M_ij` for the 21 degree-class pairs `4 ≤ i ≤ j ≤ 9` (see `R310.Mcl`).
A certificate is a list of rows with natural multipliers `y_r`. The checker verifies
`∑_r y_r rhs_r < ∑_p min(0, col_p) ub_p`, where `col_p = ∑_r y_r coef_r(p)`.
`Cert.sound` shows that then no valuation satisfies all rows inside the box `0 ≤ M_p ≤ ub_p`.
-/
import Mathlib

namespace R310.LP

/-- The 21 class pairs `(i, j)` with `4 ≤ i ≤ j ≤ 9`. -/
def pairs : List (ℕ × ℕ) :=
  [(4,4),(4,5),(4,6),(4,7),(4,8),(4,9),(5,5),(5,6),(5,7),(5,8),(5,9),(6,6),(6,7),(6,8),(6,9),
   (7,7),(7,8),(7,9),(8,8),(8,9),(9,9)]

/-- Entry `i` (for `4 ≤ i ≤ 9`) of a 6-list indexed by degrees `4..9`; `0` otherwise. -/
def get6 (l : List ℕ) (i : ℕ) : ℕ := if 4 ≤ i ∧ i ≤ 9 then l.getD (i - 4) 0 else 0

/-- An LP instance: degree distribution `n = (n4..n9)`, lower bounds `L = (L4..L9)` on
`e(H_v)` per class, and the MTF flag. -/
structure Inst where
  n : List ℕ
  L : List ℕ
  mtf : Bool
deriving Repr

namespace Inst

variable (I : Inst)

def nd (i : ℕ) : ℕ := get6 I.n i
def Ld (i : ℕ) : ℕ := get6 I.L i
/-- `2 e = ∑ i n_i`. -/
def deg2 : ℕ := 4 * I.nd 4 + 5 * I.nd 5 + 6 * I.nd 6 + 7 * I.nd 7 + 8 * I.nd 8 + 9 * I.nd 9
def e : ℕ := I.deg2 / 2

/-- Box bound for the variable `M_p` (Lemma L8(d)). -/
def ubv : ℕ × ℕ → ℤ
  | (a, b) => if a = b then 2 * (I.nd a * I.nd a / 4 : ℕ)
      else min (I.nd a * min a (I.nd b) : ℕ) (I.nd b * min b (I.nd a) : ℕ)

end Inst

/-- Row types. -/
inductive Row
  | degLe (i : ℕ)        -- `∑_j M_ij ≤ i n_i`
  | degGe (i : ℕ)        -- `-∑_j M_ij ≤ -i n_i`
  | hyp (i : ℕ)          -- `∑_j j M_ij ≤ n_i e - n_i L_i`
  | mtfZ (i : ℕ)         -- `-∑_j j M_ij ≤ -n_i (i^2 - 11 i + 78)` (MTF only)
  | mantel (x : List ℕ)  -- `∑_{i<j} 2 x_i x_j M_ij + ∑_i x_i^2 M_ii ≤ 2 ⌊(∑ x_i n_i)^2 / 4⌋`
  | ub (i j : ℕ)         -- `M_ij ≤ ub_ij`
  | forced (i j : ℕ)     -- `-M_ij ≤ -n_i (n_j - [i = j])` (`i + j ≤ 10`)
deriving Repr

/-- `∑_j j M_ij` coefficient of the pair `(a, b)`. -/
def hypCoef (i : ℕ) : ℕ × ℕ → ℤ
  | (a, b) => if a = i then b else if b = i then a else 0

def coef : Row → ℕ × ℕ → ℤ
  | .degLe i, (a, b) => if a = i ∨ b = i then 1 else 0
  | .degGe i, (a, b) => if a = i ∨ b = i then -1 else 0
  | .hyp i, p => hypCoef i p
  | .mtfZ i, p => -hypCoef i p
  | .mantel x, (a, b) => if a = b then ((get6 x a) ^ 2 : ℕ) else (2 * get6 x a * get6 x b : ℕ)
  | .ub i j, p => if p = (i, j) then 1 else 0
  | .forced i j, p => if p = (i, j) then -1 else 0

/-- `∑_i x_i n_i`. -/
def wsum (I : Inst) (x : List ℕ) : ℕ :=
  get6 x 4 * I.nd 4 + get6 x 5 * I.nd 5 + get6 x 6 * I.nd 6 + get6 x 7 * I.nd 7 +
    get6 x 8 * I.nd 8 + get6 x 9 * I.nd 9

def rhs (I : Inst) : Row → ℤ
  | .degLe i => (i * I.nd i : ℕ)
  | .degGe i => -((i * I.nd i : ℕ) : ℤ)
  | .hyp i => (I.nd i * I.e : ℕ) - (I.nd i * I.Ld i : ℕ)
  | .mtfZ i => (11 * i * I.nd i : ℕ) - (I.nd i * (i ^ 2 + 78) : ℕ)
  | .mantel x => (2 * (wsum I x * wsum I x / 4) : ℕ)
  | .ub i j => I.ubv (i, j)
  | .forced i j => -((I.nd i * (I.nd j - if i = j then 1 else 0) : ℕ) : ℤ)

def admissible (I : Inst) : Row → Bool
  | .degLe i => 4 ≤ i && i ≤ 9
  | .degGe i => 4 ≤ i && i ≤ 9
  | .hyp i => 4 ≤ i && i ≤ 9
  | .mtfZ i => I.mtf && 4 ≤ i && i ≤ 9
  | .mantel _ => true
  | .ub i j => 4 ≤ i && i ≤ j && j ≤ 9
  | .forced i j => 4 ≤ i && i ≤ j && j ≤ 9 && i + j ≤ 10

/-- Value of a linear form at a valuation of the 21 pair variables. -/
def evalLF (f val : ℕ × ℕ → ℤ) : ℤ := (pairs.map fun p => f p * val p).sum

/-- A Farkas certificate. -/
structure Cert where
  inst : Inst
  rows : List (Row × ℕ)
deriving Repr

namespace Cert

variable (c : Cert)

def col (p : ℕ × ℕ) : ℤ := (c.rows.map fun ry => (ry.2 : ℤ) * coef ry.1 p).sum
def crhs : ℤ := (c.rows.map fun ry => (ry.2 : ℤ) * rhs c.inst ry.1).sum
def boxMin : ℤ := (pairs.map fun p => min 0 (c.col p) * c.inst.ubv p).sum

/-- The exact check. -/
def check : Bool := c.rows.all (fun ry => admissible c.inst ry.1) && decide (c.crhs < c.boxMin)

end Cert

/-! ### Soundness -/

theorem evalLF_add (f g val : ℕ × ℕ → ℤ) :
    evalLF (fun p => f p + g p) val = evalLF f val + evalLF g val := by
  unfold evalLF
  induction pairs with
  | nil => simp
  | cons p l ih => simp only [List.map_cons, List.sum_cons]; rw [ih]; ring

theorem evalLF_smul (a : ℤ) (f val : ℕ × ℕ → ℤ) :
    evalLF (fun p => a * f p) val = a * evalLF f val := by
  unfold evalLF
  induction pairs with
  | nil => simp
  | cons p l ih => simp only [List.map_cons, List.sum_cons]; rw [ih]; ring

theorem evalLF_zero (val : ℕ × ℕ → ℤ) : evalLF (fun _ => 0) val = 0 := by
  unfold evalLF
  induction pairs with
  | nil => simp
  | cons p l ih => simp only [List.map_cons, List.sum_cons]; rw [ih]; ring

/-- The rows of a certificate, combined with non-negative multipliers. -/
theorem evalLF_col_le (rows : List (Row × ℕ)) (I : Inst) (val : ℕ × ℕ → ℤ)
    (hval : ∀ ry ∈ rows, evalLF (coef ry.1) val ≤ rhs I ry.1) :
    evalLF (fun p => (rows.map fun ry => (ry.2 : ℤ) * coef ry.1 p).sum) val ≤
      (rows.map fun ry => (ry.2 : ℤ) * rhs I ry.1).sum := by
  induction rows with
  | nil => simp [evalLF_zero]
  | cons ry l ih =>
    simp only [List.map_cons, List.sum_cons]
    rw [evalLF_add, evalLF_smul]
    have h1 := hval ry (by simp)
    have h2 := ih (fun r hr => hval r (by simp [hr]))
    have : (0 : ℤ) ≤ ry.2 := by positivity
    nlinarith

theorem boxMin_le (I : Inst) (f val : ℕ × ℕ → ℤ)
    (hbox : ∀ p ∈ pairs, 0 ≤ val p ∧ val p ≤ I.ubv p) :
    (pairs.map fun p => min 0 (f p) * I.ubv p).sum ≤ evalLF f val := by
  unfold evalLF
  apply List.sum_le_sum
  intro p hp
  obtain ⟨h0, h1⟩ := hbox p hp
  rcases le_total 0 (f p) with h | h
  · rw [min_eq_left h, zero_mul]; positivity
  · rw [min_eq_right h]; nlinarith

/-- Soundness: if the check passes, no valuation in the box satisfies all admissible rows. -/
theorem Cert.sound (c : Cert) (hc : c.check = true) (val : ℕ × ℕ → ℤ)
    (hval : ∀ r, admissible c.inst r = true → evalLF (coef r) val ≤ rhs c.inst r)
    (hbox : ∀ p ∈ pairs, 0 ≤ val p ∧ val p ≤ c.inst.ubv p) : False := by
  unfold Cert.check at hc
  rw [Bool.and_eq_true, List.all_eq_true, decide_eq_true_iff] at hc
  obtain ⟨hadm, hlt⟩ := hc
  have h1 := evalLF_col_le c.rows c.inst val (fun ry hry => hval ry.1 (hadm ry hry))
  have h2 := boxMin_le c.inst c.col val hbox
  unfold Cert.boxMin Cert.crhs Cert.col at hlt
  unfold Cert.col at h2
  linarith

end R310.LP
