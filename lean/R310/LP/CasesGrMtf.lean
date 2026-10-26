/-
Case table `gr_mtf` of agent `cases` (e(G) >= 161, MTF), checked by the kernel.
Data: R310/LP/Data/GrMtf*.lean, generated from lean/data/cases_pin1.
Hypotheses of the final theorems: R(3,9) <= 36, R(3,8) <= 28, e(3,9,30..35) table, e(3,10,40) >= 161.
-/
import R310.LP.Data.GrMtfSurv
import R310.LP.Data.GrMtfLpk
import R310.LP.Data.GrMtfT9None
import R310.LP.Data.GrMtfT9U8
import R310.LP.Data.GrMtfT9Known
import R310.LP.Data.GrMtfT9Ang

open Finset

namespace R310.LP.Data

open R310 R310.LP SimpleGraph

/-- Enumeration slice `(n4, n5, n6) = (a, b, c)`. -/
def enumSl_gr_mtf (a b c : ℕ) : Bool :=
  (List.range ((360 - 2 * 161 - 5 * a - 4 * b - 3 * c) / 2 + 1)).all fun d =>
    (List.range (360 - 2 * 161 - 5 * a - 4 * b - 3 * c - 2 * d + 1)).all fun e =>
      !decide (a + b + c + d + e ≤ 40) ||
        !passSimple [a, b, c, d, e, 40 - (a + b + c + d + e)] 161 true ||
        good (surv_gr_mtf.filter fun n => n.take 3 == [a, b, c]) lpkill_gr_mtf
          [a, b, c, d, e, 40 - (a + b + c + d + e)]
