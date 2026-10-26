/-
Link (a1) of `notes/cert_design.md`: the clause-level meaning of the SAT encoding.

Edge variables `x(i,j)` for `0 ≤ i < j < 40` (an assignment `x : Fin 40 → Fin 40 → Bool`;
values with `i ≥ j` are ignored). `graphOf x` is the graph with these edges.
* `fdef_iff`: `x` satisfies all TRI clauses and all IS clauses (s = 10) iff `graphOf x` is a
  (3,10,40)-graph.
* `mtfClauses_iff`: the MTF clauses hold iff `graphOf x` satisfies `MTFc`.
* `cover_assign`: the Cover Lemma restated for assignments.
-/
import R310.Cover

open Finset

set_option linter.unusedSectionVars false

namespace R310.Enc

open SimpleGraph R310

/-- An assignment of the edge variables `x(i,j)`, `i < j`. -/
abbrev Assign := Fin 40 → Fin 40 → Bool

/-- The value of the (unordered) edge `{i, j}`. -/
def edge (x : Assign) (i j : Fin 40) : Bool :=
  if i < j then x i j else if j < i then x j i else false

theorem edge_comm (x : Assign) (i j : Fin 40) : edge x i j = edge x j i := by
  unfold edge
  rcases lt_trichotomy i j with h | rfl | h
  · simp [h, h.not_gt]
  · simp
  · simp [h, h.not_gt]

/-- The graph of an assignment. -/
def graphOf (x : Assign) : SimpleGraph (Fin 40) where
  Adj i j := edge x i j = true
  symm := ⟨fun i j h => by rwa [edge_comm]⟩
  loopless := ⟨fun i h => by simp [edge] at h⟩

instance (x : Assign) : DecidableRel (graphOf x).Adj := fun i j =>
  inferInstanceAs (Decidable (edge x i j = true))

/-- The assignment of a graph. -/
def assignOf (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] : Assign :=
  fun i j => decide (G.Adj i j)

theorem graphOf_assignOf (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] :
    graphOf (assignOf G) = G := by
  ext i j
  simp only [graphOf, edge, assignOf]
  rcases lt_trichotomy i j with h | rfl | h
  · simp [h]
  · simp
  · simp [h, h.not_gt, G.adj_comm]

/-- TRI clauses: `¬x(i,j) ∨ ¬x(i,k) ∨ ¬x(j,k)` for all `i < j < k`. -/
def TRI (x : Assign) : Prop :=
  ∀ i j k : Fin 40, i < j → j < k → (!x i j || !x i k || !x j k) = true

/-- IS clauses for `s`-sets: every `s`-set `S` contains a pair `i < j` with `x(i,j)`. -/
def ISc (s : ℕ) (x : Assign) : Prop :=
  ∀ S : Finset (Fin 40), #S = s → ∃ i ∈ S, ∃ j ∈ S, i < j ∧ x i j = true

/-- `F_def = TRI + IS(10)`. -/
def Fdef (x : Assign) : Prop := TRI x ∧ ISc 10 x

theorem tri_iff (x : Assign) : TRI x ↔ (graphOf x).CliqueFree 3 := by
  constructor
  · intro h t ht
    rw [is3Clique_iff] at ht
    obtain ⟨a, b, c, hab, hac, hbc, rfl⟩ := ht
    -- sort the three vertices
    have key : ∀ i j k : Fin 40, i < j → j < k → (graphOf x).Adj i j → (graphOf x).Adj i k →
        (graphOf x).Adj j k → False := by
      intro i j k hij hjk h1 h2 h3
      have := h i j k hij hjk
      simp only [graphOf, edge, hij, hjk, hij.trans hjk, ite_true] at h1 h2 h3
      simp [h1, h2, h3] at this
    have hab' := (graphOf x).ne_of_adj hab
    have hac' := (graphOf x).ne_of_adj hac
    have hbc' := (graphOf x).ne_of_adj hbc
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
      simp [graphOf, edge, hij, hjk, hik, h1, h2, h3]

theorem isc_iff (x : Assign) : ISc 10 x ↔ (graphOf x).indepNum ≤ 9 := by
  constructor
  · intro h
    by_contra hlt
    push Not at hlt
    obtain ⟨s, hs⟩ := (graphOf x).exists_isNIndepSet_indepNum
    obtain ⟨S, hSs, hS⟩ := exists_subset_card_eq (s := s) (n := 10) (by rw [hs.card_eq]; omega)
    obtain ⟨i, hi, j, hj, hij, hx⟩ := h S hS
    have hadj : (graphOf x).Adj i j := by simp [graphOf, edge, hij, hx]
    exact hs.isIndepSet (hSs hi) (hSs hj) hij.ne hadj
  · intro h S hS
    by_contra hno
    push Not at hno
    have hind : (graphOf x).IsIndepSet (S : Set (Fin 40)) := by
      intro i hi j hj hij hadj
      simp only [graphOf, edge] at hadj
      rcases lt_or_gt_of_ne hij with h1 | h1
      · simp only [h1, ite_true] at hadj
        exact absurd hadj (by simpa using hno i hi j hj h1)
      · simp only [h1.not_gt, ite_false, h1, ite_true] at hadj
        exact absurd hadj (by simpa using hno j hj i hi h1)
    have := hind.card_le_indepNum
    omega

/-- **Link (a1).** The models of `F_def` are exactly the (3,10,40)-graphs. -/
theorem fdef_iff (x : Assign) :
    Fdef x ↔ (graphOf x).CliqueFree 3 ∧ (graphOf x).indepNum ≤ 9 := by
  rw [Fdef, tri_iff, isc_iff]

