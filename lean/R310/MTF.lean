/-
Maximal triangle-free (MTF) graphs: lemmas M0, M1, M2, M3 of `notes/cases.md`.
-/
import R310.MinDegree
import R310.Local

open Finset

set_option linter.unusedSectionVars false

namespace R310

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- `G` is maximal triangle-free: triangle-free, and no triangle-free graph is strictly larger. -/
def IsMTF (G : SimpleGraph V) : Prop := Maximal (fun H : SimpleGraph V => H.CliqueFree 3) G

/-- A larger graph has a smaller independence number. -/
theorem indepNum_anti {G H : SimpleGraph V} (hGH : G ≤ H) : H.indepNum ≤ G.indepNum := by
  obtain ⟨s, hs⟩ := H.exists_isNIndepSet_indepNum
  have : G.IsIndepSet (s : Set V) := fun a ha b hb hab h => hs.isIndepSet ha hb hab (hGH h)
  rw [← hs.card_eq]
  exact this.card_le_indepNum

/-- M0. Every triangle-free graph is contained in an MTF graph, and the independence number does
not increase. So if a `(3,k,n)`-graph exists, an MTF `(3,k,n)`-graph exists. -/
theorem exists_isMTF_le {G : SimpleGraph V} (h3 : G.CliqueFree 3) :
    ∃ H, G ≤ H ∧ IsMTF H ∧ H.indepNum ≤ G.indepNum := by
  classical
  obtain ⟨H, hGH, hH⟩ := (Set.toFinite {H : SimpleGraph V | H.CliqueFree 3}).exists_le_maximal
    (a := G) h3
  exact ⟨H, hGH, hH, indepNum_anti hGH⟩

