/-
Averaging: some vertex has `e(G - N[v])` no larger than the average given by (d).
This is the step behind Angeltveit's Prop. 2.1 (arXiv:2401.00392) and [GR] Sec. 3.
-/
import R310.Basic

open Finset

set_option linter.unusedSectionVars false

namespace R310

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

/-- For every weight `c`, some vertex `v` satisfies
`n (e(G - N[v]) + (deg v)^2) + 2 c e(G) ≤ n e(G) + n c deg v`, where `n = |V|`.
Equivalently `e(G - N[v]) + (deg v)^2 - c deg v ≤ (1 - 2c/n) e(G)`. -/
theorem exists_card_edgeFinset_delNbhd_le [Nonempty V] (h3 : G.CliqueFree 3) (c : ℕ) :
    ∃ v, Fintype.card V * (#(delNbhd G v).edgeFinset + G.degree v ^ 2) + 2 * c * #G.edgeFinset ≤
      Fintype.card V * #G.edgeFinset + Fintype.card V * c * G.degree v := by
  have hd := sum_card_edgeFinset_delNbhd_add h3 (G := G)
  have hs := sum_degrees_eq_twice_card_edges G
  obtain ⟨v, -, hv⟩ := exists_le_of_sum_le (s := univ) univ_nonempty
    (f := fun v => Fintype.card V * (#(delNbhd G v).edgeFinset + G.degree v ^ 2) +
      2 * c * #G.edgeFinset)
    (g := fun v => Fintype.card V * #G.edgeFinset + Fintype.card V * c * G.degree v) (by
      simp only [sum_add_distrib, ← mul_sum, sum_const, card_univ, smul_eq_mul, hd, hs]
      ring_nf
      exact le_rfl)
  exact ⟨v, hv⟩

end R310
