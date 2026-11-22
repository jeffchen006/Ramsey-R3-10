import R310.MinDegree

namespace R310

open Finset SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

theorem card_add_card_le_indepNum_of_common_neighbor (hTriangle : G.CliqueFree 3)
    {cell anchors : Finset V} {common : V} (hDisjoint : Disjoint cell anchors)
    (hCommon : ∀ vertex ∈ cell, G.Adj common vertex)
    (hAnchors : G.IsIndepSet (anchors : Set V))
    (hAvoid : ∀ vertex ∈ cell, ∀ anchor ∈ anchors, ¬ G.Adj vertex anchor) :
    #cell + #anchors ≤ G.indepNum := by
  have hIndep : G.IsIndepSet ((cell ∪ anchors : Finset V) : Set V) := by
    rw [coe_union, isIndepSet_iff, Set.pairwise_union]
    refine ⟨?_, hAnchors, ?_⟩
    · intro first hFirst second hSecond hNe
      exact isIndepSet_neighborFinset hTriangle common
        ((mem_neighborFinset _ _ _).mpr (hCommon first hFirst))
        ((mem_neighborFinset _ _ _).mpr (hCommon second hSecond)) hNe
    · intro vertex hVertex anchor hAnchor _
      exact ⟨hAvoid vertex hVertex anchor hAnchor,
        fun hAdj => hAvoid vertex hVertex anchor hAnchor hAdj.symm⟩
  simpa only [card_union_of_disjoint hDisjoint] using hIndep.card_le_indepNum

/-- With three independent anchors, the exterior nonneighbors of the first are
bounded by two disjoint independent-set counts. Triple supports are harmless. -/
theorem three_anchor_nonneighbor_bound (hTriangle : G.CliqueFree 3)
    {exterior : Finset V} {cross side other : V} (hCrossSide : ¬ G.Adj cross side)
    (hCrossSideNe : cross ≠ side) (hCrossOut : cross ∉ exterior) (hSideOut : side ∉ exterior)
    (hCover : ∀ vertex ∈ exterior, G.Adj cross vertex ∨ G.Adj side vertex ∨ G.Adj other vertex) :
    #{vertex ∈ exterior | ¬ G.Adj cross vertex} + 3 ≤ 2 * G.indepNum := by
  let off := exterior.filter (fun vertex => ¬ G.Adj cross vertex)
  let withSide := off.filter (G.Adj side)
  let withoutSide := off.filter (fun vertex => ¬ G.Adj side vertex)
  have hSplit : #withSide + #withoutSide = #off := card_filter_add_card_filter_not (G.Adj side)
  have hOff : ∀ vertex ∈ off, vertex ∈ exterior ∧ ¬ G.Adj cross vertex :=
    fun _ hVertex => mem_filter.mp hVertex
  have hWith : #withSide + 1 ≤ G.indepNum := by
    simpa only [card_singleton] using card_add_card_le_indepNum_of_common_neighbor hTriangle
      (cell := withSide) (anchors := {cross}) (common := side)
      (by
        rw [Finset.disjoint_left]
        intro vertex hVertex hCross
        rcases mem_singleton.mp hCross with rfl
        exact hCrossOut (hOff _ (mem_filter.mp hVertex).1).1)
      (fun _ hVertex => (mem_filter.mp hVertex).2)
      (by simp)
      (by
        intro vertex hVertex anchor hAnchor hAdj
        rcases mem_singleton.mp hAnchor with rfl
        exact (hOff _ (mem_filter.mp hVertex).1).2 hAdj.symm)
  have hWithout : #withoutSide + 2 ≤ G.indepNum := by
    have hPair : G.IsIndepSet (({cross, side} : Finset V) : Set V) := by
      rw [coe_insert, coe_singleton, isIndepSet_iff, Set.pairwise_insert]
      refine ⟨by simp, ?_⟩
      intro vertex hVertex _
      rcases Set.mem_singleton_iff.mp hVertex with rfl
      exact ⟨hCrossSide, fun hAdj => hCrossSide hAdj.symm⟩
    simpa only [card_pair hCrossSideNe] using
      card_add_card_le_indepNum_of_common_neighbor hTriangle
        (cell := withoutSide) (anchors := {cross, side}) (common := other)
        (by
          rw [Finset.disjoint_left]
          intro vertex hVertex hAnchor
          have hExt := (hOff _ (mem_filter.mp hVertex).1).1
          simp only [mem_insert, mem_singleton] at hAnchor
          rcases hAnchor with rfl | rfl
          · exact hCrossOut hExt
          · exact hSideOut hExt)
        (fun vertex hVertex => ((hCover _ (hOff _ (mem_filter.mp hVertex).1).1).resolve_left
          (hOff _ (mem_filter.mp hVertex).1).2).resolve_left (mem_filter.mp hVertex).2)
        hPair
        (by
          intro vertex hVertex anchor hAnchor hAdj
          simp only [mem_insert, mem_singleton] at hAnchor
          rcases hAnchor with rfl | rfl
          · exact (hOff _ (mem_filter.mp hVertex).1).2 hAdj.symm
          · exact (mem_filter.mp hVertex).2 hAdj.symm)
  change #off + 3 ≤ 2 * G.indepNum
  omega

