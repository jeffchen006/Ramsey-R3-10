/-
Every admissible LP row holds for the class counts `M_ij = Mcl G i j` of a (3,10,40)-graph.
With `Cert.sound` this gives `Cert.no_graph`: a checked certificate excludes its instance.
-/
import R310.LP.Cert
import R310.ClassLP

open Finset

set_option linter.unusedSectionVars false

namespace R310.LP

open SimpleGraph

variable (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj]

/-- The degree distribution `(n4, ..., n9)` of `G`. -/
def distOf : List ℕ := [ncls G 4, ncls G 5, ncls G 6, ncls G 7, ncls G 8, ncls G 9]

/-- The valuation `p ↦ M_p` of the pair variables. -/
def valG (p : ℕ × ℕ) : ℤ := (Mcl G p.1 p.2 : ℤ)

/-- The graph `G` fits the instance `I`: `I.n` is the degree distribution of `G`, every
vertex of degree `i` has `e(H_v) ≥ L_i`, and `G` is MTF if `I.mtf`. -/
structure Fits (I : Inst) : Prop where
  n_eq : I.n = distOf G
  L_ok : ∀ i ∈ Icc 4 9, ∀ v ∈ cls G i, I.Ld i ≤ #(delNbhd G v).edgeFinset
  mtf_ok : I.mtf = true → IsMTF G

theorem sum_Icc49 (f : ℕ → ℕ) : ∑ j ∈ Icc 4 9, f j = f 4 + f 5 + f 6 + f 7 + f 8 + f 9 := by
  rw [show Icc 4 9 = ({4, 5, 6, 7, 8, 9} : Finset ℕ) by decide]
  simp [add_assoc]

theorem evalLF_expand (f val : ℕ × ℕ → ℤ) : evalLF f val =
    f (4,4) * val (4,4) + f (4,5) * val (4,5) + f (4,6) * val (4,6) + f (4,7) * val (4,7) +
    f (4,8) * val (4,8) + f (4,9) * val (4,9) + f (5,5) * val (5,5) + f (5,6) * val (5,6) +
    f (5,7) * val (5,7) + f (5,8) * val (5,8) + f (5,9) * val (5,9) + f (6,6) * val (6,6) +
    f (6,7) * val (6,7) + f (6,8) * val (6,8) + f (6,9) * val (6,9) + f (7,7) * val (7,7) +
    f (7,8) * val (7,8) + f (7,9) * val (7,9) + f (8,8) * val (8,8) + f (8,9) * val (8,9) +
    f (9,9) * val (9,9) := by
  simp only [evalLF, pairs, List.map_cons, List.map_nil, List.sum_cons, List.sum_nil]
  ring

/-- `evalLF` of the indicator of a pair `q`. -/
theorem evalLF_indicator (q : ℕ × ℕ) (hq : q ∈ pairs) (a : ℤ) (val : ℕ × ℕ → ℤ) :
    evalLF (fun p => if p = q then a else 0) val = a * val q := by
  rw [evalLF_expand]
  simp only [pairs, List.mem_cons, List.not_mem_nil, or_false] at hq
  rcases hq with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl |
    rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> simp

/-- `n² ≤ 2 m → ...`: if `2 t ≤ s^2` then `t ≤ 2 ⌊s^2/4⌋`. -/
theorem le_two_mul_sq_div_four (s : ℕ) (t : ℤ) (h : 2 * t ≤ ((s * s : ℕ) : ℤ)) :
    t ≤ ((2 * (s * s / 4) : ℕ) : ℤ) := by
  have hmod : s * s % 4 = 0 ∨ s * s % 4 = 1 := by
    rw [Nat.mul_mod]
    have : s % 4 < 4 := Nat.mod_lt _ (by norm_num)
    interval_cases s % 4 <;> simp
  have hd := Nat.div_add_mod (s * s) 4
  push_cast at h ⊢
  omega

section Valid

variable {G}
variable (hrange : ∀ v, G.degree v ∈ Icc 4 9)
include hrange

theorem get6_distOf (i : ℕ) : get6 (distOf G) i = ncls G i := by
  unfold get6
  split_ifs with h
  · obtain ⟨h1, h2⟩ := h
    interval_cases i <;> rfl
  · symm
    rw [ncls, cls, card_eq_zero, filter_eq_empty_iff]
    intro v _ hv
    have := mem_Icc.1 (hrange v)
    omega

theorem two_mul_card_edgeFinset_eq :
    2 * #G.edgeFinset = 4 * ncls G 4 + 5 * ncls G 5 + 6 * ncls G 6 + 7 * ncls G 7 +
      8 * ncls G 8 + 9 * ncls G 9 := by
  rw [← sum_degrees_eq_twice_card_edges]
  have := sum_weight_univ hrange (fun i => i)
  rw [this, sum_Icc49]

