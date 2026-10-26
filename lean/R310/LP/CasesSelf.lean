/-
Case table `self` of agent `cases` (e(G) >= 159), checked by the kernel.
Data: R310/LP/Data/Self*.lean, generated from lean/data/cases_pin1.
Hypotheses of the final theorems: R(3,9) <= 36, R(3,8) <= 28, e(3,9,30..35) table, every (3,9,35)-graph is 8-regular.
-/
import R310.LP.Data.SelfSurv
import R310.LP.Data.SelfLpk
import R310.LP.Data.SelfT9None
import R310.LP.Data.SelfT9U8
import R310.LP.Data.SelfT9Known
import R310.LP.Data.SelfT9Ang

open Finset

namespace R310.LP.Data

open R310 R310.LP SimpleGraph

/-- Enumeration slice `(n4, n5, n6) = (a, b, c)`. -/
def enumSl_self (a b c : ℕ) : Bool :=
  (List.range ((360 - 2 * 159 - 5 * a - 4 * b - 3 * c) / 2 + 1)).all fun d =>
    (List.range (360 - 2 * 159 - 5 * a - 4 * b - 3 * c - 2 * d + 1)).all fun e =>
      !decide (a + b + c + d + e ≤ 40) ||
        !passSimple [a, b, c, d, e, 40 - (a + b + c + d + e)] 159 false ||
        good (surv_self.filter fun n => n.take 3 == [a, b, c]) lpkill_self
          [a, b, c, d, e, 40 - (a + b + c + d + e)]