/-- An extra cross-neighbor outside the exterior lowers the available exterior
capacity. No order assumption or source enumeration is used. -/
theorem three_anchor_exterior_bound (hTriangle : G.CliqueFree 3)
    {exterior : Finset V} {cross side other endpoint : V} (hCrossSide : ¬ G.Adj cross side)
    (hCrossSideNe : cross ≠ side) (hCrossOut : cross ∉ exterior) (hSideOut : side ∉ exterior)
    (hCover : ∀ vertex ∈ exterior, G.Adj cross vertex ∨ G.Adj side vertex ∨ G.Adj other vertex)
    (hEndpoint : G.Adj cross endpoint) (hEndpointOut : endpoint ∉ exterior) :
    #exterior + 4 ≤ 3 * G.indepNum := by
  let on := exterior.filter (G.Adj cross)
  have hIns : insert endpoint on ⊆ G.neighborFinset cross := by
    intro vertex hVertex
    rcases mem_insert.mp hVertex with rfl | hOn
    · exact (mem_neighborFinset _ _ _).mpr hEndpoint
    · exact (mem_neighborFinset _ _ _).mpr (mem_filter.mp hOn).2
  have hNot : endpoint ∉ on := fun hVertex => hEndpointOut (mem_filter.mp hVertex).1
  have hDegree := card_le_card hIns
  rw [card_insert_of_notMem hNot, card_neighborFinset_eq_degree] at hDegree
  have hα := degree_le_indepNum hTriangle cross
  have hOff := three_anchor_nonneighbor_bound hTriangle hCrossSide hCrossSideNe hCrossOut hSideOut hCover
  have hSplit := card_filter_add_card_filter_not (s := exterior) (p := G.Adj cross)
  change #on + #{vertex ∈ exterior | ¬ G.Adj cross vertex} = #exterior at hSplit
  omega

/-- The order-22 residual with 15 attached exterior vertices is impossible at
independence number at most six. -/
theorem three_anchor_exterior_card_le_fourteen (hTriangle : G.CliqueFree 3)
    (hAlpha : G.indepNum ≤ 6) {exterior : Finset V} {cross side other endpoint : V}
    (hCrossSide : ¬ G.Adj cross side) (hCrossSideNe : cross ≠ side)
    (hCrossOut : cross ∉ exterior) (hSideOut : side ∉ exterior)
    (hCover : ∀ vertex ∈ exterior, G.Adj cross vertex ∨ G.Adj side vertex ∨ G.Adj other vertex)
    (hEndpoint : G.Adj cross endpoint) (hEndpointOut : endpoint ∉ exterior) : #exterior ≤ 14 := by
  have := three_anchor_exterior_bound hTriangle hCrossSide hCrossSideNe hCrossOut hSideOut
    hCover hEndpoint hEndpointOut
  omega

