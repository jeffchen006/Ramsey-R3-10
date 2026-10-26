/-
A per-clause checker for the SB condition of `R310.LexLeader`, with a soundness proof.

For an SB clause `C` (literals over the colex edge ids `1..780`) with witness `π` (given as the
maps `p = π` and `pinv = π⁻¹`), `checkSB minOrder pos d C.lits p pinv = true` implies
`InGamma d π` and `SBValid better (valOf pos) C`, with `better = (· < ·)` if `minOrder`
(SMS, MathCheck) and `(· > ·)` otherwise (satcore, cert's demo).

Method (as cert/check_sb.py): `D(x) = val(x) - val(π x)` is a linear form `∑_t W t · x_t` in the
780 edge bits. With `α` = the bits fixed by "x falsifies C", the clause is valid iff the minimum
(`minOrder`: of `D`, must be `> 0`) or maximum (must be `< 0`) over the free bits has the right
sign; these are `lowSum` and `highSum`.
-/
import R310.SBTables

open Finset

set_option linter.unusedSectionVars false
set_option linter.deprecated false

namespace R310.SB

open R310 R310.Enc R310.Files

theorem eidx_lt (p : Fin 40 × Fin 40) (h : p.1 ≠ p.2) : eidx p < 780 := by
  unfold eidx
  have hlt : min p.1 p.2 < max p.1 p.2 := by
    rcases lt_or_gt_of_ne h with h' | h'
    · simp [min_eq_left h'.le, max_eq_right h'.le, h']
    · simp [min_eq_right h'.le, max_eq_left h'.le, h']
  have := xid_le (Fin.lt_def.1 hlt) (max p.1 p.2).2
  omega

/-- The bit of the edge with colex index `t`. -/
def bitAt (x : Assign) (t : ℕ) : ℤ := if edge x (pairOf t).1 (pairOf t).2 then 1 else 0

theorem edge_eq_bitAt (x : Assign) (p : Fin 40 × Fin 40) (h : p.1 ≠ p.2) :
    (if edge x p.1 p.2 then (1 : ℤ) else 0) = bitAt x (eidx p) := by
  unfold bitAt eidx
  rcases lt_or_gt_of_ne h with h' | h'
  · rw [min_eq_left h'.le, max_eq_right h'.le, pairOf_xid _ _ h']
  · rw [min_eq_right h'.le, max_eq_left h'.le, pairOf_xid _ _ h', edge_comm]

/-! ### The value and the action -/

/-- `val` for the position list `pos` (first position most significant). -/
def valL : List (Fin 40 × Fin 40) → Assign → ℕ
  | [], _ => 0
  | p :: ps, x => 2 ^ ps.length * (if edge x p.1 p.2 then 1 else 0) + valL ps x

theorem edge_assignOf (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (a b : Fin 40) :
    edge (assignOf G) a b = decide (G.Adj a b) := by
  unfold edge assignOf
  rcases lt_trichotomy a b with h | rfl | h
  · simp [h]
  · simp
  · simp [h, h.not_gt, G.adj_comm]

theorem edge_act (π : Equiv.Perm (Fin 40)) (x : Assign) (a b : Fin 40) :
    edge (act π x) a b = edge x (π.symm a) (π.symm b) := by
  unfold act
  rw [edge_assignOf]
  simp [relabel, graphOf]

theorem valL_act (π : Equiv.Perm (Fin 40)) (x : Assign) (pos : List (Fin 40 × Fin 40)) :
    valL pos (act π x) = valL (pos.map (sig π.symm)) x := by
  induction pos with
  | nil => rfl
  | cons p ps ih => simp [valL, ih, edge_act, sig]

/-! ### The linear form `D` -/

theorem contribsFast_eq (pinv : Fin 40 → Fin 40) (ps : List (Fin 40 × Fin 40)) :
    contribsFast pinv ps.length ps = contribs pinv ps := by
  induction ps with
  | nil => rfl
  | cons p ps ih =>
    simp only [contribsFast, contribs, List.length_cons, Nat.add_sub_cancel, ih,
      Nat.shiftLeft_eq, one_mul]

def lin (cs : List (ℤ × (Fin 40 × Fin 40))) (x : Assign) : ℤ :=
  (cs.map fun c => c.1 * if edge x c.2.1 c.2.2 then 1 else 0).sum

theorem valL_sub (pinv : Fin 40 → Fin 40) (x : Assign) (pos : List (Fin 40 × Fin 40)) :
    (valL pos x : ℤ) - valL (pos.map (sig pinv)) x = lin (contribs pinv pos) x := by
  induction pos with
  | nil => simp [valL, contribs, lin]
  | cons p ps ih =>
    have hstep : (valL (p :: ps) x : ℤ) - valL ((p :: ps).map (sig pinv)) x =
        ((2 ^ ps.length : ℕ) : ℤ) * (if edge x p.1 p.2 then 1 else 0) -
          ((2 ^ ps.length : ℕ) : ℤ) * (if edge x (sig pinv p).1 (sig pinv p).2 then 1 else 0) +
          ((valL ps x : ℤ) - valL (ps.map (sig pinv)) x) := by
      simp only [valL, List.map_cons, List.length_map]
      push_cast
      ring
    have hc : contribs pinv (p :: ps) = if sig pinv p = p then contribs pinv ps else
        ((2 ^ ps.length : ℕ), p) :: (-((2 ^ ps.length : ℕ) : ℤ), sig pinv p) :: contribs pinv ps :=
      rfl
    rw [hstep, ih, hc]
    by_cases h : sig pinv p = p
    · rw [if_pos h, h]; ring
    · rw [if_neg h]
      simp only [lin, List.map_cons, List.sum_cons]
      ring

theorem aggregate_size (cs : List (ℤ × (Fin 40 × Fin 40))) (W : Array ℤ) :
    (aggregate cs W).size = W.size := by
  induction cs generalizing W with
  | nil => rfl
  | cons c cs ih => simp [aggregate, List.foldl_cons] at ih ⊢; rw [ih]; simp

/-- `∑_{t < 780} W[t] · x_t`. -/
def wsumW (W : Array ℤ) (x : Assign) : ℤ := ∑ t ∈ Finset.range 780, W.getD t 0 * bitAt x t

theorem wsumW_modify (W : Array ℤ) (hW : W.size = 780) (i : ℕ) (hi : i < 780) (c : ℤ)
    (x : Assign) : wsumW (W.modify i (· + c)) x = wsumW W x + c * bitAt x i := by
  unfold wsumW
  have : ∀ t ∈ Finset.range 780, (W.modify i (· + c)).getD t 0 * bitAt x t =
      W.getD t 0 * bitAt x t + if t = i then c * bitAt x t else 0 := by
    intro t ht
    rw [Finset.mem_range] at ht
    simp only [Array.getD_eq_getD_getElem?, Array.getElem?_modify]
    by_cases hti : t = i
    · subst hti
      simp [hW, ht]
      ring
    · simp [Ne.symm hti, hti]
  rw [Finset.sum_congr rfl this, Finset.sum_add_distrib, Finset.sum_ite_eq']
  simp [hi]

theorem wsumW_aggregate (cs : List (ℤ × (Fin 40 × Fin 40))) (hcs : ∀ c ∈ cs, c.2.1 ≠ c.2.2)
    (W : Array ℤ) (hW : W.size = 780) (x : Assign) :
    wsumW (aggregate cs W) x = wsumW W x + lin cs x := by
  induction cs generalizing W with
  | nil => simp [aggregate, lin]
  | cons c cs ih =>
    have hc := hcs c (by simp)
    have h2 : aggregate (c :: cs) W = aggregate cs (W.modify (eidx c.2) (· + c.1)) := rfl
    rw [h2, ih (fun c' hc' => hcs c' (by simp [hc'])) _ (by simp [hW]),
      wsumW_modify W hW _ (eidx_lt _ hc), lin, lin, List.map_cons, List.sum_cons,
      edge_eq_bitAt x c.2 hc]
    ring

theorem wsumW_zero (x : Assign) : wsumW (Array.replicate 780 0) x = 0 := by
  unfold wsumW
  apply Finset.sum_eq_zero
  intro t ht
  rw [Finset.mem_range] at ht
  simp [Array.getD_eq_getD_getElem?, ht]

/-! ### Fixed bits from the clause -/

/-- `x` is consistent with `F`. -/
def Consistent (F : Array (Option Bool)) (x : Assign) : Prop :=
  ∀ t < 780, ∀ b, F.getD t none = some b → bitAt x t = if b then 1 else 0

theorem listSum_range (n : ℕ) (g : ℕ → ℤ) :
    ((List.range n).map g).sum = ∑ i ∈ Finset.range n, g i := by
  induction n with
  | zero => simp
  | succ n ih => rw [List.range_succ, List.map_append, List.sum_append, ih, Finset.sum_range_succ]; simp

theorem lowSum_le (W : Array ℤ) (F : Array (Option Bool)) (x : Assign) (hx : Consistent F x) :
    lowSum W F ≤ wsumW W x := by
  unfold lowSum wsumW
  rw [listSum_range]
  apply Finset.sum_le_sum
  intro t ht
  rw [Finset.mem_range] at ht
  have hb : bitAt x t = 0 ∨ bitAt x t = 1 := by unfold bitAt; split_ifs <;> simp
  cases hF : F.getD t none with
  | some b =>
    rw [hx t ht b hF]
    cases b <;> simp
  | none =>
    simp only
    rcases hb with h | h <;> rw [h] <;> simp [min_le_left, min_le_right]

theorem le_highSum (W : Array ℤ) (F : Array (Option Bool)) (x : Assign) (hx : Consistent F x) :
    wsumW W x ≤ highSum W F := by
  unfold highSum wsumW
  rw [listSum_range]
  apply Finset.sum_le_sum
  intro t ht
  rw [Finset.mem_range] at ht
  have hb : bitAt x t = 0 ∨ bitAt x t = 1 := by unfold bitAt; split_ifs <;> simp
  cases hF : F.getD t none with
  | some b =>
    rw [hx t ht b hF]
    cases b <;> simp
  | none =>
    simp only
    rcases hb with h | h <;> rw [h] <;> simp [le_max_left, le_max_right]

/-- The bit of edge id `n ∈ 1..780` under `assignN x`. -/
theorem assignN_bit (x : Assign) (n : ℕ) (h1 : 1 ≤ n) (h2 : n ≤ 780) :
    bitAt x (n - 1) = if assignN x n then 1 else 0 := by
  obtain ⟨hlt, hx⟩ := pairOf_spec (n - 1) (by omega)
  have hn : n = xid (pairOf (n - 1)).1 (pairOf (n - 1)).2 := by omega
  conv_rhs => rw [hn]
  rw [assignN_x x _ _ hlt, bitAt]
  simp [edge, hlt]

/-- Invariant of `fixedOf`: started from an array consistent with a falsifying `x`, the fold
succeeds and stays consistent. -/
theorem fixedOf_spec (x : Assign) :
    ∀ (lits : List Lit) (A : Array (Option Bool)), A.size = 780 → Consistent A x →
      (∀ l ∈ lits, 1 ≤ l.id ∧ l.id ≤ 780) → (∀ l ∈ lits, assignN x l.id ≠ l.pos) →
      ∃ F, lits.foldlM (fun A l => match A.getD (l.id - 1) none with
        | some b => if b = !l.pos then some A else none
        | none => some (A.set! (l.id - 1) (some (!l.pos)))) A = some F ∧ Consistent F x
  | [], A, _, hA, _, _ => ⟨A, rfl, hA⟩
  | l :: ls, A, hs, hA, hid, hfal => by
    obtain ⟨h1, h2⟩ := hid l (by simp)
    have hl := hfal l (by simp)
    have hbit := assignN_bit x l.id h1 h2
    have hval : assignN x l.id = !l.pos := by
      revert hl; cases assignN x l.id <;> cases l.pos <;> simp
    rw [List.foldlM_cons]
    cases hA' : A.getD (l.id - 1) none with
    | some b =>
      have hb := hA (l.id - 1) (by omega) b hA'
      have : b = !l.pos := by
        rw [hbit, hval] at hb
        revert hb; cases b <;> cases l.pos <;> simp
      simp only [this, if_true, Option.bind_some]
      exact fixedOf_spec x ls A hs hA (fun l' h' => hid l' (by simp [h'])) (fun l' h' => hfal l' (by simp [h']))
    | none =>
      simp only [Option.bind_some]
      refine fixedOf_spec x ls _ (by simp [hs]) ?_ (fun l' h' => hid l' (by simp [h']))
        (fun l' h' => hfal l' (by simp [h']))
      intro t ht b hb
      simp only [Array.getD_eq_getD_getElem?, Array.set!_eq_setIfInBounds,
        Array.getElem?_setIfInBounds] at hb
      by_cases htl : l.id - 1 = t
      · subst htl
        simp [hs, ht] at hb
        rw [hbit, hval, hb]
        simp
      · rw [if_neg htl] at hb
        exact hA t ht b (by simpa [Array.getD_eq_getD_getElem?] using hb)

