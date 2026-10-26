/-
Lemma R7 and the R(7) cover of `notes/cases_local.md` (agent `cases`; confirmed by `critic`).

Lemma R7: in a 9-regular (3,10,40)-graph, if `u, v` are non-adjacent with 7 common neighbours,
then with `A = N(u) \ N(v)`, `B = N(v) \ N(u)`: `|A| = |B| = 2`, every vertex of `A` is
adjacent to every vertex of `B`, and `X = V \ (N[u] ∪ N[v])` (27 vertices) spans exactly 85 edges.
Outside fact: `e(3,8,27) ≥ 85` ([D-E8], [GR] Table 3), hypothesis `EdgeLowerBound 8 27 85`.
-/
import R310.Rc7
import R310.Structure

open Finset

set_option linter.unusedSectionVars false

namespace R310.R7

open R310 R310.Files SimpleGraph

variable {G : SimpleGraph (Fin 40)} [DecidableRel G.Adj]

/-- Common neighbours of distinct vertices of an independent-neighbourhood graph: if `b ~ v` then
`N(u) ∩ N(b)` avoids `N(v)` (triangle-free). -/
theorem inter_sub (h3 : G.CliqueFree 3) {u v b : Fin 40} (hvb : G.Adj v b) :
    G.neighborFinset u ∩ G.neighborFinset b ⊆ G.neighborFinset u \ G.neighborFinset v := by
  intro x hx
  simp only [mem_inter, mem_neighborFinset, mem_sdiff] at hx ⊢
  refine ⟨hx.1, fun hvx => h3 {v, b, x} (is3Clique_triple_iff.2 ⟨hvb, hvx, hx.2⟩)⟩

