/-
Lemmas L4, L5 and Theorem A of `notes/cases.md` (agent `cases`), for `n = 40`, `k = 10`.
-/
import R310.Regular

open Finset

set_option linter.unusedSectionVars false

namespace R310

open SimpleGraph

variable (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]

/-- L4: `∑_v e(H_v) + ∑_v (deg v)^2 = 20 ∑_v deg v`, i.e. `∑_v e(H_v) = ∑_v d(v)(20 - d(v))`. -/
theorem sum_card_edgeFinset_delNbhd_add_sq (h3 : G.CliqueFree 3) :
    ∑ v, #(delNbhd G v).edgeFinset + ∑ v, G.degree v ^ 2 = 20 * ∑ v, G.degree v := by
  have := sum_card_edgeFinset_delNbhd_add h3 (G := G)
  simp only [Fintype.card_fin] at this
  rw [sum_degrees_eq_twice_card_edges]
  omega

/-- L5 (upper bound): `e(G) ≤ 180`. -/
theorem card_edgeFinset_le_180 (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) :
    #G.edgeFinset ≤ 180 := by
  have := two_mul_card_edgeFinset_le G (D := 9) (degree_le_nine G h3 hα)
  omega

/-- The four `e(3,9,m)` values used by Theorem A: `m = 32..35` ([GR] Table 4; 140 = [GR] Thm 3). -/
def E39TableA : Prop :=
  EdgeLowerBound 9 32 104 ∧ EdgeLowerBound 9 33 118 ∧ EdgeLowerBound 9 34 129 ∧
  EdgeLowerBound 9 35 140

theorem E39Table.toA (hT : E39Table) : E39TableA := ⟨hT.2.2.1, hT.2.2.2.1, hT.2.2.2.2.1, hT.2.2.2.2.2⟩

/-- Theorem A, second part. If `G` is not 9-regular, some vertex `v` has
(`deg v = 9` and `e(H_v) ≤ 98`) or (`deg v = 8` and `e(H_v) ≤ 96`).
Hypotheses: `R(3,9) ≤ 36` and `e(3,9,m)` for `m = 32..35`. -/
theorem theoremA_of_not_regular (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9)
    (hR : Ramsey3Le 9 36) (hT : E39TableA) (hreg : ∃ v, G.degree v ≠ 9) :
    ∃ v, (G.degree v = 9 ∧ #(delNbhd G v).edgeFinset ≤ 98) ∨
      (G.degree v = 8 ∧ #(delNbhd G v).edgeFinset ≤ 96) := by
  by_contra hcon
  push Not at hcon
  -- per vertex: `20 d ≤ e(H_v) + d^2`, strict unless `d = 9`
  have hle : ∀ v, 20 * G.degree v ≤ #(delNbhd G v).edgeFinset + G.degree v ^ 2 ∧
      (G.degree v ≠ 9 → 20 * G.degree v < #(delNbhd G v).edgeFinset + G.degree v ^ 2) := by
    intro v
    clear hreg
    have hlo := four_le_degree G h3 hα hR v
    have hhi := degree_le_nine G h3 hα v
    have key : ∀ e₀, EdgeLowerBound 9 (40 - G.degree v - 1) e₀ →
        e₀ ≤ #(delNbhd G v).edgeFinset := fun e₀ hE =>
      le_card_edgeFinset_delNbhd (k := 10) h3 hα v (by simpa using hE)
    obtain ⟨h32, h33, h34, h35⟩ := hT
    obtain ⟨h9, h8⟩ := hcon v
    have h9' : G.degree v ≠ 9 ∨ 98 < #(delNbhd G v).edgeFinset := by tauto
    have h8' : G.degree v ≠ 8 ∨ 96 < #(delNbhd G v).edgeFinset := by tauto
    clear h9 h8
    interval_cases h : G.degree v
    · have := key _ h35; omega
    · have := key _ h34; omega
    · have := key _ h33; omega
    · have := key _ h32; omega
    · omega
    · omega
  obtain ⟨v₀, hv₀⟩ := hreg
  have hlt : ∑ v, 20 * G.degree v < ∑ v, (#(delNbhd G v).edgeFinset + G.degree v ^ 2) :=
    sum_lt_sum (fun v _ => (hle v).1) ⟨v₀, mem_univ _, (hle v₀).2 hv₀⟩
  have h4 := sum_card_edgeFinset_delNbhd_add_sq G h3
  rw [sum_add_distrib, h4, ← mul_sum] at hlt
  exact lt_irrefl _ hlt

/-- Theorem A, first part. Some vertex `v` has
(`deg v = 9` and `e(H_v) ≤ 99`) or (`deg v = 8` and `e(H_v) ≤ 96`). -/
theorem theoremA (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR : Ramsey3Le 9 36)
    (hT : E39TableA) :
    ∃ v, (G.degree v = 9 ∧ #(delNbhd G v).edgeFinset ≤ 99) ∨
      (G.degree v = 8 ∧ #(delNbhd G v).edgeFinset ≤ 96) := by
  by_cases hreg : ∃ v, G.degree v ≠ 9
  · obtain ⟨v, hv⟩ := theoremA_of_not_regular G h3 hα hR hT hreg
    exact ⟨v, hv.imp (fun h => ⟨h.1, by omega⟩) id⟩
  · push Not at hreg
    obtain ⟨-, -, h99, -⟩ := regular_nine_delNbhd G h3 hα hreg 0
    exact ⟨0, Or.inl ⟨hreg 0, h99.le⟩⟩

end R310
