import R310.MTF

namespace R310

open Finset SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]
  {G : SimpleGraph V} [DecidableRel G.Adj] {root : V}

/-- Each neighbor of the root has an independent attachment which dominates the exterior. -/
theorem IsMTF.attachment_dominates (hmtf : IsMTF G) {anchor vertex : V}
    (hAnchor : G.Adj root anchor) (hVertex : vertex ∈ outside G root) :
    G.Adj anchor vertex ∨ ∃ witness ∈ outside G root,
      G.Adj anchor witness ∧ G.Adj vertex witness := by
  by_cases hAdj : G.Adj anchor vertex
  · exact Or.inl hAdj
  have hNe : anchor ≠ vertex := by
    rintro rfl
    exact (mem_outside.mp hVertex).2 hAnchor
  obtain ⟨witness, hwAnchor, hwVertex⟩ := hmtf.exists_common hNe hAdj
  refine Or.inr ⟨witness, mem_outside.mpr ⟨?_, ?_⟩, hwAnchor, hwVertex⟩
  · rintro rfl
    exact (mem_outside.mp hVertex).2 hwVertex.symm
  · intro hwRoot
    exact (isIndepSet_neighborFinset hmtf.1 root
      ((mem_neighborFinset _ _ _).2 hAnchor) ((mem_neighborFinset _ _ _).2 hwRoot) hwAnchor.ne) hwAnchor

/-- Singletons and pairs not joined in the exterior by an edge or a length-two path. -/
inductive RootDemand (G : SimpleGraph V) [DecidableRel G.Adj] (root : V) : Finset V → Prop
  | single {vertex : V} (hVertex : vertex ∈ outside G root) : RootDemand G root {vertex}
  | pair {first second : V} (hFirst : first ∈ outside G root) (hSecond : second ∈ outside G root)
      (hNe : first ≠ second) (hAdj : ¬ G.Adj first second)
      (hNoCommon : ∀ witness ∈ outside G root, ¬ (G.Adj first witness ∧ G.Adj second witness)) :
      RootDemand G root {first, second}

/-- Maximality places every demand in an attachment of a root neighbor. -/
theorem IsMTF.exists_attachment_for_demand (hmtf : IsMTF G) {demand : Finset V}
    (hDemand : RootDemand G root demand) :
    ∃ anchor ∈ G.neighborFinset root, ∀ vertex ∈ demand, G.Adj anchor vertex := by
  cases hDemand with
  | @single vertex hVertex =>
    obtain ⟨anchor, haRoot, haVertex⟩ :=
      hmtf.exists_common (mem_outside.mp hVertex).1.symm (mem_outside.mp hVertex).2
    exact ⟨anchor, (mem_neighborFinset _ _ _).2 haRoot, by simpa using haVertex.symm⟩
  | @pair first second hFirst _hSecond hNe hAdj hNoCommon =>
    obtain ⟨anchor, haFirst, haSecond⟩ := hmtf.exists_common hNe hAdj
    have haNe : anchor ≠ root := by
      rintro rfl
      exact (mem_outside.mp hFirst).2 haFirst.symm
    have haRoot : G.Adj root anchor := by
      by_contra haNot
      exact hNoCommon anchor (mem_outside.mpr ⟨haNe, haNot⟩) ⟨haFirst, haSecond⟩
    refine ⟨anchor, (mem_neighborFinset _ _ _).2 haRoot, ?_⟩
    simp only [mem_insert, mem_singleton]
    rintro vertex (rfl | rfl)
    · exact haFirst.symm
    · exact haSecond.symm

/-- An edge crossing each pair of distinct demands forces distinct attachments. -/
theorem IsMTF.card_incompatible_demands_le_degree (hmtf : IsMTF G) {count : ℕ}
    (demand : Fin count → Finset V) (hDemand : ∀ index, RootDemand G root (demand index))
    (hCross : ∀ ⦃first second⦄, first ≠ second →
      ∃ vertex ∈ demand first, ∃ other ∈ demand second, G.Adj vertex other) :
    count ≤ G.degree root := by
  classical
  choose anchor hAnchor hAttach using fun index => hmtf.exists_attachment_for_demand (hDemand index)
  let assign : Fin count → ↥(G.neighborFinset root) := fun index => ⟨anchor index, hAnchor index⟩
  have hInjective : Function.Injective assign := by
    intro first second hEqual
    by_contra hNe
    obtain ⟨vertex, hVertex, other, hOther, hEdge⟩ := hCross hNe
    have hSame : anchor first = anchor second := congrArg Subtype.val hEqual
    have hAdj : G.Adj (anchor first) other := hSame ▸ hAttach second other hOther
    exact (isIndepSet_neighborFinset hmtf.1 (anchor first)
      ((mem_neighborFinset _ _ _).2 (hAttach first vertex hVertex)) ((mem_neighborFinset _ _ _).2 hAdj)
      hEdge.ne) hEdge
  calc
    count ≤ Fintype.card ↥(G.neighborFinset root) := by
      simpa only [Fintype.card_fin] using Fintype.card_le_of_injective assign hInjective
    _ = G.degree root := by rw [Fintype.card_coe, card_neighborFinset_eq_degree]

/-- The arithmetic bridge from a degree-six residual floor to the total edge floor.
The residual bound is a premise; the MTF private-neighbor bound is already kernel-checked. -/
theorem IsMTF.total_edges_of_degree_six_residue {G : SimpleGraph (Fin 40)} [DecidableRel G.Adj]
    (hmtf : IsMTF G) (hAlpha : G.indepNum ≤ 9) {root : Fin 40}
    (hDegree : G.degree root = 6) {floor : ℕ} (hFloor : floor ≤ #(delNbhd G root).edgeFinset) :
    floor + 48 ≤ #G.edgeFinset := by
  have hPrivate := IsMTF.sum_degree_neighbor_ge G hmtf hAlpha root
  rw [hDegree] at hPrivate
  have hSplit := card_edgeFinset_delNbhd_add_sum_degree (G := G) hmtf.1 root
  omega

end R310
