/-
General-`n` semantics of SB clauses and the soundness of the general checker `checkG`
(request of agent `cert` for the F1 certificates, n = 23..27).

* `AssignG n`: edge assignments on `Fin n`; `actG π x` = `(π x)(i,j) = x(π⁻¹ i, π⁻¹ j)`.
* `valId x id`: value of the colex edge variable `id` (`xid i j = j(j-1)/2 + i + 1`).
* `GammaG d π`: `d = 0`, or `π` fixes vertex 0 and maps `{1..d}` onto itself.
* `SBValidG better val C`: every `x` with `valId x ⊭ C` has `val (actG π x)` strictly better.
* `checkG_sound`: `checkG ... = true` → `GammaG d π ∧ SBValidG (<|>) (valLG pos) C`.
-/
import R310.GenCore
import R310.FilesProof

open Finset

set_option linter.unusedSectionVars false
set_option linter.deprecated false

namespace R310.Gen

open R310 R310.Files

variable {n : ℕ}

/-! ### Assignments, graphs, action -/

abbrev AssignG (n : ℕ) := Fin n → Fin n → Bool

def edgeG (x : AssignG n) (i j : Fin n) : Bool :=
  if i < j then x i j else if j < i then x j i else false

theorem edgeG_comm (x : AssignG n) (i j : Fin n) : edgeG x i j = edgeG x j i := by
  unfold edgeG
  rcases lt_trichotomy i j with h | rfl | h
  · simp [h, h.not_gt]
  · simp
  · simp [h, h.not_gt]

def graphOfG (x : AssignG n) : SimpleGraph (Fin n) where
  Adj i j := edgeG x i j = true
  symm := ⟨fun i j h => by rwa [edgeG_comm]⟩
  loopless := ⟨fun i h => by simp [edgeG] at h⟩

instance (x : AssignG n) : DecidableRel (graphOfG x).Adj := fun i j =>
  inferInstanceAs (Decidable (edgeG x i j = true))

def assignOfG (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] : AssignG n :=
  fun i j => decide (G.Adj i j)

