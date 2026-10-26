/-
Lemma L8 of `notes/cases.md`: the rows of the class LP. Classes are degree classes
`C_i = {v | deg v = i}`, `n_i = |C_i|`, and `M_ij = ∑_{v ∈ C_i} |N(v) ∩ C_j|`
(so `M_ij = m_ij` for `i ≠ j` and `M_ii = 2 m_ii`, `m_ij` = number of edges between classes).
Degrees range over `I = [4, 9]` (L1).
-/
import R310.Mantel
import R310.MTF
import R310.Pair
import R310.Local

open Finset

set_option linter.unusedSectionVars false

namespace R310

open SimpleGraph

theorem card_mul_eq_sum {α : Type*} (s : Finset α) (c : ℕ) : #s * c = ∑ _x ∈ s, c := by simp

variable (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]

/-- The degree class `C_i`. -/
def cls (i : ℕ) : Finset (Fin 40) := {v | G.degree v = i}

/-- `n_i = |C_i|`. -/
def ncls (i : ℕ) : ℕ := #(cls G i)

/-- `M_ij = ∑_{v ∈ C_i} |N(v) ∩ C_j|`, the number of ordered adjacent pairs `(v, u)` with
`v ∈ C_i`, `u ∈ C_j`. -/
def Mcl (i j : ℕ) : ℕ := ∑ v ∈ cls G i, #{u ∈ G.neighborFinset v | G.degree u = j}

/-- `M_ij = ∑_v ∑_u [deg v = i ∧ v ~ u ∧ deg u = j]`. -/
theorem Mcl_eq_sum (i j : ℕ) :
    Mcl G i j = ∑ v, ∑ u, if G.degree v = i ∧ G.Adj v u ∧ G.degree u = j then 1 else 0 := by
  unfold Mcl cls
  rw [sum_filter]
  refine sum_congr rfl fun v _ => ?_
  rw [card_filter, neighborFinset_eq_filter (G := G), sum_filter]
  split_ifs with h
  · exact sum_congr rfl fun u _ => by by_cases h1 : G.Adj v u <;> by_cases h2 : G.degree u = j <;>
      simp [h, h1, h2]
  · simp [h]

/-- `M_ij = M_ji`. -/
theorem Mcl_comm (i j : ℕ) : Mcl G i j = Mcl G j i := by
  rw [Mcl_eq_sum, Mcl_eq_sum, sum_comm]
  refine sum_congr rfl fun u _ => sum_congr rfl fun v _ => ?_
  exact if_congr (by rw [G.adj_comm]; tauto) rfl rfl

