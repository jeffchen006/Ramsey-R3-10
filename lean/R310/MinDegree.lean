/-
(e) Lower bound on degrees from an outside Ramsey value, taken as an explicit hypothesis.
-/
import R310.Basic

open Finset

set_option linter.unusedSectionVars false

namespace R310

open SimpleGraph

/-- `Ramsey3Le k m`: every triangle-free graph on `m` vertices has an independent set of `k`
vertices. Equivalently `R(3,k) ≤ m`, or: no `(3,k,m)`-graph exists.
This is used only as a hypothesis (for example `Ramsey3Le 9 36`, i.e. `R(3,9) = 36`,
Grinstead–Roberts 1982). -/
def Ramsey3Le (k m : ℕ) : Prop :=
  ∀ H : SimpleGraph (Fin m), H.CliqueFree 3 → k ≤ H.indepNum

/-- `Ramsey3Le k m` applies to every finite vertex type with at least `m` vertices. -/
theorem Ramsey3Le.le_indepNum {k m : ℕ} (hR : Ramsey3Le k m) {W : Type*} [Fintype W]
    (hW : m ≤ Fintype.card W) (H : SimpleGraph W) (h3 : H.CliqueFree 3) : k ≤ H.indepNum := by
  classical
  obtain ⟨f⟩ : Nonempty (Fin m ↪ W) := Function.Embedding.nonempty_of_card_le (by simpa using hW)
  have hk := hR (H.comap f) (h3.comap (Embedding.comap f H).isContained)
  obtain ⟨s, hs⟩ := (H.comap f).exists_isNIndepSet_indepNum
  have hind : H.IsIndepSet ((s.map f : Finset W) : Set W) := by
    intro a ha b hb hab
    simp only [coe_map, Set.mem_image, mem_coe] at ha hb
    obtain ⟨a, ha, rfl⟩ := ha
    obtain ⟨b, hb, rfl⟩ := hb
    exact hs.isIndepSet ha hb (fun h => hab (congrArg f h))
  calc k ≤ (H.comap f).indepNum := hk
    _ = #(s.map f) := by rw [card_map, hs.card_eq]
    _ ≤ H.indepNum := hind.card_le_indepNum

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

theorem outside_eq_compl (v : V) : outside G v = (insert v (G.neighborFinset v))ᶜ := by
  ext w
  simp only [mem_outside, mem_compl, mem_insert, mem_neighborFinset, not_or]

/-- `|V \ N[v]| + deg v + 1 = |V|`. -/
theorem card_outside_add (v : V) : #(outside G v) + G.degree v + 1 = Fintype.card V := by
  rw [outside_eq_compl, card_compl, card_insert_of_notMem (G.notMem_neighborFinset_self v),
    card_neighborFinset_eq_degree]
  have : G.degree v + 1 ≤ Fintype.card V := by
    rw [← card_neighborFinset_eq_degree, ← card_insert_of_notMem (G.notMem_neighborFinset_self v)]
    exact card_le_univ _
  omega

/-- The vertex type of `G - N[v]` has `|V| - deg v - 1` elements. -/
theorem card_delNbhd_verts (v : V) :
    Fintype.card (outside G v : Set V) + G.degree v + 1 = Fintype.card V := by
  rw [← card_outside_add (G := G) v]
  simp only [Finset.coe_sort_coe, Fintype.card_coe]

/-- (e), general form. If `G` is triangle-free, `α(G) ≤ k - 1`, and `R(3, k-1) ≤ m`
(hypothesis), then `|V| ≤ deg v + m` for every vertex `v`. -/
theorem card_le_degree_add (h3 : G.CliqueFree 3) {k m : ℕ} (hα : G.indepNum ≤ k - 1)
    (hR : Ramsey3Le (k - 1) m) (v : V) : Fintype.card V ≤ G.degree v + m := by
  by_contra hlt
  have hcard : m ≤ Fintype.card (outside G v : Set V) := by
    have := card_delNbhd_verts (G := G) v
    omega
  have h1 := hR.le_indepNum hcard (delNbhd G v) (cliqueFree_delNbhd h3 v)
  have h2 := indepNum_delNbhd_add_one_le (G := G) v
  omega

/-- (e) In a `(3,10,40)`-graph, assuming `R(3,9) ≤ 36`, every vertex has degree at least 4. -/
theorem four_le_degree (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9) (hR : Ramsey3Le 9 36) (v : Fin 40) : 4 ≤ G.degree v := by
  have := card_le_degree_add (k := 10) h3 hα hR v
  simp at this
  omega

/-- (a) In a `(3,10,40)`-graph every vertex has degree at most 9. -/
theorem degree_le_nine (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9) (v : Fin 40) : G.degree v ≤ 9 :=
  degree_le_of_indepNum_le (k := 10) h3 hα v

end R310
