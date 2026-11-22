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

/-- Count incidences to a window by a sum of adjacency indicators. -/
theorem windowDegree_eq_sum (window : Finset V) (vertex : V) :
    windowDegree G window vertex = ∑ other ∈ window, if G.Adj vertex other then 1 else 0 := by
  rw [← Finset.sum_filter]
  simp only [sum_const, nsmul_eq_mul, mul_one, windowDegree]
  congr 1
  ext other
  simp [and_comm]

/-- The two sides count the same crossing incidences. -/
theorem sum_windowDegree_comm (left right : Finset V) :
    (∑ vertex ∈ left, windowDegree G right vertex) = ∑ vertex ∈ right, windowDegree G left vertex := by
  simp only [windowDegree_eq_sum]
  rw [Finset.sum_comm]
  refine sum_congr rfl fun other _ => sum_congr rfl fun vertex _ => ?_
  by_cases h : G.Adj vertex other
  · simp [h, h.symm]
  · have hRev : ¬G.Adj other vertex := fun hAdj => h hAdj.symm
    simp [h, hRev]

/-- Restricted handshaking, expressed as a sum over the ambient vertex type. -/
theorem sum_windowDegree_eq_double_edges (window : Finset V) :
    (∑ vertex ∈ window, windowDegree G window vertex) = 2 * #(G.induce (window : Set V)).edgeFinset := by
  rw [← (G.induce (window : Set V)).sum_degrees_eq_twice_card_edges]
  rw [← Finset.sum_finset_coe]
  exact sum_congr rfl fun vertex _ => (degree_induce_eq_windowDegree window vertex).symm

private theorem windowDegree_disjoint_union {left right : Finset V} (hDisj : Disjoint left right)
    (vertex : V) :
    windowDegree G (left ∪ right) vertex = windowDegree G left vertex + windowDegree G right vertex := by
  simp only [windowDegree_eq_sum]
  exact sum_union hDisj

private theorem sum_windowDegree_partition {first second third : Finset V}
    (hDisj : Disjoint first second) (hDisjThird : Disjoint (first ∪ second) third)
    (hCover : first ∪ second ∪ third = univ) (sites : Finset V) :
    (∑ vertex ∈ sites, G.degree vertex) =
      (∑ vertex ∈ sites, windowDegree G first vertex) +
      (∑ vertex ∈ sites, windowDegree G second vertex) +
      ∑ vertex ∈ sites, windowDegree G third vertex := by
  have hDeg (vertex : V) : G.degree vertex = windowDegree G univ vertex := by
    simp [windowDegree]
  simp_rw [← sum_add_distrib, ← windowDegree_disjoint_union hDisj,
    ← windowDegree_disjoint_union hDisjThird, hCover, ← hDeg]

