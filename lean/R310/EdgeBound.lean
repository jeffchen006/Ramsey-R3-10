/-
Edge-table hypotheses `e(3,k,m) ≥ e₀` and the degree-sum inequality (4) of
Goedgebeur–Radziszowski (EJC 20(1) 2013 #P30, Sec. 3) for `n = 40`, `k = 10`.
-/
import R310.MinDegree

open Finset

set_option linter.unusedSectionVars false

namespace R310

open SimpleGraph

/-- `EdgeLowerBound k m e₀`: every triangle-free graph on `m` vertices with `α < k`
(a `(3,k,m)`-graph) has at least `e₀` edges, i.e. `e(3,k,m) ≥ e₀`.
Used only as a hypothesis (values from computer searches in the literature). -/
def EdgeLowerBound (k m e₀ : ℕ) : Prop :=
  ∀ (H : SimpleGraph (Fin m)) [DecidableRel H.Adj], H.CliqueFree 3 → H.indepNum < k →
    e₀ ≤ #H.edgeFinset

/-- A graph embedding (induced) does not increase the independence number. -/
theorem indepNum_le_of_embedding {W W' : Type*} [Finite W] {H : SimpleGraph W}
    {H' : SimpleGraph W'} (f : H' ↪g H) : H'.indepNum ≤ H.indepNum := by
  classical
  have := Fintype.ofFinite W
  obtain ⟨s, hs⟩ := H'.exists_isNIndepSet_indepNum
  have hind : H.IsIndepSet ((s.map f.toEmbedding : Finset W) : Set W) := by
    intro a ha b hb hab
    simp only [coe_map, Set.mem_image, mem_coe] at ha hb
    obtain ⟨a, ha, rfl⟩ := ha
    obtain ⟨b, hb, rfl⟩ := hb
    rw [RelEmbedding.coe_toEmbedding, f.map_adj_iff]
    exact hs.isIndepSet ha hb (fun h => hab (congrArg f h))
  calc H'.indepNum = #(s.map f.toEmbedding) := by rw [card_map, hs.card_eq]
    _ ≤ H.indepNum := hind.card_le_indepNum

/-- `EdgeLowerBound k m e₀` applies to every vertex type with exactly `m` elements. -/
theorem EdgeLowerBound.le_card_edgeFinset {k m e₀ : ℕ} (hE : EdgeLowerBound k m e₀)
    {W : Type*} [Fintype W] [DecidableEq W] (hW : Fintype.card W = m) (H : SimpleGraph W)
    [DecidableRel H.Adj] (h3 : H.CliqueFree 3) (hα : H.indepNum < k) :
    e₀ ≤ #H.edgeFinset := by
  classical
  let e : W ≃ Fin m := Fintype.equivOfCardEq (by simpa using hW)
  let φ : H ≃g H.map e.toEmbedding := Iso.map e H
  have := hE (H.map e.toEmbedding) (h3.comap φ.symm.toEmbedding.isContained)
    ((indepNum_le_of_embedding φ.symm.toEmbedding).trans_lt hα)
  rwa [← Iso.card_edgeFinset_eq φ] at this

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

/-- If `G` is triangle-free with `α(G) ≤ k - 1` and `e(3, k-1, |V| - deg v - 1) ≥ e₀`
(hypothesis), then `e(G - N[v]) ≥ e₀`. -/
theorem le_card_edgeFinset_delNbhd (h3 : G.CliqueFree 3) {k e₀ : ℕ} (hα : G.indepNum ≤ k - 1)
    (v : V) (hE : EdgeLowerBound (k - 1) (Fintype.card V - G.degree v - 1) e₀) :
    e₀ ≤ #(delNbhd G v).edgeFinset := by
  have hc := card_delNbhd_verts (G := G) v
  have h2 := indepNum_delNbhd_add_one_le (G := G) v
  exact hE.le_card_edgeFinset (by omega) _ (cliqueFree_delNbhd h3 v) (by omega)

/-! ### The case `n = 40`, `k = 10` -/

/-- The exact values `e(3,9,m)` for `30 ≤ m ≤ 35`, as lower bounds
([GR] Table 4; see `notes/edge_tables.md`). Hypothesis. -/
def E39Table : Prop :=
  EdgeLowerBound 9 30 86 ∧ EdgeLowerBound 9 31 95 ∧ EdgeLowerBound 9 32 104 ∧
  EdgeLowerBound 9 33 118 ∧ EdgeLowerBound 9 34 129 ∧ EdgeLowerBound 9 35 140

/-- The function `d ↦ e(3,9,39-d)` for `4 ≤ d ≤ 9` (value `0` elsewhere). -/
def e39 : ℕ → ℕ
  | 4 => 140 | 5 => 129 | 6 => 118 | 7 => 104 | 8 => 95 | 9 => 86 | _ => 0

section N40

variable (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]

/-- Per vertex: `e(G - N[v]) ≥ e(3,9,39 - deg v)`. -/
theorem e39_le_card_edgeFinset_delNbhd (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9)
    (hR : Ramsey3Le 9 36) (hT : E39Table) (v : Fin 40) :
    e39 (G.degree v) ≤ #(delNbhd G v).edgeFinset := by
  have hlo := four_le_degree G h3 hα hR v
  have hhi := degree_le_nine G h3 hα v
  have key : ∀ e₀, EdgeLowerBound 9 (40 - G.degree v - 1) e₀ →
      e₀ ≤ #(delNbhd G v).edgeFinset := fun e₀ hE =>
    le_card_edgeFinset_delNbhd (k := 10) h3 hα v (by simpa using hE)
  obtain ⟨h30, h31, h32, h33, h34, h35⟩ := hT
  interval_cases h : G.degree v
  · exact key _ h35
  · exact key _ h34
  · exact key _ h33
  · exact key _ h32
  · exact key _ h31
  · exact key _ h30

/-- Inequality (4) of [GR] for `n = 40`:
`∑_v (e(3,9,39 - deg v) + (deg v)^2) ≤ 40 · e(G)`. -/
theorem sum_e39_add_sq_le (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR : Ramsey3Le 9 36)
    (hT : E39Table) :
    ∑ v, (e39 (G.degree v) + G.degree v ^ 2) ≤ 40 * #G.edgeFinset := by
  have h := sum_card_edgeFinset_delNbhd_add h3 (G := G)
  simp only [Fintype.card_fin] at h
  rw [← h, sum_add_distrib]
  gcongr with v
  exact e39_le_card_edgeFinset_delNbhd G h3 hα hR hT v

/-- Pure inequality (4) gives `e(G) ≥ 159` for a `(3,10,40)`-graph
(hypotheses: `R(3,9) ≤ 36` and the `e(3,9,m)` table). -/
theorem le_card_edgeFinset (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR : Ramsey3Le 9 36)
    (hT : E39Table) : 159 ≤ #G.edgeFinset := by
  have h4 := sum_e39_add_sq_le G h3 hα hR hT
  have hv : ∀ v, 6 * G.degree v + 111 ≤ e39 (G.degree v) + G.degree v ^ 2 := by
    intro v
    have hlo := four_le_degree G h3 hα hR v
    have hhi := degree_le_nine G h3 hα v
    interval_cases G.degree v <;> simp [e39]
  have hsum : ∑ v : Fin 40, (6 * G.degree v + 111) ≤ 40 * #G.edgeFinset :=
    (sum_le_sum fun v _ => hv v).trans h4
  rw [sum_add_distrib, ← mul_sum, sum_degrees_eq_twice_card_edges] at hsum
  simp at hsum
  omega

end N40

end R310