/-- Delete the closed neighborhood of a noncross anchor of a paired window.
The eight marked vertices and the listed adjacency/coverage facts are premises;
no enumeration or Ramsey table is needed for the resulting degree bound. -/
theorem noncross_anchor_order_le_degree_add_twenty_two (hTriangle : G.CliqueFree 3)
    (hAlpha : G.indepNum ≤ 7) {anchors : Finset V} {root cross side other endpoint : V}
    (hAnchorCount : #anchors = 8) (hRoot : root ∈ anchors)
    (hCross : cross ∈ anchors.erase root) (hSide : side ∈ anchors.erase root)
    (hOther : other ∈ anchors.erase root) (hEndpoint : endpoint ∈ anchors.erase root)
    (hNoncross : ∀ vertex ∈ anchors, ¬ G.Adj root vertex)
    (hCrossSide : ¬ G.Adj cross side) (hCrossSideNe : cross ≠ side)
    (hCrossEndpoint : G.Adj cross endpoint)
    (hCover : ∀ vertex ∉ anchors,
      G.Adj root vertex ∨ G.Adj cross vertex ∨ G.Adj side vertex ∨ G.Adj other vertex) :
    Fintype.card V ≤ G.degree root + 22 := by
  classical
  have hSurvive : anchors.erase root ⊆ outside G root := by
    intro vertex hVertex
    exact mem_outside.mpr ⟨(mem_erase.mp hVertex).1, hNoncross vertex (mem_erase.mp hVertex).2⟩
  let residual (vertex : V) (hVertex : vertex ∈ anchors.erase root) : (outside G root : Set V) :=
    ⟨vertex, hSurvive hVertex⟩
  let base := outside G root \ anchors
  let exterior : Finset (outside G root : Set V) := base.subtype (· ∈ (outside G root : Set V))
  have hInExterior (vertex : (outside G root : Set V)) (hVertex : vertex ∈ exterior) :
      (vertex : V) ∉ anchors := (mem_sdiff.mp (mem_subtype.mp hVertex)).2
  have hAnchorOut (vertex : V) (hVertex : vertex ∈ anchors.erase root) :
      residual vertex hVertex ∉ exterior := fun hIn =>
    hInExterior _ hIn ((mem_erase.mp hVertex).2)
  have hResidualAlpha := indepNum_delNbhd_le (G := G) (k := 8) (by simpa using hAlpha) root
  have hBound := three_anchor_exterior_card_le_fourteen (cliqueFree_delNbhd hTriangle root)
    hResidualAlpha (exterior := exterior) (cross := residual cross hCross)
    (side := residual side hSide) (other := residual other hOther)
    (endpoint := residual endpoint hEndpoint) hCrossSide
    (fun hEq => hCrossSideNe (congrArg Subtype.val hEq)) (hAnchorOut cross hCross) (hAnchorOut side hSide)
    (fun vertex hVertex => (hCover vertex (hInExterior vertex hVertex)).resolve_left
      (mem_outside.mp vertex.property).2) hCrossEndpoint (hAnchorOut endpoint hEndpoint)
  have hExteriorCount : #exterior = #base := by
    rw [card_subtype, filter_eq_self.mpr]
    intro vertex hVertex
    exact (mem_sdiff.mp hVertex).1
  have hBaseEq : base = outside G root \ anchors.erase root := by
    ext vertex
    simp only [base, mem_sdiff, mem_erase]
    constructor
    · rintro ⟨hOutside, hNotAnchor⟩
      exact ⟨hOutside, fun hIn => hNotAnchor hIn.2⟩
    · rintro ⟨hOutside, hNotAnchor⟩
      exact ⟨hOutside, fun hIn => hNotAnchor ⟨(mem_outside.mp hOutside).1, hIn⟩⟩
  have hBaseCount := card_sdiff_of_subset hSurvive
  rw [← hBaseEq, ← hExteriorCount, card_erase_of_mem hRoot, hAnchorCount] at hBaseCount
  have hSubsetCount := card_le_card hSurvive
  rw [card_erase_of_mem hRoot, hAnchorCount] at hSubsetCount
  have hOrder := card_outside_add (G := G) root
  omega

end R310
