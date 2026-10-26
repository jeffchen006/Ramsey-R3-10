/-
The case table of `notes/cases.md` (Sec. 2-4), generic part.

* `caseTable`: the degree distribution of a (3,10,40)-graph is in the survivor list, given
  `enumOK` (exhaustive enumeration, checked by the kernel) and LP certificates for the
  distributions that pass the simple checks but are not survivors.
* `t9_bound`: for a table entry `(n, t, c)` of a gluing scenario `U` (`c` a certificate), a graph
  with distribution `n` that satisfies the gluing hypotheses `Glue U G` has a 9-vertex `v` with
  `e(H_v) ≤ t`.
Table entries carry their certificates; `lpkOK` / `t9OK` check them (kernel `decide`, in batches).
-/
import R310.LP.Simple

open Finset

set_option linter.unusedSectionVars false

namespace R310.LP

open SimpleGraph

deriving instance DecidableEq for Inst

/-- `n` is a survivor or an LP-killed distribution. -/
def good (surv : List (List ℕ)) (lpk : List (List ℕ × Cert)) (n : List ℕ) : Bool :=
  surv.contains n || lpk.any (fun p => p.1 == n)

/-- One slice `(n4, n5) = (a, b)` of the exhaustive enumeration of all `(n4..n9)` with sum 40 and
deficiency `5 n4 + 4 n5 + 3 n6 + 2 n7 + n8 ≤ 360 - 2 elb`: each one that passes is `good`. -/
def enumSlice (elb : ℕ) (mtf : Bool) (surv : List (List ℕ)) (lpk : List (List ℕ × Cert))
    (a b : ℕ) : Bool :=
  (List.range ((360 - 2 * elb - 5 * a - 4 * b) / 3 + 1)).all fun c =>
    (List.range ((360 - 2 * elb - 5 * a - 4 * b - 3 * c) / 2 + 1)).all fun d =>
      (List.range (360 - 2 * elb - 5 * a - 4 * b - 3 * c - 2 * d + 1)).all fun e =>
        !decide (a + b + c + d + e ≤ 40) ||
          !passSimple [a, b, c, d, e, 40 - (a + b + c + d + e)] elb mtf ||
          good surv lpk [a, b, c, d, e, 40 - (a + b + c + d + e)]

/-- The full enumeration (`n4, n5 ≤ 2`). -/
def enumOK (elb : ℕ) (mtf : Bool) (surv : List (List ℕ)) (lpk : List (List ℕ × Cert)) : Bool :=
  (List.range 3).all fun a => (List.range 3).all fun b => enumSlice elb mtf surv lpk a b

/-- `e(3,9,39-d)` for `d = 4..9`. -/
def baseL : List ℕ := [140, 129, 118, 104, 95, 86]

/-- Every LP-killed entry carries a checked certificate for its base instance. -/
def lpkOK (lpk : List (List ℕ × Cert)) (mtf : Bool) : Bool :=
  lpk.all fun p => p.2.check && decide (p.2.inst = ⟨p.1, baseL, mtf⟩)

/-- Gluing hypothesis of a scenario `U = [(d, u), ...]`: every `d`-vertex has `e(H_v) ≥ u + 1`. -/
def Glue (U : List (ℕ × ℕ)) (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] : Prop :=
  ∀ p ∈ U, ∀ v ∈ cls G p.1, p.2 + 1 ≤ #(delNbhd G v).edgeFinset

/-- The lower bound for class `d` in scenario `U`. -/
def scenD (U : List (ℕ × ℕ)) (d : ℕ) : ℕ :=
  match U.lookup d with
  | some u => max (e39 d) (u + 1)
  | none => e39 d

theorem mem_of_lookup : ∀ (U : List (ℕ × ℕ)) (d u : ℕ), U.lookup d = some u → (d, u) ∈ U
  | [], _, _, h => by simp [List.lookup] at h
  | (a, b) :: U, d, u, h => by
    simp only [List.lookup] at h
    split at h
    · rename_i hda
      simp only [Option.some.injEq] at h
      have : d = a := by simpa using hda
      subst this; subst h; simp
    · exact List.mem_cons_of_mem _ (mem_of_lookup U d u h)

