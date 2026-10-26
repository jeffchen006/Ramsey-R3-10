/-
The simple (non-LP) checks of `cases/degseq.py`, as Boolean functions of a degree
distribution `n = (n4..n9)`, and the proof that the distribution of every (3,10,40)-graph
passes them (`passSimple_distOf`).

Checks (names as in degseq.py): parity, edge bounds, MTF min degree (M1), GR sum (L4),
low degree (L6), degree-4 structure (L7), min Z (L3' and M2).
-/
import R310.LP.Graph
import R310.Structure
import R310.EdgeBound

open Finset

set_option linter.unusedSectionVars false

namespace R310.LP

open SimpleGraph

section Defs

variable (n : List ℕ)

/-- `2 e = ∑ d n_d`. -/
def deg2n : ℕ :=
  4 * get6 n 4 + 5 * get6 n 5 + 6 * get6 n 6 + 7 * get6 n 7 + 8 * get6 n 8 + 9 * get6 n 9

/-- `#{vertices of degree ≤ t}`. -/
def cum (t : ℕ) : ℕ :=
  (if 4 ≤ t then get6 n 4 else 0) + (if 5 ≤ t then get6 n 5 else 0) +
  (if 6 ≤ t then get6 n 6 else 0) + (if 7 ≤ t then get6 n 7 else 0) +
  (if 8 ≤ t then get6 n 8 else 0) + (if 9 ≤ t then get6 n 9 else 0)

/-- Lower bound for `Z(v)`, `deg v = d`: the sum of the `d` smallest degrees of the other
vertices, in threshold form `4d + ∑_{t=4}^{8} max(0, d - #{u ≠ v : deg u ≤ t})`. -/
def zthr (d : ℕ) : ℕ :=
  4 * d + (d - (cum n 4 - if d ≤ 4 then 1 else 0)) + (d - (cum n 5 - if d ≤ 5 then 1 else 0)) +
    (d - (cum n 6 - if d ≤ 6 then 1 else 0)) + (d - (cum n 7 - if d ≤ 7 then 1 else 0)) +
    (d - (cum n 8 - if d ≤ 8 then 1 else 0))

/-- M2 bound `d^2 - 11 d + 78` (MTF only). -/
def zmtf (d : ℕ) : ℕ := d * d + 78 - 11 * d

def zmin (mtf : Bool) (d : ℕ) : ℕ := if mtf then max (zthr n d) (zmtf d) else zthr n d

/-- Count vectors `(k4..k9)` with sum 4 (degrees of the 4 neighbours of a 4-vertex). -/
def vecs4 : List (List ℕ) :=
  (List.range 5).flatMap fun a => (List.range (5 - a)).flatMap fun b =>
    (List.range (5 - a - b)).flatMap fun c => (List.range (5 - a - b - c)).flatMap fun d =>
      (List.range (5 - a - b - c - d)).map fun e => [a, b, c, d, e, 4 - a - b - c - d - e]

/-- Any two of the 4 neighbours have degree sum `≥ 12` (L6/L7). -/
def pairOK (k : List ℕ) : Bool :=
  [4, 5, 6, 7, 8, 9].all fun a => [4, 5, 6, 7, 8, 9].all fun b =>
    (a == b || get6 k a == 0 || get6 k b == 0 || decide (12 ≤ a + b)) &&
    (decide (get6 k a < 2) || decide (12 ≤ 2 * a))

def zOfK (k : List ℕ) : ℕ :=
  4 * get6 k 4 + 5 * get6 k 5 + 6 * get6 k 6 + 7 * get6 k 7 + 8 * get6 k 8 + 9 * get6 k 9

/-- The distribution forced by a 4-vertex whose neighbours have degree counts `k` (L7). -/
def distOfK (k : List ℕ) : List ℕ :=
  [1 + get6 k 4, get6 k 5, get6 k 6, get6 k 7, 35 - (zOfK k - 4) + get6 k 8,
    (zOfK k - 4) + get6 k 9]

def deg4ok (elb : ℕ) : Bool :=
  (vecs4).any fun k => pairOK k && decide (elb ≤ 140 + zOfK k) && n == distOfK k

def minZok (mtf : Bool) : Bool :=
  [4, 5, 6, 7, 8, 9].all fun d => get6 n d == 0 || decide (zmin n mtf d + e39 d ≤ deg2n n / 2)

/-- All simple checks of degseq.py. -/
def passSimple (elb : ℕ) (mtf : Bool) : Bool :=
  deg2n n % 2 == 0 &&
  decide (elb ≤ deg2n n / 2) && decide (deg2n n / 2 ≤ 180) &&
  (!mtf || (get6 n 4 == 0 && get6 n 5 == 0)) &&
  decide (get6 n 4 * (140 + 16) + get6 n 5 * (129 + 25) + get6 n 6 * (118 + 36) +
    get6 n 7 * (104 + 49) + get6 n 8 * (95 + 64) + get6 n 9 * (86 + 81) ≤ 20 * deg2n n) &&
  decide (get6 n 4 + get6 n 5 ≤ 2) &&
  (get6 n 4 == 0 || decide (get6 n 4 - 1 + get6 n 5 + get6 n 6 ≤ 4)) &&
  (get6 n 4 != 2 || get6 n 6 == 0) &&
  (get6 n 4 == 0 || deg4ok n elb) &&
  minZok n mtf

end Defs

/-! ### Soundness: a (3,10,40)-graph passes all simple checks -/

variable {G : SimpleGraph (Fin 40)} [DecidableRel G.Adj]

theorem mem_vecs4 (k : List ℕ) (hk : k.length = 6) (hs : k.sum = 4) : k ∈ vecs4 := by
  match k, hk with
  | [a, b, c, d, e, f], _ =>
    simp only [List.sum_cons, List.sum_nil] at hs
    have ha : a < 5 := by omega
    have hb : b < 5 - a := by omega
    have hc : c < 5 - a - b := by omega
    have hd : d < 5 - a - b - c := by omega
    have he : e < 5 - a - b - c - d := by omega
    have hf : f = 4 - a - b - c - d - e := by omega
    subst hf
    simp only [vecs4, List.mem_flatMap, List.mem_range, List.mem_map]
    exact ⟨a, ha, b, hb, c, hc, d, hd, e, he, rfl⟩

section Sound

variable (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR : Ramsey3Le 9 36)
include h3 hα hR

theorem hrange' : ∀ v, G.degree v ∈ Icc 4 9 := degree_mem_Icc G h3 hα hR

theorem deg2n_distOf : deg2n (distOf G) = 2 * #G.edgeFinset := by
  have hr := hrange' h3 hα hR
  simp only [deg2n, get6_distOf hr]
  rw [two_mul_card_edgeFinset_eq hr]

/-- `#{u | deg u ≤ t} = cum (distOf G) t`. -/
theorem card_degree_le (t : ℕ) : #{u | G.degree u ≤ t} = cum (distOf G) t := by
  have hr := hrange' h3 hα hR
  have := sum_weight_univ hr (fun d => if d ≤ t then 1 else 0)
  rw [sum_Icc49] at this
  simp only [ite_mul, one_mul, zero_mul] at this
  rw [card_filter, this]
  simp only [cum, get6_distOf hr]

/-- L3' in threshold form: `Z(v) ≥ zthr (distOf G) (deg v)`. -/
theorem zthr_le (v : Fin 40) :
    zthr (distOf G) (G.degree v) ≤ ∑ u ∈ G.neighborFinset v, G.degree u := by
  have hr := hrange' h3 hα hR
  -- `deg u = 4 + ∑_{t=4}^{8} [t < deg u]`
  have hsplit : ∑ u ∈ G.neighborFinset v, G.degree u =
      4 * G.degree v + #{u ∈ G.neighborFinset v | 4 < G.degree u} +
        #{u ∈ G.neighborFinset v | 5 < G.degree u} + #{u ∈ G.neighborFinset v | 6 < G.degree u} +
        #{u ∈ G.neighborFinset v | 7 < G.degree u} + #{u ∈ G.neighborFinset v | 8 < G.degree u} := by
    have hu : ∀ u ∈ G.neighborFinset v, G.degree u = 4 + (if 4 < G.degree u then 1 else 0) +
        (if 5 < G.degree u then 1 else 0) + (if 6 < G.degree u then 1 else 0) +
        (if 7 < G.degree u then 1 else 0) + (if 8 < G.degree u then 1 else 0) := by
      intro u _
      obtain ⟨h1, h2⟩ := mem_Icc.1 (hr u)
      interval_cases h : G.degree u <;> simp
    rw [sum_congr rfl hu]
    simp only [sum_add_distrib, sum_const, card_neighborFinset_eq_degree, smul_eq_mul, card_filter]
    ring
  -- each threshold term
  have hterm : ∀ t, G.degree v - (cum (distOf G) t - if G.degree v ≤ t then 1 else 0) ≤
      #{u ∈ G.neighborFinset v | t < G.degree u} := by
    intro t
    have hsub : ({u ∈ G.neighborFinset v | ¬ t < G.degree u} : Finset (Fin 40)) ⊆
        ({u | G.degree u ≤ t} : Finset (Fin 40)).erase v := by
      intro u hu
      simp only [mem_filter, mem_neighborFinset, not_lt] at hu
      simp only [mem_erase, mem_filter, mem_univ, true_and]
      exact ⟨fun h => G.irrefl (h ▸ hu.1), hu.2⟩
    have h1 := card_le_card hsub
    have h2 := card_filter_add_card_filter_not (s := G.neighborFinset v) (p := fun u => t < G.degree u)
    rw [card_neighborFinset_eq_degree] at h2
    have h3' : #(({u | G.degree u ≤ t} : Finset (Fin 40)).erase v) =
        #({u | G.degree u ≤ t} : Finset (Fin 40)) - if G.degree v ≤ t then 1 else 0 := by
      split_ifs with h
      · exact card_erase_of_mem (by simp [h])
      · rw [erase_eq_of_notMem (by simp [h])]
        simp
    rw [h3', card_degree_le h3 hα hR] at h1
    omega
  rw [hsplit, zthr]
  have := hterm 4
  have := hterm 5
  have := hterm 6
  have := hterm 7
  have := hterm 8
  omega

end Sound

theorem exists_of_ncls_pos {d : ℕ} (h : get6 (distOf G) d ≠ 0) (hr : ∀ v, G.degree v ∈ Icc 4 9) :
    ∃ v, G.degree v = d := by
  rw [get6_distOf hr, ncls, ← pos_iff_ne_zero, card_pos] at h
  obtain ⟨v, hv⟩ := h
  exact ⟨v, (mem_filter.1 hv).2⟩

/-- The degree counts of the neighbours of `u`. -/
def nbrCounts (G : SimpleGraph (Fin 40)) [DecidableRel G.Adj] (u : Fin 40) : List ℕ :=
  [4, 5, 6, 7, 8, 9].map fun D => #{x ∈ G.neighborFinset u | G.degree x = D}

theorem get6_nbrCounts (u : Fin 40) (D : ℕ) (hD : 4 ≤ D ∧ D ≤ 9) :
    get6 (nbrCounts G u) D = #{x ∈ G.neighborFinset u | G.degree x = D} := by
  obtain ⟨h1, h2⟩ := hD
  interval_cases D <;> rfl

section Pass

variable (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ 9) (hR : Ramsey3Le 9 36)
  (hR8 : Ramsey3Le 8 28) (hT : E39Table)
include h3 hα hR hR8 hT

/-- L7 in the form of `deg4ok`. -/
theorem deg4ok_distOf (elb : ℕ) (hE : elb ≤ #G.edgeFinset) (h35 : Regular35) (u : Fin 40)
    (hu : G.degree u = 4) : deg4ok (distOf G) elb = true := by
  have hr := hrange' h3 hα hR
  set k := nbrCounts G u with hk
  have hkD : ∀ D, 4 ≤ D ∧ D ≤ 9 → get6 k D = #{x ∈ G.neighborFinset u | G.degree x = D} :=
    fun D hD => by rw [hk]; exact get6_nbrCounts u D hD
  -- sum of the counts is 4, and their weighted sum is `Z(u)`
  have hsum1 := sum_neighbor_fiber G hr (fun _ => 1) u
  have hsumZ := sum_neighbor_fiber G hr (fun d => d) u
  simp only [sum_Icc49, one_mul, sum_const, smul_eq_mul, mul_one, card_neighborFinset_eq_degree,
    hu] at hsum1 hsumZ
  have hkmem : k ∈ vecs4 := by
    apply mem_vecs4
    · simp [hk, nbrCounts]
    · simp only [hk, nbrCounts, List.map_cons, List.map_nil, List.sum_cons, List.sum_nil]
      omega
  have hZ : zOfK k = ∑ x ∈ G.neighborFinset u, G.degree x := by
    simp only [zOfK, hkD 4 (by omega), hkD 5 (by omega), hkD 6 (by omega), hkD 7 (by omega),
      hkD 8 (by omega), hkD 9 (by omega)]
    omega
  -- pair condition
  have hpair : pairOK k = true := by
    unfold pairOK
    rw [List.all_eq_true]
    intro a ha
    rw [List.all_eq_true]
    intro b hb
    have ha' : 4 ≤ a ∧ a ≤ 9 := by simp at ha; omega
    have hb' : 4 ≤ b ∧ b ≤ 9 := by simp at hb; omega
    rw [hkD a ha', hkD b hb']
    simp only [Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq]
    constructor
    · by_cases hab : a = b
      · exact Or.inl (Or.inl (Or.inl hab))
      by_cases hka : #{x ∈ G.neighborFinset u | G.degree x = a} = 0
      · exact Or.inl (Or.inl (Or.inr hka))
      by_cases hkb : #{x ∈ G.neighborFinset u | G.degree x = b} = 0
      · exact Or.inl (Or.inr hkb)
      right
      obtain ⟨x, hx⟩ := card_pos.1 (Nat.pos_of_ne_zero hka)
      obtain ⟨x', hx'⟩ := card_pos.1 (Nat.pos_of_ne_zero hkb)
      simp only [mem_filter, mem_neighborFinset] at hx hx'
      have hne : x ≠ x' := fun h => hab (by rw [← hx.2, ← hx'.2, h])
      have := deg4_nbr_degree_sum G h3 hα hR8 h35 u hu x x' hx.1 hx'.1 hne
      omega
    · by_cases hka : #{x ∈ G.neighborFinset u | G.degree x = a} < 2
      · exact Or.inl hka
      right
      obtain ⟨t, hts, htc⟩ := exists_subset_card_eq (s := ({x ∈ G.neighborFinset u | G.degree x = a} : Finset _)) (n := 2) (by omega)
      obtain ⟨x, x', hne, rfl⟩ := card_eq_two.1 htc
      have hx := hts (mem_insert_self _ _)
      have hx' := hts (mem_insert_of_mem (mem_singleton_self _))
      simp only [mem_filter, mem_neighborFinset] at hx hx'
      have := deg4_nbr_degree_sum G h3 hα hR8 h35 u hu x x' hx.1 hx'.1 hne
      omega
  -- the distribution
  obtain ⟨hc1, hc2⟩ := deg4_count_outside G h3 hα h35 u hu
  obtain ⟨he1, he2⟩ := deg4_card_edgeFinset G h3 hα h35 u hu
  have hdist : distOf G = distOfK k := by
    have hD := fun D => (deg4_degree_counts G h3 hα h35 u hu D)
    simp only [distOf, distOfK, ncls, cls]
    rw [hZ, hkD 4 (by omega), hkD 5 (by omega), hkD 6 (by omega), hkD 7 (by omega),
      hkD 8 (by omega), hkD 9 (by omega)]
    rw [(hD 4).1, (hD 5).1, (hD 6).1, (hD 7).1, (hD 8).1, (hD 9).1,
      (hD 4).2 (by omega) (by omega), (hD 5).2 (by omega) (by omega),
      (hD 6).2 (by omega) (by omega), (hD 7).2 (by omega) (by omega)]
    simp only [List.cons.injEq, and_true]
    refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
    · simp
    · simp
    · simp
    · simp
    · simp only [show ¬ (8:ℕ) = 4 by decide, ite_false, zero_add]; omega
    · simp only [show ¬ (9:ℕ) = 4 by decide, ite_false, zero_add]; omega
  unfold deg4ok
  rw [List.any_eq_true]
  refine ⟨k, hkmem, ?_⟩
  simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq]
  exact ⟨⟨hpair, by rw [hZ]; omega⟩, hdist⟩

