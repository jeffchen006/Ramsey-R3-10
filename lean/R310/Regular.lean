/-
Maximum degree and the 9-regular case for a (3,10,40)-graph.
-/
import R310.EdgeBound

open Finset

set_option linter.unusedSectionVars false

namespace R310

open SimpleGraph

variable (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]

/-- `2 e(G) ≤ 40 · Δ`: if all degrees are at most `D` then `2 e(G) ≤ 40 D`. -/
theorem two_mul_card_edgeFinset_le {D : ℕ} (hD : ∀ v, G.degree v ≤ D) :
    2 * #G.edgeFinset ≤ 40 * D := by
  rw [← sum_degrees_eq_twice_card_edges]
  calc ∑ v, G.degree v ≤ ∑ _v : Fin 40, D := sum_le_sum fun v _ => hD v
    _ = 40 * D := by simp

/-- With `e(3,10,40) ≥ 161` ([GR] Table 5) as hypothesis, a (3,10,40)-graph has a vertex of
degree 9 (since an 8-bounded graph has at most 160 edges). -/
theorem exists_degree_nine (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9)
    (hE : EdgeLowerBound 10 40 161) : ∃ v, G.degree v = 9 := by
  have he := hE.le_card_edgeFinset (by simp) G h3 (by omega)
  by_contra hne
  push Not at hne
  have hD : ∀ v, G.degree v ≤ 8 := fun v => by
    have := degree_le_nine G h3 hα v
    have := hne v
    omega
  have := two_mul_card_edgeFinset_le G hD
  omega

/-- In a 9-regular (3,10,40)-graph, `e(G) = 180`, every `G - N[v]` has 30 vertices and
`e(G - N[v]) = 99`, and `α(G - N[v]) ≤ 8`. So every `G - N[v]` is in R(3,9;30,99). -/
theorem regular_nine_delNbhd (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9)
    (hreg : ∀ v, G.degree v = 9) (v : Fin 40) :
    #G.edgeFinset = 180 ∧ Fintype.card (outside G v : Set (Fin 40)) = 30 ∧
      #(delNbhd G v).edgeFinset = 99 ∧ (delNbhd G v).indepNum ≤ 8 := by
  have he : #G.edgeFinset = 180 := by
    have := sum_degrees_eq_twice_card_edges G
    simp [hreg] at this
    omega
  have hc := card_delNbhd_verts (G := G) v
  have hsum := card_edgeFinset_delNbhd_add_sum_degree h3 (G := G) v
  simp only [hreg, sum_const, card_neighborFinset_eq_degree, smul_eq_mul] at hsum hc
  simp only [Fintype.card_fin] at hc
  exact ⟨he, by omega, by omega, indepNum_delNbhd_le (k := 10) hα v⟩

end R310