theorem enumSl_gr_mtf_0_0_0 : enumSl_gr_mtf 0 0 0 = true := by decide +kernel
theorem enumSl_gr_mtf_0_0_1 : enumSl_gr_mtf 0 0 1 = true := by decide +kernel
theorem enumSl_gr_mtf_0_0_2 : enumSl_gr_mtf 0 0 2 = true := by decide +kernel
theorem enumSl_gr_mtf_0_0_3 : enumSl_gr_mtf 0 0 3 = true := by decide +kernel
theorem enumSl_gr_mtf_0_0_4 : enumSl_gr_mtf 0 0 4 = true := by decide +kernel
theorem enumSl_gr_mtf_0_0_5 : enumSl_gr_mtf 0 0 5 = true := by decide +kernel
theorem enumSl_gr_mtf_0_0_6 : enumSl_gr_mtf 0 0 6 = true := by decide +kernel
theorem enumSl_gr_mtf_0_0_7 : enumSl_gr_mtf 0 0 7 = true := by decide +kernel
theorem enumSl_gr_mtf_0_0_8 : enumSl_gr_mtf 0 0 8 = true := by decide +kernel
theorem enumSl_gr_mtf_0_0_9 : enumSl_gr_mtf 0 0 9 = true := by decide +kernel
theorem enumSl_gr_mtf_0_0_10 : enumSl_gr_mtf 0 0 10 = true := by decide +kernel
theorem enumSl_gr_mtf_0_0_11 : enumSl_gr_mtf 0 0 11 = true := by decide +kernel
theorem enumSl_gr_mtf_0_0_12 : enumSl_gr_mtf 0 0 12 = true := by decide +kernel
theorem enumSl_gr_mtf_0_1_0 : enumSl_gr_mtf 0 1 0 = true := by decide +kernel
theorem enumSl_gr_mtf_0_1_1 : enumSl_gr_mtf 0 1 1 = true := by decide +kernel
theorem enumSl_gr_mtf_0_1_2 : enumSl_gr_mtf 0 1 2 = true := by decide +kernel
theorem enumSl_gr_mtf_0_1_3 : enumSl_gr_mtf 0 1 3 = true := by decide +kernel
theorem enumSl_gr_mtf_0_1_4 : enumSl_gr_mtf 0 1 4 = true := by decide +kernel
theorem enumSl_gr_mtf_0_1_5 : enumSl_gr_mtf 0 1 5 = true := by decide +kernel
theorem enumSl_gr_mtf_0_1_6 : enumSl_gr_mtf 0 1 6 = true := by decide +kernel
theorem enumSl_gr_mtf_0_1_7 : enumSl_gr_mtf 0 1 7 = true := by decide +kernel
theorem enumSl_gr_mtf_0_1_8 : enumSl_gr_mtf 0 1 8 = true := by decide +kernel
theorem enumSl_gr_mtf_0_1_9 : enumSl_gr_mtf 0 1 9 = true := by decide +kernel
theorem enumSl_gr_mtf_0_1_10 : enumSl_gr_mtf 0 1 10 = true := by decide +kernel
theorem enumSl_gr_mtf_0_1_11 : enumSl_gr_mtf 0 1 11 = true := by decide +kernel
theorem enumSl_gr_mtf_0_2_0 : enumSl_gr_mtf 0 2 0 = true := by decide +kernel
theorem enumSl_gr_mtf_0_2_1 : enumSl_gr_mtf 0 2 1 = true := by decide +kernel
theorem enumSl_gr_mtf_0_2_2 : enumSl_gr_mtf 0 2 2 = true := by decide +kernel
theorem enumSl_gr_mtf_0_2_3 : enumSl_gr_mtf 0 2 3 = true := by decide +kernel
theorem enumSl_gr_mtf_0_2_4 : enumSl_gr_mtf 0 2 4 = true := by decide +kernel
theorem enumSl_gr_mtf_0_2_5 : enumSl_gr_mtf 0 2 5 = true := by decide +kernel
theorem enumSl_gr_mtf_0_2_6 : enumSl_gr_mtf 0 2 6 = true := by decide +kernel
theorem enumSl_gr_mtf_0_2_7 : enumSl_gr_mtf 0 2 7 = true := by decide +kernel
theorem enumSl_gr_mtf_0_2_8 : enumSl_gr_mtf 0 2 8 = true := by decide +kernel
theorem enumSl_gr_mtf_0_2_9 : enumSl_gr_mtf 0 2 9 = true := by decide +kernel
theorem enumSl_gr_mtf_0_2_10 : enumSl_gr_mtf 0 2 10 = true := by decide +kernel
theorem enumSl_gr_mtf_1_0_0 : enumSl_gr_mtf 1 0 0 = true := by decide +kernel
theorem enumSl_gr_mtf_1_0_1 : enumSl_gr_mtf 1 0 1 = true := by decide +kernel
theorem enumSl_gr_mtf_1_0_2 : enumSl_gr_mtf 1 0 2 = true := by decide +kernel
theorem enumSl_gr_mtf_1_0_3 : enumSl_gr_mtf 1 0 3 = true := by decide +kernel
theorem enumSl_gr_mtf_1_0_4 : enumSl_gr_mtf 1 0 4 = true := by decide +kernel
theorem enumSl_gr_mtf_1_0_5 : enumSl_gr_mtf 1 0 5 = true := by decide +kernel
theorem enumSl_gr_mtf_1_0_6 : enumSl_gr_mtf 1 0 6 = true := by decide +kernel
theorem enumSl_gr_mtf_1_0_7 : enumSl_gr_mtf 1 0 7 = true := by decide +kernel
theorem enumSl_gr_mtf_1_0_8 : enumSl_gr_mtf 1 0 8 = true := by decide +kernel
theorem enumSl_gr_mtf_1_0_9 : enumSl_gr_mtf 1 0 9 = true := by decide +kernel
theorem enumSl_gr_mtf_1_0_10 : enumSl_gr_mtf 1 0 10 = true := by decide +kernel
theorem enumSl_gr_mtf_1_0_11 : enumSl_gr_mtf 1 0 11 = true := by decide +kernel
theorem enumSl_gr_mtf_1_1_0 : enumSl_gr_mtf 1 1 0 = true := by decide +kernel
theorem enumSl_gr_mtf_1_1_1 : enumSl_gr_mtf 1 1 1 = true := by decide +kernel
theorem enumSl_gr_mtf_1_1_2 : enumSl_gr_mtf 1 1 2 = true := by decide +kernel
theorem enumSl_gr_mtf_1_1_3 : enumSl_gr_mtf 1 1 3 = true := by decide +kernel
theorem enumSl_gr_mtf_1_1_4 : enumSl_gr_mtf 1 1 4 = true := by decide +kernel
theorem enumSl_gr_mtf_1_1_5 : enumSl_gr_mtf 1 1 5 = true := by decide +kernel
theorem enumSl_gr_mtf_1_1_6 : enumSl_gr_mtf 1 1 6 = true := by decide +kernel
theorem enumSl_gr_mtf_1_1_7 : enumSl_gr_mtf 1 1 7 = true := by decide +kernel
theorem enumSl_gr_mtf_1_1_8 : enumSl_gr_mtf 1 1 8 = true := by decide +kernel
theorem enumSl_gr_mtf_1_1_9 : enumSl_gr_mtf 1 1 9 = true := by decide +kernel
theorem enumSl_gr_mtf_1_2_0 : enumSl_gr_mtf 1 2 0 = true := by decide +kernel
theorem enumSl_gr_mtf_1_2_1 : enumSl_gr_mtf 1 2 1 = true := by decide +kernel
theorem enumSl_gr_mtf_1_2_2 : enumSl_gr_mtf 1 2 2 = true := by decide +kernel
theorem enumSl_gr_mtf_1_2_3 : enumSl_gr_mtf 1 2 3 = true := by decide +kernel
theorem enumSl_gr_mtf_1_2_4 : enumSl_gr_mtf 1 2 4 = true := by decide +kernel
theorem enumSl_gr_mtf_1_2_5 : enumSl_gr_mtf 1 2 5 = true := by decide +kernel
theorem enumSl_gr_mtf_1_2_6 : enumSl_gr_mtf 1 2 6 = true := by decide +kernel
theorem enumSl_gr_mtf_1_2_7 : enumSl_gr_mtf 1 2 7 = true := by decide +kernel
theorem enumSl_gr_mtf_1_2_8 : enumSl_gr_mtf 1 2 8 = true := by decide +kernel
theorem enumSl_gr_mtf_2_0_0 : enumSl_gr_mtf 2 0 0 = true := by decide +kernel
theorem enumSl_gr_mtf_2_0_1 : enumSl_gr_mtf 2 0 1 = true := by decide +kernel
theorem enumSl_gr_mtf_2_0_2 : enumSl_gr_mtf 2 0 2 = true := by decide +kernel
theorem enumSl_gr_mtf_2_0_3 : enumSl_gr_mtf 2 0 3 = true := by decide +kernel
theorem enumSl_gr_mtf_2_0_4 : enumSl_gr_mtf 2 0 4 = true := by decide +kernel
theorem enumSl_gr_mtf_2_0_5 : enumSl_gr_mtf 2 0 5 = true := by decide +kernel
theorem enumSl_gr_mtf_2_0_6 : enumSl_gr_mtf 2 0 6 = true := by decide +kernel
theorem enumSl_gr_mtf_2_0_7 : enumSl_gr_mtf 2 0 7 = true := by decide +kernel
theorem enumSl_gr_mtf_2_0_8 : enumSl_gr_mtf 2 0 8 = true := by decide +kernel
theorem enumSl_gr_mtf_2_0_9 : enumSl_gr_mtf 2 0 9 = true := by decide +kernel
theorem enumSl_gr_mtf_2_1_0 : enumSl_gr_mtf 2 1 0 = true := by decide +kernel
theorem enumSl_gr_mtf_2_1_1 : enumSl_gr_mtf 2 1 1 = true := by decide +kernel
theorem enumSl_gr_mtf_2_1_2 : enumSl_gr_mtf 2 1 2 = true := by decide +kernel
theorem enumSl_gr_mtf_2_1_3 : enumSl_gr_mtf 2 1 3 = true := by decide +kernel
theorem enumSl_gr_mtf_2_1_4 : enumSl_gr_mtf 2 1 4 = true := by decide +kernel
theorem enumSl_gr_mtf_2_1_5 : enumSl_gr_mtf 2 1 5 = true := by decide +kernel
theorem enumSl_gr_mtf_2_1_6 : enumSl_gr_mtf 2 1 6 = true := by decide +kernel
theorem enumSl_gr_mtf_2_1_7 : enumSl_gr_mtf 2 1 7 = true := by decide +kernel
theorem enumSl_gr_mtf_2_1_8 : enumSl_gr_mtf 2 1 8 = true := by decide +kernel
theorem enumSl_gr_mtf_2_2_0 : enumSl_gr_mtf 2 2 0 = true := by decide +kernel
theorem enumSl_gr_mtf_2_2_1 : enumSl_gr_mtf 2 2 1 = true := by decide +kernel
theorem enumSl_gr_mtf_2_2_2 : enumSl_gr_mtf 2 2 2 = true := by decide +kernel
theorem enumSl_gr_mtf_2_2_3 : enumSl_gr_mtf 2 2 3 = true := by decide +kernel
theorem enumSl_gr_mtf_2_2_4 : enumSl_gr_mtf 2 2 4 = true := by decide +kernel
theorem enumSl_gr_mtf_2_2_5 : enumSl_gr_mtf 2 2 5 = true := by decide +kernel
theorem enumSl_gr_mtf_2_2_6 : enumSl_gr_mtf 2 2 6 = true := by decide +kernel

