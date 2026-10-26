/-
Weighted Mantel inequality (integer weights) and Theorem B of `notes/cases.md`.
-/
import R310.TheoremA

open Finset

set_option linter.unusedSectionVars false

namespace R310

open SimpleGraph

section Mantel

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

/-- Mantel's theorem: a triangle-free graph on `n` vertices has at most `n^2/4` edges. -/
theorem four_mul_card_edgeFinset_le {W : Type*} [Fintype W] {H : SimpleGraph W}
    [DecidableRel H.Adj] (h3 : H.CliqueFree 3) : 4 * #H.edgeFinset ≤ Fintype.card W ^ 2 := by
  have h1 := CliqueFree.card_edgeFinset_le (r := 2) h3
  have h2 := mul_turanNumber_le (n := Fintype.card W) (r := 2)
  omega

/-- The blow-up of `G`: vertex `u` is replaced by `x u` independent copies. -/
abbrev blowup (G : SimpleGraph V) (x : V → ℕ) : SimpleGraph (Σ u : V, Fin (x u)) :=
  G.comap Sigma.fst

theorem cliqueFree_blowup (h3 : G.CliqueFree 3) (x : V → ℕ) : (blowup G x).CliqueFree 3 := by
  intro t ht
  rw [is3Clique_iff] at ht
  obtain ⟨a, b, c, hab, hac, hbc, -⟩ := ht
  exact h3 {a.1, b.1, c.1} (is3Clique_triple_iff.2 ⟨hab, hac, hbc⟩)

theorem degree_blowup (x : V → ℕ) (a : Σ u : V, Fin (x u)) :
    (blowup G x).degree a = ∑ v ∈ G.neighborFinset a.1, x v := by
  rw [← card_neighborFinset_eq_degree]
  have : (blowup G x).neighborFinset a = (G.neighborFinset a.1).sigma fun _ => univ := by
    ext b
    simp
  rw [this, card_sigma]
  simp

/-- Weighted Mantel inequality (integer weights `x ≥ 0`), triangle-free `G`:
`2 ∑_u x_u ∑_{v ∈ N(u)} x_v ≤ (∑_u x_u)^2`, i.e. `4 ∑_{uv ∈ E} x_u x_v ≤ (∑ x)^2`.
Proof: Mantel's theorem for the blow-up of `G`. -/
theorem weighted_mantel (h3 : G.CliqueFree 3) (x : V → ℕ) :
    2 * ∑ u, x u * ∑ v ∈ G.neighborFinset u, x v ≤ (∑ u, x u) ^ 2 := by
  classical
  have hM := four_mul_card_edgeFinset_le (cliqueFree_blowup h3 x)
  have hS := sum_degrees_eq_twice_card_edges (blowup G x)
  simp only [degree_blowup, Fintype.sum_sigma] at hS
  simp only [Fintype.card_sigma, Fintype.card_fin] at hM
  have : ∀ u, ∑ _i : Fin (x u), ∑ v ∈ G.neighborFinset u, x v =
      x u * ∑ v ∈ G.neighborFinset u, x v := fun u => by simp
  simp only [this] at hS
  omega

end Mantel

/-! ### Theorem B -/

variable (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]

/-- Theorem B (Angeltveit-type). If a (3,10,40)-graph `G` is not 9-regular, then some vertex `v`
of degree `≤ 8` has `e(H_v) + 9 deg v ≤ 180`. -/
theorem theoremB (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hreg : ∃ v, G.degree v ≠ 9) :
    ∃ v, G.degree v ≤ 8 ∧ #(delNbhd G v).edgeFinset + 9 * G.degree v ≤ 180 := by
  have hle := degree_le_nine G h3 hα
  let w : Fin 40 → ℕ := fun u => 9 - G.degree u
  let N := ∑ u, w u
  let eps : Fin 40 → ℕ := fun v => ∑ u ∈ G.neighborFinset v, w u
  have hN : 2 * #G.edgeFinset + N = 360 := by
    rw [← sum_degrees_eq_twice_card_edges, ← sum_add_distrib]
    have : ∀ u, G.degree u + w u = 9 := fun u => by have := hle u; simp only [w]; omega
    simp [this]
  have hZ : ∀ v, ∑ u ∈ G.neighborFinset v, G.degree u + eps v = 9 * G.degree v := by
    intro v
    rw [← sum_add_distrib, ← card_neighborFinset_eq_degree, mul_comm, ← smul_eq_mul,
      ← sum_const]
    exact sum_congr rfl fun u _ => by have := hle u; simp only [w]; omega
  have hM := weighted_mantel h3 w
  -- some `v` with `w v > 0` and `2 eps v ≤ N`
  obtain ⟨v, hwv, hv⟩ : ∃ v, 0 < w v ∧ 2 * eps v ≤ N := by
    by_contra hcon
    push Not at hcon
    obtain ⟨v₀, hv₀⟩ := hreg
    have hw0 : 0 < w v₀ := by have := hle v₀; simp only [w]; omega
    have hNpos : 0 < N := lt_of_lt_of_le hw0 (single_le_sum (fun _ _ => Nat.zero_le _)
      (mem_univ v₀))
    have : ∑ u, w u * (N + 1) ≤ ∑ u, w u * (2 * eps u) := by
      refine sum_le_sum fun u _ => ?_
      rcases Nat.eq_zero_or_pos (w u) with h | h
      · simp [h]
      · exact Nat.mul_le_mul_left _ (hcon u h)
    rw [← sum_mul] at this
    have h2 : ∑ u, w u * (2 * eps u) = 2 * ∑ u, w u * eps u := by
      rw [mul_sum]; exact sum_congr rfl fun u _ => by ring
    rw [h2] at this
    have : N * (N + 1) ≤ N ^ 2 := this.trans hM
    nlinarith
  refine ⟨v, by simp only [w] at hwv; omega, ?_⟩
  have hL2 := card_edgeFinset_delNbhd_add_sum_degree h3 (G := G) v
  have := hZ v
  omega

end R310
