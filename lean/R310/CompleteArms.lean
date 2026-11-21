import R310.PathWindow

namespace R310

open Finset SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

/-- A vertex outside an independent set of maximum size must hit it. -/
theorem exists_adj_mem_of_indepNum_le_card {vertex : V} {base : Finset V}
    (hIndep : G.IsIndepSet (base : Set V)) (hMax : G.indepNum ≤ #base)
    (hOutside : vertex ∉ base) : ∃ other ∈ base, G.Adj vertex other := by
  by_contra hNone
  have hAvoid : ∀ other ∈ base, ¬ G.Adj vertex other := fun other hMem hAdj =>
    hNone ⟨other, hMem, hAdj⟩
  have hInsert : G.IsIndepSet ((insert vertex base : Finset V) : Set V) := by
    rw [coe_insert, isIndepSet_iff, Set.pairwise_insert]
    exact ⟨hIndep, fun other hMem _ => ⟨hAvoid other hMem, fun hAdj => hAvoid other hMem hAdj.symm⟩⟩
  have hCard := hInsert.card_le_indepNum
  rw [card_insert_of_notMem hOutside] at hCard
  omega

/-- With both arms complete, an exterior vertex that avoids the triple
intersection avoids both wings. The two hit arguments use maximum
independent neighborhoods; maximal triangle-freeness is unnecessary. -/
theorem complete_arms_avoid_wings {first middle last vertex : V}
    {triple leftWing rightWing firstSide lastSide middleOnly : Finset V}
    (hTriangle : G.CliqueFree 3)
    (hFirst : G.neighborFinset first = triple ∪ leftWing ∪ firstSide)
    (hMiddle : G.neighborFinset middle = triple ∪ firstSide ∪ lastSide ∪ middleOnly)
    (hLast : G.neighborFinset last = triple ∪ rightWing ∪ lastSide)
    (hFirstMax : G.indepNum ≤ G.degree first) (hMiddleMax : G.indepNum ≤ G.degree middle)
    (hLastMax : G.indepNum ≤ G.degree last)
    (hFirstOut : vertex ∉ G.neighborFinset first) (hMiddleOut : vertex ∉ G.neighborFinset middle)
    (hLastOut : vertex ∉ G.neighborFinset last)
    (hLeftComplete : ∀ wing ∈ leftWing, ∀ side ∈ lastSide ∪ middleOnly, G.Adj wing side)
    (hRightComplete : ∀ wing ∈ rightWing, ∀ side ∈ firstSide ∪ middleOnly, G.Adj wing side)
    (hAvoid : ∀ boundary ∈ triple, ¬ G.Adj vertex boundary) :
    ∀ wing ∈ leftWing ∪ rightWing, ¬ G.Adj vertex wing := by
  have hHit {root : V} (hMax : G.indepNum ≤ G.degree root) (hOut : vertex ∉ G.neighborFinset root) :
      ∃ other ∈ G.neighborFinset root, G.Adj vertex other :=
    exists_adj_mem_of_indepNum_le_card (isIndepSet_neighborFinset hTriangle root)
      (by simpa only [card_neighborFinset_eq_degree] using hMax) hOut
  have hLeftImp (hLeft : ∃ wing ∈ leftWing, G.Adj vertex wing) :
      (∃ wing ∈ rightWing, G.Adj vertex wing) ∧
      (∀ side ∈ lastSide ∪ middleOnly, ¬ G.Adj vertex side) := by
    obtain ⟨wing, hWing, hAdj⟩ := hLeft
    have hNo : ∀ side ∈ lastSide ∪ middleOnly, ¬ G.Adj vertex side := by
      intro side hSide hEdge
      exact hTriangle {vertex, wing, side}
        (is3Clique_triple_iff.mpr ⟨hAdj, hEdge, hLeftComplete wing hWing side hSide⟩)
    obtain ⟨other, hOther, hEdge⟩ := hHit hLastMax hLastOut
    rw [hLast, mem_union, mem_union] at hOther
    rcases hOther with (hOther | hOther) | hOther
    · exact (hAvoid other hOther hEdge).elim
    · exact ⟨⟨other, hOther, hEdge⟩, hNo⟩
    · exact (hNo other (mem_union_left _ hOther) hEdge).elim
  have hRightImp (hRight : ∃ wing ∈ rightWing, G.Adj vertex wing) :
      (∃ wing ∈ leftWing, G.Adj vertex wing) ∧
      (∀ side ∈ firstSide ∪ middleOnly, ¬ G.Adj vertex side) := by
    obtain ⟨wing, hWing, hAdj⟩ := hRight
    have hNo : ∀ side ∈ firstSide ∪ middleOnly, ¬ G.Adj vertex side := by
      intro side hSide hEdge
      exact hTriangle {vertex, wing, side}
        (is3Clique_triple_iff.mpr ⟨hAdj, hEdge, hRightComplete wing hWing side hSide⟩)
    obtain ⟨other, hOther, hEdge⟩ := hHit hFirstMax hFirstOut
    rw [hFirst, mem_union, mem_union] at hOther
    rcases hOther with (hOther | hOther) | hOther
    · exact (hAvoid other hOther hEdge).elim
    · exact ⟨⟨other, hOther, hEdge⟩, hNo⟩
    · exact (hNo other (mem_union_left _ hOther) hEdge).elim
  intro wing hWing hEdge
  have hBoth : (∃ wing ∈ leftWing, G.Adj vertex wing) ∧ (∃ wing ∈ rightWing, G.Adj vertex wing) := by
    rcases mem_union.mp hWing with hLeft | hRight
    · exact ⟨⟨wing, hLeft, hEdge⟩, (hLeftImp ⟨wing, hLeft, hEdge⟩).1⟩
    · exact ⟨(hRightImp ⟨wing, hRight, hEdge⟩).1, ⟨wing, hRight, hEdge⟩⟩
  obtain ⟨other, hOther, hHitMiddle⟩ := hHit hMiddleMax hMiddleOut
  rw [hMiddle, mem_union, mem_union, mem_union] at hOther
  rcases hOther with ((hOther | hOther) | hOther) | hOther
  · exact hAvoid other hOther hHitMiddle
  · exact (hRightImp hBoth.2).2 other (mem_union_left _ hOther) hHitMiddle
  · exact (hLeftImp hBoth.1).2 other (mem_union_left _ hOther) hHitMiddle
  · exact (hLeftImp hBoth.1).2 other (mem_union_right _ hOther) hHitMiddle

end R310

namespace R310

open Finset

/-- Counting a singleton support once more turns every nonempty support into
two units plus its excess over two. In the complete-wing application the
singleton count is bounded by twice the size of the common neighborhood. -/
theorem support_excess_budget {V : Type*} (exterior : Finset V) (support : V → ℕ)
    (hPositive : ∀ vertex ∈ exterior, 1 ≤ support vertex) :
    2 * #exterior + (∑ vertex ∈ exterior, (support vertex - 2)) =
      (∑ vertex ∈ exterior, support vertex) + #{vertex ∈ exterior | support vertex = 1} := by
  have hIdentity : ∑ vertex ∈ exterior, ((2 : ℕ) + (support vertex - 2)) =
      ∑ vertex ∈ exterior, (support vertex + if support vertex = 1 then 1 else 0) := by
    refine sum_congr rfl fun vertex hVertex => ?_
    have hSize := hPositive vertex hVertex
    split_ifs <;> omega
  simpa only [sum_add_distrib, sum_const, smul_eq_mul, mul_comm #exterior 2, card_filter] using hIdentity

/-- The arithmetic step for a full-wing order-26 residue at a codegree-six pair. -/
theorem complete_wings_excess_le_two {V : Type*} (exterior : Finset V) (support : V → ℕ)
    (hExterior : #exterior = 26) (hPositive : ∀ vertex ∈ exterior, 1 ≤ support vertex)
    (hSum : ∑ vertex ∈ exterior, support vertex = 42)
    (hSingletons : #{vertex ∈ exterior | support vertex = 1} ≤ 12) :
    (∑ vertex ∈ exterior, (support vertex - 2)) ≤ 2 ∧
    #{vertex ∈ exterior | support vertex = 1} = 10 + (∑ vertex ∈ exterior, (support vertex - 2)) := by
  have hBudget := support_excess_budget exterior support hPositive
  rw [hExterior, hSum] at hBudget
  omega

end R310