theorem graphOfG_assignOfG (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    graphOfG (assignOfG G) = G := by
  ext i j
  simp only [graphOfG, edgeG, assignOfG]
  rcases lt_trichotomy i j with h | rfl | h
  · simp [h]
  · simp
  · simp [h, h.not_gt, G.adj_comm]

theorem edgeG_assignOfG (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] (a b : Fin n) :
    edgeG (assignOfG G) a b = decide (G.Adj a b) := by
  unfold edgeG assignOfG
  rcases lt_trichotomy a b with h | rfl | h
  · simp [h]
  · simp
  · simp [h, h.not_gt, G.adj_comm]

/-- `(π x)(i,j) = x(π⁻¹ i, π⁻¹ j)`. -/
def actG (π : Equiv.Perm (Fin n)) (x : AssignG n) : AssignG n :=
  assignOfG ((graphOfG x).comap π.symm)

theorem edgeG_act (π : Equiv.Perm (Fin n)) (x : AssignG n) (a b : Fin n) :
    edgeG (actG π x) a b = edgeG x (π.symm a) (π.symm b) := by
  unfold actG
  rw [edgeG_assignOfG]
  simp [graphOfG]

theorem graphOfG_act (π : Equiv.Perm (Fin n)) (x : AssignG n) :
    graphOfG (actG π x) = (graphOfG x).comap π.symm := graphOfG_assignOfG _

/-! ### Colex ids -/

theorem xid_eq_choose (i j : ℕ) : xid i j = j.choose 2 + i + 1 := by
  rw [xid, Nat.choose_two_right]

theorem choose_succ_two (j : ℕ) : (j + 1).choose 2 = j.choose 2 + j := by
  rw [Nat.choose_succ_succ, Nat.choose_one_right]; ring

theorem xid_inj_gen {i j i' j' : ℕ} (hij : i < j) (hij' : i' < j')
    (h : xid i j = xid i' j') : i = i' ∧ j = j' := by
  rw [xid_eq_choose, xid_eq_choose] at h
  rcases lt_trichotomy j j' with hlt | rfl | hlt
  · have h1 := Nat.choose_le_choose 2 (show j + 1 ≤ j' by omega)
    rw [choose_succ_two] at h1; omega
  · omega
  · have h1 := Nat.choose_le_choose 2 (show j' + 1 ≤ j by omega)
    rw [choose_succ_two] at h1; omega

theorem xid_le_numE {i j : ℕ} (hij : i < j) (hj : j < n) : xid i j ≤ numE n := by
  have h1 := Nat.choose_le_choose 2 (show j + 1 ≤ n by omega)
  rw [choose_succ_two] at h1
  rw [xid_eq_choose, numE, ← Nat.choose_two_right]
  omega

/-- Value of the edge variable with colex id `id` (`false` if `id` is not an edge id). -/
noncomputable def valId (x : AssignG n) (id : ℕ) : Bool :=
  if h : ∃ p : Fin n × Fin n, p.1 < p.2 ∧ xid p.1 p.2 = id then x h.choose.1 h.choose.2 else false

theorem valId_xid (x : AssignG n) (i j : Fin n) (hij : i < j) : valId x (xid i j) = x i j := by
  have hex : ∃ p : Fin n × Fin n, p.1 < p.2 ∧ xid p.1 p.2 = xid i j := ⟨(i, j), hij, rfl⟩
  unfold valId
  rw [dite_cond_eq_true (eq_true hex)]
  obtain ⟨h1, h2⟩ := hex.choose_spec
  obtain ⟨e1, e2⟩ := xid_inj_gen (Fin.lt_def.1 h1) (Fin.lt_def.1 hij) h2
  have : hex.choose = (i, j) := Prod.ext (Fin.ext e1) (Fin.ext e2)
  rw [this]

/-- The bit with colex index `t` (id `t + 1`). -/
noncomputable def bitIdx (x : AssignG n) (t : ℕ) : ℤ := if valId x (t + 1) then 1 else 0

theorem minmax_lt {p : Fin n × Fin n} (h : p.1 ≠ p.2) : min p.1 p.2 < max p.1 p.2 := by
  rcases lt_or_gt_of_ne h with h' | h'
  · simp [min_eq_left h'.le, max_eq_right h'.le, h']
  · simp [min_eq_right h'.le, max_eq_left h'.le, h']

theorem eidxG_lt (p : Fin n × Fin n) (h : p.1 ≠ p.2) : eidxG p < numE n := by
  unfold eidxG
  have := xid_le_numE (Fin.lt_def.1 (minmax_lt h)) (max p.1 p.2).2
  have : 1 ≤ xid (min p.1 p.2 : Fin n) (max p.1 p.2 : Fin n) := by unfold xid; omega
  omega

theorem edge_eq_bitIdx (x : AssignG n) (p : Fin n × Fin n) (h : p.1 ≠ p.2) :
    (if edgeG x p.1 p.2 then (1 : ℤ) else 0) = bitIdx x (eidxG p) := by
  unfold bitIdx eidxG
  have h1 : 1 ≤ xid (min p.1 p.2 : Fin n) (max p.1 p.2 : Fin n) := by unfold xid; omega
  rw [Nat.sub_add_cancel h1, valId_xid x _ _ (minmax_lt h)]
  rcases lt_or_gt_of_ne h with h' | h'
  · rw [min_eq_left h'.le, max_eq_right h'.le]; simp [edgeG, h']
  · rw [min_eq_right h'.le, max_eq_left h'.le]; simp [edgeG, h', h'.not_gt]

/-! ### Value and the linear form -/

def valLG : List (Fin n × Fin n) → AssignG n → ℕ
  | [], _ => 0
  | p :: ps, x => 2 ^ ps.length * (if edgeG x p.1 p.2 then 1 else 0) + valLG ps x

theorem valLG_act (π : Equiv.Perm (Fin n)) (x : AssignG n) (pos : List (Fin n × Fin n)) :
    valLG pos (actG π x) = valLG (pos.map (sigG π.symm)) x := by
  induction pos with
  | nil => rfl
  | cons p ps ih => simp [valLG, ih, edgeG_act, sigG]

def linG (cs : List (ℤ × (Fin n × Fin n))) (x : AssignG n) : ℤ :=
  (cs.map fun c => c.1 * if edgeG x c.2.1 c.2.2 then 1 else 0).sum

theorem valLG_sub (pinv : Fin n → Fin n) (x : AssignG n) (pos : List (Fin n × Fin n)) :
    (valLG pos x : ℤ) - valLG (pos.map (sigG pinv)) x = linG (contribsG pinv pos.length pos) x := by
  induction pos with
  | nil => simp [valLG, contribsG, linG]
  | cons p ps ih =>
    have hstep : (valLG (p :: ps) x : ℤ) - valLG ((p :: ps).map (sigG pinv)) x =
        ((2 ^ ps.length : ℕ) : ℤ) * (if edgeG x p.1 p.2 then 1 else 0) -
          ((2 ^ ps.length : ℕ) : ℤ) * (if edgeG x (sigG pinv p).1 (sigG pinv p).2 then 1 else 0) +
          ((valLG ps x : ℤ) - valLG (ps.map (sigG pinv)) x) := by
      simp only [valLG, List.map_cons, List.length_map]
      push_cast
      ring
    have hc : contribsG pinv (p :: ps).length (p :: ps) =
        if sigG pinv p = p then contribsG pinv ps.length ps else
        ((2 ^ ps.length : ℕ), p) :: (-((2 ^ ps.length : ℕ) : ℤ), sigG pinv p) ::
          contribsG pinv ps.length ps := by
      simp [contribsG, Nat.shiftLeft_eq]
    rw [hstep, ih, hc]
    by_cases h : sigG pinv p = p
    · rw [if_pos h, h]; ring
    · rw [if_neg h]
      simp only [linG, List.map_cons, List.sum_cons]
      ring

noncomputable def wsumG (N : ℕ) (W : Array ℤ) (x : AssignG n) : ℤ :=
  ∑ t ∈ Finset.range N, W.getD t 0 * bitIdx x t

theorem wsumG_modify (N : ℕ) (W : Array ℤ) (hW : W.size = N) (i : ℕ) (hi : i < N) (c : ℤ)
    (x : AssignG n) : wsumG N (W.modify i (· + c)) x = wsumG N W x + c * bitIdx x i := by
  unfold wsumG
  have : ∀ t ∈ Finset.range N, (W.modify i (· + c)).getD t 0 * bitIdx x t =
      W.getD t 0 * bitIdx x t + if t = i then c * bitIdx x t else 0 := by
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

theorem wsumG_aggregate (cs : List (ℤ × (Fin n × Fin n))) (hcs : ∀ c ∈ cs, c.2.1 ≠ c.2.2)
    (W : Array ℤ) (hW : W.size = numE n) (x : AssignG n) :
    wsumG (numE n) (aggregateG cs W) x = wsumG (numE n) W x + linG cs x := by
  induction cs generalizing W with
  | nil => simp [aggregateG, linG]
  | cons c cs ih =>
    have hc := hcs c (by simp)
    have h2 : aggregateG (c :: cs) W = aggregateG cs (W.modify (eidxG c.2) (· + c.1)) := rfl
    rw [h2, ih (fun c' hc' => hcs c' (by simp [hc'])) _ (by simp [hW]),
      wsumG_modify _ W hW _ (eidxG_lt _ hc), linG, linG, List.map_cons, List.sum_cons,
      edge_eq_bitIdx x c.2 hc]
    ring

theorem wsumG_zero (N : ℕ) (x : AssignG n) : wsumG N (Array.replicate N 0) x = 0 := by
  unfold wsumG
  apply Finset.sum_eq_zero
  intro t ht
  rw [Finset.mem_range] at ht
  simp [Array.getD_eq_getD_getElem?, ht]

/-! ### Fixed bits and the bounds -/

def ConsistentG (N : ℕ) (F : Array (Option Bool)) (x : AssignG n) : Prop :=
  ∀ t < N, ∀ b, F.getD t none = some b → bitIdx x t = if b then 1 else 0

theorem listSum_rangeZ (m : ℕ) (g : ℕ → ℤ) :
    ((List.range m).map g).sum = ∑ i ∈ Finset.range m, g i := by
  induction m with
  | zero => simp
  | succ m ih => rw [List.range_succ, List.map_append, List.sum_append, ih, Finset.sum_range_succ]; simp

theorem bitIdx_01 (x : AssignG n) (t : ℕ) : bitIdx x t = 0 ∨ bitIdx x t = 1 := by
  unfold bitIdx; split_ifs <;> simp

theorem lowSumG_le (N : ℕ) (W : Array ℤ) (F : Array (Option Bool)) (x : AssignG n)
    (hx : ConsistentG N F x) : lowSumG N W F ≤ wsumG N W x := by
  unfold lowSumG wsumG
  rw [listSum_rangeZ]
  apply Finset.sum_le_sum
  intro t ht
  rw [Finset.mem_range] at ht
  cases hF : F.getD t none with
  | some b => rw [hx t ht b hF]; cases b <;> simp
  | none =>
    simp only
    rcases bitIdx_01 x t with h | h <;> rw [h] <;> simp

theorem le_highSumG (N : ℕ) (W : Array ℤ) (F : Array (Option Bool)) (x : AssignG n)
    (hx : ConsistentG N F x) : wsumG N W x ≤ highSumG N W F := by
  unfold highSumG wsumG
  rw [listSum_rangeZ]
  apply Finset.sum_le_sum
  intro t ht
  rw [Finset.mem_range] at ht
  cases hF : F.getD t none with
  | some b => rw [hx t ht b hF]; cases b <;> simp
  | none =>
    simp only
    rcases bitIdx_01 x t with h | h <;> rw [h] <;> simp

theorem fixedOfG_spec (N : ℕ) (x : AssignG n) :
    ∀ (lits : List Lit) (A : Array (Option Bool)), A.size = N → ConsistentG N A x →
      (∀ l ∈ lits, 1 ≤ l.id ∧ l.id ≤ N) → (∀ l ∈ lits, valId x l.id ≠ l.pos) →
      ∃ F, lits.foldlM (fun A l => match A.getD (l.id - 1) none with
        | some b => if b = !l.pos then some A else none
        | none => some (A.set! (l.id - 1) (some (!l.pos)))) A = some F ∧ ConsistentG N F x
  | [], A, _, hA, _, _ => ⟨A, rfl, hA⟩
  | l :: ls, A, hs, hA, hid, hfal => by
    obtain ⟨h1, h2⟩ := hid l (by simp)
    have hl := hfal l (by simp)
    have hbit : bitIdx x (l.id - 1) = if valId x l.id then 1 else 0 := by
      unfold bitIdx; rw [Nat.sub_add_cancel h1]
    have hval : valId x l.id = !l.pos := by
      revert hl; cases valId x l.id <;> cases l.pos <;> simp
    rw [List.foldlM_cons]
    cases hA' : A.getD (l.id - 1) none with
    | some b =>
      have hb := hA (l.id - 1) (by omega) b hA'
      have : b = !l.pos := by
        rw [hbit, hval] at hb
        revert hb; cases b <;> cases l.pos <;> simp
      simp only [this, if_true, Option.bind_some]
      exact fixedOfG_spec N x ls A hs hA (fun l' h' => hid l' (by simp [h']))
        (fun l' h' => hfal l' (by simp [h']))
    | none =>
      simp only [Option.bind_some]
      refine fixedOfG_spec N x ls _ (by simp [hs]) ?_ (fun l' h' => hid l' (by simp [h']))
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

