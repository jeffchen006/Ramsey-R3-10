/-
Lemma L9 (9-regular case) and Lemma L7 (degree-4 vertex) of `notes/cases.md`.
-/
import R310.Pair
import R310.MTF
import R310.Regular

open Finset

set_option linter.unusedSectionVars false

namespace R310

open SimpleGraph

/-- `nbrIn G v y = |N(v) ∩ N(y)|`. -/
theorem nbrIn_eq_card_inter {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (v y : V) :
    nbrIn G v y = #(G.neighborFinset v ∩ G.neighborFinset y) := by
  unfold nbrIn
  congr 1
  ext x
  simp [mem_neighborFinset]

/-- In a triangle-free graph the degree of `y` inside `H_v` is at most `α(H_v)`. -/
theorem degree_delNbhd_le_indepNum {V : Type*} [Fintype V] [DecidableEq V]
    {G : SimpleGraph V} [DecidableRel G.Adj] (h3 : G.CliqueFree 3) (v : V)
    (y : (outside G v : Set V)) : (delNbhd G v).degree y ≤ (delNbhd G v).indepNum :=
  degree_le_indepNum (cliqueFree_delNbhd h3 v) y

variable (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]

/-! ### L9: the 9-regular case -/

section Regular

variable (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR8 : Ramsey3Le 8 28)
  (hreg : ∀ v, G.degree v = 9)
include h3 hα hR8 hreg

/-- L9. In a 9-regular (3,10,40)-graph, distinct non-adjacent `u, v` have between 1 and 7
common neighbours. -/
theorem regular_card_common (u v : Fin 40) (huv : u ≠ v) (hn : ¬ G.Adj u v) :
    1 ≤ #(G.neighborFinset u ∩ G.neighborFinset v) ∧
      #(G.neighborFinset u ∩ G.neighborFinset v) ≤ 7 := by
  obtain ⟨w, huw, hvw⟩ := (isMTF_of_regular_nine G h3 hα hreg).exists_common huv hn
  refine ⟨card_pos.2 ⟨w, by simp [huw, hvw]⟩, ?_⟩
  have := pair_lemma G h3 hα hR8 huv hn
  rw [hreg, hreg] at this
  omega

/-- L9. For `y ∉ N[v]`: `1 ≤ c_v(y) ≤ 7`, `deg_{H_v} y + c_v(y) = 9`, `2 ≤ deg_{H_v} y ≤ 8`. -/
theorem regular_nbrIn (v : Fin 40) (y : (outside G v : Set (Fin 40))) :
    1 ≤ nbrIn G v y ∧ nbrIn G v y ≤ 7 ∧ (delNbhd G v).degree y + nbrIn G v y = 9 ∧
      2 ≤ (delNbhd G v).degree y ∧ (delNbhd G v).degree y ≤ 8 := by
  have hy := mem_outside.1 (mem_coe.1 y.2)
  have hc := regular_card_common G h3 hα hR8 hreg v y (Ne.symm hy.1) hy.2
  rw [← nbrIn_eq_card_inter] at hc
  have hd := degree_eq_degree_delNbhd_add (G := G) v y
  rw [hreg] at hd
  have h8 := (degree_delNbhd_le_indepNum h3 v y).trans (indepNum_delNbhd_le (k := 10) hα v)
  omega

/-- L9. `∑_{y ∉ N[v]} c_v(y) = 72` (the 72 edges between `N(v)` and `H_v`). -/
theorem regular_sum_nbrIn (v : Fin 40) : ∑ y ∈ outside G v, nbrIn G v y = 72 := by
  have := sum_nbrIn_add_degree h3 v
  simp only [hreg, sum_const, card_neighborFinset_eq_degree, smul_eq_mul] at this
  omega

/-- L9. At most 9 vertices of `H_v` have degree 8 in `H_v` (equivalently `c_v(y) = 1`). -/
theorem regular_card_private (v : Fin 40) : #{y ∈ outside G v | nbrIn G v y = 1} ≤ 9 := by
  have := card_nbrIn_eq_one_le (k := 10) h3 hα v
  rw [hreg] at this
  simpa using this

omit hR8 hreg in
/-- L9. For `x ∈ N(v)`, `S_x = N(x) - v` is an independent set inside `V \ N[v]` with
`deg x - 1` elements. -/
theorem nbr_erase_subset_outside (v x : Fin 40) (hx : G.Adj v x) :
    (G.neighborFinset x).erase v ⊆ outside G v ∧
      G.IsIndepSet (((G.neighborFinset x).erase v : Finset (Fin 40)) : Set (Fin 40)) ∧
      #((G.neighborFinset x).erase v) + 1 = G.degree x := by
  refine ⟨?_, ?_, ?_⟩
  · intro w hw
    rw [mem_erase, mem_neighborFinset] at hw
    rw [mem_outside]
    exact ⟨hw.1, fun hvw => h3 {v, x, w} (is3Clique_triple_iff.2 ⟨hx, hvw, hw.2⟩)⟩
  · exact Set.Pairwise.mono (fun z hz => by simp only [mem_coe, mem_erase] at hz ⊢; exact hz.2)
      (isIndepSet_neighborFinset h3 x)
  · rw [card_erase_of_mem (by simpa using hx.symm), card_neighborFinset_eq_degree]
    have : 0 < G.degree x := (G.degree_pos_iff_exists_adj x).2 ⟨v, hx.symm⟩
    omega

end Regular

/-! ### L7: a vertex of degree 4 -/

/-- Every `(3,9,35)`-graph is 8-regular. Hypothesis; it follows from [GR] Thm 3 (the unique
`(3,9,35)`-graph is the 8-regular circulant `C35(1,7,11,16)`, Kalbfleisch 1966). -/
def Regular35 : Prop :=
  ∀ (H : SimpleGraph (Fin 35)) [DecidableRel H.Adj], H.CliqueFree 3 → H.indepNum < 9 →
    ∀ v, H.degree v = 8

theorem Regular35.degree_eq (h : Regular35) {W : Type*} [Fintype W] [DecidableEq W]
    (hW : Fintype.card W = 35) (H : SimpleGraph W) [DecidableRel H.Adj] (h3 : H.CliqueFree 3)
    (hα : H.indepNum < 9) (w : W) : H.degree w = 8 := by
  classical
  let e : W ≃ Fin 35 := Fintype.equivOfCardEq (by simpa using hW)
  let φ : H ≃g H.map e.toEmbedding := Iso.map e H
  have := h (H.map e.toEmbedding) (h3.comap φ.symm.toEmbedding.isContained)
    ((indepNum_le_of_embedding φ.symm.toEmbedding).trans_lt hα) (e.toEmbedding w)
  rwa [degree_map_apply] at this

section Degree4

variable (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR8 : Ramsey3Le 8 28)
  (h35 : Regular35) (u : Fin 40) (hu : G.degree u = 4)
include h3 hα h35 hu

/-- L7. If `deg u = 4`, then `H_u` is 8-regular (it is a (3,9,35)-graph). -/
theorem deg4_delNbhd_regular (y : (outside G u : Set (Fin 40))) : (delNbhd G u).degree y = 8 := by
  have hc := card_delNbhd_verts (G := G) u
  rw [hu, Fintype.card_fin] at hc
  have h2 := indepNum_delNbhd_add_one_le (G := G) u
  exact h35.degree_eq (by omega) _ (cliqueFree_delNbhd h3 u) (by omega) y

/-- L7. If `deg u = 4`, every `y ∉ N[u]` has `deg y = 8 + c_u(y)` and `c_u(y) ≤ 1`. -/
theorem deg4_degree_outside (y : (outside G u : Set (Fin 40))) :
    G.degree y = 8 + nbrIn G u y ∧ nbrIn G u y ≤ 1 := by
  have hd := degree_eq_degree_delNbhd_add (G := G) u y
  rw [deg4_delNbhd_regular G h3 hα h35 u hu y] at hd
  have := degree_le_nine G h3 hα y
  omega

/-- L7. If `deg u = 4` then `e(H_u) = 140` and `e(G) = 140 + Z(u)`. -/
theorem deg4_card_edgeFinset :
    #(delNbhd G u).edgeFinset = 140 ∧
      #G.edgeFinset = 140 + ∑ x ∈ G.neighborFinset u, G.degree x := by
  have hc := card_delNbhd_verts (G := G) u
  rw [hu, Fintype.card_fin] at hc
  have hs := sum_degrees_eq_twice_card_edges (delNbhd G u)
  simp only [deg4_delNbhd_regular G h3 hα h35 u hu, sum_const, card_univ, smul_eq_mul] at hs
  have h140 : #(delNbhd G u).edgeFinset = 140 := by omega
  have hL2 := card_edgeFinset_delNbhd_add_sum_degree h3 (G := G) u
  exact ⟨h140, by omega⟩

/-- L7. If `deg u = 4`: `#{y ∉ N[u] | deg y = 9} + 4 = Z(u)` and
`#{y ∉ N[u] | deg y = 8} + #{y ∉ N[u] | deg y = 9} = 35`. -/
theorem deg4_count_outside :
    #{y ∈ outside G u | G.degree y = 9} + 4 = ∑ x ∈ G.neighborFinset u, G.degree x ∧
      #{y ∈ outside G u | G.degree y = 8} + #{y ∈ outside G u | G.degree y = 9} = 35 := by
  have hdeg : ∀ y ∈ outside G u, G.degree y = 8 + nbrIn G u y ∧ nbrIn G u y ≤ 1 :=
    fun y hy => deg4_degree_outside G h3 hα h35 u hu ⟨y, hy⟩
  have hZ := sum_nbrIn_add_degree h3 u
  rw [hu] at hZ
  have h9 : #{y ∈ outside G u | G.degree y = 9} = ∑ y ∈ outside G u, nbrIn G u y := by
    rw [card_filter]
    refine sum_congr rfl fun y hy => ?_
    obtain ⟨h1, h2⟩ := hdeg y hy
    split_ifs with h <;> omega
  have hc := card_delNbhd_verts (G := G) u
  rw [hu, Fintype.card_fin] at hc
  simp only [Finset.coe_sort_coe, Fintype.card_coe] at hc
  have h89 : #{y ∈ outside G u | G.degree y = 8} + #{y ∈ outside G u | G.degree y = 9} =
      #(outside G u) := by
    rw [← card_union_of_disjoint (disjoint_filter.2 fun _ _ h1 h2 => by omega), ← filter_or]
    congr 1
    refine filter_true_of_mem fun y hy => ?_
    obtain ⟨h1, h2⟩ := hdeg y hy
    omega
  omega

include hR8 in
/-- L7. If `deg u = 4` and `x ≠ x'` are neighbours of `u`, then `deg x + deg x' ≥ 12`
(hypothesis `R(3,8) ≤ 28` for L6). -/
theorem deg4_nbr_degree_sum (x x' : Fin 40) (hx : G.Adj u x) (hx' : G.Adj u x') (hne : x ≠ x') :
    12 ≤ G.degree x + G.degree x' := by
  have hn : ¬ G.Adj x x' := isIndepSet_neighborFinset h3 u (by simpa using hx)
    (by simpa using hx') hne
  have hcommon : G.neighborFinset x ∩ G.neighborFinset x' = {u} := by
    ext w
    simp only [mem_inter, mem_neighborFinset, mem_singleton]
    constructor
    · rintro ⟨hxw, hx'w⟩
      by_contra hwu
      by_cases huw : G.Adj u w
      · exact isIndepSet_neighborFinset h3 u (by simpa using hx) (by simpa using huw)
          (fun h => by subst h; exact G.irrefl hxw) hxw
      · have hw : w ∈ outside G u := mem_outside.2 ⟨hwu, huw⟩
        have : nbrIn G u w ≤ 1 := (deg4_degree_outside G h3 hα h35 u hu ⟨w, hw⟩).2
        rw [nbrIn_eq_card_inter] at this
        have h2 : ({x, x'} : Finset (Fin 40)) ⊆ G.neighborFinset u ∩ G.neighborFinset w := by
          intro z hz
          simp only [mem_insert, mem_singleton] at hz
          rcases hz with rfl | rfl <;> simp [hx, hx', hxw.symm, hx'w.symm]
        have := card_le_card h2
        rw [card_pair hne] at this
        omega
    · rintro rfl
      exact ⟨hx.symm, hx'.symm⟩
  have := pair_lemma G h3 hα hR8 hne hn
  rw [hcommon, card_singleton] at this
  omega

/-- L7. Degree counts when `deg u = 4`. For every `D`,
`n_D = [D = 4] + #{x ∈ N(u) | deg x = D} + #{y ∉ N[u] | deg y = D}`; the last term is
`Z(u) - 4` for `D = 9`, `39 - Z(u)` for `D = 8`, and `0` otherwise. -/
theorem deg4_degree_counts (D : ℕ) :
    #{w | G.degree w = D} = (if D = 4 then 1 else 0) + #{x ∈ G.neighborFinset u | G.degree x = D} +
      #{y ∈ outside G u | G.degree y = D} ∧
    (D ≠ 8 → D ≠ 9 → #{y ∈ outside G u | G.degree y = D} = 0) := by
  refine ⟨?_, fun h8 h9 => ?_⟩
  · rw [card_filter_split (G := G) (fun w => G.degree w = D) u, hu]
    simp only [eq_comm]
  · rw [card_eq_zero, filter_eq_empty_iff]
    intro y hy
    have : G.degree y = 8 + nbrIn G u y ∧ nbrIn G u y ≤ 1 :=
      deg4_degree_outside G h3 hα h35 u hu ⟨y, hy⟩
    omega

end Degree4

end R310
