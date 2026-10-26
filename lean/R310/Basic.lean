/-
Reduction lemmas for (3,k)-graphs (triangle-free graphs with small independence number).

Notation: for a vertex `v`, `outside G v` is the vertex set `V \ N[v]`, and
`delNbhd G v = G.induce (outside G v)` is the induced subgraph `G - N[v]`.
-/
import Mathlib

open Finset

set_option linter.unusedSectionVars false

namespace R310

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]

/-- The vertices outside the closed neighbourhood `N[v]`. -/
def outside (v : V) : Finset V := {w | w ≠ v ∧ ¬ G.Adj v w}

/-- The induced subgraph `G - N[v]` on the vertices outside `N[v]`. -/
abbrev delNbhd (v : V) : SimpleGraph (outside G v : Set V) := G.induce (outside G v : Set V)

variable {G}

@[simp] theorem mem_outside {v w : V} : w ∈ outside G v ↔ w ≠ v ∧ ¬ G.Adj v w := by
  simp [outside]

/-! ### (a) Neighbourhoods are independent; degree bound -/

/-- (a) In a triangle-free graph, every neighbourhood `N(v)` is an independent set. -/
theorem isIndepSet_neighborFinset (h3 : G.CliqueFree 3) (v : V) :
    G.IsIndepSet (G.neighborFinset v : Set V) := by
  rw [coe_neighborFinset]
  exact isIndepSet_neighborSet_of_triangleFree G h3 v

/-- (a) In a triangle-free graph, `deg v ≤ α(G)`. -/
theorem degree_le_indepNum (h3 : G.CliqueFree 3) (v : V) : G.degree v ≤ G.indepNum := by
  rw [← card_neighborFinset_eq_degree]
  exact (isIndepSet_neighborFinset h3 v).card_le_indepNum

/-- (a) In a triangle-free graph with `α(G) ≤ k - 1`, every degree is at most `k - 1`. -/
theorem degree_le_of_indepNum_le (h3 : G.CliqueFree 3) {k : ℕ} (hα : G.indepNum ≤ k - 1)
    (v : V) : G.degree v ≤ k - 1 :=
  (degree_le_indepNum h3 v).trans hα

/-! ### (b) Independence number of `G - N[v]` -/

/-- (b) `α(G - N[v]) + 1 ≤ α(G)`: add `v` to an independent set of `G - N[v]`. -/
theorem indepNum_delNbhd_add_one_le (v : V) : (delNbhd G v).indepNum + 1 ≤ G.indepNum := by
  obtain ⟨s, hs⟩ := (delNbhd G v).exists_isNIndepSet_indepNum
  set t : Finset V := s.map (Function.Embedding.subtype _) with ht
  have hvt : v ∉ t := by
    simp only [ht, mem_map, Function.Embedding.coe_subtype, not_exists, not_and]
    intro x _ hx
    exact (mem_outside.1 (hx ▸ x.2)).1 rfl
  have hind : G.IsIndepSet ((insert v t : Finset V) : Set V) := by
    rw [coe_insert, isIndepSet_iff, Set.pairwise_insert]
    refine ⟨?_, ?_⟩
    · intro a ha b hb hab
      simp only [ht, coe_map, Function.Embedding.coe_subtype, Set.mem_image, mem_coe] at ha hb
      obtain ⟨a, ha, rfl⟩ := ha
      obtain ⟨b, hb, rfl⟩ := hb
      exact hs.isIndepSet ha hb (fun h => hab (congrArg Subtype.val h))
    · intro b hb _
      simp only [ht, coe_map, Function.Embedding.coe_subtype, Set.mem_image, mem_coe] at hb
      obtain ⟨b, _, rfl⟩ := hb
      have := (mem_outside.1 b.2).2
      exact ⟨this, fun h => this h.symm⟩
  calc (delNbhd G v).indepNum + 1 = #(insert v t) := by
        rw [card_insert_of_notMem hvt, ht, card_map, hs.card_eq]
    _ ≤ G.indepNum := hind.card_le_indepNum

/-- (b) If `α(G) ≤ k - 1` then `α(G - N[v]) ≤ k - 2`. -/
theorem indepNum_delNbhd_le {k : ℕ} (hα : G.indepNum ≤ k - 1) (v : V) :
    (delNbhd G v).indepNum ≤ k - 2 := by
  have := indepNum_delNbhd_add_one_le (G := G) v
  omega

/-- `G - N[v]` is triangle-free if `G` is. -/
theorem cliqueFree_delNbhd {n : ℕ} (h : G.CliqueFree n) (v : V) : (delNbhd G v).CliqueFree n :=
  h.comap (Embedding.induce _).isContained

/-! ### (c) Edge count of `G - N[v]` -/

/-- The edges of `G - N[v]` are the edges of `G` with both ends outside `N[v]`. -/
theorem card_edgeFinset_delNbhd (v : V) :
    #(delNbhd G v).edgeFinset = #{e ∈ G.edgeFinset | e.toFinset ⊆ outside G v} :=
  (card_filter_edgeFinset_toFinset_subset (outside G v)).symm

