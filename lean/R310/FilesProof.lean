/-
The Cover Lemma for the cube files `R310.Files.cubeR/S8/N` (exact constraint lists, cert's
variable numbering), and the encoding theorem for TRI + IS.
-/
import R310.Files
import R310.Encoding

open Finset

set_option linter.unusedSectionVars false
set_option linter.deprecated false

namespace R310.Files

open R310 R310.Enc

/-! ### Variable ids -/

theorem tri_step : ∀ j < 40, ∀ j' < 40, j < j' → j * (j - 1) / 2 + j ≤ j' * (j' - 1) / 2 := by
  decide

theorem tri_le : ∀ j < 40, j * (j - 1) / 2 + j ≤ 780 := by decide

theorem xid_inj {i j i' j' : ℕ} (hij : i < j) (hij' : i' < j') (hj : j < 40) (hj' : j' < 40)
    (h : xid i j = xid i' j') : i = i' ∧ j = j' := by
  unfold xid at h
  rcases lt_trichotomy j j' with hlt | rfl | hlt
  · have := tri_step j hj j' hj' hlt; omega
  · omega
  · have := tri_step j' hj' j hj hlt; omega

theorem xid_le {i j : ℕ} (hij : i < j) (hj : j < 40) : xid i j ≤ 780 := by
  have := tri_le j hj; unfold xid; omega

theorem cid_r_lt {i j l : ℕ} (hij : i < j) (hj : j < 40) (hl : l < 40) (hli : l ≠ i) (hlj : l ≠ j) :
    l - (if i < l then 1 else 0) - (if j < l then 1 else 0) < 38 := by
  split_ifs <;> omega

theorem cid_gt {i j l : ℕ} : 780 < cid i j l := by unfold cid; omega

theorem cid_inj {i j l i' j' l' : ℕ} (hij : i < j) (hj : j < 40) (hl : l < 40) (hli : l ≠ i)
    (hlj : l ≠ j) (hij' : i' < j') (hj' : j' < 40) (hl' : l' < 40) (hli' : l' ≠ i')
    (hlj' : l' ≠ j') (h : cid i j l = cid i' j' l') : i = i' ∧ j = j' ∧ l = l' := by
  have hr := cid_r_lt hij hj hl hli hlj
  have hr' := cid_r_lt hij' hj' hl' hli' hlj'
  unfold cid at h
  have hp : j * (j - 1) / 2 + i = j' * (j' - 1) / 2 + i' := by omega
  obtain ⟨rfl, rfl⟩ := xid_inj hij hij' hj hj' (by unfold xid; omega)
  refine ⟨rfl, rfl, ?_⟩
  have : l - (if i < l then 1 else 0) - (if j < l then 1 else 0) =
      l' - (if i < l' then 1 else 0) - (if j < l' then 1 else 0) := by omega
  split_ifs at this <;> omega

/-! ### The assignment of a graph assignment `x`, with MTF aux values -/

/-- Values of all variables: `x(i,j)` on edge ids, `x(i,l) ∧ x(j,l)` on `c(i,j,l)`. -/
noncomputable def assignN (x : Assign) : ℕ → Bool := fun n =>
  if h : ∃ p : Fin 40 × Fin 40, p.1 < p.2 ∧ xid p.1 p.2 = n then x h.choose.1 h.choose.2
  else if h' : ∃ t : Fin 40 × Fin 40 × Fin 40, t.1 < t.2.1 ∧ t.2.2 ≠ t.1 ∧ t.2.2 ≠ t.2.1 ∧
      cid t.1 t.2.1 t.2.2 = n then
    edge x h'.choose.1 h'.choose.2.2 && edge x h'.choose.2.1 h'.choose.2.2
  else false

variable (x : Assign)

theorem assignN_x (i j : Fin 40) (hij : i < j) : assignN x (xid i j) = x i j := by
  have hex : ∃ p : Fin 40 × Fin 40, p.1 < p.2 ∧ xid p.1 p.2 = xid i j := ⟨(i, j), hij, rfl⟩
  unfold assignN
  rw [dite_cond_eq_true (eq_true hex)]
  obtain ⟨h1, h2⟩ := hex.choose_spec
  obtain ⟨e1, e2⟩ := xid_inj (Fin.lt_def.1 h1) (Fin.lt_def.1 hij) hex.choose.2.2 j.2 h2
  have : hex.choose = (i, j) := Prod.ext (Fin.ext e1) (Fin.ext e2)
  rw [this]

theorem assignN_xU (i l : Fin 40) (hil : i ≠ l) : assignN x (xidU i l) = edge x i l := by
  unfold xidU edge
  rcases lt_or_gt_of_ne hil with h | h
  · rw [if_pos (Fin.lt_def.1 h), assignN_x x i l h, if_pos h]
  · rw [if_neg (by have := Fin.lt_def.1 h; omega), assignN_x x l i h, if_neg (not_lt.2 h.le),
      if_pos h]

theorem assignN_c (i j l : Fin 40) (hij : i < j) (hli : l ≠ i) (hlj : l ≠ j) :
    assignN x (cid i j l) = (edge x i l && edge x j l) := by
  have hno : ¬ ∃ p : Fin 40 × Fin 40, p.1 < p.2 ∧ xid p.1 p.2 = cid i j l := by
    rintro ⟨p, hp, he⟩
    have := xid_le (Fin.lt_def.1 hp) p.2.2
    have := cid_gt (i := i) (j := j) (l := l)
    omega
  have hex : ∃ t : Fin 40 × Fin 40 × Fin 40, t.1 < t.2.1 ∧ t.2.2 ≠ t.1 ∧ t.2.2 ≠ t.2.1 ∧
      cid t.1 t.2.1 t.2.2 = cid i j l := ⟨(i, j, l), hij, hli, hlj, rfl⟩
  unfold assignN
  rw [dite_cond_eq_false (eq_false hno), dite_cond_eq_true (eq_true hex)]
  obtain ⟨h1, h2, h3, h4⟩ := hex.choose_spec
  obtain ⟨e1, e2, e3⟩ := cid_inj (Fin.lt_def.1 h1) hex.choose.2.1.2 hex.choose.2.2.2
    (fun h => h2 (Fin.ext h)) (fun h => h3 (Fin.ext h)) (Fin.lt_def.1 hij) j.2 l.2
    (fun h => hli (Fin.ext h)) (fun h => hlj (Fin.ext h)) h4
  have : hex.choose = (i, j, l) := Prod.ext (Fin.ext e1) (Prod.ext (Fin.ext e2) (Fin.ext e3))
  rw [this]

/-! ### Satisfaction helpers -/

theorem clause_sat {a : ℕ → Bool} {ls : List Lit} (h : ∃ l ∈ ls, a l.id = l.pos) :
    (clause ls).sat a := by
  obtain ⟨l, hl, hv⟩ := h
  unfold clause PB.sat
  simp only [List.map_map]
  have : 1 ≤ ((fun t : ℕ × Lit => t.1 * t.2.eval a) ∘ fun l => (1, l)) l := by
    simp [Lit.eval, hv]
  exact this.trans (List.single_le_sum (fun _ _ => Nat.zero_le _) _ (List.mem_map_of_mem hl))

theorem clause_sat_iff {a : ℕ → Bool} {ls : List Lit} :
    (clause ls).sat a ↔ ∃ l ∈ ls, a l.id = l.pos := by
  refine ⟨fun h => ?_, clause_sat⟩
  by_contra hno
  push Not at hno
  unfold clause PB.sat at h
  have : (ls.map fun l => (1, l)).map (fun t : ℕ × Lit => t.1 * t.2.eval a) = ls.map fun _ => 0 := by
    simp only [List.map_map]
    apply List.map_congr_left
    intro l hl
    simp [Lit.eval, hno l hl]
  rw [this] at h
  simp at h

theorem mem_R40 {i : ℕ} : i ∈ R40 ↔ i < 40 := by simp [R40]

/-! ### Sums over the generated lists -/

theorem sum_map_filter (l : List ℕ) (p : ℕ → Prop) [DecidablePred p] (f : ℕ → ℕ) :
    ((l.filter p).map f).sum = (l.map fun u => if p u then f u else 0).sum := by
  induction l with
  | nil => simp
  | cons u l ih =>
    by_cases h : p u <;> simp [h, ih]

theorem sum_range_list (n : ℕ) (g : ℕ → ℕ) :
    ((List.range n).map g).sum = ∑ i ∈ Finset.range n, g i := by
  induction n with
  | zero => simp
  | succ n ih => rw [List.range_succ, List.map_append, List.sum_append, ih, Finset.sum_range_succ]; simp

theorem sum_R40 (g : ℕ → ℕ) : (R40.map g).sum = ∑ i : Fin 40, g i := by
  rw [R40, sum_range_list, ← Fin.sum_univ_eq_sum_range]

theorem sum_flatMap' {α : Type*} (l : List ℕ) (g : ℕ → List α) (F : α → ℕ) :
    ((l.flatMap g).map F).sum = (l.map fun i => ((g i).map F).sum).sum := by
  induction l with
  | nil => simp
  | cons u l ih => simp [List.flatMap_cons, List.map_append, List.sum_append, ih]

theorem filterMap_pairs (l : List ℕ) (i : ℕ) (P : ℕ → Prop) [DecidablePred P] :
    l.filterMap (fun j => if P j then some (i, j) else none) = (l.filter P).map fun j => (i, j) := by
  induction l with
  | nil => simp
  | cons u l ih => by_cases h : P u <;> simp [h, ih]

/-- Sum of a function of pairs over `pairsFrom m`. -/
theorem sum_pairsFrom (m : ℕ) (F : ℕ × ℕ → ℕ) :
    ((pairsFrom m).map F).sum =
      ∑ i : Fin 40, ∑ j : Fin 40, if m ≤ (i : ℕ) ∧ (i : ℕ) < j then F (i, j) else 0 := by
  unfold pairsFrom
  rw [sum_flatMap']
  simp only [filterMap_pairs, List.map_map]
  rw [sum_R40]
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [sum_map_filter, sum_R40]
  rfl

theorem sum_neg_add_pos {α : Type*} (L : List α) (a : ℕ → Bool) (id : α → ℕ) :
    (L.map fun p => 1 * (negL (id p)).eval a).sum + (L.map fun p => 1 * (posL (id p)).eval a).sum =
      L.length := by
  induction L with
  | nil => simp
  | cons p L ih =>
    simp only [List.map_cons, List.sum_cons, List.length_cons]
    have : (negL (id p)).eval a + (posL (id p)).eval a = 1 := by
      simp only [Lit.eval, negL, posL]
      rcases Bool.eq_false_or_eq_true (a (id p)) with h | h <;> simp [h]
    omega

theorem pairsFrom_10_length : (pairsFrom 10).length = Nat.choose 30 2 := by decide +kernel
theorem pairsFrom_9_length : (pairsFrom 9).length = Nat.choose 31 2 := by decide +kernel

theorem others1_length : ∀ v < 40, (others1 v).length = 39 := by decide +kernel

/-! ### Each constraint family is satisfied -/

section Sat

variable {x}

theorem tri_sat (hT : TRI x) : ∀ c ∈ triFile, c.sat (assignN x) := by
  intro c hc
  simp only [triFile, List.mem_flatMap, List.mem_filterMap, mem_R40] at hc
  obtain ⟨i, hi, j, hj, k, hk, hc⟩ := hc
  split_ifs at hc with h
  cases hc
  obtain ⟨hij, hjk⟩ := h
  have hTi := hT ⟨i, hi⟩ ⟨j, hj⟩ ⟨k, hk⟩ (Fin.mk_lt_mk.2 hij) (Fin.mk_lt_mk.2 hjk)
  have e1 := assignN_x x ⟨i, hi⟩ ⟨j, hj⟩ (Fin.mk_lt_mk.2 hij)
  have e2 := assignN_x x ⟨i, hi⟩ ⟨k, hk⟩ (Fin.mk_lt_mk.2 (hij.trans hjk))
  have e3 := assignN_x x ⟨j, hj⟩ ⟨k, hk⟩ (Fin.mk_lt_mk.2 hjk)
  simp only at e1 e2 e3
  apply clause_sat
  simp only [List.mem_cons, List.not_mem_nil, or_false, negL]
  simp only [Bool.or_eq_true, Bool.not_eq_true'] at hTi
  rcases hTi with (h1 | h1) | h1
  · exact ⟨_, Or.inl rfl, by rw [e1, h1]⟩
  · exact ⟨_, Or.inr (Or.inl rfl), by rw [e2, h1]⟩
  · exact ⟨_, Or.inr (Or.inr rfl), by rw [e3, h1]⟩

theorem mtf_sat (hm : MTFc (graphOf x)) : ∀ c ∈ mtfFile, c.sat (assignN x) := by
  intro c hc
  simp only [mtfFile, List.mem_flatMap, mem_R40] at hc
  obtain ⟨i, hi, j, hj, hc⟩ := hc
  split_ifs at hc with hij
  swap
  · simp at hc
  set I : Fin 40 := ⟨i, hi⟩
  set J : Fin 40 := ⟨j, hj⟩
  have hIJ : I < J := Fin.mk_lt_mk.2 hij
  rw [List.mem_append, List.mem_flatMap, List.mem_singleton] at hc
  rcases hc with ⟨l, hl, hc⟩ | rfl
  · simp only [others2, List.mem_filter, mem_R40, decide_eq_true_eq] at hl
    obtain ⟨hl40, hli, hlj⟩ := hl
    set Lv : Fin 40 := ⟨l, hl40⟩
    have hLI : Lv ≠ I := fun h => hli (congrArg Fin.val h)
    have hLJ : Lv ≠ J := fun h => hlj (congrArg Fin.val h)
    have ec := assignN_c x I J Lv hIJ hLI hLJ
    have eI := assignN_xU x I Lv hLI.symm
    have eJ := assignN_xU x J Lv hLJ.symm
    simp only [I, J, Lv] at ec eI eJ
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hc
    rcases hc with rfl | rfl | rfl <;> apply clause_sat <;>
      simp only [List.mem_cons, List.not_mem_nil, or_false, negL, posL, exists_eq_or_imp,
        exists_eq_left, ec, eI, eJ] <;>
      cases edge x I Lv <;> cases edge x J Lv <;> simp_all
  · apply clause_sat
    rcases hm I J hIJ.ne with hadj | ⟨w, hw1, hw2⟩
    · refine ⟨posL (xid i j), List.mem_cons_self, ?_⟩
      have := assignN_x x I J hIJ
      simp only [I, J] at this
      simp only [posL, this]
      simpa [graphOf, edge, hIJ] using hadj
    · have hwI : w ≠ I := fun h => (graphOf x).loopless.irrefl I (by rw [h] at hw1; exact hw1)
      have hwJ : w ≠ J := fun h => (graphOf x).loopless.irrefl J (by rw [h] at hw2; exact hw2)
      refine ⟨posL (cid i j w), List.mem_cons_of_mem _ (List.mem_map.2 ⟨w, ?_, rfl⟩), ?_⟩
      · simp only [others2, List.mem_filter, mem_R40, decide_eq_true_eq]
        exact ⟨w.2, fun h => hwI (Fin.ext h), fun h => hwJ (Fin.ext h)⟩
      · have := assignN_c x I J w hIJ hwI hwJ
        simp only [I, J] at this
        simp only [posL, this, Bool.and_eq_true]
        exact ⟨hw1, hw2⟩

theorem nbhd0_sat (d : ℕ) (hN : Nbhd0 (graphOf x) d) : ∀ c ∈ nbhd0File d, c.sat (assignN x) := by
  intro c hc
  simp only [nbhd0File, List.mem_map, List.mem_filter, mem_R40, decide_eq_true_eq] at hc
  obtain ⟨u, ⟨hu, hu1⟩, rfl⟩ := hc
  have h0u : (0 : Fin 40) < ⟨u, hu⟩ := Fin.lt_def.2 (by simp; omega)
  have e := assignN_x x 0 ⟨u, hu⟩ h0u
  simp only [Fin.val_zero] at e
  have hadj := hN ⟨u, hu⟩
  simp only [graphOf, edge, h0u, if_true] at hadj
  apply clause_sat
  split_ifs with hd
  · exact ⟨_, List.mem_cons_self, by simp only [posL, e]; exact hadj.2 ⟨hu1, hd⟩⟩
  · refine ⟨_, List.mem_cons_self, ?_⟩
    simp only [negL, e]
    by_contra h
    simp only [Bool.not_eq_false] at h
    exact hd (hadj.1 h).2

theorem degPos (v : Fin 40) :
    (((others1 v).map fun u => ((1 : ℕ), posL (xidU u v))).map
      fun t => t.1 * t.2.eval (assignN x)).sum = (graphOf x).degree v := by
  rw [List.map_map, others1, sum_map_filter, sum_R40, degree_graphOf, card_filter]
  refine Finset.sum_congr rfl fun u _ => ?_
  by_cases huv : u = v
  · subst huv; simp [edge]
  · have hne : (u : ℕ) ≠ v := fun h => huv (Fin.ext h)
    have := assignN_xU x u v huv
    simp [Function.comp, hne, Lit.eval, posL, this, edge_comm x v u]

theorem degNeg (v : Fin 40) :
    (((others1 v).map fun u => ((1 : ℕ), negL (xidU u v))).map
      fun t => t.1 * t.2.eval (assignN x)).sum = 39 - (graphOf x).degree v := by
  have h := sum_neg_add_pos (others1 v) (assignN x) (fun u => xidU u v)
  have hp := degPos (x := x) v
  rw [List.map_map] at hp
  rw [List.map_map]
  rw [others1_length v v.2] at h
  simp only [Function.comp_def] at hp ⊢
  omega

theorem deg_sat (lo hi : ℕ) (hd : ∀ v, lo ≤ (graphOf x).degree v ∧ (graphOf x).degree v ≤ hi) :
    ∀ c ∈ degFile lo hi, c.sat (assignN x) := by
  intro c hc
  simp only [degFile, List.mem_flatMap, mem_R40, List.mem_cons, List.not_mem_nil, or_false] at hc
  obtain ⟨v, hv, rfl | rfl⟩ := hc
  · have := degPos (x := x) ⟨v, hv⟩
    simp only [PB.sat]
    rw [this]; exact (hd _).1
  · have := degNeg (x := x) ⟨v, hv⟩
    simp only [PB.sat]
    rw [this]; have := (hd ⟨v, hv⟩).2; omega

/-- With `N(0) = {1..d}`, the positive sum over `pairsFrom (d+1)` is `e(H_0)`. -/
theorem h0Pos (d : ℕ) (hN : Nbhd0 (graphOf x) d) :
    ((pairsFrom (d + 1)).map fun p => 1 * (posL (xid p.1 p.2)).eval (assignN x)).sum =
      #(delNbhd (graphOf x) 0).edgeFinset := by
  have hy : ∀ y : Fin 40, (y ≠ 0 ∧ edge x 0 y = false) ↔ d + 1 ≤ y.val := by
    intro y
    have h := hN y
    simp only [graphOf] at h
    constructor
    · rintro ⟨hy0, hy1⟩
      have : y.val ≠ 0 := fun h0 => hy0 (Fin.ext h0)
      by_contra hlt
      rw [hy1] at h
      simp at h
      omega
    · intro hle
      refine ⟨fun h0 => by rw [h0] at hle; simp at hle, ?_⟩
      by_contra hne
      simp only [Bool.not_eq_false] at hne
      have := (h.1 hne).2
      omega
  rw [sum_pairsFrom, h0edges_graphOf, card_filter, Fintype.sum_prod_type]
  refine Finset.sum_congr rfl fun i _ => Finset.sum_congr rfl fun j _ => ?_
  by_cases hc : d + 1 ≤ (i : ℕ) ∧ (i : ℕ) < j
  · have hij : i < j := Fin.lt_def.2 hc.2
    have e := assignN_x x i j hij
    have hi := (hy i).2 hc.1
    have hj := (hy j).2 (by omega)
    simp only [hc, and_self, if_true, one_mul, Lit.eval, posL, e]
    by_cases hx : x i j = true <;> simp [hij, hi, hj, hx]
  · rw [if_neg hc]
    symm
    rw [if_neg]
    rintro ⟨hij, hi0, hi1, -, -, -⟩
    exact hc ⟨(hy i).1 ⟨hi0, hi1⟩, Fin.lt_def.1 hij⟩


theorem h0le_sat (d t : ℕ) (hd : d = 8 ∨ d = 9) (hN : Nbhd0 (graphOf x) d)
    (he : #(delNbhd (graphOf x) 0).edgeFinset ≤ t) : ∀ c ∈ h0leFile d t, c.sat (assignN x) := by
  intro c hc
  simp only [h0leFile, List.mem_singleton] at hc
  subst hc
  have hsum := sum_neg_add_pos (pairsFrom (d + 1)) (assignN x) (fun p => xid p.1 p.2)
  have hp := h0Pos (x := x) d hN
  have hlen : (pairsFrom (d + 1)).length = Nat.choose (39 - d) 2 := by
    rcases hd with rfl | rfl
    · exact pairsFrom_9_length
    · exact pairsFrom_10_length
  simp only [PB.sat, List.map_map, Function.comp_def]
  omega

theorem h0ge_sat (d t : ℕ) (hN : Nbhd0 (graphOf x) d)
    (he : t ≤ #(delNbhd (graphOf x) 0).edgeFinset) : ∀ c ∈ h0geFile d t, c.sat (assignN x) := by
  intro c hc
  simp only [h0geFile, List.mem_singleton] at hc
  subst hc
  have hp := h0Pos (x := x) d hN
  simp only [PB.sat, List.map_map, Function.comp_def]
  omega

theorem isall_of (h : ISc 10 x) : ISall (assignN x) := by
  intro S hS
  obtain ⟨i, hi, j, hj, hij, hx⟩ := h S hS
  exact ⟨i, hi, j, hj, hij, by rw [assignN_x x i j hij, hx]⟩

end Sat

/-- **Cover Lemma for the cube files.** Assume F1, F2. If a (3,10,40)-graph exists, then some
assignment `a` of all variables (edge variables, and MTF aux `c(i,j,l) = x(i,l) ∧ x(j,l)`)
satisfies all IS clauses and every constraint of `cubeR`, of `cubeS8`, or of `cubeN`. -/
theorem cover_files (hF1 : FactF1) (hF2 : FactF2) (G : SimpleGraph (Fin 40))
    (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) :
    ∃ a : ℕ → Bool, ISall a ∧
      ((∀ c ∈ cubeR, c.sat a) ∨ (∀ c ∈ cubeS8, c.sat a) ∨ (∀ c ∈ cubeN, c.sat a)) := by
  obtain ⟨x, ⟨hT, hI⟩, -, hcube⟩ := cover_assign hF1 hF2 G h3 hα
  refine ⟨assignN x, isall_of hI, ?_⟩
  have htri := tri_sat hT
  rcases hcube with hR | hS | hN
  · left
    intro c hc
    simp only [cubeR, List.mem_append] at hc
    rcases hc with ((((hc | hc) | hc) | hc) | hc) | hc
    · exact htri c hc
    · exact mtf_sat hR.mtf c hc
    · exact nbhd0_sat 9 hR.nbhd0 c hc
    · exact deg_sat 9 9 (fun v => by rw [hR.degree v]; omega) c hc
    · exact h0le_sat 9 99 (Or.inr rfl) hR.nbhd0 hR.h0edges.le c hc
    · exact h0ge_sat 9 99 hR.nbhd0 hR.h0edges.ge c hc
  · right; left
    intro c hc
    simp only [cubeS8, List.mem_append] at hc
    rcases hc with (((hc | hc) | hc) | hc) | hc
    · exact htri c hc
    · exact mtf_sat hS.mtf c hc
    · exact nbhd0_sat 8 hS.nbhd0 c hc
    · exact deg_sat 6 9 hS.degree c hc
    · exact h0le_sat 8 96 (Or.inl rfl) hS.nbhd0 hS.h0edges c hc
  · right; right
    intro c hc
    simp only [cubeN, List.mem_append] at hc
    rcases hc with (((hc | hc) | hc) | hc) | hc
    · exact htri c hc
    · exact mtf_sat hN.mtf c hc
    · exact nbhd0_sat 9 hN.nbhd0 c hc
    · exact deg_sat 6 9 hN.degree c hc
    · exact h0le_sat 9 98 (Or.inr rfl) hN.nbhd0 hN.h0edges c hc

/-- The edge assignment read off a full assignment `a`. -/
def edgesOf (a : ℕ → Bool) : Assign := fun i j => a (xid i j)

/-- **Encoding (a1) for the files.** An assignment satisfies all constraints of `triFile` and
all IS clauses iff its graph is a (3,10,40)-graph. -/
theorem tri_is_iff (a : ℕ → Bool) :
    ((∀ c ∈ triFile, c.sat a) ∧ ISall a) ↔
      (graphOf (edgesOf a)).CliqueFree 3 ∧ (graphOf (edgesOf a)).indepNum ≤ 9 := by
  rw [← fdef_iff]
  have hT : (∀ c ∈ triFile, c.sat a) ↔ TRI (edgesOf a) := by
    constructor
    · intro h i j k hij hjk
      have hc := h (clause [negL (xid i j), negL (xid i k), negL (xid j k)]) (by
        simp only [triFile, List.mem_flatMap, List.mem_filterMap, mem_R40]
        exact ⟨i, i.2, j, j.2, k, k.2, by simp [Fin.lt_def.1 hij, Fin.lt_def.1 hjk]⟩)
      rw [clause_sat_iff] at hc
      obtain ⟨l, hl, hv⟩ := hc
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hl
      simp only [edgesOf, Bool.or_eq_true, Bool.not_eq_true']
      rcases hl with rfl | rfl | rfl <;> simp_all [negL]
    · intro h c hc
      simp only [triFile, List.mem_flatMap, List.mem_filterMap, mem_R40] at hc
      obtain ⟨i, hi, j, hj, k, hk, hc⟩ := hc
      split_ifs at hc with hh
      cases hc
      have hTi := h ⟨i, hi⟩ ⟨j, hj⟩ ⟨k, hk⟩ (Fin.mk_lt_mk.2 hh.1) (Fin.mk_lt_mk.2 hh.2)
      simp only [edgesOf, Bool.or_eq_true, Bool.not_eq_true'] at hTi
      apply clause_sat
      simp only [List.mem_cons, List.not_mem_nil, or_false, negL]
      rcases hTi with (h1 | h1) | h1
      · exact ⟨_, Or.inl rfl, h1⟩
      · exact ⟨_, Or.inr (Or.inl rfl), h1⟩
      · exact ⟨_, Or.inr (Or.inr rfl), h1⟩
  have hI : ISall a ↔ ISc 10 (edgesOf a) := Iff.rfl
  rw [hT, hI]
  rfl

end R310.Files
