import R310.ReciprocalWindow

namespace R310

open Finset SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

/-- An outside vertex with a maximum independent contact set contains two mates
when the induced old card has a fixed-point-free automorphism. For an involution this
is a whole 2-cycle. No symmetry of the pole edges is assumed. -/
theorem full_mate_pair_of_max_contacts {old : Finset V} {pole : V}
    (hTriangle : G.CliqueFree 3) (hPole : pole ∉ old)
    (mate : G.induce (old : Set V) ≃g G.induce (old : Set V))
    (hFree : ∀ site, mate site ≠ site) (hMax : G.indepNum ≤ windowDegree G old pole) :
    ∃ site : (old : Set V), G.Adj pole (site : V) ∧
      G.Adj pole ((mate site : (old : Set V)) : V) ∧
      ¬ G.Adj (site : V) ((mate site : (old : Set V)) : V) := by
  classical
  by_contra hNoPair
  let contacts := (G.neighborFinset pole).subtype (· ∈ (old : Set V))
  let mateEmbedding : (old : Set V) ↪ V :=
    mate.toEquiv.toEmbedding.trans (Function.Embedding.subtype _)
  let image := contacts.map mateEmbedding
  have hContact (site : (old : Set V)) : site ∈ contacts ↔ G.Adj pole (site : V) := by
    simp [contacts]
  have hAvoid (site : (old : Set V)) (hIn : site ∈ contacts) :
      ¬ G.Adj pole (mateEmbedding site) := by
    intro hEdge
    have hFrom := (hContact site).mp hIn
    have hNe : (site : V) ≠ mateEmbedding site := by
      intro hEq
      exact hFree site (Subtype.ext hEq.symm)
    have hOldIndep := isIndepSet_neighborFinset hTriangle pole
    have hMateEdge : G.Adj pole ((mate site : (old : Set V)) : V) := hEdge
    exact hNoPair ⟨site, hFrom, hEdge,
      hOldIndep (by simpa using hFrom) (by simpa using hMateEdge) hNe⟩
  have hIndependent : G.IsIndepSet (image : Set V) := by
    intro first hFirst second hSecond hNe hEdge
    obtain ⟨firstOld, hFirstOld, rfl⟩ := mem_map.mp (show first ∈ image from hFirst)
    obtain ⟨secondOld, hSecondOld, rfl⟩ := mem_map.mp (show second ∈ image from hSecond)
    have hOldIndep := isIndepSet_neighborFinset hTriangle pole
    exact hOldIndep (by simpa using (hContact firstOld).mp hFirstOld)
      (by simpa using (hContact secondOld).mp hSecondOld)
      (fun hEq => hNe (congrArg mateEmbedding (Subtype.ext hEq))) (mate.map_adj_iff.mp hEdge)
  have hOutside : pole ∉ image := by
    intro hIn
    obtain ⟨site, _, hEq⟩ := mem_map.mp hIn
    exact hPole (hEq ▸ (mate site).property)
  have hWithPole : G.IsIndepSet ((insert pole image : Finset V) : Set V) := by
    rw [coe_insert, isIndepSet_iff, Set.pairwise_insert]
    refine ⟨hIndependent, fun vertex hv _ => ?_⟩
    obtain ⟨site, hIn, rfl⟩ := mem_map.mp (show vertex ∈ image from hv)
    exact ⟨hAvoid site hIn, fun hEdge => hAvoid site hIn hEdge.symm⟩
  have hImage : #image = windowDegree G old pole := by
    rw [show image = contacts.map mateEmbedding by rfl, card_map]
    change #((G.neighborFinset pole).subtype (· ∈ (old : Set V))) = _
    rw [card_subtype, windowDegree]
    congr 1
  have hCard := hWithPole.card_le_indepNum
  rw [card_insert_of_notMem hOutside, hImage] at hCard
  omega

