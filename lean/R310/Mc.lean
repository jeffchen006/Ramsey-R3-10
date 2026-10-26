/-
Lemma Mc of `notes/cases_local.md` (max-codegree split of cube R; confirmed by `critic`).

Let `G` be a 9-regular (3,10,40)-graph and `c*` the maximum number of common neighbours of a
non-adjacent pair. Then `3 ≤ c* ≤ 7` (hypothesis F2 for `≤ 7`), and after relabelling:
`N(0) = {1..9}`, `0 ≁ 10`, `N(10) ∩ {1..9} = {1..c*}`, and every non-adjacent pair has at most
`c*` common neighbours.
-/
import R310.R7

open Finset

set_option linter.unusedSectionVars false

namespace R310.Mc

open R310 R310.Files SimpleGraph R310.R7

variable {G : SimpleGraph (Fin 40)} [DecidableRel G.Adj]

/-- `∑_x ∑_y |N(x) ∩ N(y)| = ∑_w deg(w)^2`. -/
theorem sum_codeg : ∑ x, ∑ y, #(G.neighborFinset x ∩ G.neighborFinset y) =
    ∑ w, G.degree w ^ 2 := by
  let a : Fin 40 → Fin 40 → ℕ := fun x w => if G.Adj x w then 1 else 0
  have hc : ∀ x y, #(G.neighborFinset x ∩ G.neighborFinset y) = ∑ w, a x w * a y w := by
    intro x y
    have : G.neighborFinset x ∩ G.neighborFinset y = univ.filter (fun w => G.Adj x w ∧ G.Adj y w) := by
      ext w; simp [mem_neighborFinset]
    rw [this, card_filter]
    refine sum_congr rfl fun w _ => ?_
    by_cases h1 : G.Adj x w <;> by_cases h2 : G.Adj y w <;> simp [a, h1, h2]
  have hd : ∀ w, G.degree w = ∑ x, a w x := fun w => by
    rw [← card_neighborFinset_eq_degree, neighborFinset_eq_filter, card_filter]
  have hsym : ∀ x w, a x w = a w x := fun x w => by simp only [a, G.adj_comm]
  simp_rw [hc, hd, sq, sum_mul_sum]
  calc ∑ x, ∑ y, ∑ w, a x w * a y w = ∑ x, ∑ y, ∑ w, a w x * a w y :=
        sum_congr rfl fun x _ => sum_congr rfl fun y _ => sum_congr rfl fun w _ => by
          rw [hsym x w, hsym y w]
    _ = ∑ x, ∑ w, ∑ y, a w x * a w y := sum_congr rfl fun x _ => sum_comm
    _ = ∑ w, ∑ x, ∑ y, a w x * a w y := sum_comm

