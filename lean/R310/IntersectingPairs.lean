import Mathlib.Data.Finset.Card
import Mathlib.Data.Finset.Basic

namespace R310

open Finset

variable {V : Type*} [DecidableEq V]

private theorem exists_eq_pair_of_mem {edge : Finset V} {vertex : V}
    (hCard : #edge = 2) (hMem : vertex ∈ edge) :
    ∃ other, vertex ≠ other ∧ edge = {vertex, other} := by
  obtain ⟨first, second, hNe, rfl⟩ := card_eq_two.mp hCard
  simp only [mem_insert, mem_singleton] at hMem
  rcases hMem with rfl | rfl
  · exact ⟨second, hNe, rfl⟩
  · exact ⟨first, hNe.symm, by ext item; simp [or_comm]⟩

private theorem eq_pair_of_two_mem {edge : Finset V} {first second : V}
    (hCard : #edge = 2) (hNe : first ≠ second) (hFirst : first ∈ edge) (hSecond : second ∈ edge) :
    edge = {first, second} := by
  symm
  apply eq_of_subset_of_card_le
  · intro vertex hVertex
    simp only [mem_insert, mem_singleton] at hVertex
    rcases hVertex with rfl | rfl
    · exact hFirst
    · exact hSecond
  · rw [hCard, card_pair hNe]

/-- If a finite family of two-element sets has no two disjoint members, then it is
empty, has a common vertex, or is exactly the three edges of a triangle. -/
theorem intersecting_pairs_empty_or_star_or_triangle {family : Finset (Finset V)}
    (hSize : ∀ edge ∈ family, #edge = 2)
    (hMeet : ∀ edge ∈ family, ∀ other ∈ family, ¬ Disjoint edge other) :
    family = ∅ ∨ (∃ hub, ∀ edge ∈ family, hub ∈ edge) ∨
      ∃ pivot left right : V, pivot ≠ left ∧ pivot ≠ right ∧ left ≠ right ∧
        family = {{pivot, left}, {pivot, right}, {left, right}} := by
  by_cases hEmpty : family = ∅
  · exact Or.inl hEmpty
  right
  by_cases hHub : ∃ hub, ∀ edge ∈ family, hub ∈ edge
  · exact Or.inl hHub
  right
  have hMiss (vertex : V) : ∃ edge ∈ family, vertex ∉ edge := by
    by_contra! hEvery
    exact hHub ⟨vertex, hEvery⟩
  obtain ⟨base, hBase⟩ := nonempty_iff_ne_empty.mpr hEmpty
  obtain ⟨pivot, left, hPivotLeft, rfl⟩ := card_eq_two.mp (hSize _ hBase)
  obtain ⟨second, hSecond, hNoLeft⟩ := hMiss left
  have hPivotIn : pivot ∈ second := by
    obtain ⟨vertex, hVertexBase, hVertexSecond⟩ := not_disjoint_iff.mp (hMeet _ hBase _ hSecond)
    simp only [mem_insert, mem_singleton] at hVertexBase
    rcases hVertexBase with rfl | rfl
    · exact hVertexSecond
    · exact (hNoLeft hVertexSecond).elim
  obtain ⟨right, hPivotRight, rfl⟩ := exists_eq_pair_of_mem (hSize _ hSecond) hPivotIn
  have hLeftRight : left ≠ right := fun hEq => hNoLeft (by simp [hEq])
  obtain ⟨third, hThird, hNoPivot⟩ := hMiss pivot
  have hBeside {vertex : V} (hEdge : ({pivot, vertex} : Finset V) ∈ family) : vertex ∈ third := by
    obtain ⟨item, hItemEdge, hItemThird⟩ := not_disjoint_iff.mp (hMeet _ hEdge _ hThird)
    simp only [mem_insert, mem_singleton] at hItemEdge
    rcases hItemEdge with rfl | rfl
    · exact (hNoPivot hItemThird).elim
    · exact hItemThird
  have hThirdPair := eq_pair_of_two_mem (hSize _ hThird) hLeftRight (hBeside hBase) (hBeside hSecond)
  rw [hThirdPair] at hThird
  refine ⟨pivot, left, right, hPivotLeft, hPivotRight, hLeftRight, ?_⟩
  ext edge
  simp only [mem_insert, mem_singleton]
  constructor
  · intro hEdge
    have hEdgesMeet {first second : V} (hPair : ({first, second} : Finset V) ∈ family) :
        first ∈ edge ∨ second ∈ edge := by
      obtain ⟨vertex, hVertexPair, hVertexEdge⟩ := not_disjoint_iff.mp (hMeet _ hPair _ hEdge)
      simp only [mem_insert, mem_singleton] at hVertexPair
      rcases hVertexPair with rfl | rfl
      · exact Or.inl hVertexEdge
      · exact Or.inr hVertexEdge
    have hCard := hSize _ hEdge
    by_cases hPivot : pivot ∈ edge
    · rcases hEdgesMeet hThird with hLeft | hRight
      · exact Or.inl (eq_pair_of_two_mem hCard hPivotLeft hPivot hLeft)
      · exact Or.inr (Or.inl (eq_pair_of_two_mem hCard hPivotRight hPivot hRight))
    · exact Or.inr (Or.inr (eq_pair_of_two_mem hCard hLeftRight
        ((hEdgesMeet hBase).resolve_left hPivot) ((hEdgesMeet hSecond).resolve_left hPivot)))
  · rintro (rfl | rfl | rfl)
    · exact hBase
    · exact hSecond
    · exact hThird

end R310
