import Mathlib.Combinatorics.Hall.Finite
import Mathlib.Combinatorics.SimpleGraph.Clique
import Mathlib.Data.Finset.Sum
import R310.PrivateGrid

open Finset SimpleGraph

namespace R310

variable {Vertex : Type*} [DecidableEq Vertex]

/-- A Hall deficiency bound gives a partial matching. Add `#left - lower` fresh dummy
partners, apply ordinary Hall, and keep precisely the assignments to real partners. -/
private theorem matching_of_deficiency (Graph : SimpleGraph Vertex) [DecidableRel Graph.Adj]
    (left right : Finset Vertex) (lower : ℕ) (hLower : lower ≤ #left)
    (hDeficiency : ∀ selected ⊆ left, #selected ≤
      #(right.filter fun target => ∃ site ∈ selected, Graph.Adj site target) + (#left - lower)) :
    ∃ (matched : Finset Vertex) (partner : Vertex → Vertex), matched ⊆ left ∧
      lower ≤ #matched ∧ Set.InjOn partner (matched : Set Vertex) ∧
      ∀ site ∈ matched, partner site ∈ right ∧ Graph.Adj site (partner site) := by
  classical
  let Dummy := Fin (#left - lower)
  let choices (site : ↥(left : Set Vertex)) : Finset (Vertex ⊕ Dummy) :=
    (right.filter fun target => Graph.Adj (site : Vertex) target).disjSum univ
  have hHall : ∀ subset : Finset ↥(left : Set Vertex), #subset ≤ #(subset.biUnion choices) := by
    intro subset
    by_cases hEmpty : subset = ∅
    · simp [hEmpty]
    let selected := subset.image Subtype.val
    have hSelected : selected ⊆ left := by
      intro site hSite
      obtain ⟨member, _, rfl⟩ := mem_image.mp hSite
      exact member.property
    have hUnion : subset.biUnion choices =
        (right.filter fun target => ∃ site ∈ selected, Graph.Adj site target).disjSum univ := by
      ext (target | dummy)
      · simp only [mem_biUnion, choices, inl_mem_disjSum, mem_filter, selected, mem_image]
        constructor
        · rintro ⟨member, hMember, hRight, hAdj⟩
          exact ⟨hRight, member, ⟨member, hMember, rfl⟩, hAdj⟩
        · rintro ⟨hRight, _, ⟨member, hMember, rfl⟩, hAdj⟩
          exact ⟨member, hMember, hRight, hAdj⟩
      · simp only [mem_biUnion, choices, inr_mem_disjSum, mem_univ, and_true, iff_true]
        exact nonempty_iff_ne_empty.mpr hEmpty
    rw [hUnion, card_disjSum, card_univ, Fintype.card_fin]
    simpa only [selected, card_image_of_injective _ Subtype.val_injective] using
      hDeficiency selected hSelected
  obtain ⟨assign, hInjective, hAssign⟩ :=
    (all_card_le_biUnion_card_iff_existsInjective' choices).mp hHall
  let matched := left.filter fun site => ∃ (hSite : site ∈ left) (target : Vertex),
    assign ⟨site, hSite⟩ = Sum.inl target
  let partner (site : Vertex) : Vertex := if hSite : site ∈ left then
    (assign ⟨site, hSite⟩).elim id (fun _ => site) else site
  have hPartner (site : Vertex) (hSite : site ∈ left) (target : Vertex)
      (hReal : assign ⟨site, hSite⟩ = Sum.inl target) : partner site = target := by
    simp [partner, hSite, hReal]
  let assigned : Finset (Vertex ⊕ Dummy) := univ.image assign
  have hAssignedCard : #assigned = #left := by
    simp [assigned, card_image_of_injective _ hInjective]
  have hRealCount : #assigned.toLeft ≤ #matched := by
    refine (card_le_card ?_).trans (card_image_le (s := matched) (f := partner))
    intro target hTarget
    obtain ⟨site, _, hReal⟩ := mem_image.mp (mem_toLeft.mp hTarget)
    exact mem_image.mpr ⟨site, mem_filter.mpr ⟨site.property, site.property, target, hReal⟩,
      hPartner site site.property target hReal⟩
  have hDummyCount : #assigned.toRight ≤ #left - lower := by
    simpa only [Dummy, Fintype.card_fin] using card_le_univ assigned.toRight
  have hSplit := card_toLeft_add_card_toRight (u := assigned)
  refine ⟨matched, partner, filter_subset _ _, by omega, ?_, ?_⟩
  · intro site hSite other hOther hEq
    obtain ⟨_, hSiteLeft, first, hFirst⟩ := mem_filter.mp hSite
    obtain ⟨_, hOtherLeft, second, hSecond⟩ := mem_filter.mp hOther
    rw [hPartner site hSiteLeft first hFirst, hPartner other hOtherLeft second hSecond] at hEq
    exact congrArg Subtype.val (hInjective (hFirst.trans (hEq ▸ hSecond.symm)))
  · intro site hSite
    obtain ⟨_, hSiteLeft, target, hReal⟩ := mem_filter.mp hSite
    have hChoice := hAssign ⟨site, hSiteLeft⟩
    rw [hReal] at hChoice
    simpa only [hPartner site hSiteLeft target hReal, choices, inl_mem_disjSum, mem_filter]
      using hChoice

/-- Matching lower bound from an independence cap on two independent shores plus an
isolated set. The vertices here are physical, not support masks. -/
theorem bipartite_matching_of_indep_bound (Graph : SimpleGraph Vertex) [DecidableRel Graph.Adj]
    {left right isolated : Finset Vertex} {cap lower : ℕ}
    (hDisjoint : Disjoint left right) (hIsolatedDisjoint : Disjoint (left ∪ right) isolated)
    (hLeft : Graph.IsIndepSet (left : Set Vertex))
    (hRight : Graph.IsIndepSet (right : Set Vertex))
    (hIsolated : ∀ vertex ∈ isolated, ∀ other ∈ left ∪ right ∪ isolated, ¬ Graph.Adj vertex other)
    (hBound : ∀ sites ⊆ left ∪ right ∪ isolated, Graph.IsIndepSet (sites : Set Vertex) → #sites ≤ cap)
    (hLower : lower ≤ #left) (hSize : cap + lower ≤ #left + #right + #isolated) :
    ∃ (matched : Finset Vertex) (partner : Vertex → Vertex), matched ⊆ left ∧
      lower ≤ #matched ∧ Set.InjOn partner (matched : Set Vertex) ∧
      ∀ site ∈ matched, partner site ∈ right ∧ Graph.Adj site (partner site) := by
  classical
  apply matching_of_deficiency Graph left right lower hLower
  intro selected hSelected
  let neighbors := right.filter fun target => ∃ site ∈ selected, Graph.Adj site target
  let remainder := right \ neighbors
  let witness := selected ∪ remainder ∪ isolated
  have hRemRight : remainder ⊆ right := sdiff_subset
  have hSubset : witness ⊆ left ∪ right ∪ isolated := by
    intro vertex hVertex
    rcases mem_union.mp hVertex with hVertex | hVertex
    · exact mem_union_left _ (mem_union.mp hVertex |>.elim
        (fun h => mem_union_left _ (hSelected h)) (fun h => mem_union_right _ (hRemRight h)))
    · exact mem_union_right _ hVertex
  have hNoCross (site target : Vertex) (hSite : site ∈ selected) (hTarget : target ∈ remainder) :
      ¬ Graph.Adj site target := by
    intro hAdj
    exact (mem_sdiff.mp hTarget).2 (mem_filter.mpr ⟨hRemRight hTarget, site, hSite, hAdj⟩)
  have hIndependent : Graph.IsIndepSet (witness : Set Vertex) := by
    rw [Graph.isIndepSet_iff]
    intro first hFirst second hSecond hNe hAdj
    have hFirstIn := hSubset hFirst
    have hSecondIn := hSubset hSecond
    rcases mem_union.mp hFirst with hFirst | hFirst
    · rcases mem_union.mp hSecond with hSecond | hSecond
      · rcases mem_union.mp hFirst with hFirst | hFirst <;>
          rcases mem_union.mp hSecond with hSecond | hSecond
        · exact (Graph.isIndepSet_iff.mp hLeft) (hSelected hFirst) (hSelected hSecond) hNe hAdj
        · exact hNoCross first second hFirst hSecond hAdj
        · exact hNoCross second first hSecond hFirst hAdj.symm
        · exact (Graph.isIndepSet_iff.mp hRight) (hRemRight hFirst) (hRemRight hSecond) hNe hAdj
      · exact hIsolated second hSecond first hFirstIn hAdj.symm
    · exact hIsolated first hFirst second hSecondIn hAdj
  have hPairDisjoint := hDisjoint.mono hSelected hRemRight
  have hPairSubset : selected ∪ remainder ⊆ left ∪ right := union_subset_union hSelected hRemRight
  have hThirdDisjoint := hIsolatedDisjoint.mono_left hPairSubset
  have hCard := hBound witness hSubset hIndependent
  have hRemCard : #remainder = #right - #neighbors := card_sdiff_of_subset (filter_subset _ _)
  have hNeighborsCard : #neighbors ≤ #right := card_le_card (filter_subset _ _)
  rw [show witness = (selected ∪ remainder) ∪ isolated from rfl,
    card_union_of_disjoint hThirdDisjoint, card_union_of_disjoint hPairDisjoint, hRemCard] at hCard
  change #selected ≤ #neighbors + (#left - lower)
  omega

/-- The four-plus-four application. An isolated double site is counted in the same
independence cap of five and increases the required matching size from three to four. -/
theorem private_cell_matching_four (Graph : SimpleGraph Vertex) [DecidableRel Graph.Adj]
    {left right isolated : Finset Vertex} {cross : Bool}
    (hDisjoint : Disjoint left right) (hIsolatedDisjoint : Disjoint (left ∪ right) isolated)
    (hLeft : Graph.IsIndepSet (left : Set Vertex))
    (hRight : Graph.IsIndepSet (right : Set Vertex))
    (hIsolated : ∀ vertex ∈ isolated, ∀ other ∈ left ∪ right ∪ isolated, ¬ Graph.Adj vertex other)
    (hBound : ∀ sites ⊆ left ∪ right ∪ isolated, Graph.IsIndepSet (sites : Set Vertex) → #sites ≤ 5)
    (hLeftCard : #left = 4) (hRightCard : #right = 4)
    (hIsolatedCard : #isolated = if cross then 1 else 0) :
    ∃ (matched : Finset Vertex) (partner : Vertex → Vertex), matched ⊆ left ∧
      3 + (if cross then 1 else 0) ≤ #matched ∧ Set.InjOn partner (matched : Set Vertex) ∧
      ∀ site ∈ matched, partner site ∈ right ∧ Graph.Adj site (partner site) := by
  apply bipartite_matching_of_indep_bound Graph hDisjoint hIsolatedDisjoint hLeft hRight hIsolated hBound
  · cases cross <;> simp [hLeftCard]
  · rw [hLeftCard, hRightCard, hIsolatedCard]
    omega

/-- Composition with H-034: the noncross private-grid margin follows from an
independence cap, without assuming a matching. Columns use the same statement on
the transposed data. The disjointness, support, and independence-cap hypotheses
are local graph inputs. -/
theorem private_grid_row_bound_of_indep (Graph : SimpleGraph Vertex) [DecidableRel Graph.Adj]
    {Row : Type*} [DecidableEq Row]
    {gridSites cell right isolated : Finset Vertex} {rowOf : Vertex → Row} {columnOf : Vertex → Vertex}
    {row crossRow : Row} {crossColumn : Vertex}
    (hSingles : (gridSites.filter fun site => rowOf site = row) ⊆ cell)
    (hDisjoint : Disjoint cell right) (hIsolatedDisjoint : Disjoint (cell ∪ right) isolated)
    (hLeft : Graph.IsIndepSet (cell : Set Vertex))
    (hRight : Graph.IsIndepSet (right : Set Vertex))
    (hIsolated : ∀ vertex ∈ isolated, ∀ other ∈ cell ∪ right ∪ isolated, ¬ Graph.Adj vertex other)
    (hBound : ∀ sites ⊆ cell ∪ right ∪ isolated, Graph.IsIndepSet (sites : Set Vertex) → #sites ≤ 5)
    (hCellCard : #cell = 4) (hRightCard : #right = 4)
    (hIsolatedCard : #isolated = if row = crossRow then 1 else 0)
    (hNoncross : crossColumn ∉ right)
    (hSingleContact : ∀ site ∈ gridSites, rowOf site = row →
      ∀ anchor ∈ right, Graph.Adj site anchor → anchor = columnOf site) :
    #(gridSites.filter fun site => rowOf site = row) -
        #(((gridSites.filter fun site => rowOf site = row).image columnOf).erase crossColumn) ≤
      1 - (if row = crossRow then 1 else 0) := by
  have hIsoBool : #isolated = if decide (row = crossRow) then 1 else 0 := by simpa using hIsolatedCard
  obtain ⟨matched, partner, hMatched, hSize, hDistinct, hEdges⟩ :=
    private_cell_matching_four Graph hDisjoint hIsolatedDisjoint hLeft hRight hIsolated hBound
      hCellCard hRightCard hIsoBool
  apply private_grid_row_bound hSingles hCellCard hMatched hDistinct
  · exact fun site hSite hEq => hNoncross (hEq ▸ (hEdges site hSite).1)
  · exact fun site hSite hGrid hRow =>
      hSingleContact site hGrid hRow (partner site) (hEdges site hSite).1 (hEdges site hSite).2
  · simpa using hSize

end R310
