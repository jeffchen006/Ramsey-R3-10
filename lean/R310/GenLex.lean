/-
General lex-leader lemma (request of agent `cert` for the F1 certificates, n = 23..27).

`PhiG s E D d G`: triangle-free, `α < s`, at most `E` edges, all degrees `≤ D`, and if `d > 0`
the units `N(0) = {1..d}`.
* `lexleader_gen`: if some graph satisfies `PhiG`, then some assignment `x` satisfies `PhiG`
  (for `graphOfG x`) and every SB clause with witness in `Γ_d` that is `SBValidG better val`.
* `edgeLowerBound_of_unsat`: if no `x` satisfies `PhiG k E D 0 + SB` (`D ≥ k - 1`), then
  `EdgeLowerBound k m (E + 1)` (Lean's form of F1 for `k = 8`, `E = 6m - 92`).
* `tri_iffG`, `isc_iffG`: TRI / IS(s) clauses on `x` mean triangle-free / `α < s`.
-/
import R310.GenCheck

open Finset

set_option linter.unusedSectionVars false
set_option linter.deprecated false

namespace R310.Gen

open R310 R310.Files SimpleGraph

variable {n : ℕ}

/-- `Φ_n(s)` + edge claim + degree bound + optional units `N(0) = {1..d}`. -/
structure PhiG (s E D d : ℕ) (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] : Prop where
  tri : G.CliqueFree 3
  alpha : G.indepNum < s
  edges : #G.edgeFinset ≤ E
  deg : ∀ v, G.degree v ≤ D
  units : 0 < d → ∀ z y : Fin n, z.val = 0 → (G.Adj z y ↔ 1 ≤ y.val ∧ y.val ≤ d)

theorem phiG_congr {s E D d : ℕ} {G G₂ : SimpleGraph (Fin n)} [DecidableRel G.Adj]
    [DecidableRel G₂.Adj] (h : G = G₂) (hp : PhiG s E D d G) : PhiG s E D d G₂ := by
  subst h; convert hp

section Relabel

variable {G : SimpleGraph (Fin n)} [DecidableRel G.Adj] (π : Equiv.Perm (Fin n))

instance : DecidableRel (G.comap π.symm).Adj := fun _ _ => inferInstanceAs (Decidable (G.Adj _ _))

theorem comap_degree (a : Fin n) : (G.comap π.symm).degree (π a) = G.degree a := by
  rw [← card_neighborFinset_eq_degree, ← card_neighborFinset_eq_degree]
  have : (G.comap π.symm).neighborFinset (π a) = (G.neighborFinset a).map π.toEmbedding := by
    ext b
    simp only [mem_neighborFinset, mem_map_equiv, comap_adj, Equiv.symm_apply_apply]
  rw [this, card_map]

theorem phiG_comap {s E D d : ℕ} (hπ : GammaG d π) (h : PhiG s E D d G) :
    PhiG s E D d (G.comap π.symm) := by
  refine ⟨h.tri.comap (Iso.comap π.symm G).toEmbedding.isContained,
    lt_of_le_of_lt (indepNum_le_of_embedding (Iso.comap π.symm G).toEmbedding) h.alpha,
    by rw [Iso.card_edgeFinset_eq (Iso.comap π.symm G)]; exact h.edges,
    fun v => by rw [show v = π (π.symm v) by simp, comap_degree]; exact h.deg _, ?_⟩
  intro hd z y hz
  rcases hπ with h0 | ⟨hfix, hblk⟩
  · omega
  have hπz : π z = z := Fin.ext (by rw [hfix z hz, hz])
  have hsz : π.symm z = z := by rw [Equiv.symm_apply_eq]; exact hπz.symm
  simp only [comap_adj, hsz]
  rw [h.units hd z (π.symm y) hz, hblk (π.symm y)]
  simp

end Relabel

/-! ### The abstract argument and the lemma -/

theorem exists_sb_of_closedG (better : ℕ → ℕ → Prop) (hb : better = (· < ·) ∨ better = (· > ·))
    (val : AssignG n → ℕ) (S : Set (AssignG n)) (SB : List (SBClauseG n))
    (hS : ∀ C ∈ SB, ∀ x ∈ S, actG C.wit x ∈ S) (hP : ∀ C ∈ SB, SBValidG better val C)
    (hne : S.Nonempty) :
    ∃ x ∈ S, ∀ C ∈ SB, (clause C.lits).sat (valId x) := by
  classical
  have hfin : S.Finite := Set.toFinite S
  have hne' : hfin.toFinset.Nonempty := by simpa using hne
  rcases hb with rfl | rfl
  · obtain ⟨x, hx, hmin⟩ := hfin.toFinset.exists_min_image val hne'
    rw [Set.Finite.mem_toFinset] at hx
    refine ⟨x, hx, fun C hC => ?_⟩
    by_contra hv
    have hlt := hP C hC x hv
    have := hmin (actG C.wit x) (by rw [Set.Finite.mem_toFinset]; exact hS C hC x hx)
    simp only at hlt
    omega
  · obtain ⟨x, hx, hmax⟩ := hfin.toFinset.exists_max_image val hne'
    rw [Set.Finite.mem_toFinset] at hx
    refine ⟨x, hx, fun C hC => ?_⟩
    by_contra hv
    have hgt := hP C hC x hv
    have := hmax (actG C.wit x) (by rw [Set.Finite.mem_toFinset]; exact hS C hC x hx)
    simp only at hgt
    omega

/-- **General lex-leader lemma.** -/
theorem lexleader_gen (s E D d : ℕ) (better : ℕ → ℕ → Prop)
    (hb : better = (· < ·) ∨ better = (· > ·)) (val : AssignG n → ℕ) (SB : List (SBClauseG n))
    (hΓ : ∀ C ∈ SB, GammaG d C.wit) (hP : ∀ C ∈ SB, SBValidG better val C)
    (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] (hG : PhiG s E D d G) :
    ∃ x : AssignG n, PhiG s E D d (graphOfG x) ∧ ∀ C ∈ SB, (clause C.lits).sat (valId x) := by
  let S : Set (AssignG n) := {x | PhiG s E D d (graphOfG x)}
  have hS : ∀ C ∈ SB, ∀ x ∈ S, actG C.wit x ∈ S := by
    intro C hC x hx
    exact phiG_congr (graphOfG_act C.wit x).symm (phiG_comap C.wit (hΓ C hC) hx)
  have h0 : assignOfG G ∈ S := phiG_congr (graphOfG_assignOfG G).symm hG
  exact exists_sb_of_closedG better hb val S SB hS hP ⟨_, h0⟩

/-- **F1 form.** If no assignment satisfies `PhiG k E D 0` (`D ≥ k - 1`) together with SB clauses
that are valid (any witnesses), then every triangle-free graph on `m` vertices with `α < k` has
more than `E` edges: `EdgeLowerBound k m (E + 1)`. -/
theorem edgeLowerBound_of_unsat {m k E D : ℕ} (hD : k - 1 ≤ D) (better : ℕ → ℕ → Prop)
    (hb : better = (· < ·) ∨ better = (· > ·)) (val : AssignG m → ℕ) (SB : List (SBClauseG m))
    (hP : ∀ C ∈ SB, SBValidG better val C)
    (hunsat : ¬ ∃ x : AssignG m, PhiG k E D 0 (graphOfG x) ∧
      ∀ C ∈ SB, (clause C.lits).sat (valId x)) :
    EdgeLowerBound k m (E + 1) := by
  intro H _ h3 hα
  by_contra hlt
  push Not at hlt
  have hdeg : ∀ v, H.degree v ≤ D := fun v => by
    have := degree_le_indepNum h3 v
    omega
  exact hunsat (lexleader_gen k E D 0 better hb val SB (fun _ _ => Or.inl rfl) hP H
    ⟨h3, hα, by omega, hdeg, fun h => absurd h (lt_irrefl 0)⟩)

/-! ### TRI and IS clauses for general `n` -/

/-- TRI clauses on `x`: for `i < j < k`, not all of `x(i,j), x(i,k), x(j,k)`. -/
def TRIG (x : AssignG n) : Prop :=
  ∀ i j k : Fin n, i < j → j < k → (!x i j || !x i k || !x j k) = true

/-- IS clauses for `s`-sets. -/
def ISG (s : ℕ) (x : AssignG n) : Prop :=
  ∀ S : Finset (Fin n), #S = s → ∃ i ∈ S, ∃ j ∈ S, i < j ∧ x i j = true

theorem tri_iffG (x : AssignG n) : TRIG x ↔ (graphOfG x).CliqueFree 3 := by
  constructor
  · intro h t ht
    rw [is3Clique_iff] at ht
    obtain ⟨a, b, c, hab, hac, hbc, rfl⟩ := ht
    have key : ∀ i j k : Fin n, i < j → j < k → (graphOfG x).Adj i j → (graphOfG x).Adj i k →
        (graphOfG x).Adj j k → False := by
      intro i j k hij hjk h1 h2 h3
      have := h i j k hij hjk
      simp only [graphOfG, edgeG, hij, hjk, hij.trans hjk, ite_true] at h1 h2 h3
      simp [h1, h2, h3] at this
    have hab' := (graphOfG x).ne_of_adj hab
    have hac' := (graphOfG x).ne_of_adj hac
    have hbc' := (graphOfG x).ne_of_adj hbc
    rcases lt_or_gt_of_ne hab' with h1 | h1 <;> rcases lt_or_gt_of_ne hac' with h2 | h2 <;>
      rcases lt_or_gt_of_ne hbc' with h3 | h3
    · exact key a b c h1 h3 hab hac hbc
    · exact key a c b h2 h3 hac hab hbc.symm
    · exact absurd (h1.trans h3) (not_lt.2 h2.le)
    · exact key c a b h2 h1 hac.symm hbc.symm hab
    · exact key b a c h1 h2 hab.symm hbc hac
    · exact absurd (h3.trans h1) (not_lt.2 h2.le)
    · exact key b c a h3 h2 hbc hab.symm hac.symm
    · exact key c b a h3 h1 hbc.symm hac.symm hab.symm
  · intro h i j k hij hjk
    by_contra hc
    simp only [Bool.or_eq_true, Bool.not_eq_true', not_or, Bool.not_eq_false] at hc
    obtain ⟨⟨h1, h2⟩, h3⟩ := hc
    have hik := hij.trans hjk
    refine h {i, j, k} (is3Clique_triple_iff.2 ⟨?_, ?_, ?_⟩) <;>
      simp [graphOfG, edgeG, hij, hjk, hik, h1, h2, h3]

theorem isc_iffG (s : ℕ) (x : AssignG n) : ISG s x ↔ (graphOfG x).indepNum < s := by
  constructor
  · intro h
    by_contra hlt
    push Not at hlt
    obtain ⟨S0, hs⟩ := (graphOfG x).exists_isNIndepSet_indepNum
    obtain ⟨S, hSs, hS⟩ := exists_subset_card_eq (s := S0) (n := s) (by rw [hs.card_eq]; omega)
    obtain ⟨i, hi, j, hj, hij, hx⟩ := h S hS
    have hadj : (graphOfG x).Adj i j := by simp [graphOfG, edgeG, hij, hx]
    exact hs.isIndepSet (hSs hi) (hSs hj) hij.ne hadj
  · intro h S hS
    by_contra hno
    push Not at hno
    have hind : (graphOfG x).IsIndepSet (S : Set (Fin n)) := by
      intro i hi j hj hij hadj
      simp only [graphOfG, edgeG] at hadj
      rcases lt_or_gt_of_ne hij with h1 | h1
      · simp only [h1, ite_true] at hadj
        exact absurd hadj (by simpa using hno i hi j hj h1)
      · simp only [h1.not_gt, ite_false, h1, ite_true] at hadj
        exact absurd hadj (by simpa using hno j hj i hi h1)
    have := hind.card_le_indepNum
    omega

/-- In variables: `x(i,j) = valId x (xid i j)`, `deg v = #{u | edge(u,v)}`. -/
theorem degree_graphOfG (x : AssignG n) (v : Fin n) :
    (graphOfG x).degree v = #{u | edgeG x v u = true} := by
  rw [← card_neighborFinset_eq_degree]
  congr 1
  ext u
  rw [mem_neighborFinset]
  simp [graphOfG]

end R310.Gen

namespace R310.Gen

open R310 R310.Files SimpleGraph

variable {n : ℕ}

theorem checkGB_sound (minOrder : Bool) (pos : List (Fin n × Fin n)) (sizes : List ℕ)
    (lits : List Lit) (p pinv : Fin n → Fin n) (h : checkGB n minOrder pos sizes lits p pinv = true) :
    ∃ π : Equiv.Perm (Fin n), (∀ v, π v = p v) ∧
      (∀ v, blockOf sizes (π v).val = blockOf sizes v.val) ∧
      SBValidG (if minOrder then (· < ·) else (· > ·)) (valLG pos) ⟨lits, π⟩ := by
  unfold checkGB at h
  rw [Bool.and_eq_true] at h
  obtain ⟨hb, hc⟩ := h
  obtain ⟨π, hπ, -, hv⟩ := checkG_sound minOrder pos 0 lits p pinv hc
  refine ⟨π, hπ, fun v => ?_, hv⟩
  unfold blocksOK at hb
  simp only [Bool.and_eq_true, List.all_eq_true, List.mem_finRange, true_implies, beq_iff_eq] at hb
  rw [hπ]; exact hb.2 v

/-- **Lex-leader lemma for any invariant formula.** If `P` is invariant under every witness
(e.g. all block-preserving permutations) and the SB clauses are valid, then a model of `P`
gives a model of `P` + all SB clauses. -/
theorem lexleader_inv (P : (G : SimpleGraph (Fin n)) → [DecidableRel G.Adj] → Prop)
    (better : ℕ → ℕ → Prop) (hb : better = (· < ·) ∨ better = (· > ·)) (val : AssignG n → ℕ)
    (SB : List (SBClauseG n))
    (hinv : ∀ C ∈ SB, ∀ (G : SimpleGraph (Fin n)) [DecidableRel G.Adj], P G →
      P (G.comap C.wit.symm))
    (hP : ∀ C ∈ SB, SBValidG better val C)
    (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] (hG : P G) :
    ∃ x : AssignG n, P (graphOfG x) ∧ ∀ C ∈ SB, (clause C.lits).sat (valId x) := by
  have congrP : ∀ {G₁ G₂ : SimpleGraph (Fin n)} [DecidableRel G₁.Adj] [DecidableRel G₂.Adj],
      G₁ = G₂ → P G₁ → P G₂ := by
    intro G₁ G₂ _ _ h hp; subst h; convert hp
  let S : Set (AssignG n) := {x | P (graphOfG x)}
  have hS : ∀ C ∈ SB, ∀ x ∈ S, actG C.wit x ∈ S := fun C hC x hx =>
    congrP (graphOfG_act C.wit x).symm (hinv C hC _ hx)
  exact exists_sb_of_closedG better hb val S SB hS hP
    ⟨_, congrP (graphOfG_assignOfG G).symm hG⟩

end R310.Gen