/-- Fibre decomposition of a sum over `N(v)` by the degree of the neighbour. -/
theorem sum_neighbor_fiber (hrange : ∀ v, G.degree v ∈ Icc 4 9) (f : ℕ → ℕ) (v : Fin 40) :
    ∑ u ∈ G.neighborFinset v, f (G.degree u) =
      ∑ j ∈ Icc 4 9, f j * #{u ∈ G.neighborFinset v | G.degree u = j} := by
  have h : ∀ u ∈ G.neighborFinset v, G.degree u ∈ Icc 4 9 := fun u _ => hrange u
  rw [← sum_fiberwise_of_maps_to' h f]
  refine sum_congr rfl fun j _ => ?_
  rw [sum_const, smul_eq_mul, mul_comm]

/-- Fibre decomposition of a sum over all vertices by degree. -/
theorem sum_univ_fiber (hrange : ∀ v, G.degree v ∈ Icc 4 9) (F : Fin 40 → ℕ) :
    ∑ v, F v = ∑ i ∈ Icc 4 9, ∑ v ∈ cls G i, F v := by
  have h : ∀ u ∈ (univ : Finset (Fin 40)), G.degree u ∈ Icc 4 9 := fun u _ => hrange u
  exact (sum_fiberwise_of_maps_to h F).symm

section Rows

variable {G} (hrange : ∀ v, G.degree v ∈ Icc 4 9)
include hrange

/-- L8(a): `∑_j M_ij = i n_i`. -/
theorem row_a (i : ℕ) : ∑ j ∈ Icc 4 9, Mcl G i j = i * ncls G i := by
  unfold Mcl ncls
  rw [sum_comm]
  rw [show i * #(cls G i) = ∑ _v ∈ cls G i, i by rw [sum_const, smul_eq_mul, mul_comm]]
  refine sum_congr rfl fun v hv => ?_
  have := sum_neighbor_fiber G hrange (fun _ => 1) v
  simp only [one_mul, sum_const, smul_eq_mul, mul_one, card_neighborFinset_eq_degree] at this
  rw [← this, (mem_filter.1 hv).2]

/-- `∑_j j M_ij = ∑_{v ∈ C_i} Z(v)`. -/
theorem sum_mul_Mcl (i : ℕ) :
    ∑ j ∈ Icc 4 9, j * Mcl G i j = ∑ v ∈ cls G i, ∑ u ∈ G.neighborFinset v, G.degree u := by
  unfold Mcl
  simp_rw [mul_sum]
  rw [sum_comm]
  refine sum_congr rfl fun v _ => ?_
  exact (sum_neighbor_fiber G hrange id v).symm

/-- L8(b): if every `v ∈ C_i` has `e(H_v) ≥ L`, then `∑_j j M_ij + n_i L ≤ n_i e(G)`. -/
theorem row_b (h3 : G.CliqueFree 3) (i L : ℕ)
    (hL : ∀ v ∈ cls G i, L ≤ #(delNbhd G v).edgeFinset) :
    ∑ j ∈ Icc 4 9, j * Mcl G i j + ncls G i * L ≤ ncls G i * #G.edgeFinset := by
  rw [sum_mul_Mcl hrange, ncls, card_mul_eq_sum, card_mul_eq_sum, ← sum_add_distrib]
  refine sum_le_sum fun v hv => ?_
  have := card_edgeFinset_delNbhd_add_sum_degree h3 (G := G) v
  have := hL v hv
  omega

/-- `∑_u x(deg u) ∑_{v ∈ N(u)} x(deg v) = ∑_i ∑_j x_i x_j M_ij`. -/
theorem sum_weight_eq (x : ℕ → ℕ) :
    ∑ u, x (G.degree u) * ∑ v ∈ G.neighborFinset u, x (G.degree v) =
      ∑ i ∈ Icc 4 9, ∑ j ∈ Icc 4 9, x i * x j * Mcl G i j := by
  rw [sum_univ_fiber G hrange]
  refine sum_congr rfl fun i _ => ?_
  unfold Mcl
  have hm : ∀ j, x i * x j * ∑ v ∈ cls G i, #{u ∈ G.neighborFinset v | G.degree u = j} =
      ∑ v ∈ cls G i, x i * x j * #{u ∈ G.neighborFinset v | G.degree u = j} :=
    fun j => mul_sum _ _ _
  simp_rw [hm]
  rw [sum_comm]
  refine sum_congr rfl fun v hv => ?_
  rw [(mem_filter.1 hv).2, sum_neighbor_fiber G hrange x v, mul_sum]
  exact sum_congr rfl fun j _ => by ring

/-- `∑_u x(deg u) = ∑_i x_i n_i`. -/
theorem sum_weight_univ (x : ℕ → ℕ) :
    ∑ u, x (G.degree u) = ∑ i ∈ Icc 4 9, x i * ncls G i := by
  rw [sum_univ_fiber G hrange]
  refine sum_congr rfl fun i _ => ?_
  rw [ncls, mul_comm, card_mul_eq_sum]
  exact sum_congr rfl fun v hv => by rw [(mem_filter.1 hv).2]

/-- L8(c) (weighted Mantel with class weights): for all `x : ℕ → ℕ`,
`2 ∑_{i,j} x_i x_j M_ij ≤ (∑_i x_i n_i)^2`, i.e. `∑_{i ≤ j} x_i x_j m_ij ≤ (∑ x_i n_i)^2 / 4`. -/
theorem row_c (h3 : G.CliqueFree 3) (x : ℕ → ℕ) :
    2 * ∑ i ∈ Icc 4 9, ∑ j ∈ Icc 4 9, x i * x j * Mcl G i j ≤
      (∑ i ∈ Icc 4 9, x i * ncls G i) ^ 2 := by
  have := weighted_mantel h3 (fun u => x (G.degree u))
  rwa [sum_weight_eq hrange, sum_weight_univ hrange] at this

/-- L8(d): `M_ij ≤ n_i · min(i, n_j)`. -/
theorem row_d (i j : ℕ) : Mcl G i j ≤ ncls G i * min i (ncls G j) := by
  unfold Mcl ncls
  rw [card_mul_eq_sum]
  refine sum_le_sum fun v hv => le_min ?_ ?_
  · rw [← (mem_filter.1 hv).2, ← card_neighborFinset_eq_degree]
    exact card_filter_le _ _
  · refine card_le_card fun u hu => ?_
    simp only [mem_filter] at hu
    simp [cls, hu.2]

/-- L8(d): `2 M_ii ≤ n_i^2` (Mantel inside `C_i`; `M_ii = 2 m_ii`). -/
theorem row_d_diag (h3 : G.CliqueFree 3) (i : ℕ) (hi : i ∈ Icc 4 9) :
    2 * Mcl G i i ≤ ncls G i ^ 2 := by
  have := row_c hrange h3 (fun j => if j = i then 1 else 0)
  simp only [ite_mul, one_mul, zero_mul, mul_ite, mul_one, mul_zero] at this
  simpa [sum_ite_eq', hi] using this

end Rows

/-- L8(e): if `i + j ≤ 10` then all possible edges between `C_i` and `C_j` are present (L6):
`M_ij = n_i (n_j - [i = j])`. Hypothesis `R(3,8) ≤ 28`. -/
theorem row_e (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR8 : Ramsey3Le 8 28) (i j : ℕ)
    (hij : i + j ≤ 10) :
    Mcl G i j = ncls G i * (ncls G j - if i = j then 1 else 0) := by
  unfold Mcl ncls
  rw [card_mul_eq_sum]
  refine sum_congr rfl fun v hv => ?_
  have hvi := (mem_filter.1 hv).2
  have heq : ({u ∈ G.neighborFinset v | G.degree u = j} : Finset (Fin 40)) = (cls G j).erase v := by
    ext u
    simp only [mem_filter, mem_neighborFinset, mem_erase, cls, mem_univ, true_and]
    constructor
    · rintro ⟨hvu, hu⟩
      exact ⟨fun h => G.irrefl (h ▸ hvu), hu⟩
    · rintro ⟨huv, hu⟩
      exact ⟨adj_of_degree_add_le G h3 hα hR8 (Ne.symm huv) (by omega), hu⟩
  rw [heq]
  split_ifs with h
  · subst h
    rw [card_erase_of_mem hv]
  · rw [erase_eq_of_notMem (by simp [cls, hvi, h])]
    simp

/-- L8(f) (MTF only, from M2): `∑_j j M_ij + 11 i n_i ≥ n_i (i^2 + 78)`. -/
theorem row_f {G : SimpleGraph (Fin 40)} [DecidableRel G.Adj]
    (hrange : ∀ v, G.degree v ∈ Icc 4 9) (hG : IsMTF G) (hα : G.indepNum ≤ 9) (i : ℕ) :
    ncls G i * (i ^ 2 + 78) ≤ ∑ j ∈ Icc 4 9, j * Mcl G i j + 11 * i * ncls G i := by
  rw [sum_mul_Mcl hrange, ncls, card_mul_eq_sum, mul_comm, card_mul_eq_sum, ← sum_add_distrib]
  refine sum_le_sum fun v hv => ?_
  have := hG.sum_degree_neighbor_ge G hα v
  rw [(mem_filter.1 hv).2] at this
  omega

/-- L1 in the form used by the class LP: every degree lies in `[4, 9]`. -/
theorem degree_mem_Icc (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR : Ramsey3Le 9 36)
    (v : Fin 40) : G.degree v ∈ Icc 4 9 :=
  mem_Icc.2 ⟨four_le_degree G h3 hα hR v, degree_le_nine G h3 hα v⟩

end R310
