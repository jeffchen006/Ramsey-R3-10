import R310.ReciprocalWindow

namespace R310

open Finset SimpleGraph
open scoped BigOperators

/-- Two-term Bonferroni for a finite family; off-diagonal pairs are counted twice.
Writing the lower bound additively avoids truncated natural subtraction. -/
theorem two_mul_sum_card_le_biUnion_add_offDiag {I V : Type*} [DecidableEq I] [DecidableEq V]
    (indices : Finset I) (sites : I → Finset V) :
    2 * (∑ index ∈ indices, #(sites index)) ≤
      2 * #(indices.biUnion sites) + ∑ pair ∈ indices.offDiag, #(sites pair.1 ∩ sites pair.2) := by
  induction indices using Finset.induction_on with
  | empty => simp
  | @insert index rest hNot ih =>
    have hLeft : Disjoint rest.offDiag ({index} ×ˢ rest) := by
      refine disjoint_left.mpr fun pair hOld hNew => ?_
      have hEq : pair.1 = index := by simpa using (mem_product.mp hNew).1
      exact hNot (hEq ▸ (mem_offDiag.mp hOld).1)
    have hRight : Disjoint (rest.offDiag ∪ {index} ×ˢ rest) (rest ×ˢ {index}) := by
      refine disjoint_left.mpr fun pair hOld hNew => ?_
      have hEq : pair.2 = index := by simpa using (mem_product.mp hNew).2
      rcases mem_union.mp hOld with hOld | hOld
      · exact hNot (hEq ▸ (mem_offDiag.mp hOld).2.1)
      · exact hNot (hEq ▸ (mem_product.mp hOld).2)
    have hIntersect : #(sites index ∩ rest.biUnion sites) ≤
        ∑ other ∈ rest, #(sites index ∩ sites other) := by
      rw [inter_biUnion]
      exact card_biUnion_le
    have hUnion := card_union_add_card_inter (sites index) (rest.biUnion sites)
    rw [sum_insert hNot, biUnion_insert, offDiag_insert hNot, sum_union hRight, sum_union hLeft]
    simp only [sum_product, sum_singleton, inter_comm _ (sites index)]
    omega

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

/-- The distinct vertices outside `boundary` reached by at least one vertex of `selected`. -/
def exteriorFootprint (G : SimpleGraph V) [DecidableRel G.Adj]
    (boundary selected : Finset V) : Finset V :=
  selected.biUnion fun vertex => G.neighborFinset vertex \ boundary

/-- Demand for a regular boundary comes from actual degree and actual codegree. An
ordered-pair bound can be tightened independently on chosen pairs. -/
theorem exteriorFootprint_two_term {boundary selected : Finset V} {degree : ℕ}
    (upper : V → V → ℕ)
    (hDegree : ∀ vertex ∈ selected, G.degree vertex = degree)
    (hUpper : ∀ first ∈ selected, ∀ second ∈ selected, first ≠ second →
      #(G.neighborFinset first ∩ G.neighborFinset second) ≤ upper first second) :
    2 * (∑ vertex ∈ selected, (degree - windowDegree G boundary vertex)) ≤
      2 * #(exteriorFootprint G boundary selected) + ∑ pair ∈ selected.offDiag,
        (upper pair.1 pair.2 - #((G.neighborFinset pair.1 ∩ G.neighborFinset pair.2) ∩ boundary)) := by
  have hBonf := two_mul_sum_card_le_biUnion_add_offDiag selected
    (fun vertex => G.neighborFinset vertex \ boundary)
  have hDemand : ∑ vertex ∈ selected, #(G.neighborFinset vertex \ boundary) =
      ∑ vertex ∈ selected, (degree - windowDegree G boundary vertex) := by
    refine sum_congr rfl fun vertex hMem => ?_
    have hSplit := card_sdiff_add_card_inter (G.neighborFinset vertex) boundary
    rw [card_neighborFinset_eq_degree, hDegree vertex hMem] at hSplit
    change #(G.neighborFinset vertex \ boundary) + windowDegree G boundary vertex = degree at hSplit
    omega
  have hCaps : (∑ pair ∈ selected.offDiag,
      #((G.neighborFinset pair.1 \ boundary) ∩ (G.neighborFinset pair.2 \ boundary))) ≤
      ∑ pair ∈ selected.offDiag,
        (upper pair.1 pair.2 - #((G.neighborFinset pair.1 ∩ G.neighborFinset pair.2) ∩ boundary)) := by
    refine sum_le_sum fun pair hMem => ?_
    obtain ⟨hFirst, hSecond, hNe⟩ := mem_offDiag.mp hMem
    have hBound := hUpper pair.1 hFirst pair.2 hSecond hNe
    have hInter : (G.neighborFinset pair.1 \ boundary) ∩ (G.neighborFinset pair.2 \ boundary) =
        (G.neighborFinset pair.1 ∩ G.neighborFinset pair.2) \ boundary := by
      ext vertex
      simp only [mem_inter, mem_sdiff]
      tauto
    rw [hInter]
    have hSplit := card_sdiff_add_card_inter (G.neighborFinset pair.1 ∩ G.neighborFinset pair.2)
      boundary
    omega
  rw [hDemand] at hBonf
  exact hBonf.trans (Nat.add_le_add_left hCaps _)

/-- A book of 11 sites in an order-40 graph has exterior capacity 29. For regular
degree nine, any subset whose two-term lower bound exceeds that capacity is impossible. -/
theorem book_footprint_le_twenty_nine {boundary selected : Finset V}
    (upper : V → V → ℕ) (hOrder : Fintype.card V = 40) (hBook : #boundary = 11)
    (hDegree : ∀ vertex ∈ selected, G.degree vertex = 9)
    (hUpper : ∀ first ∈ selected, ∀ second ∈ selected, first ≠ second →
      #(G.neighborFinset first ∩ G.neighborFinset second) ≤ upper first second) :
    2 * (∑ vertex ∈ selected, (9 - windowDegree G boundary vertex)) ≤
      58 + ∑ pair ∈ selected.offDiag,
        (upper pair.1 pair.2 - #((G.neighborFinset pair.1 ∩ G.neighborFinset pair.2) ∩ boundary)) := by
  have hSub : exteriorFootprint G boundary selected ⊆ univ \ boundary := by
    intro vertex hIn
    obtain ⟨site, _, hSite⟩ := mem_biUnion.mp hIn
    exact mem_sdiff.mpr ⟨mem_univ _, (mem_sdiff.mp hSite).2⟩
  have hCap := card_le_card hSub
  rw [card_sdiff_of_subset (subset_univ _), card_univ, hOrder, hBook] at hCap
  exact (exteriorFootprint_two_term upper hDegree hUpper).trans (by omega)

/-- A second disjoint eleven-site book leaves only 18 sites off both books. The required
contacts into the second book count distinct physical sites, not incidences. -/
theorem book_footprint_forces_opposite_contacts {boundary opposite selected : Finset V}
    (upper : V → V → ℕ) (hOrder : Fintype.card V = 40)
    (hBook : #boundary = 11) (hOpposite : #opposite = 11) (hDisjoint : Disjoint boundary opposite)
    (hDegree : ∀ vertex ∈ selected, G.degree vertex = 9)
    (hUpper : ∀ first ∈ selected, ∀ second ∈ selected, first ≠ second →
      #(G.neighborFinset first ∩ G.neighborFinset second) ≤ upper first second) :
    2 * (∑ vertex ∈ selected, (9 - windowDegree G boundary vertex)) ≤
      36 + 2 * #(exteriorFootprint G boundary selected ∩ opposite) + ∑ pair ∈ selected.offDiag,
        (upper pair.1 pair.2 - #((G.neighborFinset pair.1 ∩ G.neighborFinset pair.2) ∩ boundary)) := by
  have hSub : exteriorFootprint G boundary selected \ opposite ⊆ univ \ (boundary ∪ opposite) := by
    intro vertex hIn
    obtain ⟨site, _, hSite⟩ := mem_biUnion.mp (mem_sdiff.mp hIn).1
    exact mem_sdiff.mpr ⟨mem_univ _, not_or.mpr
      ⟨(mem_sdiff.mp hSite).2, (mem_sdiff.mp hIn).2⟩ ∘ mem_union.mp⟩
  have hCap := card_le_card hSub
  rw [card_sdiff_of_subset (subset_univ _), card_univ, card_union_of_disjoint hDisjoint,
    hOrder, hBook, hOpposite] at hCap
  have hSplit := card_sdiff_add_card_inter (exteriorFootprint G boundary selected) opposite
  exact (exteriorFootprint_two_term upper hDegree hUpper).trans (by omega)

end R310
