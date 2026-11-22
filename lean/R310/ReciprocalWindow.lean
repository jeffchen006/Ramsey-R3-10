import R310.PathWindow

namespace R310

open Finset SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

/-- The degree at `vertex` in the graph induced on `window`, when it belongs there. -/
def windowDegree (G : SimpleGraph V) [DecidableRel G.Adj] (window : Finset V) (vertex : V) : ℕ :=
  #(G.neighborFinset vertex ∩ window)

theorem degree_induce_eq_windowDegree (window : Finset V) (vertex : (window : Set V)) :
    (G.induce (window : Set V)).degree vertex = windowDegree G window vertex := by
  have hMap := congrArg Finset.card (map_neighborFinset_induce (G := G) (s := (window : Set V)) vertex)
  rw [card_map, Finset.toFinset_coe] at hMap
  rw [windowDegree, ← card_neighborFinset_eq_degree]
  convert hMap using 2
  ext other
  simp

/-- Only the neighbours of the marked vertex need to lie in the two windows. -/
theorem windowDegree_add (left right : Finset V) (vertex : V)
    (hCover : G.neighborFinset vertex ⊆ left ∪ right) :
    windowDegree G left vertex + windowDegree G right vertex =
      G.degree vertex + windowDegree G (left ∩ right) vertex := by
  have hUnion : (G.neighborFinset vertex ∩ left) ∪ (G.neighborFinset vertex ∩ right) =
      G.neighborFinset vertex := by
    ext other
    simp only [mem_inter, mem_union]
    refine ⟨by tauto, fun hNbr => ?_⟩
    have := mem_union.mp (hCover hNbr)
    tauto
  have hInter : (G.neighborFinset vertex ∩ left) ∩ (G.neighborFinset vertex ∩ right) =
      G.neighborFinset vertex ∩ (left ∩ right) := by
    ext other
    simp only [mem_inter]
    tauto
  simpa only [windowDegree, hUnion, hInter, card_neighborFinset_eq_degree] using
    (card_union_add_card_inter (G.neighborFinset vertex ∩ left)
      (G.neighborFinset vertex ∩ right)).symm

/-- Vertices outside the roots and all their neighbours. -/
def rootsWindow (G : SimpleGraph V) [DecidableRel G.Adj] (roots : Finset V) : Finset V :=
  univ \ (roots ∪ roots.biUnion fun root => G.neighborFinset root)

theorem mem_rootsWindow {roots : Finset V} {vertex : V} :
    vertex ∈ rootsWindow G roots ↔ vertex ∉ roots ∧ ∀ root ∈ roots, ¬G.Adj root vertex := by
  simp [rootsWindow, not_or]

/-- For two nonempty completely joined root sets, every nonroot belongs to a window. -/
theorem reciprocal_windows_union (hTriangle : G.CliqueFree 3) {left right : Finset V}
    (hLeft : left.Nonempty) (hRight : right.Nonempty)
    (hCross : ∀ vertex ∈ left, ∀ other ∈ right, G.Adj vertex other) :
    rootsWindow G left ∪ rootsWindow G right = univ \ (left ∪ right) := by
  ext vertex
  simp only [mem_union, mem_sdiff, mem_univ, true_and, not_or, mem_rootsWindow]
  constructor
  · rintro (⟨hOut, hAvoid⟩ | ⟨hOut, hAvoid⟩)
    · refine ⟨hOut, fun hIn => ?_⟩
      obtain ⟨root, hRoot⟩ := hLeft
      exact hAvoid root hRoot (hCross root hRoot vertex hIn)
    · refine ⟨fun hIn => ?_, hOut⟩
      obtain ⟨root, hRoot⟩ := hRight
      exact hAvoid root hRoot (hCross vertex hIn root hRoot).symm
  · rintro ⟨hOutLeft, hOutRight⟩
    by_cases hAvoid : ∀ root ∈ left, ¬G.Adj root vertex
    · exact Or.inl ⟨hOutLeft, hAvoid⟩
    · push Not at hAvoid
      obtain ⟨root, hRoot, hAdj⟩ := hAvoid
      refine Or.inr ⟨hOutRight, fun other hOther hEdge => ?_⟩
      exact hTriangle {root, other, vertex}
        (is3Clique_triple_iff.mpr ⟨hCross root hRoot other hOther, hAdj, hEdge⟩)

