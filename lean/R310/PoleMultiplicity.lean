import R310.MiddleStar

namespace R310

open Finset SimpleGraph

variable {Vertex : Type*} [Fintype Vertex] [DecidableEq Vertex]
variable (graph : SimpleGraph Vertex) [DecidableRel graph.Adj]

/-- Other common neighbours of two poles, retaining each physical site as a distinct vertex. -/
def polePairSites (first second middle : Vertex) : Finset Vertex :=
  (graph.neighborFinset first ∩ graph.neighborFinset second).erase middle

theorem mem_polePairSites {first second middle site : Vertex} :
    site ∈ polePairSites graph first second middle ↔
      site ≠ middle ∧ graph.Adj first site ∧ graph.Adj second site := by
  simp [polePairSites]

theorem polePairSites_subset_exterior {left right middle first second : Vertex}
    (hTriangle : graph.CliqueFree 3) (hMark : HasDeficientWitness graph left right middle)
    (hFirst : first ∈ pathStar graph left right middle) :
    polePairSites graph first second middle ⊆
      (pathWing graph left middle ∪ pathWing graph right middle) ∪ pathUntouched graph left right middle := by
  have hMidFirst : graph.Adj middle first := (mem_neighborFinset _ _ _).mp
    (mem_of_mem_erase (mem_of_mem_erase hFirst))
  intro site hSite
  obtain ⟨hNe, hAdj, _⟩ := (mem_polePairSites graph).mp hSite
  have hNoMiddle : ¬ graph.Adj middle site := fun hEdge =>
    hTriangle {middle, first, site} (is3Clique_triple_iff.2 ⟨hMidFirst, hEdge, hAdj⟩)
  have hNoLeft : site ≠ left := fun hEq => hNoMiddle (hEq.symm ▸ hMark.2.2.1.symm)
  have hNoRight : site ≠ right := fun hEq => hNoMiddle (hEq.symm ▸ hMark.2.2.2.1.symm)
  by_cases hLeft : graph.Adj left site
  · exact mem_union_left _ (mem_union_left _ (by simp [pathWing, hNe, hLeft]))
  by_cases hRight : graph.Adj right site
  · exact mem_union_left _ (mem_union_right _ (by simp [pathWing, hNe, hRight]))
  exact mem_union_right _ ((mem_pathUntouched graph).mpr
    ⟨hNoLeft, hNoRight, hNe, hLeft, hRight, hNoMiddle⟩)

theorem polePairSites_card_add_one {middle first second : Vertex}
    (hFirst : graph.Adj first middle) (hSecond : graph.Adj second middle) :
    #(polePairSites graph first second middle) + 1 =
      #(graph.neighborFinset first ∩ graph.neighborFinset second) :=
  card_erase_add_one (by simp [hFirst, hSecond])

/-- The lower bound is exactly the failure of the middle to uniquely witness this pair. -/
theorem polePairSites_pos_iff {middle first second : Vertex}
    (hDistinct : first ≠ second) (hNonedge : ¬ graph.Adj first second)
    (hFirst : graph.Adj first middle) (hSecond : graph.Adj second middle) :
    1 ≤ #(polePairSites graph first second middle) ↔ ¬ HasDeficientWitness graph first second middle := by
  change 0 < #(polePairSites graph first second middle) ↔ _
  rw [card_pos]
  constructor
  · rintro ⟨site, hSite⟩ hDef
    obtain ⟨hNe, hAdjFirst, hAdjSecond⟩ := (mem_polePairSites graph).mp hSite
    exact hNe (hDef.2.2.2.2 site hAdjFirst hAdjSecond)
  · intro hNoDef
    by_contra hEmpty
    apply hNoDef
    refine ⟨hDistinct, hNonedge, hFirst, hSecond, fun site hAdjFirst hAdjSecond => ?_⟩
    by_contra hNe
    exact hEmpty ⟨site, (mem_polePairSites graph).mpr ⟨hNe, hAdjFirst, hAdjSecond⟩⟩

