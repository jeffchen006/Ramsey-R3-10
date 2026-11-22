import R310.DeficientWitness
import R310.MTF

namespace R310

open Finset SimpleGraph
open scoped BigOperators

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

def starContacts (vertex : V) (sites : Finset V) : ℕ :=
  #(G.neighborFinset vertex ∩ sites)

def starMass (sources targets : Finset V) : ℕ :=
  ∑ vertex ∈ sources, starContacts G vertex targets

theorem starMass_comm (sources targets : Finset V) :
    starMass G sources targets = starMass G targets sources := by
  have hCount (vertex : V) (sites : Finset V) :
      starContacts G vertex sites = ∑ site ∈ sites, if G.Adj vertex site then 1 else 0 := by
    rw [starContacts, show G.neighborFinset vertex ∩ sites = sites.filter (G.Adj vertex) by
      ext site; simp [and_comm], card_filter]
  simp only [starMass, hCount]
  rw [sum_comm]
  exact sum_congr rfl fun vertex _ => sum_congr rfl fun site _ => by simp [G.adj_comm]

private theorem starContacts_union (vertex : V) {left right : Finset V}
    (hDisjoint : Disjoint left right) :
    starContacts G vertex (left ∪ right) =
      starContacts G vertex left + starContacts G vertex right := by
  unfold starContacts
  rw [inter_union_distrib_left, card_union_of_disjoint]
  exact hDisjoint.mono inter_subset_right inter_subset_right

private theorem starMass_union (sources : Finset V) {left right : Finset V}
    (hDisjoint : Disjoint left right) :
    starMass G sources (left ∪ right) = starMass G sources left + starMass G sources right := by
  simp only [starMass, starContacts_union G _ hDisjoint, sum_add_distrib]

private theorem starContacts_eq_zero {vertex : V} {sites : Finset V}
    (hNo : ∀ site ∈ sites, ¬ G.Adj vertex site) : starContacts G vertex sites = 0 := by
  rw [starContacts, card_eq_zero, eq_empty_iff_forall_notMem]
  intro site hMem
  exact hNo site (mem_inter.mp hMem).2 (mem_neighborFinset _ _ _ |>.mp (mem_inter.mp hMem).1)

private theorem starContacts_univ (vertex : V) :
    starContacts G vertex univ = G.degree vertex := by
  simp [starContacts]