theorem fixedOf_some (x : Assign) (lits : List Lit) (hid : ∀ l ∈ lits, 1 ≤ l.id ∧ l.id ≤ 780)
    (hfal : ∀ l ∈ lits, assignN x l.id ≠ l.pos) : ∃ F, fixedOf lits = some F ∧ Consistent F x :=
  fixedOf_spec x lits _ (by simp) (fun t ht b hb => by
    simp [Array.getD_eq_getD_getElem?, Array.getElem?_replicate, ht] at hb)
    hid hfal

/-! ### The checker -/

/-- **Soundness of the SB checker.** -/
theorem checkSB_sound (minOrder : Bool) (pos : List (Fin 40 × Fin 40)) (d : ℕ) (lits : List Lit)
    (p pinv : Fin 40 → Fin 40) (h : checkSB minOrder pos d lits p pinv = true) :
    ∃ π : Equiv.Perm (Fin 40), (∀ v, π v = p v) ∧ InGamma d π ∧
      SBValid (if minOrder then (· < ·) else (· > ·)) (valL pos) ⟨lits, π⟩ := by
  unfold checkSB at h
  simp only [Bool.and_eq_true, List.all_eq_true, List.mem_finRange, true_implies, beq_iff_eq,
    decide_eq_decide, bne_iff_ne, ne_eq] at h
  obtain ⟨⟨⟨⟨⟨hinv, hp0⟩, hgam⟩, hpos⟩, hid⟩, hmain⟩ := h
  let π : Equiv.Perm (Fin 40) := ⟨p, pinv, fun v => (hinv v).1, fun v => (hinv v).2⟩
  refine ⟨π, fun v => rfl, ⟨hp0, fun u => hgam u⟩, ?_⟩
  intro x hx
  rw [clause_sat_iff] at hx
  push Not at hx
  have hid' : ∀ l ∈ lits, 1 ≤ l.id ∧ l.id ≤ 780 := fun l hl => by simpa using hid l hl
  obtain ⟨F, hF, hcons⟩ := fixedOf_some x lits hid' hx
  rw [hF] at hmain
  simp only [contribsFast_eq] at hmain
  -- `val x - val (π x) = ∑ W x`
  have hsymm : (π.symm : Fin 40 → Fin 40) = pinv := rfl
  have hD : (valL pos x : ℤ) - valL pos (act π x) =
      wsumW (aggregate (contribs pinv pos) (Array.replicate 780 0)) x := by
    rw [valL_act, hsymm, valL_sub,
      wsumW_aggregate _ ?_ (Array.replicate 780 0) (by simp), wsumW_zero, zero_add]
    -- all contribution pairs have distinct ends
    intro c hc
    clear hmain hF
    induction pos with
    | nil => simp [contribs] at hc
    | cons e es ih =>
      have he := hpos e (by simp)
      simp only [contribs] at hc
      split_ifs at hc with hs
      · exact ih (fun e' h' => hpos e' (by simp [h'])) hc
      · simp only [List.mem_cons] at hc
        rcases hc with rfl | rfl | hc
        · exact he
        · simp only [sig]
          intro heq
          have := congrArg p heq
          rw [(hinv _).2, (hinv _).2] at this
          exact he this
        · exact ih (fun e' h' => hpos e' (by simp [h'])) hc
  cases minOrder with
  | true =>
    simp only [if_true, decide_eq_true_eq] at hmain ⊢
    have := lowSum_le (aggregate (contribs pinv pos) (Array.replicate 780 0)) F x hcons
    show valL pos (act π x) < valL pos x
    have : (valL pos (act π x) : ℤ) < valL pos x := by linarith
    exact_mod_cast this
  | false =>
    simp only [Bool.false_eq_true, if_false, decide_eq_true_eq] at hmain ⊢
    have := le_highSum (aggregate (contribs pinv pos) (Array.replicate 780 0)) F x hcons
    show valL pos (act π x) > valL pos x
    have : (valL pos x : ℤ) < valL pos (act π x) := by linarith
    exact_mod_cast this

end R310.SB
