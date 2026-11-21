import R310.Structure

namespace R310

open Finset SimpleGraph

variable {G : SimpleGraph (Fin 40)} [DecidableRel G.Adj]

/-- A degree-six vertex outside the closed neighborhood of a degree-six root has
residue degree five: maximality and the pair cap force exactly one shared neighbor. -/
theorem IsMTF.degree_five_of_degree_six_pair (hmtf : IsMTF G) (hAlpha : G.indepNum ≤ 9)
    (hR8 : Ramsey3Le 8 28) {root : Fin 40} (vertex : (outside G root : Set (Fin 40)))
    (hDegree : G.degree root = 6) (hOther : G.degree vertex = 6) :
    (delNbhd G root).degree vertex = 5 := by
  have hOutside := mem_outside.mp (mem_coe.mp vertex.2)
  have hCap := pair_lemma G hmtf.1 hAlpha hR8 hOutside.1.symm hOutside.2
  obtain ⟨common, hRoot, hVertex⟩ := hmtf.exists_common hOutside.1.symm hOutside.2
  have hPos : 0 < #(G.neighborFinset root ∩ G.neighborFinset vertex) :=
    card_pos.mpr ⟨common, by simp [hRoot, hVertex]⟩
  rw [← nbrIn_eq_card_inter] at hCap hPos
  have hSplit := degree_eq_degree_delNbhd_add (G := G) root vertex
  omega

/-- The finite outer rejection can be passed in as a lower bound on the degree
of every exterior vertex. Given this bound, the residue degree identity gives
the strengthened common-neighbor cap at a degree-six root. -/
theorem nbrIn_le_sub_six_of_exterior_minDegree (root : Fin 40)
    (vertex : (outside G root : Set (Fin 40)))
    (hMin : 6 ≤ (delNbhd G root).degree vertex) :
    nbrIn G root vertex ≤ G.degree vertex - 6 := by
  have hSplit := degree_eq_degree_delNbhd_add (G := G) root vertex
  omega

/-- Conditional on the global exterior minimum-degree bound, the degree-six
vertices form a clique. This direction needs no edge budget or Ramsey bound. -/
theorem IsMTF.degree_six_isClique_of_exterior_minDegree (hmtf : IsMTF G)
    (hExterior : ∀ root, G.degree root = 6 →
      ∀ vertex, 6 ≤ (delNbhd G root).degree vertex) :
    G.IsClique ({vertex | G.degree vertex = 6} : Set (Fin 40)) := by
  intro root firstDegree vertex secondDegree hNe
  by_contra hNonedge
  have hOutside : vertex ∈ outside G root := mem_outside.mpr ⟨hNe.symm, hNonedge⟩
  let exteriorVertex : (outside G root : Set (Fin 40)) := ⟨vertex, hOutside⟩
  have hCap := nbrIn_le_sub_six_of_exterior_minDegree root exteriorVertex
    (hExterior root firstDegree exteriorVertex)
  obtain ⟨common, hRoot, hVertex⟩ := hmtf.exists_common hNe hNonedge
  have hPos : 0 < #(G.neighborFinset root ∩ G.neighborFinset vertex) :=
    card_pos.mpr ⟨common, by simp [hRoot, hVertex]⟩
  rw [← nbrIn_eq_card_inter] at hPos
  change G.degree vertex = 6 at secondDegree
  change nbrIn G root vertex ≤ G.degree vertex - 6 at hCap
  omega

/-- The numerical global cut from the clique, still conditional on the
exterior minimum-degree bound rather than a Lean census. -/
theorem IsMTF.card_degree_six_le_two_of_exterior_minDegree (hmtf : IsMTF G)
    (hExterior : ∀ root, G.degree root = 6 →
      ∀ vertex, 6 ≤ (delNbhd G root).degree vertex) :
    #{vertex | G.degree vertex = 6} ≤ 2 := by
  refine card_le_two_of_isClique hmtf.1 ?_
  simpa only [Finset.coe_filter, mem_univ, true_and] using
    hmtf.degree_six_isClique_of_exterior_minDegree hExterior

