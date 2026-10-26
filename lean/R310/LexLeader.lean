/-
Lex-leader lemma for the symmetry-breaking (SB) clauses of the certified chain
(request of agent `cert`, 2026-10-24).

Setting: an SB clause `C` (a clause over the variable ids of `R310.Files`) comes with a witness
permutation `π` of the vertices with `π 0 = 0` and `π {1..d} = {1..d}` (`InGamma d π`), and the
property `P(C, π)`: every edge assignment `x` that violates `C` (with MTF aux variables set to the
conjunctions, `assignN x`) has `val (act π x)` strictly better than `val x`, where
`(act π x)(i,j) = x(π⁻¹ i, π⁻¹ j)`. "Better" is `<` or `>`; `val` is any function
(for instance `valOf pos`, the binary number of the edge bits in a position order `pos`).

`cover_files_sb`: F1, F2 and a (3,10,40)-graph give an assignment that satisfies all IS clauses,
every constraint of one cube file, and every SB clause of that cube.
-/
import R310.FilesProof

open Finset

set_option linter.unusedSectionVars false

namespace R310.Files

open R310 R310.Enc

/-- `π` fixes `0` and maps `{1..d}` onto itself (so it also maps `{d+1..39}` onto itself). -/
def InGamma (d : ℕ) (π : Equiv.Perm (Fin 40)) : Prop :=
  π 0 = 0 ∧ ∀ u : Fin 40, (1 ≤ u.val ∧ u.val ≤ d) ↔ (1 ≤ (π u).val ∧ (π u).val ≤ d)

/-- The action of a vertex permutation on edge assignments: `(π x)(i,j) = x(π⁻¹ i, π⁻¹ j)`. -/
def act (π : Equiv.Perm (Fin 40)) (x : Assign) : Assign := assignOf (relabel (graphOf x) π)

/-- `val` for a position order `pos` of the edges: the edge bits read as a binary number, the
first position most significant. -/
def valOf (pos : List (Fin 40 × Fin 40)) (x : Assign) : ℕ :=
  pos.foldl (fun acc p => 2 * acc + if edge x p.1 p.2 then 1 else 0) 0

/-- An SB clause with its witness. -/
structure SBClause where
  lits : List Lit
  wit : Equiv.Perm (Fin 40)

/-- `P(C, π)` for the order `better`. -/
def SBValid (better : ℕ → ℕ → Prop) (val : Assign → ℕ) (C : SBClause) : Prop :=
  ∀ x : Assign, ¬ (clause C.lits).sat (assignN x) → better (val (act C.wit x)) (val x)

theorem graphOf_act (π : Equiv.Perm (Fin 40)) (x : Assign) :
    graphOf (act π x) = relabel (graphOf x) π := graphOf_assignOf _

/-! ### Invariance of `Φ` and of the cubes under `Γ_d` -/

section Invariance

variable {G : SimpleGraph (Fin 40)} [DecidableRel G.Adj] {π : Equiv.Perm (Fin 40)}

theorem relabel_nbhd0 {d : ℕ} (hπ : InGamma d π) (h : Nbhd0 G d) : Nbhd0 (relabel G π) d := by
  intro y
  rw [show y = π (π.symm y) by simp, ← hπ.1, relabel_adj, h, ← hπ.2]

theorem relabel_mtfc (h : MTFc G) : MTFc (relabel G π) := by
  intro u v huv
  rw [show u = π (π.symm u) by simp, show v = π (π.symm v) by simp]
  rcases h (π.symm u) (π.symm v) (fun h' => huv (by simpa using congrArg π h')) with hadj | ⟨w, hw⟩
  · exact Or.inl ((relabel_adj π _ _).2 hadj)
  · exact Or.inr ⟨π w, (relabel_adj π _ _).2 hw.1, (relabel_adj π _ _).2 hw.2⟩

theorem relabel_degree' (x : Fin 40) : (relabel G π).degree x = G.degree (π.symm x) := by
  conv_lhs => rw [show x = π (π.symm x) by simp]
  exact relabel_degree π _

