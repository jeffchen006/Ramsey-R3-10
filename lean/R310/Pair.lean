/-
Lemma L6 (pair lemma) of `notes/cases.md`, with `R(3,8) ≤ 28` as hypothesis, and its
consequences for low degrees.
-/
import R310.MinDegree

open Finset

set_option linter.unusedSectionVars false

namespace R310

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

/-- In a triangle-free graph a clique has at most 2 vertices. -/
theorem card_le_two_of_isClique (h3 : G.CliqueFree 3) {s : Finset V}
    (hs : G.IsClique (s : Set V)) : #s ≤ 2 := by
  by_contra h
  obtain ⟨t, hts, ht⟩ := exists_subset_card_eq (s := s) (n := 3) (by omega)
  exact h3 t ⟨hs.subset (by simpa using hts), ht⟩

variable (G) in
/-- The vertices outside `N[u] ∪ N[v]`. -/
def outside2 (u v : V) : Finset V := outside G u ∩ outside G v

@[simp] theorem mem_outside2 {u v w : V} :
    w ∈ outside2 G u v ↔ (w ≠ u ∧ ¬ G.Adj u w) ∧ (w ≠ v ∧ ¬ G.Adj v w) := by
  simp [outside2]

/-- For distinct non-adjacent `u, v`: `α(G - N[u] - N[v]) + 2 ≤ α(G)`. -/
theorem indepNum_outside2_add_two_le {u v : V} (huv : u ≠ v) (hn : ¬ G.Adj u v) :
    (G.induce (outside2 G u v : Set V)).indepNum + 2 ≤ G.indepNum := by
  obtain ⟨s, hs⟩ := (G.induce (outside2 G u v : Set V)).exists_isNIndepSet_indepNum
  set t : Finset V := s.map (Function.Embedding.subtype _) with ht
  have hmem : ∀ w ∈ t, (w ≠ u ∧ ¬ G.Adj u w) ∧ (w ≠ v ∧ ¬ G.Adj v w) := by
    intro w hw
    simp only [ht, mem_map, Function.Embedding.coe_subtype] at hw
    obtain ⟨x, _, rfl⟩ := hw
    exact mem_outside2.1 x.2
  have hvt : v ∉ t := fun h => (hmem v h).2.1 rfl
  have hut : u ∉ insert v t := by
    rw [mem_insert, not_or]
    exact ⟨huv, fun h => (hmem u h).1.1 rfl⟩
  have hind : G.IsIndepSet ((insert u (insert v t) : Finset V) : Set V) := by
    rw [coe_insert, coe_insert, isIndepSet_iff, Set.pairwise_insert, Set.pairwise_insert]
    refine ⟨⟨?_, ?_⟩, ?_⟩
    · intro a ha b hb hab
      simp only [ht, coe_map, Function.Embedding.coe_subtype, Set.mem_image, mem_coe] at ha hb
      obtain ⟨a, ha, rfl⟩ := ha
      obtain ⟨b, hb, rfl⟩ := hb
      exact hs.isIndepSet ha hb (fun h => hab (congrArg Subtype.val h))
    · intro b hb _
      have := (hmem b hb).2.2
      exact ⟨this, fun h => this h.symm⟩
    · intro b hb _
      rcases hb with rfl | hb
      · exact ⟨hn, fun h => hn h.symm⟩
      · have := (hmem b hb).1.2
        exact ⟨this, fun h => this h.symm⟩
  calc (G.induce (outside2 G u v : Set V)).indepNum + 2 = #(insert u (insert v t)) := by
        rw [card_insert_of_notMem hut, card_insert_of_notMem hvt, ht, card_map, hs.card_eq]
    _ ≤ G.indepNum := hind.card_le_indepNum

/-- `|V \ (N[u] ∪ N[v])| + deg u + deg v + 2 = |V| + |N(u) ∩ N(v)|` for distinct
non-adjacent `u, v`. -/
theorem card_outside2_add {u v : V} (huv : u ≠ v) (hn : ¬ G.Adj u v) :
    #(outside2 G u v) + G.degree u + G.degree v + 2 =
      Fintype.card V + #(G.neighborFinset u ∩ G.neighborFinset v) := by
  have hc : outside2 G u v = (insert u (G.neighborFinset u) ∪ insert v (G.neighborFinset v))ᶜ := by
    ext w
    simp only [mem_outside2, mem_compl, mem_union, mem_insert, mem_neighborFinset]
    tauto
  have hi : insert u (G.neighborFinset u) ∩ insert v (G.neighborFinset v) =
      G.neighborFinset u ∩ G.neighborFinset v := by
    ext w
    simp only [mem_inter, mem_insert, mem_neighborFinset]
    constructor
    · rintro ⟨rfl | h1, rfl | h2⟩
      · exact absurd rfl huv
      · exact absurd h2.symm hn
      · exact absurd h1 hn
      · exact ⟨h1, h2⟩
    · rintro ⟨h1, h2⟩
      exact ⟨Or.inr h1, Or.inr h2⟩
  have hU := card_union_add_card_inter (insert u (G.neighborFinset u))
    (insert v (G.neighborFinset v))
  rw [hi, card_insert_of_notMem (G.notMem_neighborFinset_self u),
    card_insert_of_notMem (G.notMem_neighborFinset_self v), card_neighborFinset_eq_degree,
    card_neighborFinset_eq_degree] at hU
  have hcard := card_compl (insert u (G.neighborFinset u) ∪ insert v (G.neighborFinset v))
  have hle := card_le_univ (insert u (G.neighborFinset u) ∪ insert v (G.neighborFinset v))
  rw [hc]
  omega