/-- Instance bounds `(L4..L9)` of scenario `U` with `L9 = t + 1`. -/
def scenL (U : List (ℕ × ℕ)) (t : ℕ) : List ℕ :=
  [scenD U 4, scenD U 5, scenD U 6, scenD U 7, scenD U 8, t + 1]

/-- Every t9 entry carries a checked certificate for its scenario instance. -/
def t9OK (tab : List (List ℕ × ℕ × Cert)) (U : List (ℕ × ℕ)) (mtf : Bool) : Bool :=
  tab.all fun p => p.2.2.check && decide (p.2.2.inst = ⟨p.1, scenL U p.2.1, mtf⟩)

/-- The gluing scenarios of `cases/degseq.py` (`SCENARIOS`). -/
def U_none : List (ℕ × ℕ) := []
def U_U8 : List (ℕ × ℕ) := [(8, 96)]
def U_known : List (ℕ × ℕ) := [(4, 140), (5, 130), (6, 119), (7, 108), (8, 96)]
def U_ang : List (ℕ × ℕ) := [(4, 140), (5, 130), (6, 121), (7, 112), (8, 96)]

/-- The 9-regular distribution. -/
def regDist : List ℕ := [0, 0, 0, 0, 0, 40]

/-- `t9` of `n` in a table (99 if absent). -/
def t9of (tab : List (List ℕ × ℕ × Cert)) (n : List ℕ) : ℕ :=
  ((tab.find? fun p => p.1 == n).map fun p => p.2.1).getD 99

/-- Every survivor except the 9-regular one has a table entry. -/
def covered (surv : List (List ℕ)) (tab : List (List ℕ × ℕ × Cert)) : Bool :=
  surv.all fun n => n == regDist || tab.any fun p => p.1 == n

theorem covered_of_eq {surv : List (List ℕ)} {tab : List (List ℕ × ℕ × Cert)}
    (h : surv = regDist :: tab.map Prod.fst) : covered surv tab = true := by
  subst h
  unfold covered
  rw [List.all_eq_true]
  intro n hn
  rw [List.mem_cons, List.mem_map] at hn
  simp only [Bool.or_eq_true, beq_iff_eq, List.any_eq_true]
  rcases hn with rfl | ⟨p, hp, rfl⟩
  · exact Or.inl rfl
  · exact Or.inr ⟨p, hp, by simp⟩

theorem enumOK_sound {elb : ℕ} {mtf : Bool} {surv : List (List ℕ)} {lpk : List (List ℕ × Cert)}
    (h : enumOK elb mtf surv lpk = true) (n : List ℕ) (hlen : n.length = 6)
    (hsum : n.sum = 40) (hp : passSimple n elb mtf = true) : good surv lpk n = true := by
  match n, hlen with
  | [a, b, c, d, e, f], _ =>
    simp only [List.sum_cons, List.sum_nil] at hsum
    have hf : f = 40 - (a + b + c + d + e) := by omega
    have hp' := hp
    simp only [passSimple, deg2n, get6, Bool.and_eq_true] at hp'
    simp at hp'
    obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨_, h1⟩, _⟩, _⟩, _⟩, h5⟩, _⟩, _⟩, _⟩, _⟩ := hp'
    have ha : a < 3 := by omega
    have hb : b < 3 := by omega
    have hc : c < (360 - 2 * elb - 5 * a - 4 * b) / 3 + 1 := by omega
    have hd : d < (360 - 2 * elb - 5 * a - 4 * b - 3 * c) / 2 + 1 := by omega
    have he : e < 360 - 2 * elb - 5 * a - 4 * b - 3 * c - 2 * d + 1 := by omega
    unfold enumOK enumSlice at h
    simp only [List.all_eq_true, List.mem_range] at h
    have := h a ha b hb c hc d hd e he
    subst hf
    simpa [hp, show a + b + c + d + e ≤ 40 by omega] using this