/-- C's degree balance across the order-22 window. The identity is independent of the
cap-five and tight-pair hypotheses: only the regular bipartite-root marking is used. -/
theorem rootsWindow_degree_sum_of_regular {left right : Finset V}
    (hTriangle : G.CliqueFree 3) (hLeft : left.Nonempty) (hRight : right.Nonempty)
    (hCross : ∀ vertex ∈ left, ∀ other ∈ right, G.Adj vertex other)
    {degree : ℕ} (hRegular : ∀ vertex, G.degree vertex = degree) (hEqual : #left = #right) :
    let window := rootsWindow G left
    let privateSites := univ \ (window ∪ (left ∪ right))
    2 * #(G.induce (window : Set V)).edgeFinset + degree * #privateSites =
      2 * #(G.induce (privateSites : Set V)).edgeFinset + degree * #window := by
  dsimp only
  let window := rootsWindow G left
  let boundary := left ∪ right
  let privateSites := univ \ (window ∪ boundary)
  change 2 * #(G.induce (window : Set V)).edgeFinset + degree * #privateSites =
    2 * #(G.induce (privateSites : Set V)).edgeFinset + degree * #window
  have hAll := reciprocal_windows_union hTriangle hLeft hRight hCross
  have hWinBoundary : Disjoint window boundary := by
    refine disjoint_left.mpr fun vertex hw hb => ?_
    have hOut : vertex ∈ univ \ boundary := by
      change vertex ∈ univ \ (left ∪ right)
      rw [← hAll]
      exact mem_union_left _ hw
    exact (mem_sdiff.mp hOut).2 hb
  have hWinPrivate : Disjoint window privateSites := disjoint_left.mpr fun vertex hw hp =>
    (mem_sdiff.mp hp).2 (mem_union_left _ hw)
  have hRestBoundary : Disjoint (window ∪ privateSites) boundary := by
    refine disjoint_left.mpr fun vertex hm hb => ?_
    rcases mem_union.mp hm with hw | hp
    · exact disjoint_left.mp hWinBoundary hw hb
    · exact (mem_sdiff.mp hp).2 (mem_union_right _ hb)
  have hCover : window ∪ privateSites ∪ boundary = univ := by
    ext vertex
    simp [privateSites]
    tauto
  have hRemainder : ∀ vertex ∈ privateSites, vertex ∈ rootsWindow G right := by
    intro vertex hp
    have hout := (mem_sdiff.mp hp).2
    have hin : vertex ∈ window ∪ rootsWindow G right := by
      change vertex ∈ rootsWindow G left ∪ rootsWindow G right
      rw [hAll]
      exact mem_sdiff.mpr ⟨mem_univ _, fun hb => hout (mem_union_right _ hb)⟩
    exact (mem_union.mp hin).resolve_left (fun hw => hout (mem_union_left _ hw))
  have hSameSide {side other : Finset V} (hOther : other.Nonempty)
      (hJoin : ∀ vertex ∈ side, ∀ anchor ∈ other, G.Adj vertex anchor) :
      ∀ vertex ∈ side, ¬∃ anchor ∈ side, G.Adj vertex anchor := by
    intro vertex hv ⟨anchor, ha, hAdj⟩
    obtain ⟨outside, ho⟩ := hOther
    exact hTriangle {vertex, anchor, outside}
      (is3Clique_triple_iff.mpr ⟨hAdj, hJoin vertex hv outside ho, hJoin anchor ha outside ho⟩)
  have hBL : ∀ vertex ∈ left, windowDegree G boundary vertex = #right := by
    intro vertex hv
    unfold windowDegree boundary
    congr 1
    ext other
    simp only [mem_inter, mem_union, mem_neighborFinset]
    exact ⟨fun ⟨hAdj, hIn⟩ => hIn.resolve_left fun ha =>
      (hSameSide hRight hCross vertex hv) ⟨other, ha, hAdj⟩,
      fun hr => ⟨hCross vertex hv other hr, Or.inr hr⟩⟩
  have hCrossRev : ∀ vertex ∈ right, ∀ other ∈ left, G.Adj vertex other :=
    fun vertex hv other ho => (hCross other ho vertex hv).symm
  have hBR : ∀ vertex ∈ right, windowDegree G boundary vertex = #left := by
    intro vertex hv
    unfold windowDegree boundary
    congr 1
    ext other
    simp only [mem_inter, mem_union, mem_neighborFinset]
    exact ⟨fun ⟨hAdj, hIn⟩ => hIn.resolve_right fun ha =>
      (hSameSide hLeft hCrossRev vertex hv) ⟨other, ha, hAdj⟩,
      fun hl => ⟨hCrossRev vertex hv other hl, Or.inl hl⟩⟩
  have hWindowAvoid (root : V) (roots sites : Finset V) (hr : root ∈ roots)
      (hs : sites ⊆ rootsWindow G roots) : windowDegree G sites root = 0 := by
    rw [windowDegree, card_eq_zero]
    exact eq_empty_iff_forall_notMem.mpr fun vertex hv =>
      (mem_rootsWindow.mp (hs (mem_inter.mp hv).2)).2 root hr
        ((mem_neighborFinset _ _ _).mp (mem_inter.mp hv).1)
  have hSum (sites : Finset V) : ∑ vertex ∈ sites, G.degree vertex = degree * #sites := by
    simp [hRegular, Nat.mul_comm]
  have hJoinDisj : Disjoint left right := disjoint_left.mpr fun vertex hl hr =>
    (hCross vertex hl vertex hr).ne rfl
  have hBWH : (∑ vertex ∈ boundary, windowDegree G window vertex) = #right * (degree - #left) := by
    rw [show boundary = left ∪ right by rfl, sum_union hJoinDisj]
    have hL : ∑ vertex ∈ left, windowDegree G window vertex = 0 := by
      exact sum_eq_zero fun vertex hv => hWindowAvoid vertex left window hv (by rfl)
    rw [hL, zero_add]
    calc
      _ = ∑ _vertex ∈ right, (degree - #left : ℕ) := by
        refine sum_congr rfl fun vertex hv => ?_
        have hPart := sum_windowDegree_partition (G := G) hWinPrivate hRestBoundary hCover {vertex}
        simp only [sum_singleton] at hPart
        rw [hRegular, hBR vertex hv, hWindowAvoid vertex right privateSites hv hRemainder] at hPart
        omega
      _ = _ := by simp only [sum_const, nsmul_eq_mul, Nat.cast_id]
  have hBWP : (∑ vertex ∈ boundary, windowDegree G privateSites vertex) = #left * (degree - #right) := by
    rw [show boundary = left ∪ right by rfl, sum_union hJoinDisj]
    have hR : ∑ vertex ∈ right, windowDegree G privateSites vertex = 0 := by
      exact sum_eq_zero fun vertex hv => hWindowAvoid vertex right privateSites hv hRemainder
    rw [hR, add_zero]
    calc
      _ = ∑ _vertex ∈ left, (degree - #right : ℕ) := by
        refine sum_congr rfl fun vertex hv => ?_
        have hPart := sum_windowDegree_partition (G := G) hWinPrivate hRestBoundary hCover {vertex}
        simp only [sum_singleton] at hPart
        rw [hRegular, hBL vertex hv, hWindowAvoid vertex left window hv (by rfl)] at hPart
        omega
      _ = _ := by simp only [sum_const, nsmul_eq_mul, Nat.cast_id]
  have hWindow := sum_windowDegree_partition (G := G) hWinPrivate hRestBoundary hCover window
  have hPrivate := sum_windowDegree_partition (G := G) hWinPrivate hRestBoundary hCover privateSites
  rw [hSum, sum_windowDegree_eq_double_edges, sum_windowDegree_comm window boundary, hBWH] at hWindow
  rw [hSum, sum_windowDegree_eq_double_edges, sum_windowDegree_comm privateSites boundary, hBWP,
    sum_windowDegree_comm privateSites window, hEqual] at hPrivate
  rw [hEqual] at hWindow
  omega

/-- C's e(P)=e(F_A)−45 projection, including its non-truncating form. -/
theorem rootsWindow_edges_sub_forty_five {left right : Finset V}
    (hTriangle : G.CliqueFree 3) (hLeft : #left = 3) (hRight : #right = 3)
    (hCross : ∀ vertex ∈ left, ∀ other ∈ right, G.Adj vertex other)
    (hRegular : ∀ vertex, G.degree vertex = 9) (hWindow : #(rootsWindow G left) = 22)
    (hOrder : Fintype.card V = 40) :
    let window := rootsWindow G left
    let privateSites := univ \ (window ∪ (left ∪ right))
    (#(G.induce (privateSites : Set V)).edgeFinset + 45 = #(G.induce (window : Set V)).edgeFinset) := by
  let window := rootsWindow G left
  have hL := card_pos.mp (show 0 < #left by omega)
  have hR := card_pos.mp (show 0 < #right by omega)
  have hAll := reciprocal_windows_union hTriangle hL hR hCross
  have hWinBoundary : Disjoint window (left ∪ right) := by
    refine disjoint_left.mpr fun vertex hw hb => ?_
    have hOut : vertex ∈ univ \ (left ∪ right) := by
      rw [← hAll]
      exact mem_union_left _ hw
    exact (mem_sdiff.mp hOut).2 hb
  have hLeftRight : Disjoint left right := disjoint_left.mpr fun vertex hl hr =>
    (hCross vertex hl vertex hr).ne rfl
  have hCount := card_sdiff_of_subset (show window ∪ (left ∪ right) ⊆ univ from subset_univ _)
  rw [card_union_of_disjoint hWinBoundary, card_union_of_disjoint hLeftRight, card_univ, hOrder] at hCount
  have hBalance := rootsWindow_degree_sum_of_regular hTriangle hL hR hCross hRegular (hLeft.trans hRight.symm)
  change #window = 22 at hWindow
  dsimp only at hBalance ⊢
  change 2 * #(G.induce (window : Set V)).edgeFinset + 9 * #(univ \ (window ∪ (left ∪ right))) =
    2 * #(G.induce (↑(univ \ (window ∪ (left ∪ right))) : Set V)).edgeFinset + 9 * #window at hBalance
  change #(G.induce (↑(univ \ (window ∪ (left ∪ right))) : Set V)).edgeFinset + 45 =
    #(G.induce (window : Set V)).edgeFinset
  omega

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

/-- Inclusion–exclusion for the closed neighbourhood of three independent roots. -/
theorem rootsWindow_triple_count {first second third : V}
    (hFirstSecond : first ≠ second) (hFirstThird : first ≠ third) (hSecondThird : second ≠ third)
    (hNoFirstSecond : ¬G.Adj first second) (hNoFirstThird : ¬G.Adj first third)
    (hNoSecondThird : ¬G.Adj second third) :
    #(rootsWindow G {first, second, third}) + 3 + G.degree first + G.degree second +
        G.degree third + #((G.neighborFinset first ∩ G.neighborFinset second) ∩
          G.neighborFinset third) =
      Fintype.card V + #(G.neighborFinset first ∩ G.neighborFinset second) +
        #(G.neighborFinset first ∩ G.neighborFinset third) +
        #(G.neighborFinset second ∩ G.neighborFinset third) := by
  have hNoSecondFirst : ¬G.Adj second first := fun hAdj => hNoFirstSecond hAdj.symm
  have hNoThirdFirst : ¬G.Adj third first := fun hAdj => hNoFirstThird hAdj.symm
  have hNoThirdSecond : ¬G.Adj third second := fun hAdj => hNoSecondThird hAdj.symm
  have hRoots : #({first, second, third} : Finset V) = 3 := by
    simp [hFirstSecond, hFirstThird, hSecondThird]
  have hDisjoint : Disjoint ({first, second, third} : Finset V)
      (G.neighborFinset first ∪ (G.neighborFinset second ∪ G.neighborFinset third)) := by
    refine disjoint_left.mpr ?_
    intro vertex hRoot hNbr
    simp only [mem_insert, mem_singleton] at hRoot
    rcases hRoot with rfl | rfl | rfl <;>
      simp [hNoFirstSecond, hNoFirstThird, hNoSecondThird,
        hNoSecondFirst, hNoThirdFirst, hNoThirdSecond] at hNbr
  have hPair := card_union_add_card_inter (G.neighborFinset second) (G.neighborFinset third)
  have hUnion := card_union_add_card_inter (G.neighborFinset first)
    (G.neighborFinset second ∪ G.neighborFinset third)
  rw [inter_union_distrib_left] at hUnion
  have hCross := card_union_add_card_inter (G.neighborFinset first ∩ G.neighborFinset second)
    (G.neighborFinset first ∩ G.neighborFinset third)
  have hInter : (G.neighborFinset first ∩ G.neighborFinset second) ∩
      (G.neighborFinset first ∩ G.neighborFinset third) =
      (G.neighborFinset first ∩ G.neighborFinset second) ∩ G.neighborFinset third := by
    ext vertex
    simp only [mem_inter]
    tauto
  rw [hInter] at hCross
  simp only [card_neighborFinset_eq_degree] at hPair hUnion
  let near := G.neighborFinset first ∪ (G.neighborFinset second ∪ G.neighborFinset third)
  have hCount := card_sdiff_add_card_eq_card (subset_univ ({first, second, third} ∪ near))
  rw [card_union_of_disjoint hDisjoint, hRoots, card_univ] at hCount
  rw [rootsWindow, biUnion_insert, biUnion_insert, singleton_biUnion]
  dsimp only [near] at hCount
  omega

/-- With degree nine and the cap-five mark, order 22 is the extreme, and an
external order-20 bound forces five triple neighbours if all codegrees are five. -/
theorem rootsWindow_triple_cap_five {first second third : V} {opposite : Finset V}
    (hOrder : Fintype.card V = 40)
    (hFirstSecond : first ≠ second) (hFirstThird : first ≠ third) (hSecondThird : second ≠ third)
    (hNoFirstSecond : ¬G.Adj first second) (hNoFirstThird : ¬G.Adj first third)
    (hNoSecondThird : ¬G.Adj second third)
    (hFirst : G.degree first = 9) (hSecond : G.degree second = 9) (hThird : G.degree third = 9)
    (hOpposite : #opposite = 3)
    (hCross : ∀ vertex ∈ opposite, G.Adj first vertex ∧ G.Adj second vertex ∧ G.Adj third vertex) :
    let window := #(rootsWindow G {first, second, third})
    let firstSecond := #(G.neighborFinset first ∩ G.neighborFinset second)
    let firstThird := #(G.neighborFinset first ∩ G.neighborFinset third)
    let secondThird := #(G.neighborFinset second ∩ G.neighborFinset third)
    let triple := #((G.neighborFinset first ∩ G.neighborFinset second) ∩ G.neighborFinset third)
    firstSecond ≤ 5 → firstThird ≤ 5 → secondThird ≤ 5 →
      window = 10 + firstSecond + firstThird + secondThird - triple ∧ window ≤ 22 ∧
        (window = 22 ↔ firstSecond = 5 ∧ firstThird = 5 ∧ secondThird = 5 ∧ triple = 3) ∧
        (window ≤ 20 → firstSecond = 5 → firstThird = 5 → secondThird = 5 →
          window = 20 ∧ triple = 5) := by
  dsimp only
  intro hCapFirstSecond hCapFirstThird hCapSecondThird
  have hCount := rootsWindow_triple_count hFirstSecond hFirstThird hSecondThird
    hNoFirstSecond hNoFirstThird hNoSecondThird
  rw [hOrder, hFirst, hSecond, hThird] at hCount
  have hTripleLower : 3 ≤ #((G.neighborFinset first ∩ G.neighborFinset second) ∩
      G.neighborFinset third) := by
    rw [← hOpposite]
    apply card_le_card
    intro vertex hVertex
    obtain ⟨hAdjFirst, hAdjSecond, hAdjThird⟩ := hCross vertex hVertex
    simp [hAdjFirst, hAdjSecond, hAdjThird]
  have hTripleUpper := card_le_card (inter_subset_left :
    (G.neighborFinset first ∩ G.neighborFinset second) ∩ G.neighborFinset third ⊆
      G.neighborFinset first ∩ G.neighborFinset second)
  exact ⟨by omega, by omega, by omega, by omega⟩

end R310