theorem enumSl_self_0_0_0 : enumSl_self 0 0 0 = true := by decide +kernel
theorem enumSl_self_0_0_1 : enumSl_self 0 0 1 = true := by decide +kernel
theorem enumSl_self_0_0_2 : enumSl_self 0 0 2 = true := by decide +kernel
theorem enumSl_self_0_0_3 : enumSl_self 0 0 3 = true := by decide +kernel
theorem enumSl_self_0_0_4 : enumSl_self 0 0 4 = true := by decide +kernel
theorem enumSl_self_0_0_5 : enumSl_self 0 0 5 = true := by decide +kernel
theorem enumSl_self_0_0_6 : enumSl_self 0 0 6 = true := by decide +kernel
theorem enumSl_self_0_0_7 : enumSl_self 0 0 7 = true := by decide +kernel
theorem enumSl_self_0_0_8 : enumSl_self 0 0 8 = true := by decide +kernel
theorem enumSl_self_0_0_9 : enumSl_self 0 0 9 = true := by decide +kernel
theorem enumSl_self_0_0_10 : enumSl_self 0 0 10 = true := by decide +kernel
theorem enumSl_self_0_0_11 : enumSl_self 0 0 11 = true := by decide +kernel
theorem enumSl_self_0_0_12 : enumSl_self 0 0 12 = true := by decide +kernel
theorem enumSl_self_0_0_13 : enumSl_self 0 0 13 = true := by decide +kernel
theorem enumSl_self_0_0_14 : enumSl_self 0 0 14 = true := by decide +kernel
theorem enumSl_self_0_1_0 : enumSl_self 0 1 0 = true := by decide +kernel
theorem enumSl_self_0_1_1 : enumSl_self 0 1 1 = true := by decide +kernel
theorem enumSl_self_0_1_2 : enumSl_self 0 1 2 = true := by decide +kernel
theorem enumSl_self_0_1_3 : enumSl_self 0 1 3 = true := by decide +kernel
theorem enumSl_self_0_1_4 : enumSl_self 0 1 4 = true := by decide +kernel
theorem enumSl_self_0_1_5 : enumSl_self 0 1 5 = true := by decide +kernel
theorem enumSl_self_0_1_6 : enumSl_self 0 1 6 = true := by decide +kernel
theorem enumSl_self_0_1_7 : enumSl_self 0 1 7 = true := by decide +kernel
theorem enumSl_self_0_1_8 : enumSl_self 0 1 8 = true := by decide +kernel
theorem enumSl_self_0_1_9 : enumSl_self 0 1 9 = true := by decide +kernel
theorem enumSl_self_0_1_10 : enumSl_self 0 1 10 = true := by decide +kernel
theorem enumSl_self_0_1_11 : enumSl_self 0 1 11 = true := by decide +kernel
theorem enumSl_self_0_1_12 : enumSl_self 0 1 12 = true := by decide +kernel
theorem enumSl_self_0_2_0 : enumSl_self 0 2 0 = true := by decide +kernel
theorem enumSl_self_0_2_1 : enumSl_self 0 2 1 = true := by decide +kernel
theorem enumSl_self_0_2_2 : enumSl_self 0 2 2 = true := by decide +kernel
theorem enumSl_self_0_2_3 : enumSl_self 0 2 3 = true := by decide +kernel
theorem enumSl_self_0_2_4 : enumSl_self 0 2 4 = true := by decide +kernel
theorem enumSl_self_0_2_5 : enumSl_self 0 2 5 = true := by decide +kernel
theorem enumSl_self_0_2_6 : enumSl_self 0 2 6 = true := by decide +kernel
theorem enumSl_self_0_2_7 : enumSl_self 0 2 7 = true := by decide +kernel
theorem enumSl_self_0_2_8 : enumSl_self 0 2 8 = true := by decide +kernel
theorem enumSl_self_0_2_9 : enumSl_self 0 2 9 = true := by decide +kernel
theorem enumSl_self_0_2_10 : enumSl_self 0 2 10 = true := by decide +kernel
theorem enumSl_self_0_2_11 : enumSl_self 0 2 11 = true := by decide +kernel
theorem enumSl_self_1_0_0 : enumSl_self 1 0 0 = true := by decide +kernel
theorem enumSl_self_1_0_1 : enumSl_self 1 0 1 = true := by decide +kernel
theorem enumSl_self_1_0_2 : enumSl_self 1 0 2 = true := by decide +kernel
theorem enumSl_self_1_0_3 : enumSl_self 1 0 3 = true := by decide +kernel
theorem enumSl_self_1_0_4 : enumSl_self 1 0 4 = true := by decide +kernel
theorem enumSl_self_1_0_5 : enumSl_self 1 0 5 = true := by decide +kernel
theorem enumSl_self_1_0_6 : enumSl_self 1 0 6 = true := by decide +kernel
theorem enumSl_self_1_0_7 : enumSl_self 1 0 7 = true := by decide +kernel
theorem enumSl_self_1_0_8 : enumSl_self 1 0 8 = true := by decide +kernel
theorem enumSl_self_1_0_9 : enumSl_self 1 0 9 = true := by decide +kernel
theorem enumSl_self_1_0_10 : enumSl_self 1 0 10 = true := by decide +kernel
theorem enumSl_self_1_0_11 : enumSl_self 1 0 11 = true := by decide +kernel
theorem enumSl_self_1_0_12 : enumSl_self 1 0 12 = true := by decide +kernel
theorem enumSl_self_1_1_0 : enumSl_self 1 1 0 = true := by decide +kernel
theorem enumSl_self_1_1_1 : enumSl_self 1 1 1 = true := by decide +kernel
theorem enumSl_self_1_1_2 : enumSl_self 1 1 2 = true := by decide +kernel
theorem enumSl_self_1_1_3 : enumSl_self 1 1 3 = true := by decide +kernel
theorem enumSl_self_1_1_4 : enumSl_self 1 1 4 = true := by decide +kernel
theorem enumSl_self_1_1_5 : enumSl_self 1 1 5 = true := by decide +kernel
theorem enumSl_self_1_1_6 : enumSl_self 1 1 6 = true := by decide +kernel
theorem enumSl_self_1_1_7 : enumSl_self 1 1 7 = true := by decide +kernel
theorem enumSl_self_1_1_8 : enumSl_self 1 1 8 = true := by decide +kernel
theorem enumSl_self_1_1_9 : enumSl_self 1 1 9 = true := by decide +kernel
theorem enumSl_self_1_1_10 : enumSl_self 1 1 10 = true := by decide +kernel
theorem enumSl_self_1_1_11 : enumSl_self 1 1 11 = true := by decide +kernel
theorem enumSl_self_1_2_0 : enumSl_self 1 2 0 = true := by decide +kernel
theorem enumSl_self_1_2_1 : enumSl_self 1 2 1 = true := by decide +kernel
theorem enumSl_self_1_2_2 : enumSl_self 1 2 2 = true := by decide +kernel
theorem enumSl_self_1_2_3 : enumSl_self 1 2 3 = true := by decide +kernel
theorem enumSl_self_1_2_4 : enumSl_self 1 2 4 = true := by decide +kernel
theorem enumSl_self_1_2_5 : enumSl_self 1 2 5 = true := by decide +kernel
theorem enumSl_self_1_2_6 : enumSl_self 1 2 6 = true := by decide +kernel
theorem enumSl_self_1_2_7 : enumSl_self 1 2 7 = true := by decide +kernel
theorem enumSl_self_1_2_8 : enumSl_self 1 2 8 = true := by decide +kernel
theorem enumSl_self_1_2_9 : enumSl_self 1 2 9 = true := by decide +kernel
theorem enumSl_self_2_0_0 : enumSl_self 2 0 0 = true := by decide +kernel
theorem enumSl_self_2_0_1 : enumSl_self 2 0 1 = true := by decide +kernel
theorem enumSl_self_2_0_2 : enumSl_self 2 0 2 = true := by decide +kernel
theorem enumSl_self_2_0_3 : enumSl_self 2 0 3 = true := by decide +kernel
theorem enumSl_self_2_0_4 : enumSl_self 2 0 4 = true := by decide +kernel
theorem enumSl_self_2_0_5 : enumSl_self 2 0 5 = true := by decide +kernel
theorem enumSl_self_2_0_6 : enumSl_self 2 0 6 = true := by decide +kernel
theorem enumSl_self_2_0_7 : enumSl_self 2 0 7 = true := by decide +kernel
theorem enumSl_self_2_0_8 : enumSl_self 2 0 8 = true := by decide +kernel
theorem enumSl_self_2_0_9 : enumSl_self 2 0 9 = true := by decide +kernel
theorem enumSl_self_2_0_10 : enumSl_self 2 0 10 = true := by decide +kernel
theorem enumSl_self_2_1_0 : enumSl_self 2 1 0 = true := by decide +kernel
theorem enumSl_self_2_1_1 : enumSl_self 2 1 1 = true := by decide +kernel
theorem enumSl_self_2_1_2 : enumSl_self 2 1 2 = true := by decide +kernel
theorem enumSl_self_2_1_3 : enumSl_self 2 1 3 = true := by decide +kernel
theorem enumSl_self_2_1_4 : enumSl_self 2 1 4 = true := by decide +kernel
theorem enumSl_self_2_1_5 : enumSl_self 2 1 5 = true := by decide +kernel
theorem enumSl_self_2_1_6 : enumSl_self 2 1 6 = true := by decide +kernel
theorem enumSl_self_2_1_7 : enumSl_self 2 1 7 = true := by decide +kernel
theorem enumSl_self_2_1_8 : enumSl_self 2 1 8 = true := by decide +kernel
theorem enumSl_self_2_1_9 : enumSl_self 2 1 9 = true := by decide +kernel
theorem enumSl_self_2_2_0 : enumSl_self 2 2 0 = true := by decide +kernel
theorem enumSl_self_2_2_1 : enumSl_self 2 2 1 = true := by decide +kernel
theorem enumSl_self_2_2_2 : enumSl_self 2 2 2 = true := by decide +kernel
theorem enumSl_self_2_2_3 : enumSl_self 2 2 3 = true := by decide +kernel
theorem enumSl_self_2_2_4 : enumSl_self 2 2 4 = true := by decide +kernel
theorem enumSl_self_2_2_5 : enumSl_self 2 2 5 = true := by decide +kernel
theorem enumSl_self_2_2_6 : enumSl_self 2 2 6 = true := by decide +kernel
theorem enumSl_self_2_2_7 : enumSl_self 2 2 7 = true := by decide +kernel
theorem enumSl_self_2_2_8 : enumSl_self 2 2 8 = true := by decide +kernel