theorem reciprocal_window_degrees (hTriangle : G.CliqueFree 3) {left right : Finset V}
    (hLeft : left.Nonempty) (hRight : right.Nonempty)
    (hCross : ∀ vertex ∈ left, ∀ other ∈ right, G.Adj vertex other) {vertex : V}
    (hShared : vertex ∈ rootsWindow G left ∩ rootsWindow G right) :
    windowDegree G (rootsWindow G left) vertex + windowDegree G (rootsWindow G right) vertex =
      G.degree vertex + windowDegree G (rootsWindow G left ∩ rootsWindow G right) vertex := by
  apply windowDegree_add
  rw [reciprocal_windows_union hTriangle hLeft hRight hCross]
  obtain ⟨hLeftWindow, hRightWindow⟩ := mem_inter.mp hShared
  intro other hOther
  have hAdj : G.Adj other vertex := ((mem_neighborFinset G vertex other).mp hOther).symm
  exact mem_sdiff.mpr ⟨mem_univ _, fun hRoot => (mem_union.mp hRoot).elim
    (fun hIn => (mem_rootsWindow.mp hLeftWindow).2 other hIn hAdj)
    (fun hIn => (mem_rootsWindow.mp hRightWindow).2 other hIn hAdj)⟩

/-- Each diagonal of the planted order-22 square has six-neighbour roots and codegree two. -/
theorem rootsWindow_pair_card_ten (hOrder : Fintype.card V = 22) {first second : V}
    (hDistinct : first ≠ second) (hIndependent : ¬G.Adj first second)
    (hFirst : G.degree first = 6) (hSecond : G.degree second = 6)
    (hCodeg : #(G.neighborFinset first ∩ G.neighborFinset second) = 2) :
    #(rootsWindow G {first, second}) = 10 := by
  have hRoots : #({first, second} : Finset V) = 2 := by simp [hDistinct]
  have hDisjoint : Disjoint ({first, second} : Finset V)
      (G.neighborFinset first ∪ G.neighborFinset second) := by
    refine disjoint_left.mpr ?_
    intro vertex hRoot hNbr
    simp only [mem_insert, mem_singleton] at hRoot
    have hReverse : ¬G.Adj second first := fun hAdj => hIndependent hAdj.symm
    rcases hRoot with rfl | rfl <;> simp [hIndependent, hReverse] at hNbr
  have hNear := card_union_add_card_inter (G.neighborFinset first) (G.neighborFinset second)
  simp only [hCodeg, card_neighborFinset_eq_degree, hFirst, hSecond] at hNear
  unfold rootsWindow
  rw [card_sdiff_of_subset (subset_univ _), card_univ, hOrder, biUnion_insert,
    singleton_biUnion, card_union_of_disjoint hDisjoint, hRoots]
  omega

/-- The overlap of the two opposite order-ten windows of an order-22 square has order two. -/
theorem reciprocal_square_overlap (hTriangle : G.CliqueFree 3) (hOrder : Fintype.card V = 22)
    {left right : Finset V} (hLeft : #left = 2) (hRight : #right = 2)
    (hCross : ∀ vertex ∈ left, ∀ other ∈ right, G.Adj vertex other)
    (hLeftWindow : #(rootsWindow G left) = 10) (hRightWindow : #(rootsWindow G right) = 10) :
    #(rootsWindow G left ∩ rootsWindow G right) = 2 := by
  have hDisjoint : Disjoint left right := disjoint_left.mpr fun _ hv hw =>
    (hCross _ hv _ hw).ne rfl
  have hUnion := reciprocal_windows_union hTriangle
    (card_pos.mp (by omega : 0 < #left)) (card_pos.mp (by omega : 0 < #right)) hCross
  have hCount := card_union_add_card_inter (rootsWindow G left) (rootsWindow G right)
  rw [hLeftWindow, hRightWindow, hUnion, card_sdiff_of_subset (subset_univ _), card_univ,
    hOrder, card_union_of_disjoint hDisjoint, hLeft, hRight] at hCount
  omega

/-- Opposite pairs in a six-regular graph: the degree signature requests `6 + d_Z - d_left`. -/
theorem reciprocal_square_opposite_degree (hTriangle : G.CliqueFree 3)
    {left right : Finset V} (hLeft : #left = 2) (hRight : #right = 2)
    (hCross : ∀ vertex ∈ left, ∀ other ∈ right, G.Adj vertex other) {vertex : V}
    (hShared : vertex ∈ rootsWindow G left ∩ rootsWindow G right) (hDegree : G.degree vertex = 6) :
    windowDegree G (rootsWindow G right) vertex =
      6 + windowDegree G (rootsWindow G left ∩ rootsWindow G right) vertex -
        windowDegree G (rootsWindow G left) vertex := by
  have hCount := reciprocal_window_degrees hTriangle
    (card_pos.mp (by omega : 0 < #left)) (card_pos.mp (by omega : 0 < #right)) hCross hShared
  omega

end R310