/-- Every (3,10,40)-graph passes all simple checks. Hypotheses: `R(3,9) ≤ 36`, `R(3,8) ≤ 28`,
the `e(3,9,m)` table, `elb ≤ e(G)`, MTF if `mtf`, and `Regular35` if `G` has a 4-vertex. -/
theorem passSimple_distOf (elb : ℕ) (mtf : Bool) (hE : elb ≤ #G.edgeFinset)
    (hm : mtf = true → IsMTF G) (h35 : (∃ u, G.degree u = 4) → Regular35) :
    passSimple (distOf G) elb mtf = true := by
  have hr := hrange' h3 hα hR
  have hd2 := deg2n_distOf h3 hα hR (G := G)
  have he180 := card_edgeFinset_le_180 G h3 hα
  have hc5 := card_degree_le h3 hα hR (G := G) 5
  have hc6 := card_degree_le h3 hα hR (G := G) 6
  simp only [cum, show (4:ℕ) ≤ 5 by decide, show (5:ℕ) ≤ 5 by decide, show ¬ (6:ℕ) ≤ 5 by decide,
    show ¬ (7:ℕ) ≤ 5 by decide, show ¬ (8:ℕ) ≤ 5 by decide, show ¬ (9:ℕ) ≤ 5 by decide,
    show (4:ℕ) ≤ 6 by decide, show (5:ℕ) ≤ 6 by decide, show (6:ℕ) ≤ 6 by decide, show ¬ (7:ℕ) ≤ 6 by decide,
    show ¬ (8:ℕ) ≤ 6 by decide, show ¬ (9:ℕ) ≤ 6 by decide, ite_true, ite_false,
    add_zero] at hc5 hc6
  -- GR sum (L4)
  have hgr : get6 (distOf G) 4 * (140 + 16) + get6 (distOf G) 5 * (129 + 25) +
      get6 (distOf G) 6 * (118 + 36) + get6 (distOf G) 7 * (104 + 49) +
      get6 (distOf G) 8 * (95 + 64) + get6 (distOf G) 9 * (86 + 81) ≤ 20 * deg2n (distOf G) := by
    have h4 := sum_e39_add_sq_le G h3 hα hR hT
    have hw := sum_weight_univ hr (fun d => e39 d + d ^ 2)
    rw [sum_Icc49] at hw
    rw [hw] at h4
    simp only [e39, get6_distOf hr] at h4 ⊢
    omega
  -- low degree (L6)
  have hlow1 : get6 (distOf G) 4 + get6 (distOf G) 5 ≤ 2 := by
    have := card_degree_le_five G h3 hα hR8
    omega
  have hex4 : get6 (distOf G) 4 ≠ 0 → ∃ u, G.degree u = 4 := fun h => exists_of_ncls_pos h hr
  have hlow2 : get6 (distOf G) 4 = 0 ∨ get6 (distOf G) 4 - 1 + get6 (distOf G) 5 +
      get6 (distOf G) 6 ≤ 4 := by
    by_cases h : get6 (distOf G) 4 = 0
    · exact Or.inl h
    · obtain ⟨u, hu⟩ := hex4 h
      have := card_degree_le_six_of_deg4 G h3 hα hR8 hu
      omega
  have hlow3 : get6 (distOf G) 4 ≠ 2 ∨ get6 (distOf G) 6 = 0 := by
    by_cases h : get6 (distOf G) 4 = 2
    · right
      rw [get6_distOf hr, ncls] at h ⊢
      obtain ⟨u, u', hne, hcls⟩ := card_eq_two.1 h
      have hu : G.degree u = 4 := by
        have hmem : u ∈ cls G 4 := by rw [hcls]; simp
        simpa [cls] using hmem
      have hu' : G.degree u' = 4 := by
        have hmem : u' ∈ cls G 4 := by rw [hcls]; simp
        simpa [cls] using hmem
      rw [card_eq_zero, cls, filter_eq_empty_iff]
      intro w _
      exact no_degree_six_of_two_deg4 G h3 hα hR8 hne hu hu' w
    · exact Or.inl h
  -- MTF: no vertex of degree 4 or 5 (M1)
  have hmtf : mtf = false ∨ (get6 (distOf G) 4 = 0 ∧ get6 (distOf G) 5 = 0) := by
    cases mtf with
    | false => exact Or.inl rfl
    | true =>
      right
      have hG := hm rfl
      have h6 := hG.six_le_degree G hα
      constructor <;>
      · rw [get6_distOf hr, ncls, card_eq_zero, cls, filter_eq_empty_iff]
        intro w _ hw
        have := h6 w
        omega
  -- degree 4 structure (L7)
  have hdeg4 : get6 (distOf G) 4 = 0 ∨ deg4ok (distOf G) elb = true := by
    by_cases h : get6 (distOf G) 4 = 0
    · exact Or.inl h
    · obtain ⟨u, hu⟩ := hex4 h
      exact Or.inr (deg4ok_distOf h3 hα hR hR8 hT elb hE (h35 ⟨u, hu⟩) u hu)
  -- min Z (L3', M2)
  have hminZ : minZok (distOf G) mtf = true := by
    unfold minZok
    rw [List.all_eq_true]
    intro d hd
    have hd' : 4 ≤ d ∧ d ≤ 9 := by simp at hd; omega
    simp only [Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq]
    by_cases h0 : get6 (distOf G) d = 0
    · exact Or.inl h0
    right
    obtain ⟨v, hv⟩ := exists_of_ncls_pos h0 hr
    have hz := zthr_le h3 hα hR (G := G) v
    have hL2 := card_edgeFinset_delNbhd_add_sum_degree h3 (G := G) v
    have hL3 := e39_le_card_edgeFinset_delNbhd G h3 hα hR hT v
    rw [hv] at hz hL3
    have hzmin : zmin (distOf G) mtf d ≤ ∑ u ∈ G.neighborFinset v, G.degree u := by
      unfold zmin
      split_ifs with hmt
      · have := (hm hmt).sum_degree_neighbor_ge G hα v
        rw [hv] at this
        refine max_le hz ?_
        unfold zmtf
        rw [← sq]
        omega
      · exact hz
    omega
  unfold passSimple
  simp only [Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq, Bool.not_eq_true',
    bne_iff_ne, ne_eq]
  refine ⟨⟨⟨⟨⟨⟨⟨⟨⟨?_, ?_⟩, ?_⟩, ?_⟩, hgr⟩, hlow1⟩, ?_⟩, ?_⟩, ?_⟩, hminZ⟩
  · omega
  · omega
  · omega
  · rcases hmtf with h | h
    · exact Or.inl h
    · exact Or.inr h
  · exact hlow2
  · exact hlow3
  · exact hdeg4

end Pass

end R310.LP
