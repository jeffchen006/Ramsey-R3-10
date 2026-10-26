/-
Local structure around a vertex `v`: edges between `N(v)` and `H_v = G - N[v]`, and degrees
inside `H_v`.
-/
import R310.Basic

open Finset

set_option linter.unusedSectionVars false

namespace R310

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

variable (G) in
/-- `c_v(y) = |N(y) ∩ N(v)|`, the number of neighbours of `y` in `N(v)`. -/
def nbrIn (v y : V) : ℕ := #{x ∈ G.neighborFinset v | G.Adj y x}

/-- Every vertex of `V` is `v`, in `N(v)`, or in `V \ N[v]`: for any predicate `p`,
`#{w | p w} = [p v] + #{x ∈ N(v) | p x} + #{y ∈ V \ N[v] | p y}`. -/
theorem card_filter_split (p : V → Prop) [DecidablePred p] (v : V) :
    #{w | p w} = (if p v then 1 else 0) + #{x ∈ G.neighborFinset v | p x} +
      #{y ∈ outside G v | p y} := by
  have hu : (univ : Finset V) = insert v (G.neighborFinset v ∪ outside G v) := by
    ext w
    simp only [mem_univ, mem_insert, mem_union, mem_neighborFinset, mem_outside, true_iff]
    tauto
  have hd1 : v ∉ G.neighborFinset v ∪ outside G v := by simp
  have hd2 : Disjoint (G.neighborFinset v) (outside G v) := by
    rw [Finset.disjoint_left]
    intro w hw hw'
    exact (mem_outside.1 hw').2 ((mem_neighborFinset _ _ _).1 hw)
  rw [hu, filter_insert, filter_union]
  have hdisj := disjoint_filter_filter (p := p) (q := p) hd2
  have hv : v ∉ ({w ∈ G.neighborFinset v | p w} ∪ {w ∈ outside G v | p w}) := by simp
  split_ifs with hp
  · rw [card_insert_of_notMem hv, card_union_of_disjoint hdisj]
    ac_rfl
  · rw [card_union_of_disjoint hdisj]
    ac_rfl

/-- In a triangle-free graph: `∑_{y ∈ V \ N[v]} c_v(y) + deg v = ∑_{u ∈ N(v)} deg u`. -/
theorem sum_nbrIn_add_degree (h3 : G.CliqueFree 3) (v : V) :
    ∑ y ∈ outside G v, nbrIn G v y + G.degree v = ∑ u ∈ G.neighborFinset v, G.degree u := by
  have step1 : ∑ y ∈ outside G v, nbrIn G v y =
      ∑ x ∈ G.neighborFinset v, #{y ∈ outside G v | G.Adj x y} := by
    simp only [nbrIn, card_filter]
    rw [sum_comm]
    exact sum_congr rfl fun x _ => sum_congr rfl fun y _ => if_congr (G.adj_comm _ _) rfl rfl
  have step2 : ∀ x ∈ G.neighborFinset v, #{y ∈ outside G v | G.Adj x y} + 1 = G.degree x := by
    intro x hx
    rw [mem_neighborFinset] at hx
    have heq : G.neighborFinset x = insert v {y ∈ outside G v | G.Adj x y} := by
      ext w
      simp only [mem_neighborFinset, mem_insert, mem_filter, mem_outside]
      constructor
      · intro hxw
        by_cases hwv : w = v
        · exact Or.inl hwv
        · refine Or.inr ⟨⟨hwv, fun hvw => ?_⟩, hxw⟩
          exact h3 {v, x, w} (is3Clique_triple_iff.2 ⟨hx, hvw, hxw⟩)
      · rintro (rfl | ⟨-, hxw⟩)
        · exact hx.symm
        · exact hxw
    rw [← card_neighborFinset_eq_degree, heq, card_insert_of_notMem]
    simp
  rw [step1, ← card_neighborFinset_eq_degree G v, card_eq_sum_ones, ← sum_add_distrib]
  exact sum_congr rfl fun x hx => step2 x hx

/-- The degree of `y` inside `H_v = G - N[v]` is `#{z ∈ V \ N[v] | y ~ z}`. -/
theorem degree_delNbhd (v : V) (y : (outside G v : Set V)) :
    (delNbhd G v).degree y = #{z ∈ outside G v | G.Adj y z} := by
  have h := congrArg card (map_neighborFinset_induce (G := G) (s := (outside G v : Set V)) y)
  rw [card_map] at h
  rw [← card_neighborFinset_eq_degree]
  convert h using 2
  all_goals (ext z; simp [mem_neighborFinset, and_comm])

/-- For `y ∉ N[v]`: `deg y = deg_{H_v} y + c_v(y)`. -/
theorem degree_eq_degree_delNbhd_add (v : V) (y : (outside G v : Set V)) :
    G.degree y = (delNbhd G v).degree y + nbrIn G v y := by
  have hy := mem_outside.1 (mem_coe.1 y.2)
  rw [degree_delNbhd, nbrIn, ← card_union_of_disjoint]
  · rw [← card_neighborFinset_eq_degree]
    congr 1
    ext z
    simp only [mem_neighborFinset, mem_union, mem_filter, mem_outside]
    constructor
    · intro hyz
      by_cases hzv : z = v
      · exact absurd (hzv ▸ hyz.symm) hy.2
      · by_cases hvz : G.Adj v z
        · exact Or.inr ⟨hvz, hyz⟩
        · exact Or.inl ⟨⟨hzv, hvz⟩, hyz⟩
    · rintro (⟨-, h⟩ | ⟨-, h⟩) <;> exact h
  · rw [Finset.disjoint_left]
    intro z hz hz'
    simp only [mem_filter, mem_outside, mem_neighborFinset] at hz hz'
    exact hz.1.2 hz'.1

/-- Private vertices. In a triangle-free graph with `α(G) ≤ k - 1`, at most `deg v (k - deg v)`
vertices outside `N[v]` have exactly one neighbour in `N(v)`. (For `x ∈ N(v)`, the vertices whose
only `N(v)`-neighbour is `x`, together with `N(v) - x`, form an independent set.) -/
theorem card_nbrIn_eq_one_le (h3 : G.CliqueFree 3) {k : ℕ} (hα : G.indepNum ≤ k - 1) (v : V) :
    #{y ∈ outside G v | nbrIn G v y = 1} ≤ G.degree v * (k - G.degree v) := by
  set A := G.neighborFinset v with hA
  set H := outside G v with hH
  set d := G.degree v with hd
  let P : V → Finset V := fun x => {y ∈ H | nbrIn G v y = 1 ∧ G.Adj x y}
  have hP : ∀ x y, y ∈ P x ↔ y ∈ H ∧ nbrIn G v y = 1 ∧ G.Adj x y := fun x y => by
    simp only [P, mem_filter]
  have step5 : #{y ∈ H | nbrIn G v y = 1} ≤ ∑ x ∈ A, #(P x) := by
    refine (card_le_card ?_).trans card_biUnion_le
    intro y hy
    rw [mem_filter] at hy
    have hy2 := hy.2
    unfold nbrIn at hy2
    obtain ⟨x, hx⟩ := card_pos.1 (by rw [hA]; omega : 0 < #{x ∈ A | G.Adj y x})
    rw [mem_filter] at hx
    exact mem_biUnion.2 ⟨x, hx.1, (hP x y).2 ⟨hy.1, hy.2, hx.2.symm⟩⟩
  have step6 : ∀ x ∈ A, #(P x) + d ≤ k := by
    intro x hx
    have hdisj : Disjoint (P x) (A.erase x) := by
      rw [Finset.disjoint_left]
      intro y hy hyA
      have hy' := ((hP x y).1 hy).1
      rw [hH, mem_outside] at hy'
      exact hy'.2 (by simpa [hA] using mem_of_mem_erase hyA)
    have huniq : ∀ y ∈ P x, ∀ a ∈ A, G.Adj y a → a = x := by
      intro y hy a ha hya
      rw [hP] at hy
      have hy1 := hy.2.1
      unfold nbrIn at hy1
      obtain ⟨z, hz⟩ := card_eq_one.1 hy1
      have h1 : a ∈ ({x ∈ A | G.Adj y x} : Finset V) := by simp [ha, hya]
      have h2 : x ∈ ({x ∈ A | G.Adj y x} : Finset V) := by simp [hx, hy.2.2.symm]
      rw [hA, hz, mem_singleton] at h1 h2
      rw [h1, h2]
    have hind : G.IsIndepSet ((P x ∪ A.erase x : Finset V) : Set V) := by
      rw [coe_union, isIndepSet_iff, Set.pairwise_union]
      refine ⟨?_, ?_, ?_⟩
      · intro y hy y' hy' hne hyy'
        rw [mem_coe, hP] at hy hy'
        exact h3 {x, y, y'} (is3Clique_triple_iff.2 ⟨hy.2.2, hy'.2.2, hyy'⟩)
      · intro a ha b hb hab
        exact isIndepSet_neighborFinset h3 v (mem_of_mem_erase ha) (mem_of_mem_erase hb) hab
      · intro y hy a ha _
        have hax : a ≠ x := ne_of_mem_erase ha
        have haA : a ∈ A := mem_of_mem_erase ha
        exact ⟨fun h => hax (huniq y hy a haA h), fun h => hax (huniq y hy a haA h.symm)⟩
    have hcard := hind.card_le_indepNum
    rw [card_union_of_disjoint hdisj, card_erase_of_mem hx] at hcard
    have : 1 ≤ #A := card_pos.2 ⟨x, hx⟩
    have hdA : #A = d := card_neighborFinset_eq_degree G v
    have := hcard.trans hα
    have hone : #({v} : Finset V) ≤ G.indepNum :=
      (show G.IsIndepSet (({v} : Finset V) : Set V) by simp).card_le_indepNum
    rw [card_singleton] at hone
    omega
  calc #{y ∈ H | nbrIn G v y = 1} ≤ ∑ x ∈ A, #(P x) := step5
    _ ≤ ∑ _x ∈ A, (k - d) := sum_le_sum fun x hx => by have := step6 x hx; omega
    _ = d * (k - d) := by rw [sum_const, smul_eq_mul, hA, card_neighborFinset_eq_degree]

end R310