/-- The published Ramsey bound excludes exterior degree at most four; only
degree five then needs the separate, global enumeration-and-rejection input. -/
theorem IsMTF.exterior_minDegree_of_no_degree_five (hmtf : IsMTF G)
    (hAlpha : G.indepNum ≤ 9) (hR8 : Ramsey3Le 8 28)
    (hNoFive : ∀ root, G.degree root = 6 →
      ∀ vertex, (delNbhd G root).degree vertex ≠ 5)
    (root : Fin 40) (hDegree : G.degree root = 6)
    (vertex : (outside G root : Set (Fin 40))) : 6 ≤ (delNbhd G root).degree vertex := by
  have hCount := card_delNbhd_verts (G := G) root
  rw [Fintype.card_fin, hDegree] at hCount
  have hMin := card_le_degree_add (k := 9) (cliqueFree_delNbhd hmtf.1 root)
    (indepNum_delNbhd_le (k := 10) hAlpha root) hR8 vertex
  have hNot := hNoFive root hDegree vertex
  omega

private theorem degree_profile_789 (neighbors : Finset (Fin 40))
    (hRange : ∀ vertex ∈ neighbors, 7 ≤ G.degree vertex ∧ G.degree vertex ≤ 9) :
    let seven := #{vertex ∈ neighbors | G.degree vertex = 7}
    let eight := #{vertex ∈ neighbors | G.degree vertex = 8}
    let nine := #{vertex ∈ neighbors | G.degree vertex = 9}
    seven + eight + nine = #neighbors ∧
    7 * seven + 8 * eight + 9 * nine = ∑ vertex ∈ neighbors, G.degree vertex := by
  induction neighbors using Finset.induction_on with
  | empty => simp
  | @insert vertex rest hNot ih =>
    obtain ⟨hMin, hMax⟩ := hRange vertex (mem_insert_self _ _)
    obtain ⟨hCount, hSum⟩ := ih fun other hOther => hRange other (mem_insert_of_mem hOther)
    have hOptions : G.degree vertex = 7 ∨ G.degree vertex = 8 ∨ G.degree vertex = 9 := by omega
    simp only [filter_insert, card_insert_of_notMem hNot, sum_insert hNot]
    rcases hOptions with hValue | hValue | hValue <;>
      simp only [hValue, Nat.reduceEqDiff, ite_true, ite_false] <;>
      rw [card_insert_of_notMem (fun h => hNot (mem_filter.mp h).1)] <;> omega