theorem enumSl_self_all (a b c : ℕ) (ha : a < 3) (hb : b < 3)
    (hc : c < (360 - 2 * 159 - 5 * a - 4 * b) / 3 + 1) : enumSl_self a b c = true := by
  interval_cases a <;> interval_cases b <;> simp at hc <;> interval_cases c
  · exact enumSl_self_0_0_0
  · exact enumSl_self_0_0_1
  · exact enumSl_self_0_0_2
  · exact enumSl_self_0_0_3
  · exact enumSl_self_0_0_4
  · exact enumSl_self_0_0_5
  · exact enumSl_self_0_0_6
  · exact enumSl_self_0_0_7
  · exact enumSl_self_0_0_8
  · exact enumSl_self_0_0_9
  · exact enumSl_self_0_0_10
  · exact enumSl_self_0_0_11
  · exact enumSl_self_0_0_12
  · exact enumSl_self_0_0_13
  · exact enumSl_self_0_0_14
  · exact enumSl_self_0_1_0
  · exact enumSl_self_0_1_1
  · exact enumSl_self_0_1_2
  · exact enumSl_self_0_1_3
  · exact enumSl_self_0_1_4
  · exact enumSl_self_0_1_5
  · exact enumSl_self_0_1_6
  · exact enumSl_self_0_1_7
  · exact enumSl_self_0_1_8
  · exact enumSl_self_0_1_9
  · exact enumSl_self_0_1_10
  · exact enumSl_self_0_1_11
  · exact enumSl_self_0_1_12
  · exact enumSl_self_0_2_0
  · exact enumSl_self_0_2_1
  · exact enumSl_self_0_2_2
  · exact enumSl_self_0_2_3
  · exact enumSl_self_0_2_4
  · exact enumSl_self_0_2_5
  · exact enumSl_self_0_2_6
  · exact enumSl_self_0_2_7
  · exact enumSl_self_0_2_8
  · exact enumSl_self_0_2_9
  · exact enumSl_self_0_2_10
  · exact enumSl_self_0_2_11
  · exact enumSl_self_1_0_0
  · exact enumSl_self_1_0_1
  · exact enumSl_self_1_0_2
  · exact enumSl_self_1_0_3
  · exact enumSl_self_1_0_4
  · exact enumSl_self_1_0_5
  · exact enumSl_self_1_0_6
  · exact enumSl_self_1_0_7
  · exact enumSl_self_1_0_8
  · exact enumSl_self_1_0_9
  · exact enumSl_self_1_0_10
  · exact enumSl_self_1_0_11
  · exact enumSl_self_1_0_12
  · exact enumSl_self_1_1_0
  · exact enumSl_self_1_1_1
  · exact enumSl_self_1_1_2
  · exact enumSl_self_1_1_3
  · exact enumSl_self_1_1_4
  · exact enumSl_self_1_1_5
  · exact enumSl_self_1_1_6
  · exact enumSl_self_1_1_7
  · exact enumSl_self_1_1_8
  · exact enumSl_self_1_1_9
  · exact enumSl_self_1_1_10
  · exact enumSl_self_1_1_11
  · exact enumSl_self_1_2_0
  · exact enumSl_self_1_2_1
  · exact enumSl_self_1_2_2
  · exact enumSl_self_1_2_3
  · exact enumSl_self_1_2_4
  · exact enumSl_self_1_2_5
  · exact enumSl_self_1_2_6
  · exact enumSl_self_1_2_7
  · exact enumSl_self_1_2_8
  · exact enumSl_self_1_2_9
  · exact enumSl_self_2_0_0
  · exact enumSl_self_2_0_1
  · exact enumSl_self_2_0_2
  · exact enumSl_self_2_0_3
  · exact enumSl_self_2_0_4
  · exact enumSl_self_2_0_5
  · exact enumSl_self_2_0_6
  · exact enumSl_self_2_0_7
  · exact enumSl_self_2_0_8
  · exact enumSl_self_2_0_9
  · exact enumSl_self_2_0_10
  · exact enumSl_self_2_1_0
  · exact enumSl_self_2_1_1
  · exact enumSl_self_2_1_2
  · exact enumSl_self_2_1_3
  · exact enumSl_self_2_1_4
  · exact enumSl_self_2_1_5
  · exact enumSl_self_2_1_6
  · exact enumSl_self_2_1_7
  · exact enumSl_self_2_1_8
  · exact enumSl_self_2_1_9
  · exact enumSl_self_2_2_0
  · exact enumSl_self_2_2_1
  · exact enumSl_self_2_2_2
  · exact enumSl_self_2_2_3
  · exact enumSl_self_2_2_4
  · exact enumSl_self_2_2_5
  · exact enumSl_self_2_2_6
  · exact enumSl_self_2_2_7
  · exact enumSl_self_2_2_8

