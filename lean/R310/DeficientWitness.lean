import R310.Basic

namespace R310

open Finset SimpleGraph

variable {V : Type*} [DecidableEq V] {G : SimpleGraph V}

/-- A codegree-one nonedge with its unique common neighbour named. -/
def HasDeficientWitness (G : SimpleGraph V) (first second witness : V) : Prop :=
  first ≠ second ∧ ¬ G.Adj first second ∧ G.Adj first witness ∧ G.Adj second witness ∧
    ∀ other, G.Adj first other → G.Adj second other → other = witness

/-- A pair of a different witness colour misses at least one of two disjoint pairs
of the same colour. Disjointness concerns endpoints, not entire marked paths. -/
theorem deficient_other_witness_disjoint
    {leftFirst leftSecond rightFirst rightSecond first second shared other : V}
    (hDisjoint : Disjoint ({leftFirst, leftSecond} : Finset V) {rightFirst, rightSecond})
    (hLeft : HasDeficientWitness G leftFirst leftSecond shared)
    (hRight : HasDeficientWitness G rightFirst rightSecond shared)
    (hOther : HasDeficientWitness G first second other) (hDifferent : other ≠ shared) :
    Disjoint ({leftFirst, leftSecond} : Finset V) {first, second} ∨
      Disjoint ({rightFirst, rightSecond} : Finset V) {first, second} := by
  by_cases hMissesLeft : Disjoint ({leftFirst, leftSecond} : Finset V) {first, second}
  · exact Or.inl hMissesLeft
  by_cases hMissesRight : Disjoint ({rightFirst, rightSecond} : Finset V) {first, second}
  · exact Or.inr hMissesRight
  obtain ⟨leftHit, hLeftHit, hLeftPair⟩ := not_disjoint_iff.mp hMissesLeft
  obtain ⟨rightHit, hRightHit, hRightPair⟩ := not_disjoint_iff.mp hMissesRight
  have hHitsDistinct : leftHit ≠ rightHit := fun hEq =>
    disjoint_left.mp hDisjoint hLeftHit (hEq.symm ▸ hRightHit)
  have hLeftAdj : G.Adj leftHit shared := by
    simp only [mem_insert, mem_singleton] at hLeftHit
    rcases hLeftHit with rfl | rfl
    · exact hLeft.2.2.1
    · exact hLeft.2.2.2.1
  have hRightAdj : G.Adj rightHit shared := by
    simp only [mem_insert, mem_singleton] at hRightHit
    rcases hRightHit with rfl | rfl
    · exact hRight.2.2.1
    · exact hRight.2.2.2.1
  have hBoth : G.Adj first shared ∧ G.Adj second shared := by
    simp only [mem_insert, mem_singleton] at hLeftPair hRightPair
    rcases hLeftPair with rfl | rfl <;> rcases hRightPair with rfl | rfl
    · exact (hHitsDistinct rfl).elim
    · exact ⟨hLeftAdj, hRightAdj⟩
    · exact ⟨hRightAdj, hLeftAdj⟩
    · exact (hHitsDistinct rfl).elim
  exact (hDifferent (hOther.2.2.2.2 shared hBoth.1 hBoth.2).symm).elim

/-- Root-choice interface: the existence of disjoint deficient pairs and of a
different witness from the first pair suffices. Those premises are external. -/
theorem exists_disjoint_distinct_deficient_witnesses
    {leftFirst leftSecond rightFirst rightSecond first second left right other : V}
    (hDisjoint : Disjoint ({leftFirst, leftSecond} : Finset V) {rightFirst, rightSecond})
    (hLeft : HasDeficientWitness G leftFirst leftSecond left)
    (hRight : HasDeficientWitness G rightFirst rightSecond right)
    (hOther : HasDeficientWitness G first second other) (hDifferent : other ≠ left) :
    ∃ firstA secondA firstB secondB witnessA witnessB,
      HasDeficientWitness G firstA secondA witnessA ∧ HasDeficientWitness G firstB secondB witnessB ∧
        Disjoint ({firstA, secondA} : Finset V) {firstB, secondB} ∧ witnessA ≠ witnessB := by
  by_cases hEq : left = right
  · subst right
    rcases deficient_other_witness_disjoint hDisjoint hLeft hRight hOther hDifferent with hMiss | hMiss
    · exact ⟨leftFirst, leftSecond, first, second, left, other, hLeft, hOther, hMiss, hDifferent.symm⟩
    · exact ⟨rightFirst, rightSecond, first, second, left, other, hRight, hOther, hMiss, hDifferent.symm⟩
  · exact ⟨leftFirst, leftSecond, rightFirst, rightSecond, left, right, hLeft, hRight, hDisjoint, hEq⟩

end R310