theorem relabel_h0 (h3 : G.CliqueFree 3) (h0 : π 0 = 0) :
    #(delNbhd (relabel G π) 0).edgeFinset = #(delNbhd G 0).edgeFinset := by
  conv_lhs => rw [← h0]
  exact relabel_delNbhd π h3 0

theorem relabel_cubeR (h3 : G.CliqueFree 3) (hπ : InGamma 9 π) (h : CubeR G) :
    CubeR (relabel G π) :=
  ⟨fun x => by rw [relabel_degree']; exact h.degree _, relabel_nbhd0 hπ h.nbhd0,
    relabel_mtfc h.mtf, by rw [relabel_h0 h3 hπ.1]; exact h.h0edges⟩

theorem relabel_cubeS8 (h3 : G.CliqueFree 3) (hπ : InGamma 8 π) (h : CubeS8 G) :
    CubeS8 (relabel G π) :=
  ⟨relabel_mtfc h.mtf, by
    rw [relabel_degree', show π.symm 0 = 0 by rw [Equiv.symm_apply_eq]; exact hπ.1.symm]
    exact h.degree0,
    relabel_nbhd0 hπ h.nbhd0, by rw [relabel_h0 h3 hπ.1]; exact h.h0edges,
    fun x => by rw [relabel_degree']; exact h.degree _⟩

theorem relabel_cubeN (h3 : G.CliqueFree 3) (hπ : InGamma 9 π) (h : CubeN G) :
    CubeN (relabel G π) :=
  ⟨relabel_mtfc h.mtf, by
    rw [relabel_degree', show π.symm 0 = 0 by rw [Equiv.symm_apply_eq]; exact hπ.1.symm]
    exact h.degree0,
    relabel_nbhd0 hπ h.nbhd0, by rw [relabel_h0 h3 hπ.1]; exact h.h0edges,
    fun x => by rw [relabel_degree']; exact h.degree _⟩

end Invariance

theorem congr_graph {P : (G : SimpleGraph (Fin 40)) → [DecidableRel G.Adj] → Prop}
    {G G₂ : SimpleGraph (Fin 40)} [DecidableRel G.Adj] [DecidableRel G₂.Adj] (h : G = G₂)
    (hp : P G) : P G₂ := by
  subst h; convert hp

/-! ### The abstract argument -/

/-- If `S` is closed under the witnesses and every SB clause is valid for `better ∈ {<, >}`, then
a nonempty `S` contains an element that satisfies every SB clause. -/
theorem exists_sb_of_closed (better : ℕ → ℕ → Prop) (hb : better = (· < ·) ∨ better = (· > ·))
    (val : Assign → ℕ) (S : Set Assign) (SB : List SBClause)
    (hS : ∀ C ∈ SB, ∀ x ∈ S, act C.wit x ∈ S) (hP : ∀ C ∈ SB, SBValid better val C)
    (hne : S.Nonempty) :
    ∃ x ∈ S, ∀ C ∈ SB, (clause C.lits).sat (assignN x) := by
  classical
  have hfin : S.Finite := Set.toFinite S
  have hne' : hfin.toFinset.Nonempty := by simpa using hne
  rcases hb with rfl | rfl
  · obtain ⟨x, hx, hmin⟩ := hfin.toFinset.exists_min_image val hne'
    rw [Set.Finite.mem_toFinset] at hx
    refine ⟨x, hx, fun C hC => ?_⟩
    by_contra hv
    have hlt := hP C hC x hv
    have := hmin (act C.wit x) (by rw [Set.Finite.mem_toFinset]; exact hS C hC x hx)
    simp only at hlt
    omega
  · obtain ⟨x, hx, hmax⟩ := hfin.toFinset.exists_max_image val hne'
    rw [Set.Finite.mem_toFinset] at hx
    refine ⟨x, hx, fun C hC => ?_⟩
    by_contra hv
    have hgt := hP C hC x hv
    have := hmax (act C.wit x) (by rw [Set.Finite.mem_toFinset]; exact hS C hC x hx)
    simp only at hgt
    omega

/-! ### Lex-leader step for one cube -/

/-- One cube: from a model `x₀` of `Φ + cube`, a model of `Φ + cube + all SB clauses`. -/
theorem sb_generic {Cube : (G : SimpleGraph (Fin 40)) → [DecidableRel G.Adj] → Prop} (d : ℕ)
    (hinv : ∀ (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (π : Equiv.Perm (Fin 40)),
      G.CliqueFree 3 → InGamma d π → Cube G → Cube (relabel G π))
    (better : ℕ → ℕ → Prop) (hb : better = (· < ·) ∨ better = (· > ·)) (val : Assign → ℕ)
    (SB : List SBClause) (hΓ : ∀ C ∈ SB, InGamma d C.wit) (hP : ∀ C ∈ SB, SBValid better val C)
    (x₀ : Assign) (h₀ : Fdef x₀ ∧ Cube (graphOf x₀)) :
    ∃ x, (Fdef x ∧ Cube (graphOf x)) ∧ ∀ C ∈ SB, (clause C.lits).sat (assignN x) := by
  let S : Set Assign := {x | Fdef x ∧ Cube (graphOf x)}
  have hS : ∀ C ∈ SB, ∀ x ∈ S, act C.wit x ∈ S := by
    intro C hC x hx
    obtain ⟨hF, hc⟩ := hx
    have hF' := (fdef_iff x).1 hF
    refine ⟨(fdef_iff _).2 ?_, ?_⟩
    · rw [graphOf_act]
      exact ⟨relabel_cliqueFree _ hF'.1, (relabel_indepNum _).trans hF'.2⟩
    · exact congr_graph (P := Cube) (graphOf_act C.wit x).symm
        (hinv (graphOf x) C.wit hF'.1 (hΓ C hC) hc)
  exact exists_sb_of_closed better hb val S SB hS hP ⟨x₀, h₀⟩

/-! ### Cube properties give the cube files (as in `cover_files`) -/

theorem cubeR_file {x : Assign} (hF : Fdef x) (hR : CubeR (graphOf x)) :
    ∀ c ∈ cubeR, c.sat (assignN x) := by
  intro c hc
  simp only [cubeR, List.mem_append] at hc
  rcases hc with ((((hc | hc) | hc) | hc) | hc) | hc
  · exact tri_sat hF.1 c hc
  · exact mtf_sat hR.mtf c hc
  · exact nbhd0_sat 9 hR.nbhd0 c hc
  · exact deg_sat 9 9 (fun v => by rw [hR.degree v]; omega) c hc
  · exact h0le_sat 9 99 (Or.inr rfl) hR.nbhd0 hR.h0edges.le c hc
  · exact h0ge_sat 9 99 hR.nbhd0 hR.h0edges.ge c hc

theorem cubeS8_file {x : Assign} (hF : Fdef x) (hS : CubeS8 (graphOf x)) :
    ∀ c ∈ cubeS8, c.sat (assignN x) := by
  intro c hc
  simp only [cubeS8, List.mem_append] at hc
  rcases hc with (((hc | hc) | hc) | hc) | hc
  · exact tri_sat hF.1 c hc
  · exact mtf_sat hS.mtf c hc
  · exact nbhd0_sat 8 hS.nbhd0 c hc
  · exact deg_sat 6 9 hS.degree c hc
  · exact h0le_sat 8 96 (Or.inl rfl) hS.nbhd0 hS.h0edges c hc

theorem cubeN_file {x : Assign} (hF : Fdef x) (hN : CubeN (graphOf x)) :
    ∀ c ∈ cubeN, c.sat (assignN x) := by
  intro c hc
  simp only [cubeN, List.mem_append] at hc
  rcases hc with (((hc | hc) | hc) | hc) | hc
  · exact tri_sat hF.1 c hc
  · exact mtf_sat hN.mtf c hc
  · exact nbhd0_sat 9 hN.nbhd0 c hc
  · exact deg_sat 6 9 hN.degree c hc
  · exact h0le_sat 9 98 (Or.inr rfl) hN.nbhd0 hN.h0edges c hc

/-- **Cover Lemma with symmetry breaking.** Assume F1, F2. Let `SBR`, `SBS8`, `SBN` be SB
clauses for the three cubes, each with a witness in `Γ_9`, `Γ_8`, `Γ_9` and valid
(`SBValid better val`, `better ∈ {<, >}`, the same `better` and `val` for all clauses).
If a (3,10,40)-graph exists, then some assignment `a` satisfies all IS clauses, every constraint
of one cube file, and every SB clause of that cube. -/
theorem cover_files_sb (hF1 : FactF1) (hF2 : FactF2) (better : ℕ → ℕ → Prop)
    (hb : better = (· < ·) ∨ better = (· > ·)) (val : Assign → ℕ)
    (SBR SBS8 SBN : List SBClause)
    (hΓR : ∀ C ∈ SBR, InGamma 9 C.wit) (hΓS : ∀ C ∈ SBS8, InGamma 8 C.wit)
    (hΓN : ∀ C ∈ SBN, InGamma 9 C.wit)
    (hPR : ∀ C ∈ SBR, SBValid better val C) (hPS : ∀ C ∈ SBS8, SBValid better val C)
    (hPN : ∀ C ∈ SBN, SBValid better val C)
    (G : SimpleGraph (Fin 40)) (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) :
    ∃ a : ℕ → Bool, ISall a ∧
      (((∀ c ∈ cubeR, c.sat a) ∧ ∀ C ∈ SBR, (clause C.lits).sat a) ∨
       ((∀ c ∈ cubeS8, c.sat a) ∧ ∀ C ∈ SBS8, (clause C.lits).sat a) ∨
       ((∀ c ∈ cubeN, c.sat a) ∧ ∀ C ∈ SBN, (clause C.lits).sat a)) := by
  obtain ⟨G', inst, h3', hα', -, hcube⟩ := cover_lemma hF1 hF2 G h3 hα
  have hg := graphOf_assignOf G'
  have hF0 : Fdef (assignOf G') := (fdef_iff _).2 (by rw [hg]; exact ⟨h3', hα'⟩)
  rcases hcube with hR | hS | hN
  · obtain ⟨x, ⟨hF, hc⟩, hsb⟩ := sb_generic (Cube := CubeR) 9
      (fun G _ π h3 hπ h => relabel_cubeR h3 hπ h) better hb val SBR hΓR hPR (assignOf G')
      ⟨hF0, congr_graph (P := CubeR) hg.symm hR⟩
    exact ⟨assignN x, isall_of hF.2, Or.inl ⟨cubeR_file hF hc, hsb⟩⟩
  · obtain ⟨x, ⟨hF, hc⟩, hsb⟩ := sb_generic (Cube := CubeS8) 8
      (fun G _ π h3 hπ h => relabel_cubeS8 h3 hπ h) better hb val SBS8 hΓS hPS (assignOf G')
      ⟨hF0, congr_graph (P := CubeS8) hg.symm hS⟩
    exact ⟨assignN x, isall_of hF.2, Or.inr (Or.inl ⟨cubeS8_file hF hc, hsb⟩)⟩
  · obtain ⟨x, ⟨hF, hc⟩, hsb⟩ := sb_generic (Cube := CubeN) 9
      (fun G _ π h3 hπ h => relabel_cubeN h3 hπ h) better hb val SBN hΓN hPN (assignOf G')
      ⟨hF0, congr_graph (P := CubeN) hg.symm hN⟩
    exact ⟨assignN x, isall_of hF.2, Or.inr (Or.inr ⟨cubeN_file hF hc, hsb⟩)⟩

end R310.Files