/-- `Σ_{pairs ∋ i} M_p = ∑_j M_ij` and `Σ hypCoef · M = ∑_j j M_ij`, by cases on `i`. -/
theorem evalLF_deg (i : ℕ) (hi : 4 ≤ i ∧ i ≤ 9) :
    evalLF (fun p => if p.1 = i ∨ p.2 = i then 1 else 0) (valG G) =
      ((∑ j ∈ Icc 4 9, Mcl G i j : ℕ) : ℤ) := by
  rw [evalLF_expand, sum_Icc49]
  obtain ⟨h1, h2⟩ := hi
  interval_cases i <;> simp [valG, Mcl_comm G 5 4, Mcl_comm G 6 4, Mcl_comm G 6 5, Mcl_comm G 7 4,
    Mcl_comm G 7 5, Mcl_comm G 7 6, Mcl_comm G 8 4, Mcl_comm G 8 5, Mcl_comm G 8 6,
    Mcl_comm G 8 7, Mcl_comm G 9 4, Mcl_comm G 9 5, Mcl_comm G 9 6, Mcl_comm G 9 7,
    Mcl_comm G 9 8]

theorem evalLF_hyp (i : ℕ) (hi : 4 ≤ i ∧ i ≤ 9) :
    evalLF (hypCoef i) (valG G) = ((∑ j ∈ Icc 4 9, j * Mcl G i j : ℕ) : ℤ) := by
  rw [evalLF_expand, sum_Icc49]
  obtain ⟨h1, h2⟩ := hi
  interval_cases i <;> simp [valG, hypCoef, Mcl_comm G 5 4, Mcl_comm G 6 4, Mcl_comm G 6 5, Mcl_comm G 7 4,
    Mcl_comm G 7 5, Mcl_comm G 7 6, Mcl_comm G 8 4, Mcl_comm G 8 5, Mcl_comm G 8 6,
    Mcl_comm G 8 7, Mcl_comm G 9 4, Mcl_comm G 9 5, Mcl_comm G 9 6, Mcl_comm G 9 7,
    Mcl_comm G 9 8]

theorem evalLF_mantel_le (h3 : G.CliqueFree 3) (I : Inst) (hn : I.n = distOf G) (x : List ℕ) :
    evalLF (coef (.mantel x)) (valG G) ≤ rhs I (.mantel x) := by
  have hc := row_c hrange h3 (fun i => get6 x i)
  simp only [sum_Icc49] at hc
  simp only [Mcl_comm G 5 4, Mcl_comm G 6 4, Mcl_comm G 6 5, Mcl_comm G 7 4,
    Mcl_comm G 7 5, Mcl_comm G 7 6, Mcl_comm G 8 4, Mcl_comm G 8 5, Mcl_comm G 8 6,
    Mcl_comm G 8 7, Mcl_comm G 9 4, Mcl_comm G 9 5, Mcl_comm G 9 6, Mcl_comm G 9 7,
    Mcl_comm G 9 8] at hc
  simp only [rhs, wsum, Inst.nd, hn, get6_distOf hrange]
  apply le_two_mul_sq_div_four
  rw [evalLF_expand]
  simp only [coef, valG]
  push_cast
  simp only [sq] at hc ⊢
  have hc' : ((2 * _ : ℕ) : ℤ) ≤ ((_ : ℕ) : ℤ) := Nat.cast_le.2 hc
  push_cast at hc'
  linarith

theorem evalLF_ub (i j : ℕ) (hij : 4 ≤ i ∧ i ≤ j ∧ j ≤ 9) :
    evalLF (coef (.ub i j)) (valG G) = valG G (i, j) := by
  have hq : (i, j) ∈ pairs := by
    obtain ⟨h1, h2, h3⟩ := hij
    have : i ≤ 9 := by omega
    interval_cases i <;> interval_cases j <;> simp [pairs]
  have := evalLF_indicator (i, j) hq 1 (valG G)
  simp only [one_mul] at this
  exact this

theorem evalLF_forced (i j : ℕ) (hij : 4 ≤ i ∧ i ≤ j ∧ j ≤ 9) :
    evalLF (coef (.forced i j)) (valG G) = -valG G (i, j) := by
  have hq : (i, j) ∈ pairs := by
    obtain ⟨h1, h2, h3⟩ := hij
    have : i ≤ 9 := by omega
    interval_cases i <;> interval_cases j <;> simp [pairs]
  have := evalLF_indicator (i, j) hq (-1) (valG G)
  simp only [neg_one_mul] at this
  exact this

/-- The box: `0 ≤ M_p ≤ ub_p` for every pair. -/
theorem valG_le_ubv (h3 : G.CliqueFree 3) (I : Inst) (hn : I.n = distOf G) (p : ℕ × ℕ)
    (hp : p ∈ pairs) : 0 ≤ valG G p ∧ valG G p ≤ I.ubv p := by
  refine ⟨by simp [valG], ?_⟩
  obtain ⟨a, b⟩ := p
  have hab : 4 ≤ a ∧ a ≤ b ∧ b ≤ 9 := by
    simp only [pairs, List.mem_cons, List.not_mem_nil, or_false, Prod.mk.injEq] at hp
    omega
  simp only [Inst.ubv, Inst.nd, hn, get6_distOf hrange, valG]
  split_ifs with h
  · subst h
    have := row_d_diag hrange h3 a (mem_Icc.2 ⟨hab.1, hab.2.2⟩)
    rw [sq] at this
    exact le_two_mul_sq_div_four _ _ (by exact_mod_cast this)
  · have h1 := row_d (G := G) hrange a b
    have h2 := row_d (G := G) hrange b a
    rw [Mcl_comm] at h2
    exact le_min (by exact_mod_cast h1) (by exact_mod_cast h2)

