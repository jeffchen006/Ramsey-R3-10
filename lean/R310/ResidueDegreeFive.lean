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
