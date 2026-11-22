import R310.Basic
import R310.PrivateMatching

namespace R310

open Finset SimpleGraph

variable {Vertex : Type*} [Fintype Vertex] [DecidableEq Vertex]

/-- Actual contacts of a physical vertex with the open neighbourhood of a root. -/
def rootContact (Graph : SimpleGraph Vertex) [DecidableRel Graph.Adj]
    (root site : Vertex) : Finset Vertex :=
  (Graph.neighborFinset root).filter (Graph.Adj site)

omit [DecidableEq Vertex] in
theorem mem_rootContact (Graph : SimpleGraph Vertex) [DecidableRel Graph.Adj]
    {root site anchor : Vertex} :
    anchor ∈ rootContact Graph root site ↔ Graph.Adj root anchor ∧ Graph.Adj site anchor := by
  simp [rootContact]

/-- The unused neighbours of the root pad any independent set supported on two
anchors, provided its sites are outside the root's open neighbourhood. -/
theorem root_two_anchor_padding (Graph : SimpleGraph Vertex) [DecidableRel Graph.Adj]
    {root firstAnchor secondAnchor : Vertex} {sites : Finset Vertex}
    (hTriangle : Graph.CliqueFree 3)
    (hExterior : ∀ site ∈ sites, ¬ Graph.Adj root site)
    (hSupport : ∀ site ∈ sites, rootContact Graph root site ⊆ {firstAnchor, secondAnchor})
    (hIndep : Graph.IsIndepSet (sites : Set Vertex)) :
    #sites + #(Graph.neighborFinset root \ {firstAnchor, secondAnchor}) ≤ Graph.indepNum := by
  let unused := Graph.neighborFinset root \ {firstAnchor, secondAnchor}
  have hDisjoint : Disjoint sites unused := by
    rw [Finset.disjoint_left]
    intro site hSite hUnused
    exact hExterior site hSite ((mem_neighborFinset Graph root site).mp (mem_sdiff.mp hUnused).1)
  have hUnusedIndep : Graph.IsIndepSet (unused : Set Vertex) :=
    (isIndepSet_neighborFinset (G := Graph) hTriangle root).mono
      (fun _ hUnused => (mem_sdiff.mp hUnused).1)
  have hAvoid : ∀ site ∈ sites, ∀ anchor ∈ unused, ¬ Graph.Adj site anchor := by
    intro site hSite anchor hAnchor hAdj
    obtain ⟨hNeighbor, hOutside⟩ := mem_sdiff.mp hAnchor
    exact hOutside (hSupport site hSite ((mem_rootContact Graph).mpr
      ⟨(mem_neighborFinset Graph root anchor).mp hNeighbor, hAdj⟩))
  have hUnion : Graph.IsIndepSet ((sites ∪ unused : Finset Vertex) : Set Vertex) := by
    rw [coe_union, isIndepSet_iff, Set.pairwise_union]
    exact ⟨hIndep, hUnusedIndep, fun site hSite anchor hAnchor _ =>
      ⟨hAvoid site hSite anchor hAnchor, fun hAdj => hAvoid site hSite anchor hAnchor hAdj.symm⟩⟩
  simpa only [card_union_of_disjoint hDisjoint] using hUnion.card_le_indepNum