theorem enumSl_gr_mtf_all (a b c : ℕ) (ha : a < 3) (hb : b < 3)
    (hc : c < (360 - 2 * 161 - 5 * a - 4 * b) / 3 + 1) : enumSl_gr_mtf a b c = true := by
  interval_cases a <;> interval_cases b <;> simp at hc <;> interval_cases c
  · exact enumSl_gr_mtf_0_0_0
  · exact enumSl_gr_mtf_0_0_1
  · exact enumSl_gr_mtf_0_0_2
  · exact enumSl_gr_mtf_0_0_3
  · exact enumSl_gr_mtf_0_0_4
  · exact enumSl_gr_mtf_0_0_5
  · exact enumSl_gr_mtf_0_0_6
  · exact enumSl_gr_mtf_0_0_7
  · exact enumSl_gr_mtf_0_0_8
  · exact enumSl_gr_mtf_0_0_9
  · exact enumSl_gr_mtf_0_0_10
  · exact enumSl_gr_mtf_0_0_11
  · exact enumSl_gr_mtf_0_0_12
  · exact enumSl_gr_mtf_0_1_0
  · exact enumSl_gr_mtf_0_1_1
  · exact enumSl_gr_mtf_0_1_2
  · exact enumSl_gr_mtf_0_1_3
  · exact enumSl_gr_mtf_0_1_4
  · exact enumSl_gr_mtf_0_1_5
  · exact enumSl_gr_mtf_0_1_6
  · exact enumSl_gr_mtf_0_1_7
  · exact enumSl_gr_mtf_0_1_8
  · exact enumSl_gr_mtf_0_1_9
  · exact enumSl_gr_mtf_0_1_10
  · exact enumSl_gr_mtf_0_1_11
  · exact enumSl_gr_mtf_0_2_0
  · exact enumSl_gr_mtf_0_2_1
  · exact enumSl_gr_mtf_0_2_2
  · exact enumSl_gr_mtf_0_2_3
  · exact enumSl_gr_mtf_0_2_4
  · exact enumSl_gr_mtf_0_2_5
  · exact enumSl_gr_mtf_0_2_6
  · exact enumSl_gr_mtf_0_2_7
  · exact enumSl_gr_mtf_0_2_8
  · exact enumSl_gr_mtf_0_2_9
  · exact enumSl_gr_mtf_0_2_10
  · exact enumSl_gr_mtf_1_0_0
  · exact enumSl_gr_mtf_1_0_1
  · exact enumSl_gr_mtf_1_0_2
  · exact enumSl_gr_mtf_1_0_3
  · exact enumSl_gr_mtf_1_0_4
  · exact enumSl_gr_mtf_1_0_5
  · exact enumSl_gr_mtf_1_0_6
  · exact enumSl_gr_mtf_1_0_7
  · exact enumSl_gr_mtf_1_0_8
  · exact enumSl_gr_mtf_1_0_9
  · exact enumSl_gr_mtf_1_0_10
  · exact enumSl_gr_mtf_1_0_11
  · exact enumSl_gr_mtf_1_1_0
  · exact enumSl_gr_mtf_1_1_1
  · exact enumSl_gr_mtf_1_1_2
  · exact enumSl_gr_mtf_1_1_3
  · exact enumSl_gr_mtf_1_1_4
  · exact enumSl_gr_mtf_1_1_5
  · exact enumSl_gr_mtf_1_1_6
  · exact enumSl_gr_mtf_1_1_7
  · exact enumSl_gr_mtf_1_1_8
  · exact enumSl_gr_mtf_1_1_9
  · exact enumSl_gr_mtf_1_2_0
  · exact enumSl_gr_mtf_1_2_1
  · exact enumSl_gr_mtf_1_2_2
  · exact enumSl_gr_mtf_1_2_3
  · exact enumSl_gr_mtf_1_2_4
  · exact enumSl_gr_mtf_1_2_5
  · exact enumSl_gr_mtf_1_2_6
  · exact enumSl_gr_mtf_1_2_7
  · exact enumSl_gr_mtf_1_2_8
  · exact enumSl_gr_mtf_2_0_0
  · exact enumSl_gr_mtf_2_0_1
  · exact enumSl_gr_mtf_2_0_2
  · exact enumSl_gr_mtf_2_0_3
  · exact enumSl_gr_mtf_2_0_4
  · exact enumSl_gr_mtf_2_0_5
  · exact enumSl_gr_mtf_2_0_6
  · exact enumSl_gr_mtf_2_0_7
  · exact enumSl_gr_mtf_2_0_8
  · exact enumSl_gr_mtf_2_0_9
  · exact enumSl_gr_mtf_2_1_0
  · exact enumSl_gr_mtf_2_1_1
  · exact enumSl_gr_mtf_2_1_2
  · exact enumSl_gr_mtf_2_1_3
  · exact enumSl_gr_mtf_2_1_4
  · exact enumSl_gr_mtf_2_1_5
  · exact enumSl_gr_mtf_2_1_6
  · exact enumSl_gr_mtf_2_1_7
  · exact enumSl_gr_mtf_2_1_8
  · exact enumSl_gr_mtf_2_2_0
  · exact enumSl_gr_mtf_2_2_1
  · exact enumSl_gr_mtf_2_2_2
  · exact enumSl_gr_mtf_2_2_3
  · exact enumSl_gr_mtf_2_2_4
  · exact enumSl_gr_mtf_2_2_5
  · exact enumSl_gr_mtf_2_2_6