theorem starMass_self (sites : Finset V) :
    starMass G sites sites = 2 * #(G.induce (sites : Set V)).edgeFinset := by
  rw [← sum_degrees_eq_twice_card_edges]
  unfold starMass
  rw [← sum_attach]
  have hUniv : sites.attach = (univ : Finset {vertex // vertex ∈ sites}) := by
    ext vertex; simp
  rw [hUniv]
  refine sum_congr rfl fun vertex _ => ?_
  have hMap := G.map_neighborFinset_induce (s := (sites : Set V)) vertex
  have hCard := congrArg Finset.card hMap
  simp only [card_map, card_neighborFinset_eq_degree, toFinset_coe] at hCard
  unfold starContacts
  convert hCard.symm using 2

private theorem starMass_regular (sources : Finset V) {degree : ℕ}
    (hRegular : ∀ vertex, G.degree vertex = degree) :
    starMass G sources univ = #sources * degree := by
  simp [starMass, starContacts_univ, hRegular]

theorem starMass_cut_balance {book rest : Finset V} {degree : ℕ}
    (hRegular : ∀ vertex, G.degree vertex = degree)
    (hDisjoint : Disjoint book rest) (hCover : book ∪ rest = univ) :
    starMass G rest rest + #book * degree = starMass G book book + #rest * degree := by
  have hBook := starMass_union G book hDisjoint
  have hRest := starMass_union G rest hDisjoint
  rw [hCover, starMass_regular G book hRegular] at hBook
  rw [hCover, starMass_regular G rest hRegular, starMass_comm G rest book] at hRest
  omega

omit [Fintype V] in
private theorem eq_of_lower_of_sum_eq {sites : Finset V} {value : V → ℕ} {floor : ℕ}
    (hLower : ∀ vertex ∈ sites, floor ≤ value vertex)
    (hSum : ∑ vertex ∈ sites, value vertex = #sites * floor) :
    ∀ vertex ∈ sites, value vertex = floor := by
  intro vertex hVertex
  have hTail := sum_le_sum (s := sites.erase vertex)
    (f := fun _ => floor) (g := value) (fun item hItem => hLower item (mem_of_mem_erase hItem))
  simp only [sum_const, smul_eq_mul] at hTail
  have hSplit := sum_erase_add _ value hVertex
  have hSplitConst := sum_erase_add _ (fun _ => floor) hVertex
  simp only [sum_const, smul_eq_mul] at hSplitConst
  have hLo := hLower vertex hVertex
  omega

theorem middle_star_of_tight_mass {wingLeft wingRight middleSites untouched : Finset V}
    {cap outsideDegree untouchedFloor : ℕ}
    (hRow : ∀ vertex ∈ middleSites,
      starContacts G vertex wingLeft + starContacts G vertex wingRight +
        starContacts G vertex untouched = cap + cap + outsideDegree)
    (hLeft : ∀ vertex ∈ middleSites, starContacts G vertex wingLeft ≤ cap)
    (hRight : ∀ vertex ∈ middleSites, starContacts G vertex wingRight ≤ cap)
    (hMass : starMass G middleSites untouched = #middleSites * outsideDegree)
    (hColumn : ∀ vertex ∈ untouched, untouchedFloor ≤ starContacts G vertex middleSites)
    (hSizes : #middleSites * outsideDegree = #untouched * untouchedFloor) :
    (∀ vertex ∈ middleSites, starContacts G vertex wingLeft = cap ∧
      starContacts G vertex wingRight = cap ∧ starContacts G vertex untouched = outsideDegree) ∧
    (∀ vertex ∈ untouched, starContacts G vertex middleSites = untouchedFloor) := by
  have hLower (vertex : V) (hVertex : vertex ∈ middleSites) :
      outsideDegree ≤ starContacts G vertex untouched := by
    have := hRow vertex hVertex
    have := hLeft vertex hVertex
    have := hRight vertex hVertex
    omega
  have hTight := eq_of_lower_of_sum_eq hLower hMass
  refine ⟨?_, eq_of_lower_of_sum_eq hColumn ?_⟩
  · intro vertex hVertex
    have := hRow vertex hVertex
    have := hLeft vertex hVertex
    have := hRight vertex hVertex
    have := hTight vertex hVertex
    omega
  · change starMass G untouched middleSites = _
    rw [starMass_comm G untouched middleSites, hMass, hSizes]

def pathWing (endpoint middle : V) : Finset V := (G.neighborFinset endpoint).erase middle

def pathStar (left right middle : V) : Finset V :=
  ((G.neighborFinset middle).erase left).erase right

def pathBook (left right middle : V) : Finset V :=
  insert left (insert right (insert middle (pathWing G left middle ∪ pathWing G right middle)))

def pathUntouched (left right middle : V) : Finset V :=
  (pathBook G left right middle)ᶜ \ pathStar G left right middle

theorem mem_pathUntouched {left right middle vertex : V} :
    vertex ∈ pathUntouched G left right middle ↔
      vertex ≠ left ∧ vertex ≠ right ∧ vertex ≠ middle ∧
      ¬ G.Adj left vertex ∧ ¬ G.Adj right vertex ∧ ¬ G.Adj middle vertex := by
  simp only [pathUntouched, mem_sdiff, mem_compl, pathBook, pathWing, pathStar, mem_insert,
    mem_union, mem_erase, mem_neighborFinset, ne_eq]
  tauto

theorem codegree_ge_two_of_not_deficient {first second witness : V}
    (hNe : first ≠ second) (hNo : ¬ G.Adj first second)
    (hFirst : G.Adj first witness) (hSecond : G.Adj second witness)
    (hNotDeficient : ¬ HasDeficientWitness G first second witness) :
    2 ≤ #(G.neighborFinset first ∩ G.neighborFinset second) := by
  by_contra! hSmall
  have hOne : #(G.neighborFinset first ∩ G.neighborFinset second) ≤ 1 := by omega
  apply hNotDeficient
  refine ⟨hNe, hNo, hFirst, hSecond, ?_⟩
  intro other hFirstOther hSecondOther
  exact card_le_one.mp hOne other (by simp [hFirstOther, hSecondOther]) witness
    (by simp [hFirst, hSecond])

/-- Maximality supplies one common neighbour; if the middle is not a deficient
endpoint, every untouched site has at least two. The endpoint premise is separate
from the absence of another pair *witnessed* by the middle. -/
theorem pathUntouched_codegree_ge_two_of_mtf {left right middle : V} (hMTF : IsMTF G)
    (hNoDef : ∀ endpoint witness, ¬ HasDeficientWitness G middle endpoint witness) :
    ∀ vertex ∈ pathUntouched G left right middle,
      2 ≤ #(G.neighborFinset middle ∩ G.neighborFinset vertex) := by
  intro vertex hVertex
  obtain ⟨_, _, hNe, _, _, hNo⟩ := (mem_pathUntouched G).mp hVertex
  obtain ⟨witness, hMid, hAdj⟩ := hMTF.exists_common hNe.symm hNo
  exact codegree_ge_two_of_not_deficient G hNe.symm hNo hMid hAdj (hNoDef vertex witness)

omit [Fintype V] [DecidableRel G.Adj] in
private theorem triangle_free_no_common (hTriangle : G.CliqueFree 3) {first second other : V}
    (hEdge : G.Adj first second) (hFirst : G.Adj first other) (hSecond : G.Adj second other) :
    False :=
  hTriangle {first, second, other} (is3Clique_triple_iff.2 ⟨hEdge, hFirst, hSecond⟩)

private theorem starContacts_insert_adj {vertex site : V} {sites : Finset V}
    (hAdj : G.Adj vertex site) (hNew : site ∉ sites) :
    starContacts G vertex (insert site sites) = starContacts G vertex sites + 1 := by
  unfold starContacts
  rw [show G.neighborFinset vertex ∩ insert site sites =
      insert site (G.neighborFinset vertex ∩ sites) by
    ext item
    simp only [mem_inter, mem_insert, mem_neighborFinset]
    constructor
    · rintro ⟨_, rfl | hItem⟩ <;> tauto
    · rintro (rfl | hItem) <;> tauto,
    card_insert_of_notMem (fun hMem => hNew (mem_inter.mp hMem).2)]

private theorem starContacts_insert_nonadj {vertex site : V} (sites : Finset V)
    (hNo : ¬ G.Adj vertex site) :
    starContacts G vertex (insert site sites) = starContacts G vertex sites := by
  unfold starContacts
  congr 1
  ext item
  simp only [mem_inter, mem_insert, mem_neighborFinset]
  exact ⟨fun ⟨hAdj, hItem⟩ => ⟨hAdj, hItem.resolve_left (fun hEq => hNo (hEq ▸ hAdj))⟩,
    fun ⟨hAdj, hItem⟩ => ⟨hAdj, Or.inr hItem⟩⟩

private theorem pathWing_neighborFinset {endpoint middle : V} (hEdge : G.Adj endpoint middle) :
    insert middle (pathWing G endpoint middle) = G.neighborFinset endpoint :=
  insert_erase (mem_neighborFinset _ _ _ |>.mpr hEdge)

/-- The regular cut identity before any lower bounds on codegrees. -/
structure MiddleStarBalance (left right middle : V) : Prop where
  poleCount : #(pathStar G left right middle) = 7
  untouchedCount : #(pathUntouched G left right middle) = 14
  row : ∀ pole ∈ pathStar G left right middle,
    starContacts G pole (pathWing G left middle) + starContacts G pole (pathWing G right middle) +
      starContacts G pole (pathUntouched G left right middle) = 8
  nonedges : ∀ pole ∈ pathStar G left right middle,
    pole ≠ left ∧ pole ≠ right ∧ ¬ G.Adj pole left ∧ ¬ G.Adj pole right
  leftCodegree : ∀ pole ∈ pathStar G left right middle,
    #(G.neighborFinset pole ∩ G.neighborFinset left) = starContacts G pole (pathWing G left middle) + 1
  rightCodegree : ∀ pole ∈ pathStar G left right middle,
    #(G.neighborFinset pole ∩ G.neighborFinset right) = starContacts G pole (pathWing G right middle) + 1
  middleCodegree : ∀ vertex ∈ pathUntouched G left right middle,
    #(G.neighborFinset middle ∩ G.neighborFinset vertex) = starContacts G vertex (pathStar G left right middle)
  mass : starMass G (pathStar G left right middle) (pathUntouched G left right middle) +
    #((G.induce (pathUntouched G left right middle : Set V)).edgeFinset) =
      starMass G (pathWing G left middle) (pathWing G right middle) + 27

theorem middle_star_balance {left right middle : V}
    (hOrder : Fintype.card V = 40) (hRegular : ∀ vertex, G.degree vertex = 9)
    (hTriangle : G.CliqueFree 3) (hPath : HasDeficientWitness G left right middle) :
    MiddleStarBalance G left right middle := by
  let wingLeft := pathWing G left middle
  let wingRight := pathWing G right middle
  let wings := wingLeft ∪ wingRight
  let book := pathBook G left right middle
  let middleSites := pathStar G left right middle
  let untouched := pathUntouched G left right middle
  obtain ⟨hDifferent, hNonedge, hLeftMid, hRightMid, hUnique⟩ := hPath
  have hLeftSet : G.neighborFinset left = insert middle wingLeft :=
    (pathWing_neighborFinset G hLeftMid).symm
  have hRightSet : G.neighborFinset right = insert middle wingRight :=
    (pathWing_neighborFinset G hRightMid).symm
  have hMiddleSet : G.neighborFinset middle = insert left (insert right middleSites) := by
    ext vertex
    simp only [middleSites, pathStar, mem_neighborFinset, mem_insert, mem_erase]
    constructor
    · intro hAdj
      by_cases hLeft : vertex = left
      · exact Or.inl hLeft
      by_cases hRight : vertex = right
      · exact Or.inr (Or.inl hRight)
      exact Or.inr (Or.inr ⟨hRight, hLeft, hAdj⟩)
    · rintro (rfl | rfl | ⟨_, _, hAdj⟩)
      · exact hLeftMid.symm
      · exact hRightMid.symm
      · exact hAdj
  have hWingLeft vertex : vertex ∈ wingLeft ↔ vertex ≠ middle ∧ G.Adj left vertex := by
    simp [wingLeft, pathWing]
  have hWingRight vertex : vertex ∈ wingRight ↔ vertex ≠ middle ∧ G.Adj right vertex := by
    simp [wingRight, pathWing]
  have hStar vertex : vertex ∈ middleSites ↔ vertex ≠ right ∧ vertex ≠ left ∧ G.Adj middle vertex := by
    simp [middleSites, pathStar]
  have hWings : Disjoint wingLeft wingRight := by
    refine disjoint_left.mpr fun {vertex} hL hR => ?_
    exact (hWingLeft vertex).mp hL |>.1 (hUnique vertex ((hWingLeft vertex).mp hL).2
      ((hWingRight vertex).mp hR).2)
  have hLeftOut : left ∉ wings := by
    simp [wings, hWingLeft, hWingRight, G.adj_comm right left, hNonedge]
  have hRightOut : right ∉ wings := by
    simp [wings, hWingLeft, hWingRight, hNonedge]
  have hMidOut : middle ∉ wings := by simp [wings, hWingLeft, hWingRight]
  have hLeftWingCount : #wingLeft = 8 := by
    have h := hRegular left
    rw [← card_neighborFinset_eq_degree, hLeftSet, card_insert_of_notMem] at h
    · omega
    · simp [hWingLeft]
  have hRightWingCount : #wingRight = 8 := by
    have h := hRegular right
    rw [← card_neighborFinset_eq_degree, hRightSet, card_insert_of_notMem] at h
    · omega
    · simp [hWingRight]
  have hStarCount : #middleSites = 7 := by
    have h := hRegular middle
    have hR : right ∉ middleSites := by simp [hStar]
    have hL : left ∉ insert right middleSites := by simp [hDifferent, hStar]
    rw [← card_neighborFinset_eq_degree, hMiddleSet, card_insert_of_notMem hL,
      card_insert_of_notMem hR] at h
    omega
  have hBookForm : book = insert left (insert right (insert middle wings)) := rfl
  have hLeftNew : left ∉ insert right (insert middle wings) := by
    simp [hLeftOut, hDifferent, hLeftMid.ne]
  have hRightNew : right ∉ insert middle wings := by simp [hRightOut, hRightMid.ne]
  have hBookCount : #book = 19 := by
    rw [hBookForm, card_insert_of_notMem hLeftNew, card_insert_of_notMem hRightNew,
      card_insert_of_notMem hMidOut]
    change #(wingLeft ∪ wingRight) + 1 + 1 + 1 = 19
    rw [card_union_of_disjoint hWings, hLeftWingCount, hRightWingCount]
  have hRestCount : #bookᶜ = 21 := by rw [card_compl, hOrder, hBookCount]
  have hMiddleNoWings : ∀ vertex ∈ wings, ¬ G.Adj middle vertex := by
    intro vertex hMem hAdj
    rcases mem_union.mp hMem with hL | hR
    · exact triangle_free_no_common G hTriangle hLeftMid ((hWingLeft vertex).mp hL).2 hAdj
    · exact triangle_free_no_common G hTriangle hRightMid ((hWingRight vertex).mp hR).2 hAdj
  have hStarSub : middleSites ⊆ bookᶜ := by
    intro vertex hMem
    obtain ⟨hRight, hLeft, hAdj⟩ := (hStar vertex).mp hMem
    have hMid := hAdj.ne.symm
    have hNo : vertex ∉ wings := fun hW => hMiddleNoWings vertex hW hAdj
    simp [hBookForm, hLeft, hRight, hMid, hNo]
  have hUntouchedCount : #untouched = 14 := by
    change #(bookᶜ \ middleSites) = 14
    rw [card_sdiff_of_subset hStarSub, hRestCount, hStarCount]
  have hRestCut : middleSites ∪ untouched = bookᶜ := by
    change middleSites ∪ (bookᶜ \ middleSites) = bookᶜ
    exact union_sdiff_of_subset hStarSub
  have hRestDisjoint : Disjoint middleSites untouched := by
    refine Finset.disjoint_left.mpr ?_
    intro vertex hStarMem hUntouchedMem
    exact (mem_sdiff.mp hUntouchedMem).2 hStarMem
  have hLeftContacts : starContacts G left book = 9 := by
    rw [starContacts, inter_eq_left.mpr, card_neighborFinset_eq_degree, hRegular]
    intro vertex hMem
    rw [hLeftSet] at hMem
    simp only [hBookForm, mem_insert]
    rcases mem_insert.mp hMem with rfl | hWing
    · simp
    · exact Or.inr (Or.inr (Or.inr (mem_union_left _ hWing)))
  have hRightContacts : starContacts G right book = 9 := by
    rw [starContacts, inter_eq_left.mpr, card_neighborFinset_eq_degree, hRegular]
    intro vertex hMem
    rw [hRightSet] at hMem
    simp only [hBookForm, mem_insert]
    rcases mem_insert.mp hMem with rfl | hWing
    · simp
    · exact Or.inr (Or.inr (Or.inr (mem_union_right _ hWing)))
  have hMiddleContacts : starContacts G middle book = 2 := by
    rw [hBookForm, starContacts_insert_adj G hLeftMid.symm hLeftNew,
      starContacts_insert_adj G hRightMid.symm hRightNew,
      starContacts_insert_nonadj G _ (G.irrefl), starContacts_eq_zero G hMiddleNoWings]
  have hBookLeft : ∀ vertex ∈ wingLeft,
      starContacts G vertex book = starContacts G vertex wingRight + 1 := by
    intro vertex hMem
    obtain ⟨hNotMid, hAdj⟩ := (hWingLeft vertex).mp hMem
    have hNoRight : ¬ G.Adj vertex right := fun hHit => hNotMid (hUnique vertex hAdj hHit.symm)
    have hNoMid := hMiddleNoWings vertex (mem_union_left _ hMem)
    have hZero : starContacts G vertex wingLeft = 0 := starContacts_eq_zero G fun other hOther hEdge =>
      triangle_free_no_common G hTriangle hAdj ((hWingLeft other).mp hOther).2 hEdge
    rw [hBookForm, starContacts_insert_adj G hAdj.symm hLeftNew,
      starContacts_insert_nonadj G _ hNoRight, starContacts_insert_nonadj G _ (fun h => hNoMid h.symm)]
    change starContacts G vertex (wingLeft ∪ wingRight) + 1 = _
    rw [starContacts_union G _ hWings, hZero, zero_add]
  have hBookRight : ∀ vertex ∈ wingRight,
      starContacts G vertex book = starContacts G vertex wingLeft + 1 := by
    intro vertex hMem
    obtain ⟨hNotMid, hAdj⟩ := (hWingRight vertex).mp hMem
    have hNoLeft : ¬ G.Adj vertex left := fun hHit => hNotMid (hUnique vertex hHit.symm hAdj)
    have hNoMid := hMiddleNoWings vertex (mem_union_right _ hMem)
    have hZero : starContacts G vertex wingRight = 0 := starContacts_eq_zero G fun other hOther hEdge =>
      triangle_free_no_common G hTriangle hAdj ((hWingRight other).mp hOther).2 hEdge
    rw [hBookForm, starContacts_insert_nonadj G _ hNoLeft,
      starContacts_insert_adj G hAdj.symm hRightNew,
      starContacts_insert_nonadj G _ (fun h => hNoMid h.symm)]
    change starContacts G vertex (wingLeft ∪ wingRight) + 1 = _
    rw [starContacts_union G _ hWings, hZero, add_zero]
  have hBookMass : starMass G book book = 2 * starMass G wingLeft wingRight + 36 := by
    change (∑ v ∈ insert left (insert right (insert middle wings)), starContacts G v book) = _
    rw [sum_insert hLeftNew, sum_insert hRightNew, sum_insert hMidOut,
      hLeftContacts, hRightContacts, hMiddleContacts]
    change 9 + (9 + (2 + ∑ v ∈ wingLeft ∪ wingRight, starContacts G v book)) = _
    rw [sum_union hWings, sum_congr rfl hBookLeft, sum_congr rfl hBookRight,
      sum_add_distrib, sum_add_distrib, sum_const, sum_const, smul_eq_mul, smul_eq_mul]
    change 9 + (9 + (2 + (starMass G wingLeft wingRight + #wingLeft * 1 +
      (starMass G wingRight wingLeft + #wingRight * 1)))) = _
    rw [starMass_comm G wingRight wingLeft, hLeftWingCount, hRightWingCount]
    omega
  have hCut := starMass_cut_balance G hRegular (disjoint_compl_right : Disjoint book bookᶜ)
    (union_compl book)
  rw [hBookCount, hRestCount, hBookMass] at hCut
  have hStarIndependent : starMass G middleSites middleSites = 0 := by
    unfold starMass
    refine sum_eq_zero fun vertex hVertex => starContacts_eq_zero G fun other hOther hEdge => ?_
    exact triangle_free_no_common G hTriangle ((hStar vertex).mp hVertex).2.2
      ((hStar other).mp hOther).2.2 hEdge
  have hBetween : starMass G middleSites untouched + #((G.induce (untouched : Set V)).edgeFinset) =
      starMass G wingLeft wingRight + 27 := by
    have hExpand := starMass_union G bookᶜ hRestDisjoint
    rw [hRestCut] at hExpand
    have hStarPart := starMass_union G middleSites hRestDisjoint
    rw [hRestCut, hStarIndependent, zero_add, starMass_comm G middleSites bookᶜ] at hStarPart
    have hUntouchedPart := starMass_union G untouched hRestDisjoint
    rw [hRestCut, starMass_self G untouched, starMass_comm G untouched bookᶜ,
      starMass_comm G untouched middleSites] at hUntouchedPart
    omega
  have hStarNotAdj (vertex : V) (hVertex : vertex ∈ middleSites) :
      ¬ G.Adj vertex left ∧ ¬ G.Adj vertex right := by
    exact ⟨fun h => triangle_free_no_common G hTriangle hLeftMid h.symm ((hStar vertex).mp hVertex).2.2,
      fun h => triangle_free_no_common G hTriangle hRightMid h.symm ((hStar vertex).mp hVertex).2.2⟩
  have hRow : ∀ vertex ∈ middleSites,
      starContacts G vertex wingLeft + starContacts G vertex wingRight +
        starContacts G vertex untouched = 8 := by
    intro vertex hVertex
    have hTotal := starContacts_union G vertex (disjoint_compl_right : Disjoint book bookᶜ)
    have hStarZero : starContacts G vertex middleSites = 0 :=
      starContacts_eq_zero G fun other hOther hEdge => triangle_free_no_common G hTriangle
        ((hStar vertex).mp hVertex).2.2 ((hStar other).mp hOther).2.2 hEdge
    have hBookRow : starContacts G vertex book = starContacts G vertex wings + 1 := by
      rw [hBookForm, starContacts_insert_nonadj G _ (hStarNotAdj vertex hVertex).1,
        starContacts_insert_nonadj G _ (hStarNotAdj vertex hVertex).2,
        starContacts_insert_adj G ((hStar vertex).mp hVertex).2.2.symm hMidOut]
    rw [union_compl, starContacts_univ, hRegular, hBookRow,
      ← hRestCut, starContacts_union G _ hRestDisjoint, hStarZero] at hTotal
    change 9 = starContacts G vertex (wingLeft ∪ wingRight) + 1 +
      (0 + starContacts G vertex untouched) at hTotal
    rw [starContacts_union G _ hWings] at hTotal
    omega
  refine ⟨hStarCount, hUntouchedCount, hRow, ?_, ?_, ?_, ?_, hBetween⟩
  · intro pole hPole
    obtain ⟨hRight, hLeft, _⟩ := (hStar pole).mp hPole
    exact ⟨hLeft, hRight, hStarNotAdj pole hPole⟩
  · intro pole hPole
    change starContacts G pole (G.neighborFinset left) = starContacts G pole wingLeft + 1
    rw [hLeftSet, starContacts_insert_adj G ((hStar pole).mp hPole).2.2.symm (by simp [hWingLeft])]
  · intro pole hPole
    change starContacts G pole (G.neighborFinset right) = starContacts G pole wingRight + 1
    rw [hRightSet, starContacts_insert_adj G ((hStar pole).mp hPole).2.2.symm (by simp [hWingRight])]
  · intro vertex hVertex
    obtain ⟨_, _, _, hNoLeft, hNoRight, _⟩ := (mem_pathUntouched G).mp hVertex
    rw [inter_comm]
    change starContacts G vertex (G.neighborFinset middle) = starContacts G vertex middleSites
    rw [hMiddleSet, starContacts_insert_nonadj G _ (fun h => hNoLeft h.symm),
      starContacts_insert_nonadj G _ (fun h => hNoRight h.symm)]

theorem MiddleStarBalance.tipCaps {left right middle : V} (balance : MiddleStarBalance G left right middle)
    (hCap : ∀ first second, first ≠ second → ¬ G.Adj first second →
      #(G.neighborFinset first ∩ G.neighborFinset second) ≤ 3) :
    ∀ pole ∈ pathStar G left right middle,
      starContacts G pole (pathWing G left middle) ≤ 2 ∧
      starContacts G pole (pathWing G right middle) ≤ 2 := by
  intro pole hPole
  obtain ⟨hLeft, hRight, hNoLeft, hNoRight⟩ := balance.nonedges pole hPole
  have hFirst := hCap pole left hLeft hNoLeft
  have hSecond := hCap pole right hRight hNoRight
  rw [balance.leftCodegree pole hPole] at hFirst
  rw [balance.rightCodegree pole hPole] at hSecond
  omega

/-- The maximal-residue slice of D's marked path. A positive codegree lower bound
is only needed between the middle and each untouched site; the rest of the K=2
argument and the support roster are not premises or conclusions of this theorem. -/
theorem middle_star_at_seventeen_sixteen {left right middle : V}
    (hOrder : Fintype.card V = 40) (hRegular : ∀ vertex, G.degree vertex = 9)
    (hTriangle : G.CliqueFree 3) (hPath : HasDeficientWitness G left right middle)
    (hCap : ∀ first second, first ≠ second → ¬ G.Adj first second →
      #(G.neighborFinset first ∩ G.neighborFinset second) ≤ 3)
    (hMiddle : ∀ vertex ∈ pathUntouched G left right middle,
      2 ≤ #(G.neighborFinset middle ∩ G.neighborFinset vertex))
    (hPetals : starMass G (pathWing G left middle) (pathWing G right middle) = 17)
    (hResidue : #((G.induce (pathUntouched G left right middle : Set V)).edgeFinset) = 16) :
    #(pathStar G left right middle) = 7 ∧ #(pathUntouched G left right middle) = 14 ∧
    (∀ vertex ∈ pathStar G left right middle,
      starContacts G vertex (pathWing G left middle) = 2 ∧
      starContacts G vertex (pathWing G right middle) = 2 ∧
      starContacts G vertex (pathUntouched G left right middle) = 4) ∧
    (∀ vertex ∈ pathUntouched G left right middle,
      starContacts G vertex (pathStar G left right middle) = 2) := by
  have balance := middle_star_balance G hOrder hRegular hTriangle hPath
  have hCaps := balance.tipCaps G hCap
  have hMass := balance.mass
  rw [hPetals, hResidue] at hMass
  refine ⟨balance.poleCount, balance.untouchedCount, middle_star_of_tight_mass G (cap := 2)
    (outsideDegree := 4) (untouchedFloor := 2) balance.row
    (fun pole hPole => (hCaps pole hPole).1) (fun pole hPole => (hCaps pole hPole).2) ?_ ?_ ?_⟩
  · rw [balance.poleCount]; omega
  · intro vertex hVertex
    simpa only [balance.middleCodegree vertex hVertex] using hMiddle vertex hVertex
  · rw [balance.poleCount, balance.untouchedCount]

end R310