/-- MTF clauses: for `i < j`, `x(i,j)` or some `w` with `{i,w}` and `{j,w}` edges. -/
def MTFclauses (x : Assign) : Prop :=
  ∀ i j : Fin 40, i < j → x i j = true ∨ ∃ w, edge x i w = true ∧ edge x j w = true

theorem mtfClauses_iff (x : Assign) : MTFclauses x ↔ MTFc (graphOf x) := by
  constructor
  · intro h u v huv
    rcases lt_or_gt_of_ne huv with h1 | h1
    · rcases h u v h1 with h2 | ⟨w, hw⟩
      · exact Or.inl (by simp [graphOf, edge, h1, h2])
      · exact Or.inr ⟨w, hw⟩
    · rcases h v u h1 with h2 | ⟨w, hw⟩
      · exact Or.inl (by simp [graphOf, edge, h1, h1.not_gt, h2])
      · exact Or.inr ⟨w, hw.2, hw.1⟩
  · intro h i j hij
    rcases h i j hij.ne with h2 | ⟨w, hw⟩
    · left; simpa [graphOf, edge, hij] using h2
    · exact Or.inr ⟨w, hw⟩

/-- Degree of `v` in terms of the variables: `#{y | edge x v y}`. -/
theorem degree_graphOf (x : Assign) (v : Fin 40) :
    (graphOf x).degree v = #{y | edge x v y = true} := by
  rw [← card_neighborFinset_eq_degree]
  congr 1
  ext y
  rw [mem_neighborFinset]
  simp [graphOf]

/-- `e(H_0)` in terms of the variables: the number of pairs `i < j`, both outside `N[0]`, with
`x(i,j)`. -/
theorem h0edges_graphOf (x : Assign) :
    #(delNbhd (graphOf x) 0).edgeFinset =
      #{p : Fin 40 × Fin 40 | p.1 < p.2 ∧ p.1 ≠ 0 ∧ edge x 0 p.1 = false ∧ p.2 ≠ 0 ∧
        edge x 0 p.2 = false ∧ x p.1 p.2 = true} := by
  rw [card_edgeFinset_delNbhd]
  symm
  refine card_bij (fun p _ => s(p.1, p.2)) ?_ ?_ ?_
  · rintro ⟨a, b⟩ hp
    simp only [mem_filter, mem_univ, true_and] at hp
    obtain ⟨hab, ha0, ha, hb0, hb, hx⟩ := hp
    simp only [mem_filter, mem_edgeFinset, mem_edgeSet, Sym2.toFinset_mk_eq, insert_subset_iff,
      singleton_subset_iff, mem_outside]
    refine ⟨by simp [graphOf, edge, hab, hx], ⟨ha0, ?_⟩, ⟨hb0, ?_⟩⟩
    · simp [graphOf, ha]
    · simp [graphOf, hb]
  · rintro ⟨a, b⟩ hp ⟨c, d⟩ hq h
    simp only [mem_filter, mem_univ, true_and] at hp hq
    simp only [Sym2.eq_iff] at h
    rcases h with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
    · rfl
    · exact absurd (hp.1.trans hq.1) (lt_irrefl _)
  · intro e he
    induction e using Sym2.ind with
    | _ a b =>
      simp only [mem_filter, mem_edgeFinset, mem_edgeSet, Sym2.toFinset_mk_eq, insert_subset_iff,
        singleton_subset_iff, mem_outside] at he
      obtain ⟨hadj, ⟨ha0, ha⟩, ⟨hb0, hb⟩⟩ := he
      have ha' : edge x 0 a = false := by simpa [graphOf] using ha
      have hb' : edge x 0 b = false := by simpa [graphOf] using hb
      have hne : a ≠ b := (graphOf x).ne_of_adj hadj
      rcases lt_or_gt_of_ne hne with h | h
      · refine ⟨(a, b), ?_, rfl⟩
        simp only [graphOf, edge, h, ite_true] at hadj
        simp [h, ha0, ha', hb0, hb', hadj]
      · refine ⟨(b, a), ?_, Sym2.eq_swap⟩
        simp only [graphOf, edge, h.not_gt, h, ite_true, ite_false] at hadj
        simp [h, ha0, ha', hb0, hb', hadj]

theorem cube_congr {G G₂ : SimpleGraph (Fin 40)} [DecidableRel G.Adj] [DecidableRel G₂.Adj]
    (h : G = G₂) (hc : CodegOK G ∧ (CubeR G ∨ CubeS8 G ∨ CubeN G)) :
    CodegOK G₂ ∧ (CubeR G₂ ∨ CubeS8 G₂ ∨ CubeN G₂) := by
  subst h
  convert hc

/-- **Cover Lemma, clause form.** Assume F1, F2. If a (3,10,40)-graph exists, then some
assignment `x` satisfies `F_def` (TRI + IS), the codegree bound, and one of the cubes R, S8, N
(stated on `graphOf x`; see `degree_graphOf`, `h0edges_graphOf`, `mtfClauses_iff` for their
form in the variables). -/
theorem cover_assign (hF1 : FactF1) (hF2 : FactF2) (G : SimpleGraph (Fin 40))
    (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) :
    ∃ x : Assign, Fdef x ∧ CodegOK (graphOf x) ∧
      (CubeR (graphOf x) ∨ CubeS8 (graphOf x) ∨ CubeN (graphOf x)) := by
  obtain ⟨G', inst, h3', hα', hc, hcube⟩ := cover_lemma hF1 hF2 G h3 hα
  have h := graphOf_assignOf G'
  refine ⟨assignOf G', (fdef_iff _).2 (by rw [h]; exact ⟨h3', hα'⟩), ?_⟩
  exact cube_congr h.symm ⟨hc, hcube⟩

end R310.Enc
