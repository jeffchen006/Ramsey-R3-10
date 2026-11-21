import R310.MTF

open Finset SimpleGraph

namespace R310

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

/-- The neighbours of a root that remain in an induced vertex set. -/
def windowNeighbors (G : SimpleGraph V) [DecidableRel G.Adj]
    (middle : Finset V) (root : V) : Finset V := middle ∩ G.neighborFinset root

/-- Delete an endpoint and its neighbours from a window. -/
def deleteWindowRoot (G : SimpleGraph V) [DecidableRel G.Adj]
    (middle : Finset V) (root : V) : Finset V :=
  middle \ insert root (windowNeighbors G middle root)

/-- Opposite endpoints that are adjacent give two windows with independent wings.
The hypotheses are local to the window; no maximality or global codegree cap is needed. -/
theorem adjacent_window_overlap (middle : Finset V) {first last : V}
    (hTriangle : G.CliqueFree 3) (hEdge : G.Adj first last)
    (hFirst : first ∈ middle) (hLast : last ∈ middle) :
    let left := windowNeighbors G middle last
    let right := windowNeighbors G middle first
    let wingLeft := left.erase first
    let wingRight := right.erase last
    let overlap := middle \ (left ∪ right)
    deleteWindowRoot G middle first = overlap ∪ wingLeft ∧
    deleteWindowRoot G middle last = overlap ∪ wingRight ∧
    Disjoint wingLeft wingRight ∧
    G.IsIndepSet (wingLeft : Set V) ∧ G.IsIndepSet (wingRight : Set V) ∧
    #wingLeft + 1 = #left ∧ #wingRight + 1 = #right ∧
    #overlap + #left + #right = #middle := by
  dsimp only
  let left := windowNeighbors G middle last
  let right := windowNeighbors G middle first
  have hInLeft : first ∈ left := mem_inter.2 ⟨hFirst, (mem_neighborFinset _ _ _).2 hEdge.symm⟩
  have hInRight : last ∈ right := mem_inter.2 ⟨hLast, (mem_neighborFinset _ _ _).2 hEdge⟩
  have hLeftSub : left ⊆ middle := inter_subset_left
  have hRightSub : right ⊆ middle := inter_subset_left
  have hDisjoint : Disjoint left right := by
    refine Finset.disjoint_left.2 fun vertex hLeft hRight => ?_
    exact hTriangle {first, last, vertex} (is3Clique_triple_iff.2
      ⟨hEdge, (mem_neighborFinset _ _ _).1 (mem_inter.1 hRight).2,
        (mem_neighborFinset _ _ _).1 (mem_inter.1 hLeft).2⟩)
  have deleteEq (root : V) {near far : Finset V} (hRoot : root ∈ far)
      (hFarSub : far ⊆ middle) (hDisj : Disjoint far near) :
      middle \ insert root near = (middle \ (far ∪ near)) ∪ far.erase root := by
    ext vertex
    simp only [mem_sdiff, mem_insert, mem_union, mem_erase]
    have hNotNear : vertex ∈ far → vertex ∉ near := fun hv => Finset.disjoint_left.1 hDisj hv
    have hMem : vertex = root → vertex ∈ far := fun heq => heq.symm ▸ hRoot
    have hMiddle : vertex ∈ far → vertex ∈ middle := fun hv => hFarSub hv
    tauto
  have indepWing (root other : V) :
      G.IsIndepSet ((windowNeighbors G middle root).erase other : Set V) := by
    refine Set.Pairwise.mono ?_ (isIndepSet_neighborFinset hTriangle root)
    intro vertex hv
    exact (mem_inter.1 (mem_erase.1 hv).2).2
  refine ⟨deleteEq first hInLeft hLeftSub hDisjoint, ?_,
    hDisjoint.mono (erase_subset _ _) (erase_subset _ _),
    indepWing last first, indepWing first last,
    card_erase_add_one hInLeft, card_erase_add_one hInRight, ?_⟩
  · change middle \ insert last left = (middle \ (left ∪ right)) ∪ right.erase last
    simpa only [union_comm right left] using deleteEq last hInRight hRightSub hDisjoint.symm
  · have hCounts := card_sdiff_add_card_eq_card (union_subset hLeftSub hRightSub)
    rw [card_union_of_disjoint hDisjoint] at hCounts
    change #(middle \ (left ∪ right)) + #left + #right = #middle
    omega