section Graph

variable {G : SimpleGraph (Fin 40)} [DecidableRel G.Adj]

theorem distOf_length : (distOf G).length = 6 := rfl

theorem distOf_sum (hr : ∀ v, G.degree v ∈ Icc 4 9) : (distOf G).sum = 40 := by
  have := sum_weight_univ hr (fun _ => 1)
  simp only [sum_Icc49, one_mul, sum_const, card_univ, Fintype.card_fin, smul_eq_mul,
    mul_one] at this
  simp only [distOf, List.sum_cons, List.sum_nil]
  simp only [ncls] at this ⊢
  omega

variable (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR : Ramsey3Le 9 36)
  (hR8 : Ramsey3Le 8 28) (hT : E39Table)
include h3 hα hR hR8 hT

/-- The case table: the degree distribution of a (3,10,40)-graph is a survivor. -/
theorem caseTable {elb : ℕ} {mtf : Bool} {surv : List (List ℕ)} {lpk : List (List ℕ × Cert)}
    (henum : enumOK elb mtf surv lpk = true) (hlpk : lpkOK lpk mtf = true)
    (hE : elb ≤ #G.edgeFinset) (hm : mtf = true → IsMTF G)
    (h35 : (∃ u, G.degree u = 4) → Regular35) : distOf G ∈ surv := by
  have hr := hrange' h3 hα hR
  have hp := passSimple_distOf h3 hα hR hR8 hT elb mtf hE hm h35
  have hg := enumOK_sound henum (distOf G) distOf_length (distOf_sum hr) hp
  unfold good at hg
  rw [Bool.or_eq_true, List.contains_iff_mem, List.any_eq_true] at hg
  rcases hg with hs | ⟨⟨n, c⟩, hmem, hn⟩
  · exact hs
  exfalso
  simp only [beq_iff_eq] at hn
  have hk := (List.all_eq_true.1 hlpk) (n, c) hmem
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hk
  obtain ⟨hck, hinst⟩ := hk
  refine Cert.no_graph G c hck h3 hα hR hR8 ⟨?_, ?_, ?_⟩
  · rw [hinst, hn]
  · intro i hi v hv
    rw [hinst]
    have := e39_le_card_edgeFinset_delNbhd G h3 hα hR hT v
    rw [(mem_filter.1 hv).2] at this
    obtain ⟨h1, h2⟩ := mem_Icc.1 hi
    interval_cases i <;> simpa [Inst.Ld, get6, baseL, e39] using this
  · intro h
    rw [hinst] at h
    exact hm h

/-- t9 bound of a gluing scenario: if `G` (distribution `n`) satisfies `Glue U G`, then some
9-vertex `v` has `e(H_v) ≤ t`. -/
theorem t9_bound {mtf : Bool} {tab : List (List ℕ × ℕ × Cert)} {U : List (ℕ × ℕ)}
    (ht : t9OK tab U mtf = true) (hm : mtf = true → IsMTF G) (hglue : Glue U G)
    {n : List ℕ} {t : ℕ} {c : Cert} (hmem : (n, t, c) ∈ tab) (hn : distOf G = n) :
    ∃ v, G.degree v = 9 ∧ #(delNbhd G v).edgeFinset ≤ t := by
  by_contra hcon
  push Not at hcon
  have hk := (List.all_eq_true.1 ht) (n, t, c) hmem
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hk
  obtain ⟨hck, hinst⟩ := hk
  refine Cert.no_graph G c hck h3 hα hR hR8 ⟨?_, ?_, ?_⟩
  · rw [hinst, hn]
  · intro i hi v hv
    have hvi := (mem_filter.1 hv).2
    rw [hinst]
    have hbase := e39_le_card_edgeFinset_delNbhd G h3 hα hR hT v
    rw [hvi] at hbase
    have hscen : ∀ d, G.degree v = d → scenD U d ≤ #(delNbhd G v).edgeFinset := by
      intro d hd
      unfold scenD
      split
      · rename_i u hu
        have hpu : (d, u) ∈ U := mem_of_lookup U d u hu
        have := hglue (d, u) hpu v (by simp [cls, hd])
        rw [← hd]
        exact max_le (hvi ▸ hbase) this
      · rw [← hd, hvi]; exact hbase
    obtain ⟨h1, h2⟩ := mem_Icc.1 hi
    interval_cases i
    · simpa [Inst.Ld, get6, scenL] using hscen 4 hvi
    · simpa [Inst.Ld, get6, scenL] using hscen 5 hvi
    · simpa [Inst.Ld, get6, scenL] using hscen 6 hvi
    · simpa [Inst.Ld, get6, scenL] using hscen 7 hvi
    · simpa [Inst.Ld, get6, scenL] using hscen 8 hvi
    · simpa [Inst.Ld, get6, scenL] using hcon v hvi
  · intro h
    rw [hinst] at h
    exact hm h

/-- Combined form: some 9-vertex has `e(H_v) ≤ t9of tab (distOf G)`. -/
theorem t9_main {mtf : Bool} {surv : List (List ℕ)} {tab : List (List ℕ × ℕ × Cert)}
    {U : List (ℕ × ℕ)} (ht : t9OK tab U mtf = true) (hcov : covered surv tab = true)
    (hsurv : distOf G ∈ surv) (hm : mtf = true → IsMTF G) (hglue : Glue U G) :
    ∃ v, G.degree v = 9 ∧ #(delNbhd G v).edgeFinset ≤ t9of tab (distOf G) := by
  have hr := hrange' h3 hα hR
  have h1 := (List.all_eq_true.1 hcov) _ hsurv
  rw [Bool.or_eq_true, beq_iff_eq] at h1
  rcases h1 with hreg | hin
  · -- 9-regular: `e(H_v) = 99`
    have h9 : ∀ v, G.degree v = 9 := by
      have hc9 : ncls G 9 = 40 := by
        have := congrArg (fun l => get6 l 9) hreg
        rw [get6_distOf hr] at this
        rw [this]
        rfl
      have : cls G 9 = univ := eq_univ_of_card _ (by rw [← ncls, hc9]; simp)
      intro v
      have hv : v ∈ cls G 9 := by rw [this]; exact mem_univ v
      exact (mem_filter.1 hv).2
    obtain ⟨-, -, h99, -⟩ := regular_nine_delNbhd G h3 hα h9 0
    refine ⟨0, h9 0, ?_⟩
    rw [h99]
    unfold t9of
    cases hf : tab.find? (fun p => p.1 == distOf G) with
    | none => simp
    | some p =>
      have hp := List.mem_of_find?_eq_some hf
      have hpn := List.find?_some hf
      simp only [beq_iff_eq] at hpn
      obtain ⟨v, hv9, hv⟩ := t9_bound h3 hα hR hR8 hT ht hm hglue
        (n := p.1) (t := p.2.1) (c := p.2.2) (by simpa using hp) hpn.symm
      have := (regular_nine_delNbhd G h3 hα h9 v).2.2.1
      simp only [Option.map_some, Option.getD_some]
      omega
  · rw [List.any_eq_true] at hin
    unfold t9of
    cases hf : tab.find? (fun p => p.1 == distOf G) with
    | none =>
      obtain ⟨p, hp, hpn⟩ := hin
      exact absurd hf (by
        rw [List.find?_eq_none]; push Not; exact ⟨p, hp, hpn⟩)
    | some p =>
      have hp := List.mem_of_find?_eq_some hf
      have hpn := List.find?_some hf
      simp only [beq_iff_eq] at hpn
      simpa using t9_bound h3 hα hR hR8 hT ht hm hglue
        (n := p.1) (t := p.2.1) (c := p.2.2) (by simpa using hp) hpn.symm

end Graph

end R310.LP