private theorem polePairSites_card_partition {left right middle first second : Vertex}
    (hTriangle : graph.CliqueFree 3) (hMark : HasDeficientWitness graph left right middle)
    (hFirst : first ∈ pathStar graph left right middle) :
    #(polePairSites graph first second middle) =
      #(polePairSites graph first second middle ∩ pathWing graph left middle) +
      #(polePairSites graph first second middle ∩ pathWing graph right middle) +
      #(polePairSites graph first second middle ∩ pathUntouched graph left right middle) := by
  have hWings : Disjoint (pathWing graph left middle) (pathWing graph right middle) := by
    refine disjoint_left.2 fun site hLeft hRight => ?_
    simp only [pathWing, mem_erase, mem_neighborFinset] at hLeft hRight
    exact hLeft.1 (hMark.2.2.2.2 site hLeft.2 hRight.2)
  have hAway : Disjoint (pathWing graph left middle ∪ pathWing graph right middle)
      (pathUntouched graph left right middle) := by
    refine disjoint_left.2 fun site hWing hUntouched => ?_
    obtain ⟨_, _, _, hAvoidLeft, hAvoidRight, _⟩ := (mem_pathUntouched graph).mp hUntouched
    simp only [mem_union, pathWing, mem_erase, mem_neighborFinset] at hWing
    exact hWing.elim (fun hLeft => hAvoidLeft hLeft.2) (fun hRight => hAvoidRight hRight.2)
  let sites := polePairSites graph first second middle
  change #sites = #(sites ∩ _) + #(sites ∩ _) + #(sites ∩ _)
  have hCover : sites ⊆ (pathWing graph left middle ∪ pathWing graph right middle) ∪
      pathUntouched graph left right middle := polePairSites_subset_exterior graph hTriangle hMark hFirst
  conv_lhs => rw [← inter_eq_left.mpr hCover]
  rw [inter_union_distrib_left, card_union_of_disjoint
    (hAway.mono inter_subset_right inter_subset_right), inter_union_distrib_left,
    card_union_of_disjoint (hWings.mono inter_subset_right inter_subset_right)]

/-- The pole-pair support row. The upper bound does not use the no-other-witness
premise; it is recorded separately from the conditional lower bound. -/
theorem polePair_multiplicity {left right middle first second : Vertex}
    (hTriangle : graph.CliqueFree 3) (hMark : HasDeficientWitness graph left right middle)
    (hCap : ∀ first second : Vertex, first ≠ second → ¬ graph.Adj first second →
      #(graph.neighborFinset first ∩ graph.neighborFinset second) ≤ 3)
    (hFirst : first ∈ pathStar graph left right middle)
    (hSecond : second ∈ pathStar graph left right middle) (hDistinct : first ≠ second) :
    let total := #(polePairSites graph first second middle ∩ pathWing graph left middle) +
      #(polePairSites graph first second middle ∩ pathWing graph right middle) +
      #(polePairSites graph first second middle ∩ pathUntouched graph left right middle)
    total ≤ 2 ∧ (1 ≤ total ↔ ¬ HasDeficientWitness graph first second middle) := by
  have hFirstMid : graph.Adj first middle := ((mem_neighborFinset _ _ _).mp
    (mem_of_mem_erase (mem_of_mem_erase hFirst))).symm
  have hSecondMid : graph.Adj second middle := ((mem_neighborFinset _ _ _).mp
    (mem_of_mem_erase (mem_of_mem_erase hSecond))).symm
  have hNonedge : ¬ graph.Adj first second := fun hAdj =>
    hTriangle {first, second, middle} (is3Clique_triple_iff.2 ⟨hAdj, hFirstMid, hSecondMid⟩)
  dsimp only
  rw [← polePairSites_card_partition graph hTriangle hMark hFirst]
  refine ⟨?_, polePairSites_pos_iff graph hDistinct hNonedge hFirstMid hSecondMid⟩
  have hBound := hCap first second hDistinct hNonedge
  have hCount := polePairSites_card_add_one graph hFirstMid hSecondMid
  omega

end R310