/-- At e168 and the degree-six residue floor 120, an adjacent degree-six peer
leaves only two possible degree profiles on the other five neighbors. This is
conditional on the given adjacent pair and on there being no third degree-six vertex. -/
theorem IsMTF.e168_degree_six_peer_profiles (hmtf : IsMTF G) (hAlpha : G.indepNum ≤ 9)
    {root peer : Fin 40} (hDegree : G.degree root = 6) (hPeer : G.degree peer = 6)
    (hAdj : G.Adj root peer) (hNoOther : ∀ vertex, G.degree vertex = 6 → vertex = root ∨ vertex = peer)
    (hEdges : #G.edgeFinset = 168) (hFloor : 120 ≤ #(delNbhd G root).edgeFinset) :
    let other := (G.neighborFinset root).erase peer
    let seven := #{vertex ∈ other | G.degree vertex = 7}
    let eight := #{vertex ∈ other | G.degree vertex = 8}
    let nine := #{vertex ∈ other | G.degree vertex = 9}
    (seven = 0 ∧ eight = 3 ∧ nine = 2) ∨
      (seven = 1 ∧ eight = 1 ∧ nine = 3) := by
  let other := (G.neighborFinset root).erase peer
  have hMem : peer ∈ G.neighborFinset root := (mem_neighborFinset _ _ _).mpr hAdj
  have hCount : #other = 5 := by simp [other, card_erase_of_mem hMem, hDegree]
  have hRange : ∀ vertex ∈ other, 7 ≤ G.degree vertex ∧ G.degree vertex ≤ 9 := by
    intro vertex hVertex
    have ⟨hNe, hNbr⟩ := mem_erase.mp hVertex
    have hRoot : vertex ≠ root := ((mem_neighborFinset _ _ _).mp hNbr).ne.symm
    have hSix := IsMTF.six_le_degree G hmtf hAlpha vertex
    have hNot : G.degree vertex ≠ 6 := fun h => (hNoOther vertex h).elim hRoot hNe
    exact ⟨by omega, (degree_le_indepNum hmtf.1 vertex).trans hAlpha⟩
  have hZ := IsMTF.sum_degree_neighbor_ge G hmtf hAlpha root
  rw [hDegree] at hZ
  have hSplit := card_edgeFinset_delNbhd_add_sum_degree hmtf.1 root
  have hErase := sum_erase_add (G.neighborFinset root) (fun vertex => G.degree vertex) hMem
  change (∑ vertex ∈ other, G.degree vertex) + G.degree peer = _ at hErase
  obtain ⟨hProfileSize, hProfileSum⟩ := degree_profile_789 other hRange
  unfold other at hCount hErase hProfileSize hProfileSum
  omega

/-- A complete exclusion of order-33 triangle-free residues at minimum degree five
and at most 121 edges would rule out three degree-six vertices through total e169.
This only certifies the reduction, not the external `(3,8)` bound or the census. -/
theorem IsMTF.exists_minDegree_five_residue_through_e169 (hmtf : IsMTF G)
    (hAlpha : G.indepNum ≤ 9) (hR8 : Ramsey3Le 8 28) (hTotal : #G.edgeFinset ≤ 169)
    (hThree : 3 ≤ #{vertex | G.degree vertex = 6}) :
    ∃ root, G.degree root = 6 ∧ #(delNbhd G root).edgeFinset ≤ 121 ∧
      (delNbhd G root).CliqueFree 3 ∧ (delNbhd G root).indepNum ≤ 8 ∧
      (∀ vertex, 5 ≤ (delNbhd G root).degree vertex) ∧
      (∃ vertex, (delNbhd G root).degree vertex = 5) := by
  let low : Finset (Fin 40) := {vertex | G.degree vertex = 6}
  have hNonedge : ∃ root ∈ low, ∃ vertex ∈ low, root ≠ vertex ∧ ¬ G.Adj root vertex := by
    by_contra hNo
    have hClique : G.IsClique (low : Set (Fin 40)) := by
      intro root hRoot vertex hVertex hNe
      by_contra hNot
      exact hNo ⟨root, hRoot, vertex, hVertex, hNe, hNot⟩
    have hCut := card_le_two_of_isClique hmtf.1 (s := low) hClique
    change 3 ≤ #low at hThree
    omega
  obtain ⟨root, hRoot, vertex, hVertex, hNe, hNot⟩ := hNonedge
  have hDegree : G.degree root = 6 := by simpa only [low, mem_filter, mem_univ, true_and] using hRoot
  have hOther : G.degree vertex = 6 := by simpa only [low, mem_filter, mem_univ, true_and] using hVertex
  have hOutside : vertex ∈ outside G root := mem_outside.mpr ⟨hNe.symm, hNot⟩
  have hFive := hmtf.degree_five_of_degree_six_pair hAlpha hR8 ⟨vertex, hOutside⟩ hDegree hOther
  have hZ := IsMTF.sum_degree_neighbor_ge G hmtf hAlpha root
  rw [hDegree] at hZ
  have hSplit := card_edgeFinset_delNbhd_add_sum_degree hmtf.1 root
  have hResidue := cliqueFree_delNbhd hmtf.1 root
  have hAlphaResidue := indepNum_delNbhd_le (k := 10) hAlpha root
  have hOrder : Fintype.card (outside G root : Set (Fin 40)) = 33 := by
    have hCount := card_delNbhd_verts (G := G) root
    rw [Fintype.card_fin, hDegree] at hCount
    omega
  refine ⟨root, hDegree, by omega, hResidue, hAlphaResidue, ?_, ⟨_, hFive⟩⟩
  intro other
  have hMin := card_le_degree_add (k := 9) hResidue hAlphaResidue hR8 other
  omega

end R310
