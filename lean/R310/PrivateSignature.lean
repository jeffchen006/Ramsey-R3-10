import R310.RootDemand

namespace R310

open Finset SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]
  {G : SimpleGraph V} [DecidableRel G.Adj] {root : V}

/-- The neighbors of an exterior vertex that belong to the root neighborhood. -/
def rootSignature (G : SimpleGraph V) [DecidableRel G.Adj] (root vertex : V) : Finset V :=
  (G.neighborFinset root).filter (G.Adj vertex)

omit [DecidableEq V] in
@[simp] theorem mem_rootSignature {vertex anchor : V} :
    anchor ∈ rootSignature G root vertex ↔ anchor ∈ G.neighborFinset root ∧ G.Adj vertex anchor := by
  rw [rootSignature, mem_filter]

/-- A family whose signatures lie in a boundary block and share an anchor can be
joined to the rest of the root neighborhood in an independent set. -/
theorem card_signature_family_add_degree_le (hTriangle : G.CliqueFree 3)
    {family block : Finset V} {anchor : V} (hBlock : block ⊆ G.neighborFinset root)
    (hFamily : family ⊆ outside G root)
    (hSignatures : ∀ vertex ∈ family,
      anchor ∈ rootSignature G root vertex ∧ rootSignature G root vertex ⊆ block) :
    #family + G.degree root ≤ G.indepNum + #block := by
  have hDisjoint : Disjoint family (G.neighborFinset root \ block) := by
    rw [Finset.disjoint_left]
    intro vertex hv hw
    exact (mem_outside.mp (hFamily hv)).2 ((mem_neighborFinset _ _ _).mp (mem_sdiff.mp hw).1)
  have hIndep : G.IsIndepSet ((family ∪ (G.neighborFinset root \ block) : Finset V) : Set V) := by
    rw [coe_union, isIndepSet_iff, Set.pairwise_union]
    refine ⟨?_, ?_, ?_⟩
    · intro first hf second hs hNe
      exact isIndepSet_neighborFinset hTriangle anchor
        ((mem_neighborFinset _ _ _).mpr (mem_rootSignature.mp (hSignatures first hf).1).2.symm)
        ((mem_neighborFinset _ _ _).mpr (mem_rootSignature.mp (hSignatures second hs).1).2.symm) hNe
    · intro first hf second hs hNe
      exact isIndepSet_neighborFinset hTriangle root (mem_sdiff.mp hf).1 (mem_sdiff.mp hs).1 hNe
    · intro first hf second hs _
      have hNo : ¬ G.Adj first second := fun hAdj => (mem_sdiff.mp hs).2
        ((hSignatures first hf).2 (mem_rootSignature.mpr ⟨(mem_sdiff.mp hs).1, hAdj⟩))
      exact ⟨hNo, fun hAdj => hNo hAdj.symm⟩
  have hCard := hIndep.card_le_indepNum
  rw [card_union_of_disjoint hDisjoint, card_sdiff_of_subset hBlock,
    card_neighborFinset_eq_degree] at hCard
  have hBlockCard := card_le_card hBlock
  rw [card_neighborFinset_eq_degree] at hBlockCard
  omega

