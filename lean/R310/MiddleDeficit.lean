import R310.PoleMultiplicity

namespace R310

open Finset SimpleGraph
open scoped BigOperators

theorem exists_one_above_floor {Vertex : Type*} [DecidableEq Vertex] {sites : Finset Vertex}
    {value : Vertex → ℕ} {floor : ℕ} (hFloor : ∀ site ∈ sites, floor ≤ value site)
    (hMass : ∑ site ∈ sites, value site = #sites * floor + 1) :
    ∃ exceptional ∈ sites, value exceptional = floor + 1 ∧
      ∀ site ∈ sites, site ≠ exceptional → value site = floor := by
  let excess := fun site => value site - floor
  have hTotal : ∑ site ∈ sites, excess site = 1 := by
    calc
      (∑ site ∈ sites, excess site) = (∑ site ∈ sites, value site) - ∑ _site ∈ sites, floor :=
        sum_tsub_distrib sites hFloor
      _ = 1 := by simp [hMass]
  obtain ⟨exceptional, hMem, hNonzero⟩ := exists_ne_zero_of_sum_ne_zero (by rw [hTotal]; decide)
  have hSplit := sum_erase_add sites excess hMem
  rw [hTotal] at hSplit
  have hUnit : excess exceptional = 1 := by omega
  have hZero : ∑ site ∈ sites.erase exceptional, excess site = 0 := by omega
  refine ⟨exceptional, hMem, ?_, ?_⟩
  · have := hFloor exceptional hMem
    dsimp [excess] at hUnit
    omega
  · intro site hSite hNe
    have hBound := single_le_sum (f := excess) (s := sites.erase exceptional)
      (fun other _ => Nat.zero_le (excess other)) (mem_erase.mpr ⟨hNe, hSite⟩)
    rw [hZero] at hBound
    have := hFloor site hSite
    dsimp [excess] at hBound
    omega

structure SingleDeficitContacts {Vertex : Type*} (poles untouched : Finset Vertex)
    (leftCount rightCount outsideCount columnCount : Vertex → ℕ) : Prop where
  pole : ∃ exceptional ∈ poles, outsideCount exceptional = 5 ∧
    ((leftCount exceptional = 1 ∧ rightCount exceptional = 2) ∨
      (leftCount exceptional = 2 ∧ rightCount exceptional = 1)) ∧
    ∀ site ∈ poles, site ≠ exceptional →
      leftCount site = 2 ∧ rightCount site = 2 ∧ outsideCount site = 4
  column : ∃ exceptional ∈ untouched, columnCount exceptional = 3 ∧
    ∀ site ∈ untouched, site ≠ exceptional → columnCount site = 2

theorem single_deficit_contacts {Vertex : Type*} [DecidableEq Vertex] {poles untouched : Finset Vertex}
    {leftCount rightCount outsideCount columnCount : Vertex → ℕ}
    (hRow : ∀ site ∈ poles, leftCount site + rightCount site + outsideCount site = 8)
    (hWings : ∀ site ∈ poles, leftCount site ≤ 2 ∧ rightCount site ≤ 2)
    (hOutside : ∑ site ∈ poles, outsideCount site = #poles * 4 + 1)
    (hColumn : ∀ site ∈ untouched, 2 ≤ columnCount site)
    (hMass : ∑ site ∈ untouched, columnCount site = #untouched * 2 + 1) :
    SingleDeficitContacts poles untouched leftCount rightCount outsideCount columnCount := by
  have hOutsideFloor : ∀ site ∈ poles, 4 ≤ outsideCount site := by
    intro site hSite
    obtain ⟨hLeft, hRight⟩ := hWings site hSite
    have := hRow site hSite
    omega
  obtain ⟨exceptional, hMem, hFive, hRest⟩ := exists_one_above_floor hOutsideFloor hOutside
  refine ⟨⟨exceptional, hMem, hFive, ?_, ?_⟩, exists_one_above_floor hColumn hMass⟩
  · obtain ⟨hLeftHi, hRightHi⟩ := hWings exceptional hMem
    have := hRow exceptional hMem
    omega
  · intro site hSite hNe
    obtain ⟨hLeft, hRight⟩ := hWings site hSite
    have := hRow site hSite
    have := hRest site hSite hNe
    omega

variable {Vertex : Type*} [Fintype Vertex] [DecidableEq Vertex]
variable (graph : SimpleGraph Vertex) [DecidableRel graph.Adj]

/-- The direct local codegree hypotheses for the single-unit deficit. The tip
floor follows from the balance: it need not be assumed on this layer. -/
theorem middle_star_at_seventeen_fifteen {left right middle : Vertex}
    (balance : MiddleStarBalance graph left right middle)
    (hCap : ∀ first second, first ≠ second → ¬ graph.Adj first second →
      #(graph.neighborFinset first ∩ graph.neighborFinset second) ≤ 3)
    (hMiddle : ∀ vertex ∈ pathUntouched graph left right middle,
      2 ≤ #(graph.neighborFinset middle ∩ graph.neighborFinset vertex))
    (hPetals : starMass graph (pathWing graph left middle) (pathWing graph right middle) = 17)
    (hResidue : #((graph.induce (pathUntouched graph left right middle : Set Vertex)).edgeFinset) = 15) :
    SingleDeficitContacts (pathStar graph left right middle) (pathUntouched graph left right middle)
      (fun pole => starContacts graph pole (pathWing graph left middle))
      (fun pole => starContacts graph pole (pathWing graph right middle))
      (fun pole => starContacts graph pole (pathUntouched graph left right middle))
      (fun site => starContacts graph site (pathStar graph left right middle)) := by
  have hMass := balance.mass
  rw [hPetals, hResidue] at hMass
  refine single_deficit_contacts balance.row (balance.tipCaps graph hCap) ?_ ?_ ?_
  · change starMass graph _ _ = _
    rw [balance.poleCount]
    omega
  · intro site hSite
    simpa only [balance.middleCodegree site hSite] using hMiddle site hSite
  · change starMass graph _ _ = _
    rw [starMass_comm graph (pathUntouched graph left right middle), balance.untouchedCount]
    omega

/-- Uniqueness of the deficient pair *witnessed by* this middle (up to endpoint order).
This does not say that the middle is not a deficient endpoint. -/
def OnlyMarkedDeficiencyAt (left right middle : Vertex) : Prop :=
  ∀ first second, HasDeficientWitness graph first second middle →
    (first = left ∧ second = right) ∨ (first = right ∧ second = left)

theorem MiddleStarBalance.tipFloors {left right middle : Vertex}
    (balance : MiddleStarBalance graph left right middle)
    (hPath : HasDeficientWitness graph left right middle) (hOnly : OnlyMarkedDeficiencyAt graph left right middle) :
    ∀ pole ∈ pathStar graph left right middle,
      2 ≤ #(graph.neighborFinset pole ∩ graph.neighborFinset left) ∧
      2 ≤ #(graph.neighborFinset pole ∩ graph.neighborFinset right) := by
  intro pole hPole
  obtain ⟨hLeft, hRight, hNoLeft, hNoRight⟩ := balance.nonedges pole hPole
  have hAdj : graph.Adj pole middle := ((mem_neighborFinset _ _ _).mp
    (mem_of_mem_erase (mem_of_mem_erase hPole))).symm
  have hNotDeficient (tip : Vertex) : ¬ HasDeficientWitness graph pole tip middle := fun hDef =>
    (hOnly pole tip hDef).elim (fun h => hLeft h.1) (fun h => hRight h.1)
  exact ⟨codegree_ge_two_of_not_deficient graph hLeft hNoLeft hAdj hPath.2.2.1 (hNotDeficient left),
    codegree_ge_two_of_not_deficient graph hRight hNoRight hAdj hPath.2.2.2.1 (hNotDeficient right)⟩

/-- Pairwise nonzero multiplicity uses the witness premise, not the separate
condition that the middle is not a deficient endpoint. -/
theorem polePair_multiplicity_of_only_marked {left right middle first second : Vertex}
    (hTriangle : graph.CliqueFree 3) (hPath : HasDeficientWitness graph left right middle)
    (hCap : ∀ first second, first ≠ second → ¬ graph.Adj first second →
      #(graph.neighborFinset first ∩ graph.neighborFinset second) ≤ 3)
    (hOnly : OnlyMarkedDeficiencyAt graph left right middle)
    (hFirst : first ∈ pathStar graph left right middle)
    (hSecond : second ∈ pathStar graph left right middle) (hDistinct : first ≠ second) :
    let total := #(polePairSites graph first second middle ∩ pathWing graph left middle) +
      #(polePairSites graph first second middle ∩ pathWing graph right middle) +
      #(polePairSites graph first second middle ∩ pathUntouched graph left right middle)
    1 ≤ total ∧ total ≤ 2 := by
  have hFirstRight : first ≠ right := (mem_erase.mp hFirst).1
  have hFirstLeft : first ≠ left := (mem_erase.mp (mem_of_mem_erase hFirst)).1
  have hNo : ¬ HasDeficientWitness graph first second middle := fun hDef =>
    (hOnly first second hDef).elim (fun h => hFirstLeft h.1) (fun h => hFirstRight h.1)
  have hPair := polePair_multiplicity graph hTriangle hPath hCap hFirst hSecond hDistinct
  exact ⟨hPair.2.mpr hNo, hPair.1⟩

/-- Graph interface for the marked `(t,m)=(17,15)` layer. It does not
assert a support census, nor any relation between the two exceptional vertices. -/
theorem middle_star_at_seventeen_fifteen_of_mtf {left right middle : Vertex}
    (hOrder : Fintype.card Vertex = 40) (hRegular : ∀ vertex, graph.degree vertex = 9)
    (hMTF : IsMTF graph) (hPath : HasDeficientWitness graph left right middle)
    (hCap : ∀ first second, first ≠ second → ¬ graph.Adj first second →
      #(graph.neighborFinset first ∩ graph.neighborFinset second) ≤ 3)
    (hNoEndpoint : ∀ endpoint witness, ¬ HasDeficientWitness graph middle endpoint witness)
    (hPetals : starMass graph (pathWing graph left middle) (pathWing graph right middle) = 17)
    (hResidue : #((graph.induce (pathUntouched graph left right middle : Set Vertex)).edgeFinset) = 15) :
    MiddleStarBalance graph left right middle ∧
    SingleDeficitContacts (pathStar graph left right middle) (pathUntouched graph left right middle)
      (fun pole => starContacts graph pole (pathWing graph left middle))
      (fun pole => starContacts graph pole (pathWing graph right middle))
      (fun pole => starContacts graph pole (pathUntouched graph left right middle))
      (fun site => starContacts graph site (pathStar graph left right middle)) := by
  have balance := middle_star_balance graph hOrder hRegular hMTF.1 hPath
  exact ⟨balance, middle_star_at_seventeen_fifteen graph balance hCap
    (pathUntouched_codegree_ge_two_of_mtf graph hMTF hNoEndpoint) hPetals hResidue⟩

end R310