/-- In a 9-regular (3,10,40)-graph some non-adjacent pair has at least 3 common neighbours. -/
theorem exists_codeg3 (h3 : G.CliqueFree 3) (hreg : ∀ x, G.degree x = 9) :
    ∃ u v : Fin 40, u ≠ v ∧ ¬ G.Adj u v ∧ 3 ≤ #(G.neighborFinset u ∩ G.neighborFinset v) := by
  by_contra hno
  push Not at hno
  have hs := sum_codeg (G := G)
  simp only [hreg] at hs
  have hrow : ∀ x, ∑ y, #(G.neighborFinset x ∩ G.neighborFinset y) ≤ 69 := by
    intro x
    have hout := card_outside_add (G := G) x
    rw [hreg, Fintype.card_fin] at hout
    calc ∑ y, #(G.neighborFinset x ∩ G.neighborFinset y)
        ≤ ∑ y, ((if y = x then 9 else 0) + (if y ∈ outside G x then 2 else 0)) :=
          sum_le_sum fun y _ => by
            by_cases h : y = x
            · subst h; rw [inter_self, card_neighborFinset_eq_degree, hreg]; simp
            · by_cases had : G.Adj x y
              · have : G.neighborFinset x ∩ G.neighborFinset y = ∅ := by
                  ext w
                  simp only [mem_inter, mem_neighborFinset, Finset.notMem_empty, iff_false,
                    not_and]
                  exact fun hxw hyw => h3 {x, y, w} (is3Clique_triple_iff.2 ⟨had, hxw, hyw⟩)
                rw [this]; simp
              · have hy : y ∈ outside G x := mem_outside.2 ⟨h, had⟩
                have := hno x y (Ne.symm h) had
                simp [h, hy]; omega
      _ = 9 + 2 * #(outside G x) := by
          rw [sum_add_distrib, sum_ite_eq', ← sum_filter, sum_const, smul_eq_mul]
          simp [mul_comm]; rfl
      _ ≤ 69 := by omega
  have := sum_le_sum fun x (_ : x ∈ univ) => hrow x
  rw [hs] at this
  simp at this

/-- **Lemma Mc.** -/
theorem lemma_Mc (hF2 : FactF2) (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9)
    (hreg : ∀ x, G.degree x = 9) :
    ∃ c, 3 ≤ c ∧ c ≤ 7 ∧ ∃ G' : SimpleGraph (Fin 40), ∃ _ : DecidableRel G'.Adj,
      G'.CliqueFree 3 ∧ G'.indepNum ≤ 9 ∧ (∀ x, G'.degree x = 9) ∧
      (∀ y : Fin 40, G'.Adj 0 y ↔ 1 ≤ y.val ∧ y.val ≤ 9) ∧ ¬ G'.Adj 0 10 ∧
      (∀ i : Fin 40, 1 ≤ i.val → i.val ≤ 9 → (G'.Adj 10 i ↔ i.val ≤ c)) ∧
      (∀ x y : Fin 40, x ≠ y → ¬ G'.Adj x y → #(G'.neighborFinset x ∩ G'.neighborFinset y) ≤ c) := by
  classical
  -- the maximum codegree over non-adjacent pairs
  let S : Finset (Fin 40 × Fin 40) := {p | p.1 ≠ p.2 ∧ ¬ G.Adj p.1 p.2}
  let cg : Fin 40 × Fin 40 → ℕ := fun p => #(G.neighborFinset p.1 ∩ G.neighborFinset p.2)
  obtain ⟨u0, v0, h0ne, h0n, h03⟩ := exists_codeg3 h3 hreg
  have hSne : S.Nonempty := ⟨(u0, v0), by simp [S, h0ne, h0n]⟩
  obtain ⟨⟨u, v⟩, hmem, hmax⟩ := S.exists_max_image cg hSne
  simp only [S, mem_filter, mem_univ, true_and] at hmem
  obtain ⟨huv, hn⟩ := hmem
  set c := cg (u, v) with hcdef
  have hc3 : 3 ≤ c := le_trans h03 (hmax (u0, v0) (by simp [S, h0ne, h0n]))
  have hc7 : c ≤ 7 := by
    have := pair_lemma G h3 hα hF2 huv hn; rw [hreg, hreg] at this; simp only [c, cg]; omega
  refine ⟨c, hc3, hc7, ?_⟩
  have hcu : #(G.neighborFinset u) = 9 := by rw [card_neighborFinset_eq_degree, hreg]
  have hcC : #(G.neighborFinset u ∩ G.neighborFinset v) = c := rfl
  have hcA : #(G.neighborFinset u \ G.neighborFinset v) = 9 - c := by
    have := card_sdiff_add_card_inter (G.neighborFinset u) (G.neighborFinset v); omega
  let rest : Finset (Fin 40) := univ.filter fun x => x ≠ u ∧ x ≠ v ∧ ¬ G.Adj u x
  have hvN : v ∉ G.neighborFinset u := by simpa [mem_neighborFinset] using hn
  have hcR : #rest = 29 := by
    have h1 : rest = (insert v (outside G u)).erase v := by
      ext x; simp only [rest, mem_filter, mem_univ, true_and, mem_erase, mem_insert, mem_outside]
      tauto
    have hvo : v ∈ outside G u := mem_outside.2 ⟨Ne.symm huv, hn⟩
    have hout := card_outside_add (G := G) u
    rw [hreg, Fintype.card_fin] at hout
    rw [h1, insert_eq_of_mem hvo, card_erase_of_mem hvo]; omega
  let P : Fin 5 → Finset (Fin 40) :=
    ![{u}, G.neighborFinset u ∩ G.neighborFinset v, G.neighborFinset u \ G.neighborFinset v, {v}, rest]
  let T : Fin 5 → Finset (Fin 40) :=
    ![univ.filter (fun y : Fin 40 => y.val = 0), univ.filter (fun y : Fin 40 => 1 ≤ y.val ∧ y.val ≤ c),
      univ.filter (fun y : Fin 40 => c + 1 ≤ y.val ∧ y.val ≤ 9), univ.filter (fun y : Fin 40 => y.val = 10),
      univ.filter (fun y : Fin 40 => 11 ≤ y.val)]
  have hnu : ∀ x, G.Adj u x → x ≠ u := fun x h e => G.loopless.irrefl u (e ▸ h)
  have hPc : ∀ x, ∃ i, x ∈ P i := by
    intro x
    by_cases h1 : x = u; · exact ⟨0, by simp [P, h1]⟩
    by_cases h2 : x = v; · exact ⟨3, by simp [P, h2]⟩
    by_cases hu : G.Adj u x
    · by_cases hv : G.Adj v x
      · exact ⟨1, by simp [P, hu, hv]⟩
      · exact ⟨2, by simp [P, hu, hv]⟩
    · exact ⟨4, by simp [P, rest, h1, h2, hu]⟩
  have hPd : ∀ i j, i ≠ j → Disjoint (P i) (P j) := by
    intro i j hij
    rw [Finset.disjoint_left]
    intro x hi hj
    fin_cases i <;> fin_cases j <;> simp_all [P, rest] <;>
      first | exact hn hi | exact hn hj.symm | exact hn hi.symm | exact hnu _ hi rfl |
        (subst_vars; simp_all) | skip
  have hTd : ∀ i j, i ≠ j → Disjoint (T i) (T j) := by
    intro i j hij
    rw [Finset.disjoint_left]
    intro x hi hj
    fin_cases i <;> fin_cases j <;> simp_all [T] <;> omega
  have tc : ∀ c' : ℕ, 3 ≤ c' → c' ≤ 7 →
      #(univ.filter (fun y : Fin 40 => 1 ≤ y.val ∧ y.val ≤ c')) = c' ∧
      #(univ.filter (fun y : Fin 40 => c' + 1 ≤ y.val ∧ y.val ≤ 9)) = 9 - c' := by
    intro c' h1 h2; interval_cases c' <;> decide
  have t0 : #(univ.filter (fun y : Fin 40 => y.val = 0)) = 1 := by decide
  have t10 : #(univ.filter (fun y : Fin 40 => y.val = 10)) = 1 := by decide
  have t11 : #(univ.filter (fun y : Fin 40 => 11 ≤ y.val)) = 29 := by decide
  obtain ⟨tc1, tc2⟩ := tc c hc3 hc7
  have hcard : ∀ i, #(P i) = #(T i) := by
    intro i
    fin_cases i <;> simp only [P, T] <;> simp only [Fin.zero_eta, Fin.mk_one, Matrix.cons_val_zero,
      Matrix.cons_val_one, Matrix.head_cons, Matrix.cons_val, Fin.reduceFinMk] <;>
      first | (rw [card_singleton, t0]) | (rw [hcC, tc1]) | (rw [hcA, tc2]) |
        (rw [card_singleton, t10]) | (rw [hcR, t11]) | simp_all
  obtain ⟨σ, hσ⟩ := exists_perm_partition P T hPc hPd hTd hcard
  have hs : ∀ i y, y ∈ T i ↔ σ.symm y ∈ P i := fun i y => by rw [hσ]; simp
  have m0 : σ.symm 0 = u := by have := (hs 0 0).1 (by simp [T]); simpa [P] using this
  have m10 : σ.symm 10 = v := by have := (hs 3 10).1 (by simp [T]); simpa [P] using this
  let G' := relabel G σ
  have hadj : ∀ a b, G'.Adj a b ↔ G.Adj (σ.symm a) (σ.symm b) := fun a b => Iff.rfl
  have h3' : G'.CliqueFree 3 := relabel_cliqueFree σ h3
  have hα' : G'.indepNum ≤ 9 := (relabel_indepNum σ).trans hα
  have hN : ∀ w : Fin 40, G'.neighborFinset w = (G.neighborFinset (σ.symm w)).map σ.toEmbedding :=
    fun w => by ext b; simp only [mem_neighborFinset, mem_map_equiv]; exact Iff.rfl
  refine ⟨G', inferInstance, h3', hα', fun x => ?_, fun y => ?_, ?_, fun i hi1 hi9 => ?_,
    fun x y hxy hxy' => ?_⟩
  · rw [show x = σ (σ.symm x) by simp, relabel_degree, hreg]
  · rw [hadj, m0]
    have h1 := hs 1 y; have h2 := hs 2 y
    simp [T, P, mem_neighborFinset] at h1 h2
    constructor
    · intro hu
      by_cases hv : G.Adj v (σ.symm y)
      · have := h1.2 ⟨hu, hv⟩; omega
      · have := h2.2 ⟨hu, hv⟩; omega
    · intro hy
      by_cases hle : y.val ≤ c
      · exact (h1.1 ⟨hy.1, hle⟩).1
      · exact (h2.1 ⟨by omega, hy.2⟩).1
  · rw [hadj, m0, m10]; exact hn
  · rw [hadj, m10]
    have h1 := hs 1 i; have h2 := hs 2 i
    simp [T, P, mem_neighborFinset] at h1 h2
    constructor
    · intro hv
      by_contra hgt
      have := (h2.1 ⟨by omega, hi9⟩).2; exact this hv
    · intro hle; exact (h1.1 ⟨hi1, hle⟩).2
  · rw [hN, hN, ← Finset.map_inter, card_map]
    exact hmax (σ.symm x, σ.symm y) (by
      simp only [S, mem_filter, mem_univ, true_and]
      exact ⟨fun e => hxy (σ.symm.injective e), fun h => hxy' ((hadj x y).2 h)⟩)

end R310.Mc
