import R310.Local
import R310.MinDegree

namespace R310

open Finset SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]
  {G : SimpleGraph V} [DecidableRel G.Adj]

/-- Degree in the center-deleted window depends on how many support vertices
the retained anchor shares with the center, not on its role in the upper mark. -/
theorem strip_window_anchor_degree {center : V} (anchor : (outside G center : Set V))
    (hits : ℕ) (hDegree : G.degree anchor = 7 + hits)
    (hHits : nbrIn G center anchor = hits) : (delNbhd G center).degree anchor = 7 := by
  have hSplit := degree_eq_degree_delNbhd_add (G := G) center anchor
  omega

/-- A unique double witness stays unique after deleting a third independent
anchor, provided the witness is not attached to the deleted anchor. -/
theorem strip_window_unique_common {center : V}
    (first second : (outside G center : Set V))
    (hCommon : ∃! vertex, G.Adj first vertex ∧ G.Adj second vertex)
    (hNoTriple : ∀ vertex, G.Adj first vertex → G.Adj second vertex → ¬ G.Adj center vertex) :
    ∃! vertex, (delNbhd G center).Adj first vertex ∧ (delNbhd G center).Adj second vertex := by
  obtain ⟨witness, ⟨hFirst, hSecond⟩, hUnique⟩ := hCommon
  have hOutside : witness ∈ outside G center := mem_outside.mpr ⟨by
    rintro rfl
    exact (mem_outside.mp (mem_coe.mp first.2)).2 hFirst.symm,
    hNoTriple witness hFirst hSecond⟩
  refine ⟨⟨witness, hOutside⟩, ⟨hFirst, hSecond⟩, ?_⟩
  intro other hOther
  exact Subtype.ext (hUnique other hOther)

/-- The lower 33-vertex residue, not its two-edge augmentation, supplies the
order-26 `(3,8)` window at the six-neighbor path center. -/
theorem strip_window_order_alpha (hTriangle : G.CliqueFree 3) (hOrder : Fintype.card V = 33)
    (hAlpha : G.indepNum ≤ 8) (center : V) (hCenter : G.degree center = 6) :
    Fintype.card (outside G center : Set V) = 26 ∧ (delNbhd G center).CliqueFree 3 ∧
      (delNbhd G center).indepNum ≤ 7 := by
  have hCount := card_delNbhd_verts (G := G) center
  refine ⟨by omega, cliqueFree_delNbhd hTriangle center, ?_⟩
  exact indepNum_delNbhd_le (k := 9) hAlpha center

/-- At a deleted X-neighbor the degree in the lower half loses exactly its
opposite-strip support. The edge level includes both this loss and the
original deficiency from degree nine. -/
theorem strip_window_edge_level (hTriangle : G.CliqueFree 3) (center : V)
    (hCenter : G.degree center = 6) (hEdges : #G.edgeFinset = 120)
    (originalDegree oppositeSupport : V → ℕ)
    (hDegree : ∀ vertex ∈ G.neighborFinset center,
      G.degree vertex + oppositeSupport vertex = originalDegree vertex)
    (hBound : ∀ vertex ∈ G.neighborFinset center, originalDegree vertex ≤ 9)
    (hSupport : ∀ vertex ∈ G.neighborFinset center, 1 ≤ oppositeSupport vertex) :
    #(delNbhd G center).edgeFinset = 72 +
      (∑ vertex ∈ G.neighborFinset center, (oppositeSupport vertex - 1)) +
      ∑ vertex ∈ G.neighborFinset center, (9 - originalDegree vertex) := by
  have hSum : (∑ vertex ∈ G.neighborFinset center,
        (G.degree vertex + (oppositeSupport vertex - 1) + (9 - originalDegree vertex))) =
      ∑ _vertex ∈ G.neighborFinset center, 8 := by
    refine sum_congr rfl ?_
    intro vertex hVertex
    have := hDegree vertex hVertex
    have := hBound vertex hVertex
    have := hSupport vertex hVertex
    omega
  simp only [sum_add_distrib, sum_const, card_neighborFinset_eq_degree, smul_eq_mul, hCenter] at hSum
  have hEdgeCount := card_edgeFinset_delNbhd_add_sum_degree hTriangle center
  omega

/-- A support cap of `originalDegree - 6` bounds the window by 84 edges.
Each deleted vertex already known to have original degree nine improves
the cap by one, in particular the two deleted doubles if no degree eight
occurs in `X`. -/
theorem strip_window_edge_cap (hTriangle : G.CliqueFree 3) (center : V)
    (hCenter : G.degree center = 6) (hEdges : #G.edgeFinset = 120)
    (originalDegree oppositeSupport : V → ℕ) (knownNine : Finset V)
    (hNineSub : knownNine ⊆ G.neighborFinset center)
    (hNine : ∀ vertex ∈ knownNine, originalDegree vertex = 9)
    (hDegree : ∀ vertex ∈ G.neighborFinset center,
      G.degree vertex + oppositeSupport vertex = originalDegree vertex)
    (hBound : ∀ vertex ∈ G.neighborFinset center, originalDegree vertex ≤ 9)
    (hNonempty : ∀ vertex ∈ G.neighborFinset center, 1 ≤ oppositeSupport vertex)
    (hDouble : ∀ vertex ∈ G.neighborFinset center, oppositeSupport vertex ≤ 2)
    (hCap : ∀ vertex ∈ G.neighborFinset center, 6 + oppositeSupport vertex ≤ originalDegree vertex) :
    #(delNbhd G center).edgeFinset + #knownNine ≤ 84 := by
  classical
  have hSum : (∑ vertex ∈ G.neighborFinset center,
      (oppositeSupport vertex - 1 + (9 - originalDegree vertex) +
        (if vertex ∈ knownNine then 1 else 0))) ≤ ∑ _vertex ∈ G.neighborFinset center, 2 := by
    apply sum_le_sum
    intro vertex hVertex
    have := hBound vertex hVertex
    have := hNonempty vertex hVertex
    have := hDouble vertex hVertex
    have := hCap vertex hVertex
    split
    · have := hNine vertex ‹vertex ∈ knownNine›
      omega
    · omega
  have hCount : (∑ vertex ∈ G.neighborFinset center, if vertex ∈ knownNine then (1 : ℕ) else 0) =
      #knownNine := (card_eq_sum_ite hNineSub).symm
  simp only [sum_add_distrib, hCount, sum_const, card_neighborFinset_eq_degree,
    smul_eq_mul, hCenter] at hSum
  have hLevel := strip_window_edge_level hTriangle center hCenter hEdges originalDegree oppositeSupport
    hDegree hBound hNonempty
  omega

end R310