theorem good_filter {surv : List (List ℕ)} {lpk : List (List ℕ × Cert)} {p : List ℕ → Bool}
    {n : List ℕ} (h : good (surv.filter p) lpk n = true) : good surv lpk n = true := by
  unfold good at h ⊢
  simp only [Bool.or_eq_true, List.contains_iff_mem, List.mem_filter] at h ⊢
  tauto

theorem enum_gr_mtf : enumOK 161 true surv_gr_mtf lpkill_gr_mtf = true := by
  unfold enumOK enumSlice
  simp only [List.all_eq_true, List.mem_range]
  intro a ha b hb c hc d hd e he
  have h := enumSl_gr_mtf_all a b c ha hb hc
  unfold enumSl_gr_mtf at h
  simp only [List.all_eq_true, List.mem_range] at h
  have := h d hd e he
  simp only [Bool.or_eq_true] at this ⊢
  rcases this with h1 | h1
  · exact Or.inl h1
  · exact Or.inr (good_filter h1)

/-- Case table: the degree distribution `(n4..n9)` of every maximal triangle-free (3,10,40)-graph is in `surv_gr_mtf`. -/
theorem caseTable_gr_mtf
    (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9)
    (hmtf : IsMTF G)
    (hR : Ramsey3Le 9 36) (hR8 : Ramsey3Le 8 28) (hT : E39Table)
    (hE : EdgeLowerBound 10 40 161) :
    distOf G ∈ surv_gr_mtf :=
  caseTable h3 hα hR hR8 hT enum_gr_mtf lpkill_gr_mtf_ok (hE.le_card_edgeFinset (by simp) G h3 (by omega)) (fun _ => hmtf) (fun ⟨u, hu⟩ => absurd hu (by have := hmtf.six_le_degree G hα u; omega))

