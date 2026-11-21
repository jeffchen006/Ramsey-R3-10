import R310.Basic

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

end R310