/-- In an MTF graph, two distinct non-adjacent vertices have a common neighbour. -/
theorem IsMTF.exists_common {G : SimpleGraph V} (hG : IsMTF G) {u v : V} (huv : u ≠ v)
    (hn : ¬ G.Adj u v) : ∃ w, G.Adj u w ∧ G.Adj v w := by
  by_contra hno
  push Not at hno
  have hlt : G < G ⊔ edge u v := lt_sup_edge _ _ _ huv hn
  have h3 : (G ⊔ edge u v).CliqueFree 3 := by
    intro t ht
    rw [is3Clique_iff] at ht
    obtain ⟨a, b, c, hab, hac, hbc, rfl⟩ := ht
    simp only [sup_adj, edge_adj] at hab hac hbc
    have hG3 := hG.1
    have tri : ∀ x y z, G.Adj x y → G.Adj x z → G.Adj y z → False := fun x y z h1 h2 h3' =>
      hG3 {x, y, z} (is3Clique_triple_iff.2 ⟨h1, h2, h3'⟩)
    have hs : ∀ x y, G.Adj x y → G.Adj y x := fun _ _ h => h.symm
    have hno' : ∀ w, G.Adj w u → G.Adj w v → False := fun w h1 h2 => hno w h1.symm h2.symm
    rcases hab with hab | ⟨⟨rfl, rfl⟩ | ⟨rfl, rfl⟩, -⟩ <;>
      rcases hac with hac | ⟨⟨h1, h2⟩ | ⟨h1, h2⟩, -⟩ <;>
      rcases hbc with hbc | ⟨⟨h3, h4⟩ | ⟨h3, h4⟩, -⟩ <;>
      subst_vars <;> first | exact tri _ _ _ hab hac hbc | grind
  exact hlt.not_ge (hG.2 h3 hlt.le)

variable {G : SimpleGraph V} [DecidableRel G.Adj]

/-- M3, general form. If `G` is triangle-free and every degree is at least `α(G)`, then `G` is
MTF. (A larger triangle-free graph would have a vertex of degree `> α`.) -/
theorem isMTF_of_indepNum_le_degree (h3 : G.CliqueFree 3) (hdeg : ∀ v, G.indepNum ≤ G.degree v) :
    IsMTF G := by
  classical
  refine ⟨h3, fun H hH hGH => ?_⟩
  intro a b hab
  by_contra hn
  have hsub : insert b (G.neighborFinset a) ⊆ H.neighborFinset a := by
    intro w hw
    rw [mem_insert] at hw
    rcases hw with rfl | hw
    · simpa using hab
    · simpa using hGH (by simpa using hw)
  have hb : b ∉ G.neighborFinset a := by simpa using hn
  have h1 := card_le_card hsub
  rw [card_insert_of_notMem hb, card_neighborFinset_eq_degree, card_neighborFinset_eq_degree] at h1
  have h2 := degree_le_indepNum hH a
  have h4 := indepNum_anti hGH
  have h5 := hdeg a
  omega

/-- M3. A 9-regular `(3,10,40)`-graph is MTF. -/
theorem isMTF_of_regular_nine (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]
    (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hreg : ∀ v, G.degree v = 9) : IsMTF G :=
  isMTF_of_indepNum_le_degree h3 fun v => by rw [hreg v]; exact hα

/-- Key counting bound for MTF graphs (proof of M1/M2). Let `G` be MTF with `α(G) ≤ k - 1`,
`d = deg v ≤ k`, `Z(v) = ∑_{u ∈ N(v)} deg u`. Then `d + 2 |V \ N[v]| ≤ Z(v) + d (k - d)`. -/
theorem IsMTF.degree_add_two_mul_card_outside_le (hG : IsMTF G) {k : ℕ}
    (hα : G.indepNum ≤ k - 1) (v : V) :
    G.degree v + 2 * #(outside G v) ≤
      ∑ u ∈ G.neighborFinset v, G.degree u + G.degree v * (k - G.degree v) := by
  have h3 : G.CliqueFree 3 := hG.1
  have hZ := sum_nbrIn_add_degree h3 v
  have hp := card_nbrIn_eq_one_le h3 hα v
  -- MTF: every `y ∉ N[v]` has a neighbour in `N(v)`
  have step3 : ∀ y ∈ outside G v, 1 ≤ nbrIn G v y := by
    intro y hy
    rw [mem_outside] at hy
    obtain ⟨w, hvw, hyw⟩ := hG.exists_common (Ne.symm hy.1) hy.2
    exact card_pos.2 ⟨w, by simp [hvw, hyw]⟩
  -- `2 |V \ N[v]| ≤ ∑ c + #{c = 1}`
  have step4 : 2 * #(outside G v) ≤
      ∑ y ∈ outside G v, nbrIn G v y + #{y ∈ outside G v | nbrIn G v y = 1} := by
    rw [card_filter, ← sum_add_distrib, mul_comm, ← smul_eq_mul, ← sum_const]
    refine sum_le_sum fun y hy => ?_
    have := step3 y hy
    split_ifs with h <;> omega
  omega

/-- M1. In an MTF `(3,10,40)`-graph every degree is at least 6 (no outside hypothesis). -/
theorem IsMTF.six_le_degree (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (hG : IsMTF G)
    (hα : G.indepNum ≤ 9) (v : Fin 40) : 6 ≤ G.degree v := by
  have key := hG.degree_add_two_mul_card_outside_le (k := 10) hα v
  have hc := card_outside_add (G := G) v
  have hhi := degree_le_nine G hG.1 hα v
  have hZ : ∑ u ∈ G.neighborFinset v, G.degree u ≤ 9 * G.degree v := by
    calc ∑ u ∈ G.neighborFinset v, G.degree u ≤ ∑ _u ∈ G.neighborFinset v, 9 :=
          sum_le_sum fun u _ => degree_le_nine G hG.1 hα u
      _ = 9 * G.degree v := by rw [sum_const, card_neighborFinset_eq_degree, smul_eq_mul, mul_comm]
  simp only [Fintype.card_fin] at hc
  by_contra hlt
  interval_cases h : G.degree v <;> omega

/-- M2. In an MTF `(3,10,40)`-graph, `Z(v) ≥ d^2 - 11 d + 78` with `d = deg v`
(stated as `d^2 + 78 ≤ Z(v) + 11 d`). -/
theorem IsMTF.sum_degree_neighbor_ge (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]
    (hG : IsMTF G) (hα : G.indepNum ≤ 9) (v : Fin 40) :
    G.degree v ^ 2 + 78 ≤ ∑ u ∈ G.neighborFinset v, G.degree u + 11 * G.degree v := by
  have key := hG.degree_add_two_mul_card_outside_le (k := 10) hα v
  have hc := card_outside_add (G := G) v
  have hhi := degree_le_nine G hG.1 hα v
  simp only [Fintype.card_fin] at hc
  interval_cases h : G.degree v <;> omega

end R310

namespace R310

open SimpleGraph

/-- M0 + M1. If a (3,10,40)-graph exists, then an MTF (3,10,40)-graph with minimum degree
`≥ 6` exists. -/
theorem exists_mtf_min_degree_six (G : SimpleGraph (Fin 40)) (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9) :
    ∃ H : SimpleGraph (Fin 40), H.CliqueFree 3 ∧ H.indepNum ≤ 9 ∧ IsMTF H ∧
      ∀ [DecidableRel H.Adj] (v : Fin 40), 6 ≤ H.degree v := by
  obtain ⟨H, -, hH, hα'⟩ := exists_isMTF_le h3
  exact ⟨H, hH.1, hα'.trans hα, hH, fun v => hH.six_le_degree H (hα'.trans hα) v⟩

end R310