theorem cov_gr_mtf_none : covered surv_gr_mtf t9_gr_mtf_none = true := by
  apply covered_of_eq
  decide +kernel

/-- t9 table, scenario `none`: under the gluing hypothesis `Glue U_none G`, some 9-vertex `v` of a
maximal triangle-free (3,10,40)-graph has `e(H_v) ≤ t9of t9_gr_mtf_none (distOf G)`. -/
theorem t9_gr_mtf_none_main
    (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9)
    (hmtf : IsMTF G)
    (hR : Ramsey3Le 9 36) (hR8 : Ramsey3Le 8 28) (hT : E39Table)
    (hE : EdgeLowerBound 10 40 161)
    (hglue : Glue U_none G) :
    ∃ v, G.degree v = 9 ∧ #(delNbhd G v).edgeFinset ≤ t9of t9_gr_mtf_none (distOf G) :=
  t9_main h3 hα hR hR8 hT t9_gr_mtf_none_ok cov_gr_mtf_none (caseTable_gr_mtf G h3 hα hmtf hR hR8 hT hE) (fun _ => hmtf) hglue

theorem cov_gr_mtf_U8 : covered surv_gr_mtf t9_gr_mtf_U8 = true := by
  apply covered_of_eq
  decide +kernel

/-- t9 table, scenario `U8`: under the gluing hypothesis `Glue U_U8 G`, some 9-vertex `v` of a
maximal triangle-free (3,10,40)-graph has `e(H_v) ≤ t9of t9_gr_mtf_U8 (distOf G)`. -/
theorem t9_gr_mtf_U8_main
    (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9)
    (hmtf : IsMTF G)
    (hR : Ramsey3Le 9 36) (hR8 : Ramsey3Le 8 28) (hT : E39Table)
    (hE : EdgeLowerBound 10 40 161)
    (hglue : Glue U_U8 G) :
    ∃ v, G.degree v = 9 ∧ #(delNbhd G v).edgeFinset ≤ t9of t9_gr_mtf_U8 (distOf G) :=
  t9_main h3 hα hR hR8 hT t9_gr_mtf_U8_ok cov_gr_mtf_U8 (caseTable_gr_mtf G h3 hα hmtf hR hR8 hT hE) (fun _ => hmtf) hglue