theorem good_filter {surv : List (List ℕ)} {lpk : List (List ℕ × Cert)} {p : List ℕ → Bool}
    {n : List ℕ} (h : good (surv.filter p) lpk n = true) : good surv lpk n = true := by
  unfold good at h ⊢
  simp only [Bool.or_eq_true, List.contains_iff_mem, List.mem_filter] at h ⊢
  tauto

theorem enum_self : enumOK 159 false surv_self lpkill_self = true := by
  unfold enumOK enumSlice
  simp only [List.all_eq_true, List.mem_range]
  intro a ha b hb c hc d hd e he
  have h := enumSl_self_all a b c ha hb hc
  unfold enumSl_self at h
  simp only [List.all_eq_true, List.mem_range] at h
  have := h d hd e he
  simp only [Bool.or_eq_true] at this ⊢
  rcases this with h1 | h1
  · exact Or.inl h1
  · exact Or.inr (good_filter h1)

/-- Case table: the degree distribution `(n4..n9)` of every (3,10,40)-graph is in `surv_self`. -/
theorem caseTable_self
    (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9)
    (hR : Ramsey3Le 9 36) (hR8 : Ramsey3Le 8 28) (hT : E39Table)
    (h35 : Regular35) :
    distOf G ∈ surv_self :=
  caseTable h3 hα hR hR8 hT enum_self lpkill_self_ok (le_card_edgeFinset G h3 hα hR hT) (fun h => absurd h (by simp)) (fun _ => h35)

