import Mathlib.Combinatorics.SimpleGraph.Clique

namespace R310

variable {LeftSlot RightSlot GridCopy Vertex : Type*}

/-- The active slots have one mate each. The left positions distinguish physical
sites, not masks; the right positions name those same sites on selected pairs.
Positions outside the active domain carry no information. -/
structure PhysicalSlotMatching (LeftSlot RightSlot Vertex : Type*) where
  selected : LeftSlot → RightSlot → Prop
  leftVertex : LeftSlot → Vertex
  rightVertex : RightSlot → Vertex
  leftUnique : ∀ {left right firstMate}, selected left right → selected left firstMate →
    right = firstMate
  rightUnique : ∀ {left right firstMate}, selected left right → selected firstMate right →
    left = firstMate
  leftInj : Set.InjOn leftVertex {left | ∃ right, selected left right}
  mateVertex : ∀ {left right}, selected left right → leftVertex left = rightVertex right

namespace PhysicalSlotMatching

variable (matching : PhysicalSlotMatching LeftSlot RightSlot Vertex)

/-- Distinct active right slots also denote distinct physical sites. -/
theorem right_inj : Set.InjOn matching.rightVertex {right | ∃ left, matching.selected left right} := by
  intro first hFirst second hSecond hVertex
  obtain ⟨firstLeft, hFirstSelected⟩ := hFirst
  obtain ⟨secondLeft, hSecondSelected⟩ := hSecond
  have hLeft : firstLeft = secondLeft := matching.leftInj ⟨first, hFirstSelected⟩
    ⟨second, hSecondSelected⟩ ((matching.mateVertex hFirstSelected).trans
      (hVertex.trans (matching.mateVertex hSecondSelected).symm))
  subst secondLeft
  exact matching.leftUnique hFirstSelected hSecondSelected

/-- Two different selected pairs give different vertices even if their masks
coincide. A difference in either coordinate suffices. -/
theorem pair_vertices_distinct {first second : LeftSlot × RightSlot}
    (hFirst : matching.selected first.1 first.2) (hSecond : matching.selected second.1 second.2)
    (hDistinct : first ≠ second) : matching.leftVertex first.1 ≠ matching.leftVertex second.1 := by
  intro hVertex
  have hLeft := matching.leftInj ⟨first.2, hFirst⟩ ⟨second.2, hSecond⟩ hVertex
  have hRight : first.2 = second.2 := matching.leftUnique hFirst (hLeft.symm ▸ hSecond)
  exact hDistinct (Prod.ext hLeft hRight)

end PhysicalSlotMatching

/-- The truth value of a folded grid edge in one shore's coordinates. An inactive
slot or overlapping anchor support yields false, regardless of any variable name. -/
def foldedGridEdge (Graph : SimpleGraph Vertex) (active : Prop) (site grid : Vertex)
    (slotSupport gridSupport : Set Vertex) : Prop :=
  active ∧ Disjoint slotSupport gridSupport ∧ Graph.Adj site grid

/-- When the support labels are actual contacts, dropping a shared-support edge
does not change the true graph value. Exact contact sets are not required. -/
theorem foldedGridEdge_iff_adj (Graph : SimpleGraph Vertex) (hTriangle : Graph.CliqueFree 3)
    {active : Prop} {site grid : Vertex} {slotSupport gridSupport : Set Vertex}
    (hActive : active) (hSite : ∀ anchor ∈ slotSupport, Graph.Adj site anchor)
    (hGrid : ∀ anchor ∈ gridSupport, Graph.Adj grid anchor) :
    foldedGridEdge Graph active site grid slotSupport gridSupport ↔ Graph.Adj site grid := by
  constructor
  · exact fun hEdge => hEdge.2.2
  · intro hEdge
    refine ⟨hActive, Set.disjoint_left.mpr ?_, hEdge⟩
    intro anchor hSlotAnchor hGridAnchor
    exact (Graph.isIndepSet_neighborSet_of_triangleFree hTriangle anchor)
      (hSite anchor hSlotAnchor).symm (hGrid anchor hGridAnchor).symm hEdge.ne hEdge