/-- With a full private cell at one anchor, a fixed double signature cannot repeat.
This local step only needs triangle-freeness and the supplied cell saturation. -/
theorem eq_of_double_signature_of_full_cell (hTriangle : G.CliqueFree 3)
    {anchor other first second : V} (hAnchor : anchor ∈ G.neighborFinset root)
    (hOther : other ∈ G.neighborFinset root) (hDifferent : anchor ≠ other)
    (hFirst : first ∈ outside G root) (hSecond : second ∈ outside G root)
    (hSigFirst : rootSignature G root first = {anchor, other})
    (hSigSecond : rootSignature G root second = {anchor, other})
    (hFull : G.indepNum + 1 ≤
      #{vertex ∈ outside G root | rootSignature G root vertex = {anchor}} + G.degree root) :
    first = second := by
  by_contra hNe
  let cell := {vertex ∈ outside G root | rootSignature G root vertex = {anchor}}
  have hSize : #({anchor, other} : Finset V) = 2 := card_pair hDifferent
  have hNot : ∀ vertex, rootSignature G root vertex = {anchor, other} → vertex ∉ cell := by
    intro vertex hSig hIn
    have hSingle := (mem_filter.mp hIn).2
    rw [hSig] at hSingle
    have := congrArg Finset.card hSingle
    simp [hSize] at this
  have hBound := card_signature_family_add_degree_le (G := G) (root := root)
    hTriangle (family := insert first (insert second cell)) (block := {anchor, other})
    (anchor := anchor)
    (by intro vertex hv; simp only [mem_insert, mem_singleton] at hv;
        rcases hv with rfl | rfl; exact hAnchor; exact hOther)
    (by intro vertex hv; simp only [mem_insert] at hv;
        rcases hv with rfl | rfl | hv; exact hFirst; exact hSecond; exact (mem_filter.mp hv).1)
    (by
      intro vertex hv
      simp only [mem_insert] at hv
      rcases hv with rfl | rfl | hv
      · simp [hSigFirst]
      · simp [hSigSecond]
      · simp [(mem_filter.mp hv).2])
  rw [card_insert_of_notMem (by simp [hNe, hNot first hSigFirst]),
    card_insert_of_notMem (hNot second hSigSecond), hSize] at hBound
  change G.indepNum + 1 ≤ #cell + G.degree root at hFull
  omega

/-- At the 48-edge budget for a degree-six root, all six private cells have size
four and all other exterior signatures have size two. This applies to e168 with a
residue floor of 120, and to e169 with a residue floor of 121. -/
theorem IsMTF.degree_six_signature_equality {G : SimpleGraph (Fin 40)} [DecidableRel G.Adj]
    (hmtf : IsMTF G) (hAlpha : G.indepNum ≤ 9) {root : Fin 40} (hDegree : G.degree root = 6)
    (hBudget : #G.edgeFinset ≤ #(delNbhd G root).edgeFinset + 48) :
    (∀ anchor ∈ G.neighborFinset root,
      #{vertex ∈ outside G root | rootSignature G root vertex = {anchor}} = 4) ∧
    (∀ vertex ∈ outside G root, #(rootSignature G root vertex) = 1 ∨
      #(rootSignature G root vertex) = 2) ∧
    #{vertex ∈ outside G root | #(rootSignature G root vertex) = 2} = 9 := by
  let exterior := outside G root
  let boundary := G.neighborFinset root
  let signature := rootSignature G root
  let cell := fun anchor => {vertex ∈ exterior | signature vertex = {anchor}}
  let singles := {vertex ∈ exterior | #(signature vertex) = 1}
  let weight := fun vertex => #(signature vertex) + if #(signature vertex) = 1 then 1 else 0
  have hExt : #exterior = 33 := by
    have hSize := card_outside_add (G := G) root
    simp only [Fintype.card_fin, hDegree] at hSize
    change #exterior + 6 + 1 = 40 at hSize
    omega
  have hBoundary : #boundary = 6 := (card_neighborFinset_eq_degree _ _).trans hDegree
  have hSum : (∑ vertex ∈ exterior, #(signature vertex)) ≤ 42 := by
    have hZ := sum_nbrIn_add_degree hmtf.1 root
    have hSplit := card_edgeFinset_delNbhd_add_sum_degree hmtf.1 root
    change (∑ vertex ∈ exterior, #(signature vertex)) + G.degree root = _ at hZ
    omega
  have hWeight : ∀ vertex ∈ exterior, 2 ≤ weight vertex := by
    intro vertex hVertex
    obtain ⟨anchor, hAnchor, hAttach⟩ := hmtf.exists_attachment_for_demand (RootDemand.single hVertex)
    have hPos : 0 < #(signature vertex) := card_pos.mpr
      ⟨anchor, mem_rootSignature.mpr ⟨hAnchor, (hAttach vertex (mem_singleton_self _)).symm⟩⟩
    dsimp only [weight]
    split_ifs <;> omega
  have hWeightSum : (∑ vertex ∈ exterior, weight vertex) =
      (∑ vertex ∈ exterior, #(signature vertex)) + #singles := by
    dsimp only [weight, singles]
    rw [sum_add_distrib, card_filter]
  have hCellBound : ∀ anchor ∈ boundary, #(cell anchor) ≤ 4 := by
    intro anchor hAnchor
    have hBound := card_signature_family_add_degree_le (G := G) (root := root)
      hmtf.1 (family := cell anchor) (block := {anchor}) (anchor := anchor)
      (singleton_subset_iff.mpr hAnchor) (filter_subset _ _)
      (by
        intro vertex hv
        have hSig : rootSignature G root vertex = {anchor} := (mem_filter.mp hv).2
        rw [hSig]
        exact ⟨mem_singleton_self _, Subset.refl _⟩)
    simp only [hDegree, card_singleton] at hBound
    omega
  have hPartition : boundary.biUnion cell = singles := by
    ext vertex
    constructor
    · intro hv
      obtain ⟨anchor, _, hCell⟩ := mem_biUnion.mp hv
      obtain ⟨hVertex, hSig⟩ := mem_filter.mp hCell
      exact mem_filter.mpr ⟨hVertex, by simp [hSig]⟩
    · intro hv
      obtain ⟨hVertex, hSize⟩ := mem_filter.mp hv
      obtain ⟨anchor, hSig⟩ := card_eq_one.mp hSize
      have hMem : anchor ∈ signature vertex := by simp [hSig]
      exact mem_biUnion.mpr ⟨anchor, (mem_rootSignature.mp hMem).1,
        mem_filter.mpr ⟨hVertex, hSig⟩⟩
  have hDisjoint : (boundary : Set (Fin 40)).PairwiseDisjoint cell := by
    intro first _ second _ hNe
    change Disjoint (cell first) (cell second)
    rw [Finset.disjoint_left]
    intro vertex hf hs
    have heq := (mem_filter.mp hf).2.symm.trans (mem_filter.mp hs).2
    exact hNe (by simpa using heq)
  have hSingleSum : #singles = ∑ anchor ∈ boundary, #(cell anchor) := by
    rw [← hPartition, card_biUnion hDisjoint]
  have hCellSum : (∑ anchor ∈ boundary, #(cell anchor)) ≤ ∑ _anchor ∈ boundary, 4 :=
    sum_le_sum hCellBound
  have hDoubleLower : (∑ _vertex ∈ exterior, 2) ≤ ∑ vertex ∈ exterior, weight vertex :=
    sum_le_sum hWeight
  have hConst4 : (∑ _anchor ∈ boundary, (4 : ℕ)) = 24 := by simp [hBoundary]
  have hConst2 : (∑ _vertex ∈ exterior, (2 : ℕ)) = 66 := by simp [hExt]
  have hSingles : #singles = 24 := by omega
  have hAllCells : ∀ anchor ∈ boundary, #(cell anchor) = 4 := by
    intro anchor hAnchor
    by_contra hNot
    have hStrict := sum_lt_sum hCellBound ⟨anchor, hAnchor, lt_of_le_of_ne (hCellBound anchor hAnchor) hNot⟩
    omega
  have hAllWeights : ∀ vertex ∈ exterior, weight vertex = 2 := by
    intro vertex hVertex
    by_contra hNot
    have hStrict := sum_lt_sum hWeight ⟨vertex, hVertex,
      lt_of_le_of_ne (hWeight vertex hVertex) (Ne.symm hNot)⟩
    omega
  have hSizes : ∀ vertex ∈ exterior, #(signature vertex) = 1 ∨ #(signature vertex) = 2 := by
    intro vertex hVertex
    have hEq := hAllWeights vertex hVertex
    dsimp only [weight] at hEq
    by_cases hOne : #(signature vertex) = 1
    · exact Or.inl hOne
    · exact Or.inr (by simpa [hOne] using hEq)
  refine ⟨hAllCells, hSizes, ?_⟩
  have hDoubles : {vertex ∈ exterior | #(signature vertex) = 2} = exterior \ singles := by
    ext vertex
    simp only [mem_filter, mem_sdiff, singles]
    constructor
    · rintro ⟨hv, hTwo⟩
      exact ⟨hv, by simp [hTwo]⟩
    · rintro ⟨hv, hNot⟩
      exact ⟨hv, (hSizes vertex hv).resolve_left (fun hOne => hNot ⟨hv, hOne⟩)⟩
  change #({vertex ∈ exterior | #(signature vertex) = 2} : Finset (Fin 40)) = 9
  rw [hDoubles, card_sdiff_of_subset (filter_subset _ _), hExt, hSingles]

/-- The nine double signatures at a degree-six root on the edge budget are distinct. -/
theorem IsMTF.degree_six_double_signatures_injective {G : SimpleGraph (Fin 40)}
    [DecidableRel G.Adj] (hmtf : IsMTF G) (hAlpha : G.indepNum ≤ 9) {root : Fin 40}
    (hDegree : G.degree root = 6) (hBudget : #G.edgeFinset ≤ #(delNbhd G root).edgeFinset + 48) :
    Set.InjOn (rootSignature G root)
      ({vertex ∈ outside G root | #(rootSignature G root vertex) = 2} : Finset (Fin 40)) := by
  intro first hf second hs hEq
  obtain ⟨hFirst, hSize⟩ := mem_filter.mp (show first ∈
    ({vertex ∈ outside G root | #(rootSignature G root vertex) = 2} : Finset (Fin 40)) from hf)
  have hSecond := (mem_filter.mp (show second ∈
    ({vertex ∈ outside G root | #(rootSignature G root vertex) = 2} : Finset (Fin 40)) from hs)).1
  obtain ⟨anchor, other, hNe, hSig⟩ := card_eq_two.mp hSize
  have hAnchor : anchor ∈ G.neighborFinset root :=
    (mem_rootSignature.mp (show anchor ∈ rootSignature G root first by simp [hSig])).1
  have hOther : other ∈ G.neighborFinset root :=
    (mem_rootSignature.mp (show other ∈ rootSignature G root first by simp [hSig])).1
  have hFull := (hmtf.degree_six_signature_equality hAlpha hDegree hBudget).1 anchor hAnchor
  exact eq_of_double_signature_of_full_cell hmtf.1 hAnchor hOther hNe hFirst hSecond hSig
    (hEq.symm.trans hSig) (by omega)

/-- The unordered edges of the signature graph are represented by nine distinct
two-element finsets. No finite classification of the possible graphs is used. -/
theorem IsMTF.degree_six_signature_edge_count {G : SimpleGraph (Fin 40)} [DecidableRel G.Adj]
    (hmtf : IsMTF G) (hAlpha : G.indepNum ≤ 9) {root : Fin 40} (hDegree : G.degree root = 6)
    (hBudget : #G.edgeFinset ≤ #(delNbhd G root).edgeFinset + 48) :
    #(({vertex ∈ outside G root | #(rootSignature G root vertex) = 2}).image
      (rootSignature G root)) = 9 := by
  rw [card_image_of_injOn (hmtf.degree_six_double_signatures_injective hAlpha hDegree hBudget)]
  exact (hmtf.degree_six_signature_equality hAlpha hDegree hBudget).2.2

end R310