/-- Membership in the two exact singleton contact classes and in the exact
double contact class supplies the cell geometry and the cap for H-035. -/
theorem private_grid_row_bound_of_root_contacts (Graph : SimpleGraph Vertex)
    [DecidableRel Graph.Adj]
    {root rowAnchor peer crossRow crossColumn : Vertex}
    {gridSites cell right isolated : Finset Vertex} {rowOf columnOf : Vertex → Vertex}
    (hTriangle : Graph.CliqueFree 3) (hAlpha : Graph.indepNum ≤ 9)
    (hRootDegree : Graph.degree root = 6)
    (hRowAnchor : Graph.Adj root rowAnchor) (hPeer : Graph.Adj root peer)
    (hDistinct : rowAnchor ≠ peer)
    (hExterior : ∀ site ∈ cell ∪ right ∪ isolated, ¬ Graph.Adj root site)
    (hCell : ∀ site ∈ cell, rootContact Graph root site = {rowAnchor})
    (hRight : ∀ site ∈ right, rootContact Graph root site = {peer})
    (hDouble : ∀ site ∈ isolated, rootContact Graph root site = {rowAnchor, peer})
    (hCellCard : #cell = 4) (hRightCard : #right = 4)
    (hDoubleCard : #isolated = if rowAnchor = crossRow then 1 else 0)
    (hSingles : (gridSites.filter fun site => rowOf site = rowAnchor) ⊆ cell)
    (hNoncross : crossColumn ∉ right)
    (hOppositeContact : ∀ site ∈ gridSites, rowOf site = rowAnchor →
      rootContact Graph peer site = {columnOf site}) :
    #(gridSites.filter fun site => rowOf site = rowAnchor) -
        #(((gridSites.filter fun site => rowOf site = rowAnchor).image columnOf).erase crossColumn) ≤
      1 - (if rowAnchor = crossRow then 1 else 0) := by
  have hCellMem : ∀ site ∈ cell, rowAnchor ∈ rootContact Graph root site := by
    intro site hSite
    simp [hCell site hSite]
  have hRightMem : ∀ site ∈ right, peer ∈ rootContact Graph root site := by
    intro site hSite
    simp [hRight site hSite]
  have hDoubleRow : ∀ site ∈ isolated, rowAnchor ∈ rootContact Graph root site := by
    intro site hSite
    simp [hDouble site hSite]
  have hDoublePeer : ∀ site ∈ isolated, peer ∈ rootContact Graph root site := by
    intro site hSite
    simp [hDouble site hSite]
  have hDisjoint : Disjoint cell right := by
    rw [Finset.disjoint_left]
    intro site hSite hOther
    simpa [hRight site hOther, hDistinct] using hCellMem site hSite
  have hDoubleDisjoint : Disjoint (cell ∪ right) isolated := by
    rw [Finset.disjoint_left]
    intro site hSite hIso
    rcases mem_union.mp hSite with hLeft | hRightSite
    · simpa [hCell site hLeft, Ne.symm hDistinct] using hDoublePeer site hIso
    · simpa [hRight site hRightSite, hDistinct] using hDoubleRow site hIso
  have independent_of_contact (shore : Finset Vertex) (anchor : Vertex)
      (hContact : ∀ site ∈ shore, anchor ∈ rootContact Graph root site) :
      Graph.IsIndepSet (shore : Set Vertex) :=
    (isIndepSet_neighborFinset (G := Graph) hTriangle anchor).mono (fun site hSite =>
      (mem_neighborFinset Graph anchor site).mpr
        ((mem_rootContact Graph).mp (hContact site hSite)).2.symm)
  have hRowIndep := independent_of_contact (cell ∪ isolated) rowAnchor (fun site hSite =>
    (mem_union.mp hSite).elim (hCellMem site) (hDoubleRow site))
  have hPeerIndep := independent_of_contact (right ∪ isolated) peer (fun site hSite =>
    (mem_union.mp hSite).elim (hRightMem site) (hDoublePeer site))
  have hIsolation : ∀ site ∈ isolated, ∀ other ∈ cell ∪ right ∪ isolated,
      ¬ Graph.Adj site other := by
    intro site hSite other hOther hAdj
    rcases mem_union.mp hOther with hShore | hIso
    · rcases mem_union.mp hShore with hLeft | hRightSite
      · exact (Graph.isIndepSet_iff.mp hRowIndep) (mem_union_right _ hSite)
          (mem_union_left _ hLeft) hAdj.ne hAdj
      · exact (Graph.isIndepSet_iff.mp hPeerIndep) (mem_union_right _ hSite)
          (mem_union_left _ hRightSite) hAdj.ne hAdj
    · exact (Graph.isIndepSet_iff.mp hRowIndep) (mem_union_right _ hSite)
        (mem_union_right _ hIso) hAdj.ne hAdj
  have hPair : ({rowAnchor, peer} : Finset Vertex) ⊆ Graph.neighborFinset root := by
    intro anchor hAnchor
    rcases mem_insert.mp hAnchor with hFirst | hSecond
    · rw [hFirst]
      exact (mem_neighborFinset Graph root rowAnchor).mpr hRowAnchor
    · rw [mem_singleton.mp hSecond]
      exact (mem_neighborFinset Graph root peer).mpr hPeer
  have hUnusedCard : #(Graph.neighborFinset root \ {rowAnchor, peer}) = 4 := by
    rw [card_sdiff_of_subset hPair, card_neighborFinset_eq_degree, hRootDegree]
    simp [hDistinct]
  have hCap : ∀ sites ⊆ cell ∪ right ∪ isolated,
      Graph.IsIndepSet (sites : Set Vertex) → #sites ≤ 5 := by
    intro sites hSubset hIndependent
    have hSupport : ∀ site ∈ sites, rootContact Graph root site ⊆ {rowAnchor, peer} := by
      intro site hSite
      rcases mem_union.mp (hSubset hSite) with hShore | hIso
      · rcases mem_union.mp hShore with hLeft | hRightSite
        · simp [hCell site hLeft]
        · simp [hRight site hRightSite]
      · simp [hDouble site hIso]
    have hPadded := root_two_anchor_padding Graph hTriangle
      (fun site hSite => hExterior site (hSubset hSite)) hSupport hIndependent
    omega
  apply private_grid_row_bound_of_indep Graph hSingles hDisjoint hDoubleDisjoint
    (hRowIndep.mono (fun _ hSite => mem_union_left _ hSite))
    (hPeerIndep.mono (fun _ hSite => mem_union_left _ hSite)) hIsolation hCap
    hCellCard hRightCard hDoubleCard hNoncross
  intro site hGrid hRow anchor hAnchor hAdj
  have hPeerAdj := ((mem_rootContact Graph).mp (hRightMem anchor hAnchor)).2.symm
  have hContact := (mem_rootContact Graph).mpr ⟨hPeerAdj, hAdj⟩
  rwa [hOppositeContact site hGrid hRow, mem_singleton] at hContact

end R310