/-- Every admissible row holds at `valG G`. -/
theorem row_valid (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR8 : Ramsey3Le 8 28)
    (I : Inst) (hfit : Fits G I) (r : Row) (hr : admissible I r = true) :
    evalLF (coef r) (valG G) ≤ rhs I r := by
  have hn := hfit.n_eq
  have hnd : ∀ i, I.nd i = ncls G i := fun i => by rw [Inst.nd, hn, get6_distOf hrange]
  have he : I.e = #G.edgeFinset := by
    rw [Inst.e, Inst.deg2]
    simp only [hnd]
    have := two_mul_card_edgeFinset_eq hrange
    omega
  cases r with
  | degLe i =>
    simp only [admissible, Bool.and_eq_true, decide_eq_true_eq] at hr
    have := evalLF_deg hrange i hr
    change evalLF (fun p => if p.1 = i ∨ p.2 = i then 1 else 0) (valG G) ≤ _
    rw [this, rhs, hnd, row_a hrange]
  | degGe i =>
    simp only [admissible, Bool.and_eq_true, decide_eq_true_eq] at hr
    have h := evalLF_deg hrange i hr
    have h' : evalLF (coef (.degGe i)) (valG G) =
        -evalLF (fun p => if p.1 = i ∨ p.2 = i then 1 else 0) (valG G) := by
      rw [show ∀ t : ℤ, -t = (-1) * t from fun t => by ring, ← evalLF_smul]
      congr 1
      ext ⟨a, b⟩
      simp only [coef]
      split_ifs <;> simp
    rw [h', h, rhs, hnd, row_a hrange]
  | hyp i =>
    simp only [admissible, Bool.and_eq_true, decide_eq_true_eq] at hr
    have h := evalLF_hyp hrange i hr
    change evalLF (hypCoef i) (valG G) ≤ _
    rw [h, rhs, hnd, he]
    have := row_b hrange h3 i (I.Ld i) (hfit.L_ok i (mem_Icc.2 hr))
    rw [Inst.Ld] at this
    push_cast
    have := (Nat.cast_le (α := ℤ)).2 this
    push_cast at this
    simp only [ncls, Inst.Ld] at this ⊢
    linarith
  | mtfZ i =>
    simp only [admissible, Bool.and_eq_true, decide_eq_true_eq] at hr
    obtain ⟨⟨hm, h1⟩, h2⟩ := hr
    have h := evalLF_hyp hrange i ⟨h1, h2⟩
    have h' : evalLF (coef (.mtfZ i)) (valG G) = -evalLF (hypCoef i) (valG G) := by
      rw [show ∀ t : ℤ, -t = (-1) * t from fun t => by ring, ← evalLF_smul]
      congr 1
      funext p
      show -hypCoef i p = -1 * hypCoef i p
      ring
    rw [h', h, rhs, hnd]
    have := row_f hrange (hfit.mtf_ok hm) hα i
    have := (Nat.cast_le (α := ℤ)).2 this
    push_cast at this ⊢
    linarith
  | mantel x => exact evalLF_mantel_le hrange h3 I hn x
  | ub i j =>
    simp only [admissible, Bool.and_eq_true, decide_eq_true_eq] at hr
    rw [evalLF_ub hrange i j ⟨hr.1.1, hr.1.2, hr.2⟩, rhs]
    exact (valG_le_ubv hrange h3 I hn (i, j) (by
      obtain ⟨⟨h1, h2⟩, h3⟩ := hr
      have : i ≤ 9 := by omega
      interval_cases i <;> interval_cases j <;> simp [pairs])).2
  | forced i j =>
    simp only [admissible, Bool.and_eq_true, decide_eq_true_eq] at hr
    obtain ⟨⟨⟨h1, h2⟩, h3'⟩, h4⟩ := hr
    rw [evalLF_forced hrange i j ⟨h1, h2, h3'⟩, rhs, hnd, hnd, valG]
    simp only
    rw [row_e G h3 hα hR8 i j h4]

end Valid

/-- Main link: a checked certificate excludes every (3,10,40)-graph that fits its instance.
Hypotheses: `R(3,9) ≤ 36` (degrees in `[4,9]`) and `R(3,8) ≤ 28` (forced rows). -/
theorem Cert.no_graph (c : Cert) (hc : c.check = true) (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9) (hR : Ramsey3Le 9 36) (hR8 : Ramsey3Le 8 28) (hfit : Fits G c.inst) :
    False := by
  have hrange := degree_mem_Icc G h3 hα hR
  exact c.sound hc (valG G) (fun r hr => row_valid hrange h3 hα hR8 c.inst hfit r hr)
    (fun p hp => valG_le_ubv hrange h3 c.inst hfit.n_eq p hp)

end R310.LP