/-- A selected mate equates both descriptions of the edge to each physical grid
copy, even when one side has a constant-false literal. Soundness of each mask is
enough. Without a selected mate no equality is asserted. -/
theorem guarded_folded_grid_edge (Graph : SimpleGraph Vertex) (hTriangle : Graph.CliqueFree 3)
    (matching : PhysicalSlotMatching LeftSlot RightSlot Vertex)
    (gridVertex : GridCopy → Vertex)
    (leftSupport : LeftSlot → Set Vertex) (rightSupport : RightSlot → Set Vertex)
    (gridLeftSupport gridRightSupport : GridCopy → Set Vertex)
    {left : LeftSlot} {right : RightSlot} (copy : GridCopy)
    (hLeft : ∀ anchor ∈ leftSupport left, Graph.Adj (matching.leftVertex left) anchor)
    (hRight : ∀ anchor ∈ rightSupport right, Graph.Adj (matching.rightVertex right) anchor)
    (hGridLeft : ∀ anchor ∈ gridLeftSupport copy, Graph.Adj (gridVertex copy) anchor)
    (hGridRight : ∀ anchor ∈ gridRightSupport copy, Graph.Adj (gridVertex copy) anchor) :
    matching.selected left right →
      (foldedGridEdge Graph (∃ mate, matching.selected left mate) (matching.leftVertex left)
        (gridVertex copy) (leftSupport left) (gridLeftSupport copy) ↔
       foldedGridEdge Graph (∃ mate, matching.selected mate right) (matching.rightVertex right)
        (gridVertex copy) (rightSupport right) (gridRightSupport copy)) := by
  intro hSelected
  rw [foldedGridEdge_iff_adj Graph hTriangle ⟨right, hSelected⟩ hLeft hGridLeft,
    foldedGridEdge_iff_adj Graph hTriangle ⟨left, hSelected⟩ hRight hGridRight,
    matching.mateVertex hSelected]

/-- For an optional/optional edge, both endpoints need selection guards. As
above, shared support on either shore forces the physical edge to be absent. -/
theorem guarded_folded_slot_edge (Graph : SimpleGraph Vertex) (hTriangle : Graph.CliqueFree 3)
    (matching : PhysicalSlotMatching LeftSlot RightSlot Vertex)
    (leftSupport : LeftSlot → Set Vertex) (rightSupport : RightSlot → Set Vertex)
    {first second : LeftSlot × RightSlot}
    (hFirstLeft : ∀ anchor ∈ leftSupport first.1, Graph.Adj (matching.leftVertex first.1) anchor)
    (hSecondLeft : ∀ anchor ∈ leftSupport second.1, Graph.Adj (matching.leftVertex second.1) anchor)
    (hFirstRight : ∀ anchor ∈ rightSupport first.2, Graph.Adj (matching.rightVertex first.2) anchor)
    (hSecondRight : ∀ anchor ∈ rightSupport second.2, Graph.Adj (matching.rightVertex second.2) anchor) :
    matching.selected first.1 first.2 → matching.selected second.1 second.2 →
      (foldedGridEdge Graph
        ((∃ mate, matching.selected first.1 mate) ∧ (∃ mate, matching.selected second.1 mate))
        (matching.leftVertex first.1) (matching.leftVertex second.1)
        (leftSupport first.1) (leftSupport second.1) ↔
       foldedGridEdge Graph
        ((∃ mate, matching.selected mate first.2) ∧ (∃ mate, matching.selected mate second.2))
        (matching.rightVertex first.2) (matching.rightVertex second.2)
        (rightSupport first.2) (rightSupport second.2)) := by
  intro hFirst hSecond
  rw [foldedGridEdge_iff_adj Graph hTriangle ⟨⟨first.2, hFirst⟩, ⟨second.2, hSecond⟩⟩
      hFirstLeft hSecondLeft,
    foldedGridEdge_iff_adj Graph hTriangle ⟨⟨first.1, hFirst⟩, ⟨second.1, hSecond⟩⟩
      hFirstRight hSecondRight,
    matching.mateVertex hFirst, matching.mateVertex hSecond]

end R310
