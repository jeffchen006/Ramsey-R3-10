/-
Theorem A'' and the Cover Lemma of `notes/cases.md` (Sec. 4a, agreed with `cert`).

Outside facts (explicit hypotheses):
  F1: e(3,8,m) ≥ 6m - 91 for 23 ≤ m ≤ 27, i.e. `EdgeLowerBound 8 m (6m - 91)`;
  F2: R(3,8) ≤ 28, i.e. `Ramsey3Le 8 28`.
No other table value is used (no R(3,9), no e(3,9,·), no e(3,10,40)).
-/
import R310.MTF
import R310.Pair
import R310.EdgeBound
import R310.Local
import R310.Regular

open Finset

set_option linter.unusedSectionVars false

namespace R310

open SimpleGraph

/-- Fact F1: `e(3,8,m) ≥ 6m - 91` for `23 ≤ m ≤ 27`. -/
def FactF1 : Prop := ∀ m, 23 ≤ m → m ≤ 27 → EdgeLowerBound 8 m (6 * m - 91)

/-- Fact F2: `R(3,8) ≤ 28`. -/
abbrev FactF2 : Prop := Ramsey3Le 8 28

section ThmA2

variable {W : Type*} [Fintype W] [DecidableEq W] {H : SimpleGraph W} [DecidableRel H.Adj]

/-- Per vertex of a triangle-free `H` with `α(H) ≤ 8` and `|H| ≥ 32`: `deg w ≤ 8`,
`|H| ≤ deg w + 28` (F2) and `e(H - N[w]) ≥ 6 (|H| - 1 - deg w) - 91` (F1). -/
theorem thmA2_vertex (hF1 : FactF1) (hF2 : FactF2) (h3 : H.CliqueFree 3) (hα : H.indepNum ≤ 8)
    (hM : 32 ≤ Fintype.card W) (w : W) :
    H.degree w ≤ 8 ∧ Fintype.card W ≤ H.degree w + 28 ∧
      6 * (Fintype.card W - 1 - H.degree w) - 91 ≤ #(delNbhd H w).edgeFinset := by
  have hd := degree_le_of_indepNum_le (k := 9) h3 hα w
  have hlow := card_le_degree_add (k := 9) h3 hα hF2 w
  refine ⟨hd, hlow, ?_⟩
  have hE := hF1 (Fintype.card W - 1 - H.degree w) (by omega) (by omega)
  exact le_card_edgeFinset_delNbhd (k := 9) h3 hα w (by
    rw [show Fintype.card W - H.degree w - 1 = Fintype.card W - 1 - H.degree w by omega]
    exact hE)

/-- Theorem A'' (32 vertices): every triangle-free graph on 32 vertices with `α ≤ 8` has at
least 95 edges. Uses only F1 and F2. -/
theorem thmA2_32 (hF1 : FactF1) (hF2 : FactF2) : EdgeLowerBound 9 32 95 := by
  intro H _ h3 hα
  have hα' : H.indepNum ≤ 8 := by omega
  have hv := fun w => thmA2_vertex hF1 hF2 h3 hα' (by simp) w
  simp only [Fintype.card_fin] at hv
  have hsum := sum_card_edgeFinset_delNbhd_add h3 (G := H)
  have hdeg := sum_degrees_eq_twice_card_edges H
  simp only [Fintype.card_fin] at hsum
  -- per vertex: `e(H_w) + d^2 ≥ 5 d + 65` (tangent line of `d^2 - 6d + 95` at d = 5, 6)
  have hline : ∀ w, 5 * H.degree w + 65 ≤ #(delNbhd H w).edgeFinset + H.degree w ^ 2 := by
    intro w
    obtain ⟨h1, h2, h3'⟩ := hv w
    interval_cases h : H.degree w <;> omega
  have := sum_le_sum fun w (_ : w ∈ univ) => hline w
  rw [sum_add_distrib, sum_add_distrib, ← mul_sum, hdeg, hsum] at this
  simp only [sum_const, card_univ, Fintype.card_fin, smul_eq_mul] at this
  omega