theorem fixedOfG_some (N : ℕ) (x : AssignG n) (lits : List Lit)
    (hid : ∀ l ∈ lits, 1 ≤ l.id ∧ l.id ≤ N) (hfal : ∀ l ∈ lits, valId x l.id ≠ l.pos) :
    ∃ F, fixedOfG N lits = some F ∧ ConsistentG N F x :=
  fixedOfG_spec N x lits _ (by simp) (fun t ht b hb => by
    simp [Array.getD_eq_getD_getElem?, Array.getElem?_replicate, ht] at hb) hid hfal

/-! ### Witness group, validity, soundness -/

/-- `Γ_d`: all permutations if `d = 0`; otherwise those fixing vertex 0 and `{1..d}`. -/
def GammaG (d : ℕ) (π : Equiv.Perm (Fin n)) : Prop :=
  d = 0 ∨ ((∀ v : Fin n, v.val = 0 → (π v).val = 0) ∧
    ∀ u : Fin n, (1 ≤ u.val ∧ u.val ≤ d) ↔ (1 ≤ (π u).val ∧ (π u).val ≤ d))

structure SBClauseG (n : ℕ) where
  lits : List Lit
  wit : Equiv.Perm (Fin n)

def SBValidG (better : ℕ → ℕ → Prop) (val : AssignG n → ℕ) (C : SBClauseG n) : Prop :=
  ∀ x : AssignG n, ¬ (clause C.lits).sat (valId x) → better (val (actG C.wit x)) (val x)

