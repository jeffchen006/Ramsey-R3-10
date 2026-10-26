/-
Theorem C of `notes/cases.md`: minimum degree 8.
-/
import R310.TheoremA

open Finset

set_option linter.unusedSectionVars false

namespace R310

open SimpleGraph

/-- `∑_v ∑_{u ∈ N(v)} f u = ∑_u deg u · f u`. -/
theorem sum_sum_neighborFinset {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (f : V → ℕ) :
    ∑ v, ∑ u ∈ G.neighborFinset v, f u = ∑ u, G.degree u * f u := by
  simp_rw [neighborFinset_eq_filter (G := G), sum_filter]
  rw [sum_comm]
  refine sum_congr rfl fun u _ => ?_
  simp_rw [G.adj_comm _ u]
  rw [← sum_filter, sum_const, ← neighborFinset_eq_filter, card_neighborFinset_eq_degree,
    smul_eq_mul]

variable (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]

/-- `ε(v)` = number of neighbours of `v` of degree 8. -/
def eps8 (v : Fin 40) : ℕ := #{u ∈ G.neighborFinset v | G.degree u = 8}

/-- Theorem C. Let `G` be a (3,10,40)-graph with all degrees in `{8, 9}`, `N = n₈ < 40`, and
suppose every 8-vertex `u` has `e(H_u) ≥ L₈`. Put `c = 108 - L₈`. Then some 9-vertex `v` has
`e(H_v) = 99 - N/2 + ε(v)` with `ε(v) ≤ 9` and `(40 - N) ε(v) ≤ 8N - N (N/2 - c)`
(natural-number subtraction, so `N/2 - c` means `max(0, N/2 - c)`). -/
theorem theoremC_aux (h3 : G.CliqueFree 3) (hdeg : ∀ v, G.degree v = 8 ∨ G.degree v = 9)
    (hN : #{v | G.degree v = 8} < 40) {L₈ : ℕ}
    (hL : ∀ u, G.degree u = 8 → L₈ ≤ #(delNbhd G u).edgeFinset) :
    ∃ v, G.degree v = 9 ∧
      #(delNbhd G v).edgeFinset + #{v | G.degree v = 8} / 2 = 99 + eps8 G v ∧
      eps8 G v ≤ 9 ∧
      (40 - #{v | G.degree v = 8}) * eps8 G v ≤
        8 * #{v | G.degree v = 8} -
          #{v | G.degree v = 8} * (#{v | G.degree v = 8} / 2 - (108 - L₈)) := by
  set N := #{v | G.degree v = 8} with hNdef
  set C8 : Finset (Fin 40) := {v | G.degree v = 8} with hC8
  set C9 : Finset (Fin 40) := {v | G.degree v = 9} with hC9
  have hC9eq : ({v | ¬ G.degree v = 8} : Finset (Fin 40)) = C9 := by
    ext v
    simp only [hC9, mem_filter, mem_univ, true_and]
    have := hdeg v
    omega
  have hC9card : #C9 = 40 - N := by
    have h := card_filter_add_card_filter_not (s := (univ : Finset (Fin 40)))
      (p := fun v => G.degree v = 8)
    rw [hC9eq, card_univ, Fintype.card_fin] at h
    omega
  -- `2 e = 360 - N`
  have he : 2 * #G.edgeFinset + N = 360 := by
    rw [← sum_degrees_eq_twice_card_edges]
    have : ∀ v, G.degree v + (if G.degree v = 8 then 1 else 0) = 9 := fun v => by
      rcases hdeg v with h | h <;> simp [h]
    rw [hNdef, card_filter, ← sum_add_distrib]
    simp [this]
  -- `Z(v) + ε(v) = 9 deg v`
  have hZ : ∀ v, ∑ u ∈ G.neighborFinset v, G.degree u + eps8 G v = 9 * G.degree v := by
    intro v
    rw [eps8, card_filter, ← sum_add_distrib, ← card_neighborFinset_eq_degree, mul_comm,
      ← smul_eq_mul, ← sum_const]
    refine sum_congr rfl fun u _ => ?_
    rcases hdeg u with h | h <;> simp [h]
  have hL2 := fun v => card_edgeFinset_delNbhd_add_sum_degree h3 (G := G) v
  -- double counting: `∑_v ε(v) = 8 N`
  have hsum : ∑ v, eps8 G v = 8 * N := by
    have := sum_sum_neighborFinset G (fun u => if G.degree u = 8 then 1 else 0)
    simp only [← card_filter] at this
    rw [show (∑ v, eps8 G v) = ∑ v, #{u ∈ G.neighborFinset v | G.degree u = 8} from rfl, this,
      hNdef, card_filter, mul_sum]
    refine sum_congr rfl fun u _ => ?_
    split_ifs with h <;> simp [h]
  have hsplit : ∑ v, eps8 G v = ∑ v ∈ C8, eps8 G v + ∑ v ∈ C9, eps8 G v := by
    rw [← sum_filter_add_sum_filter_not univ (fun v => G.degree v = 8), hC9eq]
  -- 8-vertices: `ε(u) ≥ N/2 - c`
  have hlow : ∀ u ∈ C8, N / 2 - (108 - L₈) ≤ eps8 G u := by
    intro u hu
    simp only [hC8, mem_filter, mem_univ, true_and] at hu
    have := hL u hu
    have := hL2 u
    have := hZ u
    rw [hu] at *
    omega
  have hC8sum : N * (N / 2 - (108 - L₈)) ≤ ∑ v ∈ C8, eps8 G v := by
    calc N * (N / 2 - (108 - L₈)) = ∑ _v ∈ C8, (N / 2 - (108 - L₈)) := by
          rw [sum_const, smul_eq_mul]
      _ ≤ ∑ v ∈ C8, eps8 G v := sum_le_sum hlow
  -- averaging over the 9-vertices
  have hne : C9.Nonempty := card_pos.1 (by omega)
  obtain ⟨v, hv, hvle⟩ := exists_le_of_sum_le hne
    (f := fun v => (40 - N) * eps8 G v) (g := fun _ => ∑ w ∈ C9, eps8 G w) (by
      rw [← mul_sum, sum_const, smul_eq_mul, hC9card])
  simp only [hC9, mem_filter, mem_univ, true_and] at hv
  refine ⟨v, hv, ?_, ?_, ?_⟩
  · have := hL2 v
    have := hZ v
    rw [hv] at *
    omega
  · have : eps8 G v ≤ G.degree v := by
      rw [eps8, ← card_neighborFinset_eq_degree]
      exact card_filter_le _ _
    omega
  · omega

/-- Theorem C with the hypothesis `e(H_u) ≥ 95` for 8-vertices taken from the table
`e(3,9,31) = 95` (the case `s = 2`, i.e. `c = 13`). -/
theorem theoremC (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR : Ramsey3Le 9 36)
    (hT : E39Table) (hdeg : ∀ v, G.degree v = 8 ∨ G.degree v = 9)
    (hN : #{v | G.degree v = 8} < 40) :
    ∃ v, G.degree v = 9 ∧
      #(delNbhd G v).edgeFinset + #{v | G.degree v = 8} / 2 = 99 + eps8 G v ∧
      eps8 G v ≤ 9 ∧
      (40 - #{v | G.degree v = 8}) * eps8 G v ≤
        8 * #{v | G.degree v = 8} -
          #{v | G.degree v = 8} * (#{v | G.degree v = 8} / 2 - 13) :=
  theoremC_aux G h3 hdeg hN (L₈ := 95) fun u hu => by
    have := e39_le_card_edgeFinset_delNbhd G h3 hα hR hT u
    rw [hu] at this
    simpa [e39] using this

end R310