/-- **Lemma R7, counting part** (no relabelling). -/
theorem r7_count (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hreg : ∀ x, G.degree x = 9)
    (hE : EdgeLowerBound 8 27 85) {u v : Fin 40} (huv : u ≠ v) (hn : ¬ G.Adj u v)
    (hc : #(G.neighborFinset u ∩ G.neighborFinset v) = 7) :
    (∀ b, G.Adj v b → ¬ G.Adj u b →
      G.neighborFinset u ∩ G.neighborFinset b = G.neighborFinset u \ G.neighborFinset v) ∧
    #(delNbhd (delNbhd G u) ⟨v, by simp [mem_outside, Ne.symm huv, hn]⟩).edgeFinset = 85 := by
  have hvo : v ∈ outside G u := by simp [mem_outside, Ne.symm huv, hn]
  set v' : (outside G u : Set (Fin 40)) := ⟨v, hvo⟩ with hv'
  have h3H : (delNbhd G u).CliqueFree 3 := cliqueFree_delNbhd h3 u
  -- degrees in H: deg_H y + c_u(y) = 9
  have hdH : ∀ y : (outside G u : Set (Fin 40)), (delNbhd G u).degree y + nbrIn G u y = 9 := fun y => by
    have := degree_eq_degree_delNbhd_add (G := G) u y; rw [hreg] at this; omega
  have hcv : nbrIn G u v = 7 := by rw [nbrIn_eq_card_inter, hc]
  have hdv : (delNbhd G u).degree v' = 2 := by have := hdH v'; simp only [hv'] at this; omega
  have heH : #(delNbhd G u).edgeFinset = 99 := (regular_nine_delNbhd G h3 hα hreg u).2.2.1
  have hcardH : Fintype.card (outside G u : Set (Fin 40)) = 30 :=
    (regular_nine_delNbhd G h3 hα hreg u).2.1
  -- X = H - N[v'] has 27 vertices and α ≤ 7
  have hcX := card_delNbhd_verts (G := (delNbhd G u)) v'
  rw [hcardH, hdv] at hcX
  have hαH := indepNum_delNbhd_add_one_le (G := G) u
  have hαX := indepNum_delNbhd_add_one_le (G := (delNbhd G u)) v'
  have heX : 85 ≤ #(delNbhd (delNbhd G u) v').edgeFinset :=
    hE.le_card_edgeFinset (by omega) _ (cliqueFree_delNbhd h3H v') (by omega)
  -- L2 in H at v'
  have hL2 := card_edgeFinset_delNbhd_add_sum_degree h3H (G := (delNbhd G u)) v'
  rw [heH] at hL2
  -- each b ∈ N_H(v') has c_u(b) ≤ 2
  have hAcard : #(G.neighborFinset u \ G.neighborFinset v) = 2 := by
    have := card_sdiff_add_card_inter (G.neighborFinset u) (G.neighborFinset v)
    rw [hc, card_neighborFinset_eq_degree, hreg] at this; omega
  have hle2 : ∀ b ∈ (delNbhd G u).neighborFinset v', nbrIn G u b ≤ 2 := by
    intro b hb
    rw [mem_neighborFinset] at hb
    have hvb : G.Adj v b := by simpa [hv'] using hb
    rw [nbrIn_eq_card_inter, ← hAcard]
    exact card_le_card (inter_sub h3 hvb)
  -- sum over the two neighbours: ∑ deg_H b ≥ 14, so equality everywhere
  have hsum : ∑ b ∈ (delNbhd G u).neighborFinset v', (delNbhd G u).degree b ≥ 14 := by
    have : ∑ b ∈ (delNbhd G u).neighborFinset v', (7 : ℕ) ≤ ∑ b ∈ (delNbhd G u).neighborFinset v', (delNbhd G u).degree b :=
      sum_le_sum fun b hb => by have := hdH b; have := hle2 b hb; omega
    rw [sum_const, card_neighborFinset_eq_degree, hdv] at this
    simpa using this
  have hsum_eq : ∑ b ∈ (delNbhd G u).neighborFinset v', (delNbhd G u).degree b = 14 := by omega
  have heq2 : ∀ b ∈ (delNbhd G u).neighborFinset v', nbrIn G u b = 2 := by
    intro b hb
    by_contra hne
    have hlt : nbrIn G u b < 2 := lt_of_le_of_ne (hle2 b hb) hne
    have : ∑ b' ∈ (delNbhd G u).neighborFinset v', (delNbhd G u).degree b' >
        ∑ b' ∈ (delNbhd G u).neighborFinset v', (7 : ℕ) := by
      apply sum_lt_sum (fun b' hb' => by have := hdH b'; have := hle2 b' hb'; omega)
      exact ⟨b, hb, by have := hdH b; omega⟩
    rw [sum_const, card_neighborFinset_eq_degree, hdv] at this
    rw [smul_eq_mul] at this; omega
  refine ⟨fun b hvb hub => ?_, by omega⟩
  -- b is a neighbour of v' in H
  have hbo : b ∈ outside G u := by
    simp only [mem_outside]
    exact ⟨fun h => hn (h ▸ hvb.symm), hub⟩
  have hbN : (⟨b, hbo⟩ : (outside G u : Set (Fin 40))) ∈ (delNbhd G u).neighborFinset v' := by
    rw [mem_neighborFinset]; simpa [hv'] using hvb
  have h2 := heq2 _ hbN
  rw [nbrIn_eq_card_inter] at h2
  exact eq_of_subset_of_card_le (inter_sub h3 hvb) (by simp only at h2; omega)

/-- Edges of the nested induced graph `(G - N[u]) - N[v]` are the edges of `G` inside
`V \ (N[u] ∪ N[v])`. -/
theorem card_nested (u v : Fin 40) (hvo : v ∈ outside G u) :
    #(delNbhd (delNbhd G u) ⟨v, hvo⟩).edgeFinset =
      #{e ∈ G.edgeFinset | ∀ x ∈ e, x ∈ outside2 G u v} := by
  have mem2 : ∀ y : (outside G u : Set (Fin 40)),
      y ∈ outside (delNbhd G u) ⟨v, hvo⟩ ↔ y.val ∈ outside2 G u v := by
    intro y
    have hy := mem_outside.1 (mem_coe.1 y.2)
    simp only [mem_outside, mem_outside2, ne_eq, comap_adj, Function.Embedding.coe_subtype]
    constructor
    · rintro ⟨h1, h2⟩; exact ⟨hy, fun h => h1 (Subtype.ext h), h2⟩
    · rintro ⟨-, h1, h2⟩; exact ⟨fun h => h1 (congrArg Subtype.val h), h2⟩
  let φ : delNbhd (delNbhd G u) ⟨v, hvo⟩ ≃g G.induce (outside2 G u v : Set (Fin 40)) :=
    { toFun := fun y => ⟨y.1.1, mem_coe.2 ((mem2 y.1).1 (mem_coe.1 y.2))⟩
      invFun := fun x => ⟨⟨x.1, mem_coe.2 (mem_outside.2 (mem_outside2.1 (mem_coe.1 x.2)).1)⟩,
        mem_coe.2 ((mem2 _).2 (mem_coe.1 x.2))⟩
      left_inv := fun y => rfl
      right_inv := fun x => rfl
      map_rel_iff' := Iff.rfl }
  have h1 := Iso.card_edgeFinset_eq φ
  have h2 := card_filter_edgeFinset_toFinset_subset (G := G) (outside2 G u v)
  have h3 : ({e ∈ G.edgeFinset | ∀ x ∈ e, x ∈ outside2 G u v} : Finset (Sym2 (Fin 40))) =
      {e ∈ G.edgeFinset | e.toFinset ⊆ outside2 G u v} :=
    filter_congr fun e _ => by simp only [subset_iff, Sym2.mem_toFinset]
  rw [h3, h2]
  convert h1 using 2

/-- A permutation of `Fin 40` mapping each piece of a partition onto the corresponding target
(targets pairwise disjoint, same sizes). -/
theorem exists_perm_partition {k : ℕ} (P T : Fin k → Finset (Fin 40)) (hP : ∀ x, ∃ i, x ∈ P i)
    (hPd : ∀ i j, i ≠ j → Disjoint (P i) (P j)) (hTd : ∀ i j, i ≠ j → Disjoint (T i) (T j))
    (hc : ∀ i, #(P i) = #(T i)) :
    ∃ σ : Equiv.Perm (Fin 40), ∀ i x, x ∈ P i ↔ σ x ∈ T i := by
  classical
  let e : ∀ i, { x // x ∈ P i } ≃ { y // y ∈ T i } := fun i => Finset.equivOfCardEq (hc i)
  let idx : Fin 40 → Fin k := fun x => (hP x).choose
  have hidx : ∀ x, x ∈ P (idx x) := fun x => (hP x).choose_spec
  let f : Fin 40 → Fin 40 := fun x => (e (idx x) ⟨x, hidx x⟩).1
  have hfT : ∀ x, f x ∈ T (idx x) := fun x => (e (idx x) ⟨x, hidx x⟩).2
  have uniqP : ∀ x i, x ∈ P i → i = idx x := fun x i hx => by
    by_contra hne; exact Finset.disjoint_left.1 (hPd i (idx x) hne) hx (hidx x)
  have uniqT : ∀ y i j, y ∈ T i → y ∈ T j → i = j := fun y i j hi hj => by
    by_contra hne; exact Finset.disjoint_left.1 (hTd i j hne) hi hj
  have key : ∀ x y (i j : Fin k) (hx : x ∈ P i) (hy : y ∈ P j),
      (e i ⟨x, hx⟩).1 = (e j ⟨y, hy⟩).1 → x = y := by
    intro x y i j hx hy h
    have hij : i = j := uniqT _ i j (e i ⟨x, hx⟩).2 (h ▸ (e j ⟨y, hy⟩).2)
    subst hij
    have := (e i).injective (Subtype.ext h)
    simpa using this
  have hinj : Function.Injective f := fun x y h => key x y _ _ (hidx x) (hidx y) h
  let σ := Equiv.ofBijective f (Finite.injective_iff_bijective.1 hinj)
  refine ⟨σ, fun i x => ⟨fun hx => ?_, fun hx => ?_⟩⟩
  · have := hfT x; rw [← uniqP x i hx] at this; exact this
  · have := uniqT _ i (idx x) hx (hfT x); rw [this]; exact hidx x

/-- Target blocks `{0}, {1..7}, {8,9}, {10}, {11,12}, {13..39}`. -/
def Tb : Fin 6 → Finset (Fin 40) :=
  ![univ.filter (fun y : Fin 40 => y.val = 0), univ.filter (fun y : Fin 40 => 1 ≤ y.val ∧ y.val ≤ 7),
    univ.filter (fun y : Fin 40 => 8 ≤ y.val ∧ y.val ≤ 9), univ.filter (fun y : Fin 40 => y.val = 10),
    univ.filter (fun y : Fin 40 => 11 ≤ y.val ∧ y.val ≤ 12), univ.filter (fun y : Fin 40 => 13 ≤ y.val)]

theorem Tb_disj : ∀ i j : Fin 6, i ≠ j → Disjoint (Tb i) (Tb j) := by decide

theorem Tb_card : (fun i => #(Tb i)) = ![1, 7, 2, 1, 2, 27] := by decide

/-- **R(7) cover.** Let `G` be a 9-regular (3,10,40)-graph with non-adjacent `u ≠ v` having 7
common neighbours. Assume `R(3,8) ≤ 28` (F2) and `e(3,8,27) ≥ 85` ([D-E8]). Then some graph
satisfies the R(7) case formula `PRc7` (cube_R.opb + Rc7b/case.opb). -/
theorem r7_cover (hF2 : FactF2) (hE : EdgeLowerBound 8 27 85) (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9) (hreg : ∀ x, G.degree x = 9) {u v : Fin 40} (huv : u ≠ v)
    (hn : ¬ G.Adj u v) (hc : #(G.neighborFinset u ∩ G.neighborFinset v) = 7) :
    ∃ G' : SimpleGraph (Fin 40), ∃ _ : DecidableRel G'.Adj, Rc7.PRc7 G' := by
  classical
  obtain ⟨hAB, hX⟩ := r7_count h3 hα hreg hE huv hn hc
  have hvo : v ∈ outside G u := by simp [mem_outside, Ne.symm huv, hn]
  rw [card_nested u v hvo] at hX
  let P : Fin 6 → Finset (Fin 40) :=
    ![{u}, G.neighborFinset u ∩ G.neighborFinset v, G.neighborFinset u \ G.neighborFinset v, {v},
      G.neighborFinset v \ G.neighborFinset u, outside2 G u v]
  have hnu : ∀ x, G.Adj u x → x ≠ u := fun x h e => G.loopless.irrefl u (e ▸ h)
  have hnv : ∀ x, G.Adj v x → x ≠ v := fun x h e => G.loopless.irrefl v (e ▸ h)
  have hPc : ∀ x, ∃ i, x ∈ P i := by
    intro x
    by_cases h1 : x = u; · exact ⟨0, by simp [P, h1]⟩
    by_cases h2 : x = v; · exact ⟨3, by simp [P, h2]⟩
    by_cases hu : G.Adj u x
    · by_cases hv : G.Adj v x
      · exact ⟨1, by simp [P, hu, hv]⟩
      · exact ⟨2, by simp [P, hu, hv]⟩
    · by_cases hv : G.Adj v x
      · exact ⟨4, by simp [P, hu, hv]⟩
      · exact ⟨5, by simp [P, mem_outside2, h1, h2, hu, hv]⟩
  have hPd : ∀ i j, i ≠ j → Disjoint (P i) (P j) := by
    intro i j hij
    rw [Finset.disjoint_left]
    intro x hi hj
    fin_cases i <;> fin_cases j <;> simp_all [P, mem_outside2] <;>
      first | exact hn hi | exact hn hj.symm | exact hn hi.symm | exact hnu _ hi rfl | exact hnv _ hj rfl |
        (subst_vars; simp_all) | skip
  -- sizes
  have hcu : #(G.neighborFinset u) = 9 := by rw [card_neighborFinset_eq_degree, hreg]
  have hcv : #(G.neighborFinset v) = 9 := by rw [card_neighborFinset_eq_degree, hreg]
  have hA : #(G.neighborFinset u \ G.neighborFinset v) = 2 := by
    have := card_sdiff_add_card_inter (G.neighborFinset u) (G.neighborFinset v); omega
  have hB : #(G.neighborFinset v \ G.neighborFinset u) = 2 := by
    have := card_sdiff_add_card_inter (G.neighborFinset v) (G.neighborFinset u)
    rw [inter_comm] at this; omega
  have hXc : #(outside2 G u v) = 27 := by
    have := card_outside2_add (G := G) huv hn; rw [hreg, hreg, hc] at this; simp at this; omega
  have hTc := fun i => congrFun Tb_card i
  have hcard : ∀ i, #(P i) = #(Tb i) := by
    intro i; rw [hTc i]; fin_cases i <;> simp [P, hc, hA, hB, hXc]
  obtain ⟨σ, hσ⟩ := exists_perm_partition P Tb hPc hPd Tb_disj hcard
  have hs : ∀ i y, y ∈ Tb i ↔ σ.symm y ∈ P i := fun i y => by rw [hσ]; simp
  -- facts about σ⁻¹ on the target blocks
  have m0 : σ.symm 0 = u := by have := (hs 0 0).1 (by simp [Tb]); simpa [P] using this
  have m10 : σ.symm 10 = v := by have := (hs 3 10).1 (by simp [Tb]); simpa [P] using this
  have mT : ∀ (y : Fin 40), (1 ≤ y.val ∧ y.val ≤ 9 ↔ G.Adj u (σ.symm y)) ∧
      (1 ≤ y.val ∧ y.val ≤ 7 ↔ G.Adj u (σ.symm y) ∧ G.Adj v (σ.symm y)) ∧
      (8 ≤ y.val ∧ y.val ≤ 9 ↔ G.Adj u (σ.symm y) ∧ ¬ G.Adj v (σ.symm y)) ∧
      (11 ≤ y.val ∧ y.val ≤ 12 ↔ G.Adj v (σ.symm y) ∧ ¬ G.Adj u (σ.symm y)) ∧
      (13 ≤ y.val ↔ σ.symm y ∈ outside2 G u v) := by
    intro y
    have h1 := hs 1 y; have h2 := hs 2 y; have h4 := hs 4 y; have h5 := hs 5 y
    simp only [Tb, P, Matrix.cons_val_one, Matrix.head_cons, Matrix.cons_val_two,
      Matrix.tail_cons, Matrix.cons_val, mem_filter, mem_univ, true_and, mem_inter,
      mem_sdiff, mem_neighborFinset] at h1 h2 h4 h5
    refine ⟨?_, h1, h2, h4, h5⟩
    constructor
    · intro hy
      by_cases h7 : y.val ≤ 7
      · exact (h1.1 ⟨hy.1, h7⟩).1
      · exact (h2.1 ⟨by omega, hy.2⟩).1
    · intro hu
      by_cases hv : G.Adj v (σ.symm y)
      · have := h1.2 ⟨hu, hv⟩; omega
      · have := h2.2 ⟨hu, hv⟩; omega
  let G' := relabel G σ
  have h3' : G'.CliqueFree 3 := relabel_cliqueFree σ h3
  have hα' : G'.indepNum ≤ 9 := (relabel_indepNum σ).trans hα
  have hadj : ∀ a b, G'.Adj a b ↔ G.Adj (σ.symm a) (σ.symm b) := fun a b => Iff.rfl
  have hdeg' : ∀ x, G'.degree x = 9 := fun x => by
    rw [show x = σ (σ.symm x) by simp, relabel_degree, hreg]
  have hmtf' : IsMTF G' := isMTF_of_regular_nine G' h3' hα' hdeg'
  -- A × B complete
  have hab : ∀ a b : Fin 40, G.Adj u a → ¬ G.Adj v a → G.Adj v b → ¬ G.Adj u b → G.Adj a b := by
    intro a b hua hva hvb hub
    have := hAB b hvb hub
    have ha : a ∈ G.neighborFinset u ∩ G.neighborFinset b := by
      rw [this]; simp [hua, hva]
    simp only [mem_inter, mem_neighborFinset] at ha
    exact ha.2.symm
  have unit : ∀ a b : Fin 40, (8 ≤ a.val ∧ a.val ≤ 10) → (11 ≤ b.val ∧ b.val ≤ 12) → G'.Adj a b := by
    intro a b ha hb
    rw [hadj]
    obtain ⟨-, -, -, hb', -⟩ := mT b
    obtain ⟨hbv, hbu⟩ := hb'.1 hb
    by_cases h10 : a.val = 10
    · rw [show a = 10 from Fin.ext h10, m10]; exact hbv
    · obtain ⟨-, -, ha', -, -⟩ := mT a
      obtain ⟨hau, hav⟩ := ha'.1 ⟨ha.1, by omega⟩
      exact hab _ _ hau hav hbv hbu
  refine ⟨G', inferInstance, h3', hα', ⟨hdeg', fun y => ?_, hmtf'.mtfc,
    (regular_nine_delNbhd G' h3' hα' hdeg' 0).2.2.1⟩,
    unit 10 11 (by simp) (by simp), unit 10 12 (by simp) (by simp),
    unit 8 11 (by simp) (by simp), unit 8 12 (by simp) (by simp), unit 9 11 (by simp) (by simp),
    unit 9 12 (by simp) (by simp), ?_, ?_, ?_⟩
  · rw [hadj, m0]; exact ((mT y).1).symm
  · intro i hi1 hi9
    rw [hadj, m10]
    obtain ⟨h19, h17, -, -, -⟩ := mT i
    have hu := h19.1 ⟨hi1, hi9⟩
    exact ⟨fun hv => (h17.2 ⟨hu, hv⟩).2, fun h => (h17.1 ⟨hi1, h⟩).2⟩
  · intro a b hab
    by_cases had : G'.Adj a b
    · have : G'.neighborFinset a ∩ G'.neighborFinset b = ∅ := by
        ext w
        simp only [mem_inter, mem_neighborFinset, Finset.notMem_empty, iff_false, not_and]
        intro haw hbw
        exact h3' {a, b, w} (is3Clique_triple_iff.2 ⟨had, haw, hbw⟩)
      rw [this]; simp
    · have := pair_lemma G' h3' hα' hF2 hab had
      rw [hdeg', hdeg'] at this; omega
  · unfold Rc7.blockEdges
    rw [← hX]
    have h13 : ∀ y : Fin 40, 13 ≤ y.val ↔ σ.symm y ∈ outside2 G u v := fun y => (mT y).2.2.2.2
    refine card_bij (fun e _ => e.map σ.symm) ?_ ?_ ?_
    · intro e he
      induction e using Sym2.ind with
      | _ a b =>
        simp only [mem_filter, mem_edgeFinset, mem_edgeSet, Sym2.map_mk, Sym2.mem_iff,
          forall_eq_or_imp, forall_eq] at he ⊢
        exact ⟨(hadj a b).1 he.1, (h13 a).1 he.2.1, (h13 b).1 he.2.2⟩
    · intro e₁ _ e₂ _ heq
      exact Sym2.map.injective σ.symm.injective heq
    · intro e he
      refine ⟨e.map σ, ?_, by simp [Sym2.map_map]⟩
      induction e using Sym2.ind with
      | _ a b =>
        simp only [mem_filter, mem_edgeFinset, mem_edgeSet, Sym2.map_mk, Sym2.mem_iff,
          forall_eq_or_imp, forall_eq] at he ⊢
        refine ⟨(hadj _ _).2 (by simpa using he.1), (h13 _).2 (by simpa using he.2.1),
          (h13 _).2 (by simpa using he.2.2)⟩

/-- **R(7) conclusion.** If the certified SAT run shows that no assignment satisfies `PRc7` together
with SB clauses whose witnesses preserve the blocks `1:7,2,1,2,27` and that are valid (checked by
`sbcheck`, `Gen.checkGB_sound`), then in every 9-regular (3,10,40)-graph all non-adjacent pairs
have at most 6 common neighbours. Hypotheses: F2, `e(3,8,27) ≥ 85`. -/
theorem no_codeg7 (hF2 : FactF2) (hE : EdgeLowerBound 8 27 85) (better : ℕ → ℕ → Prop)
    (hb : better = (· < ·) ∨ better = (· > ·)) (val : Gen.AssignG 40 → ℕ)
    (SB : List (Gen.SBClauseG 40))
    (hblk : ∀ C ∈ SB, ∀ v : Fin 40, Gen.blockOf Rc7.blk7 (C.wit v).val = Gen.blockOf Rc7.blk7 v.val)
    (hP : ∀ C ∈ SB, Gen.SBValidG better val C)
    (hunsat : ¬ ∃ x : Gen.AssignG 40, Rc7.PRc7 (Gen.graphOfG x) ∧
      ∀ C ∈ SB, (clause C.lits).sat (Gen.valId x))
    (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hreg : ∀ x, G.degree x = 9)
    {u v : Fin 40} (huv : u ≠ v) (hn : ¬ G.Adj u v) :
    #(G.neighborFinset u ∩ G.neighborFinset v) ≤ 6 := by
  by_contra hlt
  have h7 := pair_lemma G h3 hα hF2 huv hn
  rw [hreg, hreg] at h7
  obtain ⟨G', inst, hG'⟩ := r7_cover hF2 hE h3 hα hreg huv hn (by omega)
  exact hunsat (Rc7.lexleader_rc7 better hb val SB hblk hP G' hG')

end R310.R7