/-- Theorem A'' (33 vertices): every triangle-free graph on 33 vertices with `α ≤ 8` has at
least 103 edges. Uses only F1 and F2. -/
theorem thmA2_33 (hF1 : FactF1) (hF2 : FactF2) : EdgeLowerBound 9 33 103 := by
  intro H _ h3 hα
  have hα' : H.indepNum ≤ 8 := by omega
  have hv := fun w => thmA2_vertex hF1 hF2 h3 hα' (by simp) w
  simp only [Fintype.card_fin] at hv
  have hsum := sum_card_edgeFinset_delNbhd_add h3 (G := H)
  have hdeg := sum_degrees_eq_twice_card_edges H
  simp only [Fintype.card_fin] at hsum
  -- per vertex: `e(H_w) + d^2 ≥ 7 d + 59` (tangent line of `d^2 - 6d + 101` at d = 6, 7)
  have hline : ∀ w, 7 * H.degree w + 59 ≤ #(delNbhd H w).edgeFinset + H.degree w ^ 2 := by
    intro w
    obtain ⟨h1, h2, h3'⟩ := hv w
    interval_cases h : H.degree w <;> omega
  have := sum_le_sum fun w (_ : w ∈ univ) => hline w
  rw [sum_add_distrib, sum_add_distrib, ← mul_sum, hdeg, hsum] at this
  simp only [sum_const, card_univ, Fintype.card_fin, smul_eq_mul] at this
  omega

end ThmA2

/-! ### Theorem A for MTF graphs, from F1 and F2 only -/

section ThmAMTF

variable (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]