/-- For a four-pole complement, pairwise disjoint physical contact columns imply that
each column has size at most `α(G) − 2`, without any symmetry premise. -/
theorem contact_add_two_le_of_disjoint_pole_columns {old poles : Finset V}
    (hTriangle : G.CliqueFree 3) (hSeparation : Disjoint old poles) (hPoles : #poles = 4)
    (hColumns : ∀ first ∈ poles, ∀ second ∈ poles, first ≠ second →
      Disjoint (G.neighborFinset first ∩ old) (G.neighborFinset second ∩ old))
    {pole : V} (hPole : pole ∈ poles) : windowDegree G old pole + 2 ≤ G.indepNum := by
  let contacts := G.neighborFinset pole ∩ old
  have hThree : #(poles.erase pole) = 3 := by rw [card_erase_of_mem hPole, hPoles]
  obtain ⟨first, second, third, hFS, hFT, hST, hRoster⟩ := card_eq_three.mp hThree
  have hOfRoster {site : V} (hIn : site ∈ ({first, second, third} : Finset V)) :
      site ≠ pole ∧ site ∈ poles := mem_erase.mp (hRoster ▸ hIn)
  have hFirst := hOfRoster (site := first) (by simp)
  have hSecond := hOfRoster (site := second) (by simp)
  have hThird := hOfRoster (site := third) (by simp)
  have hPair : ∃ first ∈ poles, ∃ second ∈ poles,
      first ≠ pole ∧ second ≠ pole ∧ first ≠ second ∧ ¬ G.Adj first second := by
    by_cases hEdgeFS : G.Adj first second
    · by_cases hEdgeFT : G.Adj first third
      · exact ⟨second, hSecond.2, third, hThird.2, hSecond.1, hThird.1, hST,
          fun hEdgeST => hTriangle {first, second, third}
            (is3Clique_triple_iff.mpr ⟨hEdgeFS, hEdgeFT, hEdgeST⟩)⟩
      · exact ⟨first, hFirst.2, third, hThird.2, hFirst.1, hThird.1, hFT, hEdgeFT⟩
    · exact ⟨first, hFirst.2, second, hSecond.2, hFirst.1, hSecond.1, hFS, hEdgeFS⟩
  obtain ⟨first, hFirst, second, hSecond, hFirstPole, hSecondPole, hNe, hNonedge⟩ := hPair
  have hOutside {site : V} (hSite : site ∈ poles) : site ∉ contacts :=
    fun hIn => disjoint_left.mp hSeparation (mem_inter.mp hIn).2 hSite
  have hAvoid {site vertex : V} (hSite : site ∈ poles) (hNe : site ≠ pole)
      (hIn : vertex ∈ contacts) : ¬ G.Adj site vertex :=
    fun hEdge => disjoint_left.mp (hColumns site hSite pole hPole hNe)
      (mem_inter.mpr ⟨(mem_neighborFinset _ _ _).mpr hEdge, (mem_inter.mp hIn).2⟩) hIn
  have hIndep : G.IsIndepSet ((insert first (insert second contacts) : Finset V) : Set V) := by
    rw [coe_insert, coe_insert, isIndepSet_iff, Set.pairwise_insert, Set.pairwise_insert]
    refine ⟨⟨(isIndepSet_neighborFinset hTriangle pole).mono (fun _ hv => (mem_inter.mp hv).1),
      fun vertex hv _ => ⟨hAvoid hSecond hSecondPole hv,
        fun hEdge => hAvoid hSecond hSecondPole hv hEdge.symm⟩⟩, fun vertex hv _ => ?_⟩
    rcases hv with rfl | hv
    · exact ⟨hNonedge, fun hEdge => hNonedge hEdge.symm⟩
    · exact ⟨hAvoid hFirst hFirstPole hv, fun hEdge => hAvoid hFirst hFirstPole hv hEdge.symm⟩
  have hFirstOut : first ∉ insert second contacts := by
    simp [hNe, hOutside hFirst]
  have hCount := hIndep.card_le_indepNum
  rw [card_insert_of_notMem hFirstOut, card_insert_of_notMem (hOutside hSecond)] at hCount
  exact hCount

/-- At most one free degree slot at every old site forces disjoint contact columns. -/
theorem disjoint_pole_columns_of_one_slot {old poles : Finset V}
    (hSeparation : Disjoint old poles)
    (hSlots : ∀ site ∈ old, G.degree site ≤ windowDegree G old site + 1)
    {first second : V} (hFirst : first ∈ poles) (hSecond : second ∈ poles)
    (hNe : first ≠ second) :
    Disjoint (G.neighborFinset first ∩ old) (G.neighborFinset second ∩ old) := by
  refine disjoint_left.mpr fun site hf hs => ?_
  have hOld := (mem_inter.mp hf).2
  have hPair : ({first, second} : Finset V) ⊆ poles := by
    intro vertex hv
    simp only [mem_insert, mem_singleton] at hv
    rcases hv with rfl | rfl <;> assumption
  have hDisjoint : Disjoint (G.neighborFinset site ∩ old) ({first, second} : Finset V) :=
    hSeparation.mono inter_subset_right hPair
  have hSub : (G.neighborFinset site ∩ old) ∪ {first, second} ⊆ G.neighborFinset site := by
    refine union_subset inter_subset_left ?_
    intro vertex hv
    simp only [mem_insert, mem_singleton] at hv
    rcases hv with rfl | rfl
    · exact (mem_neighborFinset _ _ _).mpr ((mem_neighborFinset _ _ _).mp (mem_inter.mp hf).1).symm
    · exact (mem_neighborFinset _ _ _).mpr ((mem_neighborFinset _ _ _).mp (mem_inter.mp hs).1).symm
  have hCount := card_le_card hSub
  rw [card_union_of_disjoint hDisjoint, card_insert_of_notMem (by simpa using hNe),
    card_singleton, card_neighborFinset_eq_degree] at hCount
  change windowDegree G old site + (1 + 1) ≤ G.degree site at hCount
  have := hSlots site hOld
  omega

/-- The disjoint-column size-seven obstruction under old minimum degree eight and
the target independence cap. This does not require the old card to have an involution. -/
theorem pole_contacts_le_seven_of_min_old_degree_eight {old poles : Finset V}
    (hTriangle : G.CliqueFree 3) (hAlpha : G.indepNum ≤ 9)
    (hSeparation : Disjoint old poles) (hPoles : #poles = 4)
    (hMin : ∀ site ∈ old, 8 ≤ windowDegree G old site)
    {pole : V} (hPole : pole ∈ poles) : windowDegree G old pole ≤ 7 := by
  have hSlots (site : V) (hSite : site ∈ old) : G.degree site ≤ windowDegree G old site + 1 := by
    have := (degree_le_indepNum hTriangle site).trans hAlpha
    have := hMin site hSite
    omega
  have hColumns (first : V) (hf : first ∈ poles) (second : V) (hs : second ∈ poles)
      (hne : first ≠ second) := disjoint_pole_columns_of_one_slot hSeparation hSlots hf hs hne
  have := contact_add_two_le_of_disjoint_pole_columns hTriangle hSeparation hPoles hColumns hPole
  omega

end R310
