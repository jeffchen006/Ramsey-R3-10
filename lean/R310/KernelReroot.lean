import R310.Basic

open Finset

namespace R310

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- An ordered simple six-vertex path in the edge kernel on `root, pivot`.
The first vertex lies on the `root` side. -/
def KernelP6 (root pivot first second third fourth fifth sixth : V) : Prop :=
  G.Adj root first ∧ first ≠ pivot ∧ G.Adj pivot second ∧ second ≠ root ∧
  G.Adj root third ∧ third ≠ pivot ∧ G.Adj pivot fourth ∧ fourth ≠ root ∧
  G.Adj root fifth ∧ fifth ≠ pivot ∧ G.Adj pivot sixth ∧ sixth ≠ root ∧
  [first, second, third, fourth, fifth, sixth].Nodup ∧
  G.Adj first second ∧ G.Adj second third ∧ G.Adj third fourth ∧
  G.Adj fourth fifth ∧ G.Adj fifth sixth

/-- Given the first/fifth codegree property of all oriented simple P6s in
this kernel, the two triple-mask witnesses force the high opposite pair.
The profile property is a hypothesis, not a catalogue verified in Lean. -/
theorem kernelP6_opposite_pair
    (triangleFree : G.CliqueFree 3)
    {root anchorA anchorB anchorC anchorD witnessABC witnessABD : V}
    (rootA : G.Adj root anchorA) (rootB : G.Adj root anchorB)
    (rootC : G.Adj root anchorC) (rootD : G.Adj root anchorD)
    (neAB : anchorA ≠ anchorB) (neAC : anchorA ≠ anchorC)
    (neAD : anchorA ≠ anchorD) (neBC : anchorB ≠ anchorC)
    (neBD : anchorB ≠ anchorD) (neCD : anchorC ≠ anchorD)
    (abcA : G.Adj witnessABC anchorA) (abcB : G.Adj witnessABC anchorB)
    (abcC : G.Adj witnessABC anchorC) (abcNotD : ¬ G.Adj witnessABC anchorD)
    (abdA : G.Adj witnessABD anchorA) (abdB : G.Adj witnessABD anchorB)
    (abdD : G.Adj witnessABD anchorD) (abdNotRoot : witnessABD ≠ root)
    (abcNotRoot : witnessABC ≠ root)
    (highAD : #(G.neighborFinset anchorA ∩ G.neighborFinset anchorD) = 3)
    (profile : ∀ first second third fourth fifth sixth,
      KernelP6 G root anchorA first second third fourth fifth sixth →
        #(G.neighborFinset first ∩ G.neighborFinset fifth) = 3) :
    #(G.neighborFinset anchorC ∩ G.neighborFinset anchorD) = 3 := by
  have fresh : ∃ witness ∈ G.neighborFinset anchorA ∩ G.neighborFinset anchorD,
      witness ≠ root ∧ witness ≠ witnessABD := by
    by_contra absent
    push Not at absent
    have subset : G.neighborFinset anchorA ∩ G.neighborFinset anchorD ⊆
        {root, witnessABD} := by
      intro witness inside
      by_cases eqRoot : witness = root
      · simp [eqRoot]
      · simp [absent witness inside eqRoot]
    have bound := card_le_card subset
    rw [highAD, card_insert_of_notMem (by simpa using abdNotRoot.symm), card_singleton] at bound
    omega
  obtain ⟨witnessAD, inside, freshRoot, freshABD⟩ := fresh
  simp only [mem_inter, SimpleGraph.mem_neighborFinset] at inside
  have sidesDisjoint {rootSide pivotSide : V} (rootAdj : G.Adj root rootSide)
      (pivotAdj : G.Adj anchorA pivotSide) (pivotNotRoot : pivotSide ≠ root) :
      rootSide ≠ pivotSide := by
    intro equal
    subst pivotSide
    exact (isIndepSet_neighborFinset triangleFree anchorA
      ((G.mem_neighborFinset anchorA root).mpr rootA.symm)
      ((G.mem_neighborFinset anchorA rootSide).mpr pivotAdj)
      pivotNotRoot.symm) rootAdj
  have distinct : [anchorC, witnessABC, anchorB, witnessABD, anchorD, witnessAD].Nodup := by
    have distinctABCABD : witnessABC ≠ witnessABD := by
      rintro rfl
      exact abcNotD abdD
    have distinctABCAD : witnessABC ≠ witnessAD := by
      rintro rfl
      exact abcNotD inside.2.symm
    have crossCABC := sidesDisjoint rootC abcA.symm abcNotRoot
    have crossCABD := sidesDisjoint rootC abdA.symm abdNotRoot
    have crossCAD := sidesDisjoint rootC inside.1 freshRoot
    have crossBABC := sidesDisjoint rootB abcA.symm abcNotRoot
    have crossBABD := sidesDisjoint rootB abdA.symm abdNotRoot
    have crossBAD := sidesDisjoint rootB inside.1 freshRoot
    have crossDABC := sidesDisjoint rootD abcA.symm abcNotRoot
    have crossDABD := sidesDisjoint rootD abdA.symm abdNotRoot
    have crossDAD := sidesDisjoint rootD inside.1 freshRoot
    simp only [List.nodup_cons, List.mem_cons, List.not_mem_nil, or_false, not_or,
      List.nodup_nil, and_true]
    tauto
  exact profile anchorC witnessABC anchorB witnessABD anchorD witnessAD
    ⟨rootC, neAC.symm, abcA.symm, abcNotRoot, rootB, neAB.symm,
     abdA.symm, abdNotRoot, rootD, neAD.symm, inside.1, freshRoot, distinct,
     abcC.symm, abcB, abdB.symm, abdD, inside.2⟩

end R310
