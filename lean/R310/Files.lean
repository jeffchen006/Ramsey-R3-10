/-
The three cube formulas of the certified chain as Lean data, in the exact variable numbering
of agent `cert` (cert/gen.py, satcore):
* edge variable `x(i,j)`, `0 ≤ i < j < 40`: DIMACS id `j(j-1)/2 + i + 1` (colex), `1..780`;
* MTF aux `c(i,j,l)`, `i < j`, `l ∉ {i,j}`: id `781 + p(i,j) * 38 + r`, `p(i,j) = j(j-1)/2 + i`,
  `r = l - [l > i] - [l > j]`.
A constraint is a PB constraint `∑ coef · lit ≥ rhs` (a clause has all coefficients 1, rhs 1).
`cubeR`, `cubeS8`, `cubeN` = TRI + MTF definitions + cube constraints (cert's message of
2026-10-24). The IS clauses are not listed; they enter as the predicate `ISall`.
`scripts/EmitCubes.lean` writes these lists as OPB files.
-/
import Mathlib
import R310.Core

namespace R310.Files

/-- `∑ coef · lit ≥ rhs`. -/
structure PB where
  terms : List (ℕ × Lit)
  rhs : ℕ
deriving Repr

def Lit.eval (a : ℕ → Bool) (l : Lit) : ℕ := if a l.id = l.pos then 1 else 0

def PB.sat (a : ℕ → Bool) (c : PB) : Prop := c.rhs ≤ (c.terms.map fun t => t.1 * t.2.eval a).sum

def posL (n : ℕ) : Lit := ⟨n, true⟩
def negL (n : ℕ) : Lit := ⟨n, false⟩

def clause (ls : List Lit) : PB := ⟨ls.map fun l => (1, l), 1⟩

/-- Edge variable id of the unordered pair `{i, j}`. -/
def xidU (i j : ℕ) : ℕ := if i < j then xid i j else xid j i

/-- MTF aux variable id of `c(i,j,l)`. -/
def cid (i j l : ℕ) : ℕ :=
  781 + (j * (j - 1) / 2 + i) * 38 + (l - (if i < l then 1 else 0) - (if j < l then 1 else 0))

def R40 : List ℕ := List.range 40

/-- TRI: `(-x(i,j) -x(i,k) -x(j,k))` for `i < j < k`. -/
def triFile : List PB :=
  R40.flatMap fun i => R40.flatMap fun j => R40.filterMap fun k =>
    if i < j ∧ j < k then some (clause [negL (xid i j), negL (xid i k), negL (xid j k)]) else none

/-- `l ∉ {i, j}`. -/
def others2 (i j : ℕ) : List ℕ := R40.filter fun l => l ≠ i ∧ l ≠ j

/-- MTF definitions: `c ↔ x(i,l) ∧ x(j,l)` (three clauses) and the pair clause
`x(i,j) ∨ ⋁_l c(i,j,l)`, for `i < j`. -/
def mtfFile : List PB :=
  R40.flatMap fun i => R40.flatMap fun j =>
    if i < j then
      ((others2 i j).flatMap fun l =>
        [clause [negL (cid i j l), posL (xidU i l)], clause [negL (cid i j l), posL (xidU j l)],
         clause [posL (cid i j l), negL (xidU i l), negL (xidU j l)]]) ++
      [clause (posL (xid i j) :: (others2 i j).map fun l => posL (cid i j l))]
    else []

/-- `N(0) = {1..d}`: units. -/
def nbhd0File (d : ℕ) : List PB :=
  (R40.filter fun u => 1 ≤ u).map fun u =>
    clause [if u ≤ d then posL (xid 0 u) else negL (xid 0 u)]

/-- `u ≠ v`. -/
def others1 (v : ℕ) : List ℕ := R40.filter fun u => u ≠ v

/-- Degrees `lo..hi` for every vertex `v`: `∑_u x(u,v) ≥ lo`, `∑_u ~x(u,v) ≥ 39 - hi`. -/
def degFile (lo hi : ℕ) : List PB :=
  R40.flatMap fun v =>
    [⟨(others1 v).map fun u => (1, posL (xidU u v)), lo⟩,
     ⟨(others1 v).map fun u => (1, negL (xidU u v)), 39 - hi⟩]

/-- Pairs `m ≤ i < j ≤ 39`. -/
def pairsFrom (m : ℕ) : List (ℕ × ℕ) :=
  R40.flatMap fun i => R40.filterMap fun j => if m ≤ i ∧ i < j then some (i, j) else none

/-- `e(H_0) ≤ t` when `N(0) = {1..d}`: `∑_{d+1 ≤ i < j} ~x(i,j) ≥ C(39-d, 2) - t`. -/
def h0leFile (d t : ℕ) : List PB :=
  [⟨(pairsFrom (d + 1)).map fun p => (1, negL (xid p.1 p.2)), Nat.choose (39 - d) 2 - t⟩]

/-- `e(H_0) ≥ t`: `∑_{d+1 ≤ i < j} x(i,j) ≥ t`. -/
def h0geFile (d t : ℕ) : List PB :=
  [⟨(pairsFrom (d + 1)).map fun p => (1, posL (xid p.1 p.2)), t⟩]

def cubeR : List PB :=
  triFile ++ mtfFile ++ nbhd0File 9 ++ degFile 9 9 ++ h0leFile 9 99 ++ h0geFile 9 99
def cubeS8 : List PB := triFile ++ mtfFile ++ nbhd0File 8 ++ degFile 6 9 ++ h0leFile 8 96
def cubeN : List PB := triFile ++ mtfFile ++ nbhd0File 9 ++ degFile 6 9 ++ h0leFile 9 98

/-- All IS clauses for 10-sets (not written out). -/
def ISall (a : ℕ → Bool) : Prop :=
  ∀ S : Finset (Fin 40), S.card = 10 → ∃ i ∈ S, ∃ j ∈ S, i < j ∧ a (xid i j) = true

/-! ### Rendering as OPB text -/

def Lit.render (l : Lit) : String := (if l.pos then "x" else "~x") ++ toString l.id

def PB.render (c : PB) : String :=
  " ".intercalate (c.terms.map fun t => toString t.1 ++ " " ++ t.2.render) ++
    " >= " ++ toString c.rhs ++ " ;\n"

def renderFile (cs : List PB) : String := String.join (cs.map PB.render)

end R310.Files