/-- Removing successive roots commutes: two pair windows have as intersection
the triple window, and their union deletes from the middle window only what
both exterior roots delete. -/
theorem successive_window_inter_union (middle : Finset V) (first last : V) :
    let removeFirst := insert first (windowNeighbors G middle first)
    let removeLast := insert last (windowNeighbors G middle last)
    deleteWindowRoot G middle first ∩ deleteWindowRoot G middle last =
      middle \ (removeFirst ∪ removeLast) ∧
    deleteWindowRoot G middle first ∪ deleteWindowRoot G middle last =
      middle \ (removeFirst ∩ removeLast) := by
  constructor <;> ext vertex <;> simp only [deleteWindowRoot, mem_inter, mem_union, mem_sdiff] <;> tauto

/-- In the four-root window, two opposing wing vertices are adjacent exactly when
their overlap masks are disjoint. The four-block decomposition is used only via
`hCover`: any neighbour of either middle root also sees an endpoint. -/
theorem adjacent_window_cross_iff_disjoint (hMTF : IsMTF G) {first midLeft midRight last y z : V}
    (hSpan : G.Adj first last)
    (hCover : ∀ vertex, G.Adj midLeft vertex ∨ G.Adj midRight vertex →
      G.Adj first vertex ∨ G.Adj last vertex) :
    let middle := outside G midLeft ∩ outside G midRight
    let overlap := middle ∩ (outside G first ∩ outside G last)
    y ∈ (windowNeighbors G middle last).erase first →
    z ∈ (windowNeighbors G middle first).erase last →
    (G.Adj y z ↔ Disjoint (windowNeighbors G overlap y) (windowNeighbors G overlap z)) := by
  dsimp only
  intro hy hz
  have hyLast := (mem_neighborFinset _ _ _).1 (mem_inter.1 (mem_erase.1 hy).2).2
  have hzFirst := (mem_neighborFinset _ _ _).1 (mem_inter.1 (mem_erase.1 hz).2).2
  have noTriangle {a b c : V} (hab : G.Adj a b) (hac : G.Adj a c) (hbc : G.Adj b c) :
      False := hMTF.1 {a, b, c} (is3Clique_triple_iff.2 ⟨hab, hac, hbc⟩)
  have hyz : y ≠ z := fun heq => noTriangle hSpan hzFirst (heq ▸ hyLast)
  constructor
  · intro hedge
    exact Finset.disjoint_left.2 fun vertex hLeft hRight =>
      noTriangle hedge ((mem_neighborFinset _ _ _).1 (mem_inter.1 hLeft).2)
        ((mem_neighborFinset _ _ _).1 (mem_inter.1 hRight).2)
  · intro hDisjoint
    by_contra hNoEdge
    obtain ⟨vertex, hyVertex, hzVertex⟩ := hMTF.exists_common hyz hNoEdge
    have hNoFirst : ¬ G.Adj first vertex :=
      fun h => noTriangle hzFirst h hzVertex
    have hNoLast : ¬ G.Adj last vertex :=
      fun h => noTriangle hyLast h hyVertex
    have hNoMid : ¬ (G.Adj midLeft vertex ∨ G.Adj midRight vertex) :=
      fun h => (hCover vertex h).elim hNoFirst hNoLast
    have hyMiddle := mem_inter.1 (mem_inter.1 (mem_erase.1 hy).2).1
    have hmLeft : vertex ≠ midLeft := fun heq => (mem_outside.1 hyMiddle.1).2 (heq ▸ hyVertex.symm)
    have hmRight : vertex ≠ midRight := fun heq => (mem_outside.1 hyMiddle.2).2 (heq ▸ hyVertex.symm)
    have hFirst : vertex ≠ first := fun heq => hNoLast (heq.symm ▸ hSpan.symm)
    have hLast : vertex ≠ last := fun heq => hNoFirst (heq.symm ▸ hSpan)
    have hx : vertex ∈ (outside G midLeft ∩ outside G midRight) ∩ (outside G first ∩ outside G last) :=
      mem_inter.2 ⟨mem_inter.2 ⟨mem_outside.2 ⟨hmLeft, fun h => hNoMid (.inl h)⟩,
          mem_outside.2 ⟨hmRight, fun h => hNoMid (.inr h)⟩⟩,
        mem_inter.2 ⟨mem_outside.2 ⟨hFirst, hNoFirst⟩, mem_outside.2 ⟨hLast, hNoLast⟩⟩⟩
    exact Finset.disjoint_left.1 hDisjoint (mem_inter.2 ⟨hx, (mem_neighborFinset _ _ _).2 hyVertex⟩)
      (mem_inter.2 ⟨hx, (mem_neighborFinset _ _ _).2 hzVertex⟩)