/-- L6, general form. `G` triangle-free with `α(G) ≤ k - 1`, `R(3, k-2) ≤ m` (hypothesis),
`u ≠ v` non-adjacent. Then `|V| + |N(u) ∩ N(v)| < deg u + deg v + 2 + m`. -/
theorem pair_lemma_general (h3 : G.CliqueFree 3) {k m : ℕ} (hα : G.indepNum ≤ k - 1)
    (hR : Ramsey3Le (k - 2) m) {u v : V} (huv : u ≠ v) (hn : ¬ G.Adj u v) :
    Fintype.card V + #(G.neighborFinset u ∩ G.neighborFinset v) <
      G.degree u + G.degree v + 2 + m := by
  have hc := card_outside2_add huv hn (G := G)
  by_contra hlt
  have hm : m ≤ Fintype.card (outside2 G u v : Set V) := by
    simp only [Finset.coe_sort_coe, Fintype.card_coe]
    omega
  have h1 := hR.le_indepNum hm _ (h3.comap (Embedding.induce _).isContained)
  have h2 := indepNum_outside2_add_two_le huv hn (G := G)
  omega

/-- L6 for a (3,10,40)-graph, assuming `R(3,8) ≤ 28`: if `u ≠ v` are non-adjacent then
`|N(u) ∩ N(v)| + 11 ≤ deg u + deg v`. -/
theorem pair_lemma (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9) (hR8 : Ramsey3Le 8 28) {u v : Fin 40} (huv : u ≠ v)
    (hn : ¬ G.Adj u v) :
    #(G.neighborFinset u ∩ G.neighborFinset v) + 11 ≤ G.degree u + G.degree v := by
  have := pair_lemma_general (k := 10) h3 hα hR8 huv hn
  simp only [Fintype.card_fin] at this
  omega

/-- L6 consequence: if `deg u + deg v ≤ 10` and `u ≠ v` then `u ~ v`. -/
theorem adj_of_degree_add_le (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]
    (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR8 : Ramsey3Le 8 28) {u v : Fin 40}
    (huv : u ≠ v) (hd : G.degree u + G.degree v ≤ 10) : G.Adj u v := by
  by_contra hn
  have := pair_lemma G h3 hα hR8 huv hn
  omega

/-- L6 consequence: `n4 + n5 ≤ 2` (the vertices of degree `≤ 5` form a clique). -/
theorem card_degree_le_five (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]
    (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR8 : Ramsey3Le 8 28) :
    #{v | G.degree v ≤ 5} ≤ 2 := by
  apply card_le_two_of_isClique h3
  intro a ha b hb hab
  simp only [coe_filter, mem_univ, true_and, Set.mem_ofPred_eq] at ha hb
  exact adj_of_degree_add_le G h3 hα hR8 hab (by omega)

/-- L6 consequence: if `deg u = 4`, then `u` is adjacent to every other vertex of degree `≤ 6`,
so `#{w | deg w ≤ 6} ≤ 5`, i.e. `(n4 - 1) + n5 + n6 ≤ 4`. -/
theorem card_degree_le_six_of_deg4 (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]
    (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR8 : Ramsey3Le 8 28) {u : Fin 40}
    (hu : G.degree u = 4) : #{w | G.degree w ≤ 6} ≤ 5 := by
  have hsub : ({w | G.degree w ≤ 6} : Finset (Fin 40)) ⊆ insert u (G.neighborFinset u) := by
    intro w hw
    simp only [mem_filter, mem_univ, true_and] at hw
    rw [mem_insert, mem_neighborFinset]
    by_cases hwu : w = u
    · exact Or.inl hwu
    · exact Or.inr (adj_of_degree_add_le G h3 hα hR8 (Ne.symm hwu) (by omega))
  have := card_le_card hsub
  rw [card_insert_of_notMem (G.notMem_neighborFinset_self u), card_neighborFinset_eq_degree,
    hu] at this
  exact this

/-- L6 consequence: if two distinct vertices have degree 4, no vertex has degree 6. -/
theorem no_degree_six_of_two_deg4 (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]
    (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR8 : Ramsey3Le 8 28) {u u' : Fin 40}
    (hne : u ≠ u') (hu : G.degree u = 4) (hu' : G.degree u' = 4) (w : Fin 40) :
    G.degree w ≠ 6 := by
  intro hw
  have hwu : w ≠ u := fun h => by rw [h, hu] at hw; omega
  have hwu' : w ≠ u' := fun h => by rw [h, hu'] at hw; omega
  have h1 := adj_of_degree_add_le G h3 hα hR8 hne (by omega)
  have h2 := adj_of_degree_add_le G h3 hα hR8 hwu (by omega)
  have h3' := adj_of_degree_add_le G h3 hα hR8 hwu' (by omega)
  exact h3 {u, u', w} (is3Clique_triple_iff.2 ⟨h1, h2.symm, h3'.symm⟩)

end R310