theorem cov_gr_mtf_known : covered surv_gr_mtf t9_gr_mtf_known = true := by
  apply covered_of_eq
  decide +kernel

/-- t9 table, scenario `known`: under the gluing hypothesis `Glue U_known G`, some 9-vertex `v` of a
maximal triangle-free (3,10,40)-graph has `e(H_v) ≤ t9of t9_gr_mtf_known (distOf G)`. -/
theorem t9_gr_mtf_known_main
    (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9)
    (hmtf : IsMTF G)
    (hR : Ramsey3Le 9 36) (hR8 : Ramsey3Le 8 28) (hT : E39Table)
    (hE : EdgeLowerBound 10 40 161)
    (hglue : Glue U_known G) :
    ∃ v, G.degree v = 9 ∧ #(delNbhd G v).edgeFinset ≤ t9of t9_gr_mtf_known (distOf G) :=
  t9_main h3 hα hR hR8 hT t9_gr_mtf_known_ok cov_gr_mtf_known (caseTable_gr_mtf G h3 hα hmtf hR hR8 hT hE) (fun _ => hmtf) hglue

theorem cov_gr_mtf_ang : covered surv_gr_mtf t9_gr_mtf_ang = true := by
  apply covered_of_eq
  decide +kernel

/-- t9 table, scenario `ang`: under the gluing hypothesis `Glue U_ang G`, some 9-vertex `v` of a
maximal triangle-free (3,10,40)-graph has `e(H_v) ≤ t9of t9_gr_mtf_ang (distOf G)`. -/
theorem t9_gr_mtf_ang_main
    (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (h3 : G.CliqueFree 3)
    (hα : G.indepNum ≤ 9)
    (hmtf : IsMTF G)
    (hR : Ramsey3Le 9 36) (hR8 : Ramsey3Le 8 28) (hT : E39Table)
    (hE : EdgeLowerBound 10 40 161)
    (hglue : Glue U_ang G) :
    ∃ v, G.degree v = 9 ∧ #(delNbhd G v).edgeFinset ≤ t9of t9_gr_mtf_ang (distOf G) :=
  t9_main h3 hα hR hR8 hT t9_gr_mtf_ang_ok cov_gr_mtf_ang (caseTable_gr_mtf G h3 hα hmtf hR hR8 hT hE) (fun _ => hmtf) hglue

end R310.LP.Data