/-- Vertices within a group that have no neighbour in the projected set. -/
def unhitIn (G : SimpleGraph V) [DecidableRel G.Adj] (group projected : Finset V) : Finset V :=
  group.filter fun vertex => Disjoint (G.neighborFinset vertex) projected

/-- The one-side bound using an independent base and the available group vertices.
Edges from the group to the base are tested only on the projection. -/
theorem card_add_unhitIn_le_indepNum {base group projected : Finset V}
    (hBase : G.IsIndepSet (base : Set V)) (hGroup : G.IsIndepSet (group : Set V))
    (hDisj : Disjoint base group)
    (hProj : ∀ vertex ∈ group, ∀ other ∈ base, G.Adj vertex other → other ∈ projected) :
    #base + #(unhitIn G group projected) ≤ G.indepNum := by
  have hSub : unhitIn G group projected ⊆ group := filter_subset _ _
  have hUnion : G.IsIndepSet ((base ∪ unhitIn G group projected : Finset V) : Set V) := by
    rw [coe_union, isIndepSet_iff, Set.pairwise_union]
    refine ⟨hBase, Set.Pairwise.mono (by simpa only [coe_subset] using hSub) hGroup, ?_⟩
    intro other hOther vertex hv _
    have hAvail := mem_filter.1 (show vertex ∈ unhitIn G group projected from hv)
    have hNo : ¬ G.Adj vertex other := fun h => Finset.disjoint_left.1 hAvail.2
      ((mem_neighborFinset _ _ _).2 h) (hProj vertex hAvail.1 other hOther h)
    exact ⟨fun h => hNo h.symm, hNo⟩
  simpa only [card_union_of_disjoint (hDisj.mono (Subset.refl _) hSub)] using hUnion.card_le_indepNum

/-- The strengthened outer-block row: an extra root avoids the independent base
and this group, even if it has neighbours in another boundary block. -/
theorem card_add_unhitIn_add_one_le_indepNum {base group projected : Finset V} {root : V}
    (hBase : G.IsIndepSet (base : Set V)) (hGroup : G.IsIndepSet (group : Set V))
    (hDisj : Disjoint base group) (hRootBase : root ∉ base) (hRootGroup : root ∉ group)
    (hAvoidBase : ∀ vertex ∈ base, ¬ G.Adj root vertex)
    (hAvoidGroup : ∀ vertex ∈ group, ¬ G.Adj root vertex)
    (hProj : ∀ vertex ∈ group, ∀ other ∈ base, G.Adj vertex other → other ∈ projected) :
    #base + #(unhitIn G group projected) + 1 ≤ G.indepNum := by
  have hBigger : G.IsIndepSet ((insert root base : Finset V) : Set V) := by
    rw [coe_insert, isIndepSet_iff, Set.pairwise_insert]
    exact ⟨hBase, fun vertex hv _ => ⟨hAvoidBase vertex hv, fun h => hAvoidBase vertex hv h.symm⟩⟩
  have hSeparate : Disjoint (insert root base) group := disjoint_insert_left.2 ⟨hRootGroup, hDisj⟩
  have hKeep : ∀ vertex ∈ group, ∀ other ∈ insert root base, G.Adj vertex other → other ∈ projected := by
    intro vertex hv other hOther hEdge
    rcases mem_insert.1 hOther with rfl | hOther
    · exact (hAvoidGroup vertex hv hEdge.symm).elim
    · exact hProj vertex hv other hOther hEdge
  have h := card_add_unhitIn_le_indepNum hBigger hGroup hSeparate hKeep
  rw [card_insert_of_notMem hRootBase] at h
  omega

end R310