/-- Theorem A (non-regular part) for an MTF (3,10,40)-graph, using only F1 and F2 (through
Theorem A''): if `G` is not 9-regular, some `v` has (`deg v = 9` and `e(H_v) ≤ 98`) or
(`deg v = 8` and `e(H_v) ≤ 96`). -/
theorem theoremA_mtf (hG : IsMTF G) (hα : G.indepNum ≤ 9) (hF1 : FactF1) (hF2 : FactF2)
    (hreg : ∃ v, G.degree v ≠ 9) :
    ∃ v, (G.degree v = 9 ∧ #(delNbhd G v).edgeFinset ≤ 98) ∨
      (G.degree v = 8 ∧ #(delNbhd G v).edgeFinset ≤ 96) := by
  have h3 : G.CliqueFree 3 := hG.1
  by_contra hcon
  push Not at hcon
  have hle : ∀ v, 20 * G.degree v ≤ #(delNbhd G v).edgeFinset + G.degree v ^ 2 ∧
      (G.degree v ≠ 9 → 20 * G.degree v < #(delNbhd G v).edgeFinset + G.degree v ^ 2) := by
    intro v
    have hlo := hG.six_le_degree G hα v
    have hhi := degree_le_nine G h3 hα v
    have key : ∀ e₀, EdgeLowerBound 9 (40 - G.degree v - 1) e₀ →
        e₀ ≤ #(delNbhd G v).edgeFinset := fun e₀ hE =>
      le_card_edgeFinset_delNbhd (k := 10) h3 hα v (by simpa using hE)
    obtain ⟨h9, h8⟩ := hcon v
    have h9' : G.degree v ≠ 9 ∨ 98 < #(delNbhd G v).edgeFinset := by tauto
    have h8' : G.degree v ≠ 8 ∨ 96 < #(delNbhd G v).edgeFinset := by tauto
    clear h9 h8 hreg
    interval_cases h : G.degree v
    · have := key _ (thmA2_33 hF1 hF2); omega
    · have := key _ (thmA2_32 hF1 hF2); omega
    · omega
    · omega
  obtain ⟨v₀, hv₀⟩ := hreg
  have hlt : ∑ v, 20 * G.degree v < ∑ v, (#(delNbhd G v).edgeFinset + G.degree v ^ 2) :=
    sum_lt_sum (fun v _ => (hle v).1) ⟨v₀, mem_univ _, (hle v₀).2 hv₀⟩
  have h4 := sum_card_edgeFinset_delNbhd_add h3 (G := G)
  have hd := sum_degrees_eq_twice_card_edges G
  simp only [Fintype.card_fin] at h4
  rw [sum_add_distrib, h4, ← mul_sum, hd] at hlt
  omega

end ThmAMTF

/-! ### Relabelling -/

section Relabel

/-- Pull back `G` along the inverse of a permutation `σ`: `σ` becomes an isomorphism
`G ≃g G.relabel σ`, i.e. `(G.relabel σ).Adj (σ a) (σ b) ↔ G.Adj a b`. -/
abbrev relabel (G : SimpleGraph (Fin 40)) (σ : Equiv.Perm (Fin 40)) : SimpleGraph (Fin 40) :=
  G.comap σ.symm

variable {G : SimpleGraph (Fin 40)} [DecidableRel G.Adj] (σ : Equiv.Perm (Fin 40))

instance : DecidableRel (relabel G σ).Adj := fun _ _ => inferInstanceAs (Decidable (G.Adj _ _))

theorem relabel_adj (a b : Fin 40) : (relabel G σ).Adj (σ a) (σ b) ↔ G.Adj a b := by
  simp [relabel]

theorem relabel_neighborFinset (a : Fin 40) :
    (relabel G σ).neighborFinset (σ a) = (G.neighborFinset a).map σ.toEmbedding := by
  ext b
  simp only [mem_neighborFinset, mem_map_equiv]
  rw [show b = σ (σ.symm b) by simp, relabel_adj]
  simp

theorem relabel_degree (a : Fin 40) : (relabel G σ).degree (σ a) = G.degree a := by
  rw [← card_neighborFinset_eq_degree, relabel_neighborFinset, card_map,
    card_neighborFinset_eq_degree]

theorem relabel_cliqueFree {n : ℕ} (h : G.CliqueFree n) : (relabel G σ).CliqueFree n :=
  h.comap (Iso.comap σ.symm G).toEmbedding.isContained

theorem relabel_indepNum : (relabel G σ).indepNum ≤ G.indepNum :=
  indepNum_le_of_embedding (Iso.comap σ.symm G).toEmbedding

theorem relabel_card_edgeFinset : #(relabel G σ).edgeFinset = #G.edgeFinset :=
  Iso.card_edgeFinset_eq (Iso.comap σ.symm G)

theorem relabel_isMTF (h : IsMTF G) : IsMTF (relabel G σ) := by
  refine ⟨relabel_cliqueFree σ h.1, fun H' hH' hle => ?_⟩
  -- pull `H'` back to `G`'s labels
  have h1 : (H'.comap σ).CliqueFree 3 := hH'.comap (Iso.comap σ H').toEmbedding.isContained
  have h2 : G ≤ H'.comap σ := by
    intro a b hab
    have := hle ((relabel_adj σ a b).2 hab)
    simpa using this
  have h3 := h.2 h1 h2
  intro a b hab
  have : (H'.comap σ).Adj (σ.symm a) (σ.symm b) := by simpa using hab
  have := h3 this
  simpa [relabel] using this

/-- `e(H_0)` is invariant: `e((relabel G σ) - N[σ a]) = e(G - N[a])` (triangle-free `G`). -/
theorem relabel_delNbhd (h3 : G.CliqueFree 3) (a : Fin 40) :
    #(delNbhd (relabel G σ) (σ a)).edgeFinset = #(delNbhd G a).edgeFinset := by
  have h1 := card_edgeFinset_delNbhd_add_sum_degree h3 (G := G) a
  have h2 := card_edgeFinset_delNbhd_add_sum_degree (relabel_cliqueFree σ h3) (G := relabel G σ)
    (σ a)
  rw [relabel_neighborFinset, sum_map, relabel_card_edgeFinset] at h2
  simp only [Equiv.toEmbedding_apply, relabel_degree] at h2
  omega

/-- For a vertex `v` of degree `d`, there is a permutation `σ` with `σ v = 0` and
`σ(N(v)) = {1..d}`. -/
theorem exists_relabel (v : Fin 40) :
    ∃ σ : Equiv.Perm (Fin 40), σ v = 0 ∧
      ∀ y, (relabel G σ).Adj 0 y ↔ 1 ≤ y.val ∧ y.val ≤ G.degree v := by
  classical
  set d := G.degree v with hd
  let P : Finset (Fin 40) := insert v (G.neighborFinset v)
  let T : Finset (Fin 40) := {y | y.val ≤ d}
  have hdle : d ≤ 39 := by
    have := card_le_univ (insert v (G.neighborFinset v))
    rw [card_insert_of_notMem (G.notMem_neighborFinset_self v), card_neighborFinset_eq_degree] at this
    simp at this
    omega
  have hPcard : #P = d + 1 := by
    simp only [P]
    rw [card_insert_of_notMem (G.notMem_neighborFinset_self v), card_neighborFinset_eq_degree]
  have hTcard : #T = d + 1 := by
    simp only [T]
    have : ({y | y.val ≤ d} : Finset (Fin 40)) = (Finset.range (d + 1)).attachFin
        (fun i hi => by simp at hi; omega) := by
      ext y; simp
    rw [this, card_attachFin, card_range]
  -- an equivalence `P ≃ T` sending `v` to `0`
  obtain ⟨g, hg⟩ := Finset.exists_equiv_extend_of_card_eq (α := { x // x ∈ P }) (t := T)
    (by rw [Fintype.card_coe, hPcard, hTcard]) (s := {⟨v, mem_insert_self _ _⟩})
    (f := fun _ => (0 : Fin 40)) (by intro y hy; simp at hy; rw [hy]; simp [T])
    (by intro a ha b hb _; simp at ha hb; rw [ha, hb])
  have hg0 : (g ⟨v, mem_insert_self _ _⟩ : Fin 40) = 0 := hg _ (mem_singleton_self _)
  let e : { x // x ∈ P } ≃ { y // y ∈ T } := g
  let σ := e.extendSubtype
  have hσv : σ v = 0 := by
    rw [Equiv.extendSubtype_apply_of_mem e v (mem_insert_self _ _)]
    exact hg0
  refine ⟨σ, hσv, fun y => ?_⟩
  rw [← hσv, show y = σ (σ.symm y) by simp, relabel_adj]
  set x := σ.symm y with hx
  constructor
  · intro hvx
    have hxP : x ∈ P := mem_insert_of_mem ((mem_neighborFinset _ _ _).2 hvx)
    have hT := Equiv.extendSubtype_mem e x hxP
    simp only [T, mem_filter, mem_univ, true_and] at hT
    refine ⟨?_, hT⟩
    by_contra h0
    have : σ x = σ v := by
      rw [hσv]; ext; simp only [Fin.val_zero]; omega
    exact G.loopless.irrefl v (by rwa [σ.injective this] at hvx)
  · rintro ⟨h1, h2⟩
    have hyT : σ x ∈ T := by simp [T, h2]
    have hxP : x ∈ P := by
      by_contra hn
      exact Equiv.extendSubtype_not_mem e x hn hyT
    simp only [P, mem_insert] at hxP
    rcases hxP with hxv | hxN
    · rw [hxv, hσv] at h1; simp at h1
    · exact (mem_neighborFinset _ _ _).1 hxN

end Relabel

/-! ### The cubes and the Cover Lemma (`notes/cases.md` Sec. 4a, `cert/cases40.txt`) -/

/-- MTF in clause form (as encoded for the SAT solvers): any two distinct vertices are adjacent
or have a common neighbour. -/
def MTFc (G : SimpleGraph (Fin 40)) : Prop :=
  ∀ u v : Fin 40, u ≠ v → G.Adj u v ∨ ∃ w, G.Adj u w ∧ G.Adj v w

/-- `N(0) = {1, ..., d}`. -/
def Nbhd0 (G : SimpleGraph (Fin 40)) (d : ℕ) : Prop :=
  ∀ y : Fin 40, G.Adj 0 y ↔ 1 ≤ y.val ∧ y.val ≤ d

/-- Codegree bound (L6, needs F2): non-adjacent `u ≠ v` have at most `d(u) + d(v) - 11`
common neighbours. Optional row of every cube (Note 2 of Sec. 4a). -/
def CodegOK (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] : Prop :=
  ∀ u v : Fin 40, u ≠ v → ¬ G.Adj u v →
    #(G.neighborFinset u ∩ G.neighborFinset v) + 11 ≤ G.degree u + G.degree v

/-- Cube R: 9-regular, `N(0) = {1..9}`; optional rows: MTF, `e(H_0) = 99`. -/
structure CubeR (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] : Prop where
  degree : ∀ x, G.degree x = 9
  nbhd0 : Nbhd0 G 9
  mtf : MTFc G
  h0edges : #(delNbhd G 0).edgeFinset = 99

/-- Cube S8: MTF, `d(0) = 8`, `N(0) = {1..8}`, `e(H_0) ≤ 96`; optional row: degrees 6..9. -/
structure CubeS8 (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] : Prop where
  mtf : MTFc G
  degree0 : G.degree 0 = 8
  nbhd0 : Nbhd0 G 8
  h0edges : #(delNbhd G 0).edgeFinset ≤ 96
  degree : ∀ x, 6 ≤ G.degree x ∧ G.degree x ≤ 9

/-- Cube N: MTF, `d(0) = 9`, `N(0) = {1..9}`, `e(H_0) ≤ 98`; optional row: degrees 6..9. -/
structure CubeN (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] : Prop where
  mtf : MTFc G
  degree0 : G.degree 0 = 9
  nbhd0 : Nbhd0 G 9
  h0edges : #(delNbhd G 0).edgeFinset ≤ 98
  degree : ∀ x, 6 ≤ G.degree x ∧ G.degree x ≤ 9

theorem IsMTF.mtfc {G : SimpleGraph (Fin 40)} (h : IsMTF G) : MTFc G := by
  intro u v huv
  by_cases hadj : G.Adj u v
  · exact Or.inl hadj
  · exact Or.inr (h.exists_common huv hadj)

/-- **Cover Lemma.** Assume F1 and F2. If a (3,10,40)-graph exists, then some graph on
`{0..39}` is triangle-free, has `α ≤ 9`, satisfies the codegree bound, and satisfies one of the
cubes R, S8, N. -/
theorem cover_lemma (hF1 : FactF1) (hF2 : FactF2) (G : SimpleGraph (Fin 40))
    (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) :
    ∃ G' : SimpleGraph (Fin 40), ∃ _ : DecidableRel G'.Adj, G'.CliqueFree 3 ∧
      G'.indepNum ≤ 9 ∧ CodegOK G' ∧ (CubeR G' ∨ CubeS8 G' ∨ CubeN G') := by
  classical
  -- M0: an MTF supergraph
  obtain ⟨H, -, hH, hαH⟩ := exists_isMTF_le h3
  have hαH' : H.indepNum ≤ 9 := hαH.trans hα
  have h3H : H.CliqueFree 3 := hH.1
  -- facts that hold for every relabelling of `H`
  have hrel : ∀ σ : Equiv.Perm (Fin 40), (relabel H σ).CliqueFree 3 ∧
      (relabel H σ).indepNum ≤ 9 ∧ IsMTF (relabel H σ) ∧ CodegOK (relabel H σ) := by
    intro σ
    have h1 := relabel_cliqueFree σ h3H
    have h2 := (relabel_indepNum σ).trans hαH'
    exact ⟨h1, h2, relabel_isMTF σ hH, fun u v huv hn => pair_lemma _ h1 h2 hF2 huv hn⟩
  by_cases hreg : ∀ v, H.degree v = 9
  · -- cube R
    obtain ⟨σ, hσ0, hN⟩ := exists_relabel (G := H) 0
    obtain ⟨h1, h2, hm, hc⟩ := hrel σ
    have hdeg : ∀ x, (relabel H σ).degree x = 9 := fun x => by
      rw [show x = σ (σ.symm x) by simp, relabel_degree, hreg]
    refine ⟨relabel H σ, inferInstance, h1, h2, hc, Or.inl ⟨hdeg, ?_, hm.mtfc, ?_⟩⟩
    · intro y; rw [hN y, hreg 0]
    · exact (regular_nine_delNbhd _ h1 h2 hdeg 0).2.2.1
  · push Not at hreg
    obtain ⟨v, hv⟩ := theoremA_mtf H hH hαH' hF1 hF2 hreg
    obtain ⟨σ, hσv, hN⟩ := exists_relabel (G := H) v
    obtain ⟨h1, h2, hm, hc⟩ := hrel σ
    have hdeg0 : (relabel H σ).degree 0 = H.degree v := by rw [← hσv, relabel_degree]
    have hh0 : #(delNbhd (relabel H σ) 0).edgeFinset = #(delNbhd H v).edgeFinset := by
      rw [← hσv, relabel_delNbhd σ h3H v]
    have hdegs : ∀ x, 6 ≤ (relabel H σ).degree x ∧ (relabel H σ).degree x ≤ 9 := fun x =>
      ⟨hm.six_le_degree _ h2 x, degree_le_nine _ h1 h2 x⟩
    refine ⟨relabel H σ, inferInstance, h1, h2, hc, Or.inr ?_⟩
    rcases hv with ⟨hd9, he⟩ | ⟨hd8, he⟩
    · refine Or.inr ⟨hm.mtfc, by rw [hdeg0, hd9], fun y => by rw [hN y, hd9], by omega, hdegs⟩
    · refine Or.inl ⟨hm.mtfc, by rw [hdeg0, hd8], fun y => by rw [hN y, hd8], by omega, hdegs⟩

end R310