/-- **Soundness of the general SB checker.** -/
theorem checkG_sound (minOrder : Bool) (pos : List (Fin n × Fin n)) (d : ℕ) (lits : List Lit)
    (p pinv : Fin n → Fin n) (h : checkG n minOrder pos d lits p pinv = true) :
    ∃ π : Equiv.Perm (Fin n), (∀ v, π v = p v) ∧ GammaG d π ∧
      SBValidG (if minOrder then (· < ·) else (· > ·)) (valLG pos) ⟨lits, π⟩ := by
  unfold checkG at h
  simp only [Bool.and_eq_true, List.all_eq_true, List.mem_finRange, true_implies, beq_iff_eq,
    bne_iff_ne, ne_eq] at h
  obtain ⟨⟨⟨⟨hinv, hgam⟩, hpos⟩, hid⟩, hmain⟩ := h
  let π : Equiv.Perm (Fin n) := ⟨p, pinv, fun v => (hinv v).1, fun v => (hinv v).2⟩
  refine ⟨π, fun v => rfl, ?_, ?_⟩
  · unfold gammaOK at hgam
    simp only [Bool.or_eq_true, beq_iff_eq, Bool.and_eq_true, List.all_eq_true,
      List.mem_finRange, true_implies, bne_iff_ne, ne_eq, decide_eq_decide] at hgam
    rcases hgam with h0 | ⟨h1, h2⟩
    · exact Or.inl h0
    · refine Or.inr ⟨fun v hv => ?_, fun u => h2 u⟩
      rcases h1 v with h | h
      · exact absurd hv h
      · exact h
  intro x hx
  rw [clause_sat_iff] at hx
  push Not at hx
  have hid' : ∀ l ∈ lits, 1 ≤ l.id ∧ l.id ≤ numE n := fun l hl => by simpa using hid l hl
  obtain ⟨F, hF, hcons⟩ := fixedOfG_some (numE n) x lits hid' hx
  rw [hF] at hmain
  simp only at hmain
  have hsymm : (π.symm : Fin n → Fin n) = pinv := rfl
  have hD : (valLG pos x : ℤ) - valLG pos (actG π x) =
      wsumG (numE n) (aggregateG (contribsG pinv pos.length pos) (Array.replicate (numE n) 0)) x := by
    rw [valLG_act, hsymm, valLG_sub,
      wsumG_aggregate _ ?_ (Array.replicate (numE n) 0) (by simp), wsumG_zero, zero_add]
    intro c hc
    clear hmain hF
    induction pos with
    | nil => simp [contribsG] at hc
    | cons e es ih =>
      have he := hpos e (by simp)
      simp only [List.length_cons, contribsG, Nat.add_sub_cancel] at hc
      split_ifs at hc with hs
      · exact ih (fun e' h' => hpos e' (by simp [h'])) hc
      · simp only [List.mem_cons] at hc
        rcases hc with rfl | rfl | hc
        · exact he
        · simp only [sigG]
          intro heq
          have := congrArg p heq
          rw [(hinv _).2, (hinv _).2] at this
          exact he this
        · exact ih (fun e' h' => hpos e' (by simp [h'])) hc
  cases minOrder with
  | true =>
    simp only [if_true, decide_eq_true_eq] at hmain ⊢
    have := lowSumG_le (numE n)
      (aggregateG (contribsG pinv pos.length pos) (Array.replicate (numE n) 0)) F x hcons
    show valLG pos (actG π x) < valLG pos x
    have : (valLG pos (actG π x) : ℤ) < valLG pos x := by linarith
    exact_mod_cast this
  | false =>
    simp only [Bool.false_eq_true, if_false, decide_eq_true_eq] at hmain ⊢
    have := le_highSumG (numE n)
      (aggregateG (contribsG pinv pos.length pos) (Array.replicate (numE n) 0)) F x hcons
    show valLG pos (actG π x) > valLG pos x
    have : (valLG pos x : ℤ) < valLG pos (actG π x) := by linarith
    exact_mod_cast this

end R310.Gen