/-- The edges of `G` that meet `N[v]` are the edges incident to some `u ∈ N(v)`. -/
theorem filter_not_subset_outside (v : V) :
    {e ∈ G.edgeFinset | ¬ e.toFinset ⊆ outside G v} =
      (G.neighborFinset v).biUnion (fun u => G.incidenceFinset u) := by
  ext e
  induction e using Sym2.ind with
  | _ a b =>
    simp only [mem_filter, mem_edgeFinset, mem_edgeSet, mem_biUnion, mem_neighborFinset,
      mem_incidenceFinset, incidenceSet, Set.mem_ofPred_eq, Sym2.mem_iff, subset_iff,
      Sym2.mem_toFinset, mem_outside, not_forall, not_and, not_not]
    constructor
    · rintro ⟨hab, x, hx, hxo⟩
      by_cases hxv : x = v
      · subst hxv
        rcases hx with rfl | rfl
        · exact ⟨b, hab, hab, Or.inr rfl⟩
        · exact ⟨a, hab.symm, hab, Or.inl rfl⟩
      · exact ⟨x, hxo hxv, hab, hx⟩
    · rintro ⟨u, hvu, hab, hu⟩
      refine ⟨hab, u, hu, fun _ => hvu⟩

/-- In a triangle-free graph the incidence sets of the neighbours of `v` are pairwise disjoint. -/
theorem pairwiseDisjoint_incidenceFinset (h3 : G.CliqueFree 3) (v : V) :
    ((G.neighborFinset v : Finset V) : Set V).PairwiseDisjoint (fun u => G.incidenceFinset u) := by
  intro a ha b hb hab
  rw [Function.onFun, Finset.disjoint_left]
  intro e hea heb
  rw [mem_incidenceFinset] at hea heb
  exact isIndepSet_neighborFinset h3 v ha hb hab (G.adj_of_mem_incidenceSet hab hea heb)

/-- (c) In a triangle-free graph, `e(G - N[v]) + ∑_{u ∈ N(v)} deg u = e(G)`. -/
theorem card_edgeFinset_delNbhd_add_sum_degree (h3 : G.CliqueFree 3) (v : V) :
    #(delNbhd G v).edgeFinset + ∑ u ∈ G.neighborFinset v, G.degree u = #G.edgeFinset := by
  rw [card_edgeFinset_delNbhd, ← card_filter_add_card_filter_not
    (s := G.edgeFinset) (p := fun e => e.toFinset ⊆ outside G v), filter_not_subset_outside,
    card_biUnion (pairwiseDisjoint_incidenceFinset h3 v)]
  simp_rw [card_incidenceFinset_eq_degree]

/-- (c) In a triangle-free graph, `e(G - N[v]) = e(G) - ∑_{u ∈ N(v)} deg u`. -/
theorem card_edgeFinset_delNbhd_eq (h3 : G.CliqueFree 3) (v : V) :
    #(delNbhd G v).edgeFinset = #G.edgeFinset - ∑ u ∈ G.neighborFinset v, G.degree u := by
  have := card_edgeFinset_delNbhd_add_sum_degree h3 v
  omega

/-! ### (d) Sum over all vertices -/

/-- `∑_v ∑_{u ∈ N(v)} deg u = ∑_u (deg u)^2`. -/
theorem sum_sum_neighborFinset_degree :
    ∑ v, ∑ u ∈ G.neighborFinset v, G.degree u = ∑ u, G.degree u ^ 2 := by
  simp_rw [neighborFinset_eq_filter (G := G), sum_filter]
  rw [sum_comm]
  refine sum_congr rfl fun u _ => ?_
  simp_rw [G.adj_comm _ u]
  rw [← sum_filter, sum_const, ← neighborFinset_eq_filter, card_neighborFinset_eq_degree,
    smul_eq_mul, sq]

/-- (d) In a triangle-free graph on `n` vertices,
`∑_v e(G - N[v]) + ∑_u (deg u)^2 = n · e(G)`. -/
theorem sum_card_edgeFinset_delNbhd_add (h3 : G.CliqueFree 3) :
    ∑ v, #(delNbhd G v).edgeFinset + ∑ u, G.degree u ^ 2 =
      Fintype.card V * #G.edgeFinset := by
  rw [← sum_sum_neighborFinset_degree, ← sum_add_distrib]
  simp_rw [card_edgeFinset_delNbhd_add_sum_degree h3]
  rw [sum_const, card_univ, smul_eq_mul]

/-- (d) In a triangle-free graph on `n` vertices,
`∑_v e(G - N[v]) = n · e(G) - ∑_u (deg u)^2`. -/
theorem sum_card_edgeFinset_delNbhd (h3 : G.CliqueFree 3) :
    ∑ v, #(delNbhd G v).edgeFinset = Fintype.card V * #G.edgeFinset - ∑ u, G.degree u ^ 2 := by
  have := sum_card_edgeFinset_delNbhd_add h3 (G := G)
  omega

end R310