theorem cov_self_U8 : covered surv_self t9_self_U8 = true := by
  apply covered_of_eq
  decide +kernel

/-- t9 table, scenario `U8`: under the gluing hypothesis `Glue U_U8 G`, some 9-vertex `v` of a
(3,10,40)-graph has `e(H_v) ≤ t9of t9_self_U8 (distOf G)`. -/
theorem t9_self_U8_main
    (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9)
    (hR : Ramsey3Le 9 36) (hR8 : Ramsey3Le 8 28) (hT : E39Table)
    (h35 : Regular35)
    (hglue : Glue U_U8 G) :
    ∃ v, G.degree v = 9 ∧ #(delNbhd G v).edgeFinset ≤ t9of t9_self_U8 (distOf G) :=
  t9_main h3 hα hR hR8 hT t9_self_U8_ok cov_self_U8 (caseTable_self G h3 hα hR hR8 hT h35) (fun h => absurd h (by simp)) hglue

theorem cov_self_known : covered surv_self t9_self_known = true := by
  apply covered_of_eq
  decide +kernel

/-- t9 table, scenario `known`: under the gluing hypothesis `Glue U_known G`, some 9-vertex `v` of a
(3,10,40)-graph has `e(H_v) ≤ t9of t9_self_known (distOf G)`. -/
theorem t9_self_known_main
    (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9)
    (hR : Ramsey3Le 9 36) (hR8 : Ramsey3Le 8 28) (hT : E39Table)
    (h35 : Regular35)
    (hglue : Glue U_known G) :
    ∃ v, G.degree v = 9 ∧ #(delNbhd G v).edgeFinset ≤ t9of t9_self_known (distOf G) :=
  t9_main h3 hα hR hR8 hT t9_self_known_ok cov_self_known (caseTable_self G h3 hα hR hR8 hT h35) (fun h => absurd h (by simp)) hglue

theorem cov_self_ang : covered surv_self t9_self_ang = true := by
  apply covered_of_eq
  decide +kernel

/-- t9 table, scenario `ang`: under the gluing hypothesis `Glue U_ang G`, some 9-vertex `v` of a
(3,10,40)-graph has `e(H_v) ≤ t9of t9_self_ang (distOf G)`. -/
theorem t9_self_ang_main
    (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9)
    (hR : Ramsey3Le 9 36) (hR8 : Ramsey3Le 8 28) (hT : E39Table)
    (h35 : Regular35)
    (hglue : Glue U_ang G) :
    ∃ v, G.degree v = 9 ∧ #(delNbhd G v).edgeFinset ≤ t9of t9_self_ang (distOf G) :=
  t9_main h3 hα hR hR8 hT t9_self_ang_ok cov_self_ang (caseTable_self G h3 hα hR hR8 hT h35) (fun h => absurd h (by simp)) hglue

end R310.LP.Data
