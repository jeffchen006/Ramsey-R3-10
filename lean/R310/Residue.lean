/-
Independent-set residues for mask-count projections. Published Ramsey bounds are
explicit hypotheses, not part of the formal proof.
-/
import R310.MinDegree

open Finset SimpleGraph

namespace R310

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V}

/-- A disjoint set anticomplete to an independent set has a limited independence number. -/
theorem indepNum_induce_add_card_le {fixed residue : Finset V}
    (hind : G.IsIndepSet (fixed : Set V)) (hdisj : Disjoint fixed residue)
    (hanti : ∀ u ∈ fixed, ∀ v ∈ residue, ¬ G.Adj u v) :
    (G.induce (residue : Set V)).indepNum + #fixed ≤ G.indepNum := by
  classical
  obtain ⟨s, hs⟩ := (G.induce (residue : Set V)).exists_isNIndepSet_indepNum
  let lifted := s.map (Function.Embedding.subtype (· ∈ (residue : Set V)))
  have hsub : lifted ⊆ residue := by
    intro v hv
    obtain ⟨w, _, rfl⟩ := mem_map.1 hv
    exact w.property
  have hLifted : G.IsIndepSet (lifted : Set V) := by
    intro u hu v hv huv
    obtain ⟨u', hu', rfl⟩ := mem_map.1 hu
    obtain ⟨v', hv', rfl⟩ := mem_map.1 hv
    exact hs.isIndepSet hu' hv' (fun h => huv (congrArg Subtype.val h))
  have hUnion : G.IsIndepSet ((fixed ∪ lifted : Finset V) : Set V) := by
    rw [coe_union, isIndepSet_iff, Set.pairwise_union]
    refine ⟨hind, hLifted, ?_⟩
    intro u hu v hv _
    have h := hanti u hu v (hsub hv)
    exact ⟨h, fun he => h he.symm⟩
  have hcard := hUnion.card_le_indepNum
  rw [card_union_of_disjoint (disjoint_of_subset_right hsub hdisj)] at hcard
  dsimp only [lifted] at hcard
  rw [card_map, hs.card_eq, add_comm] at hcard
  exact hcard

/-- Mask projection row 4: disjoint pieces of a residue sum to less than a Ramsey bound. -/
theorem residue_order_row {fixed localPart outsidePart : Finset V} {k order : ℕ}
    (h3 : G.CliqueFree 3) (hα : G.indepNum < #fixed + k) (hR : Ramsey3Le k order)
    (hind : G.IsIndepSet (fixed : Set V)) (hdisj : Disjoint fixed (localPart ∪ outsidePart))
    (hanti : ∀ u ∈ fixed, ∀ v ∈ localPart ∪ outsidePart, ¬ G.Adj u v)
    (hpartition : Disjoint localPart outsidePart) : #localPart + #outsidePart < order := by
  classical
  have h := indepNum_induce_add_card_le hind hdisj hanti
  by_contra! hlarge
  have hcard : order ≤ Fintype.card (↑(localPart ∪ outsidePart) : Set V) := by
    simpa [card_union_of_disjoint hpartition] using hlarge
  have hlow := hR.le_indepNum hcard _ (h3.comap (Embedding.induce _).isContained)
  omega

/-- Mask projection row 5, valid for any vertex (even one outside the residue). -/
theorem residue_neighbor_row [DecidableRel G.Adj] {fixed localPart outsidePart : Finset V}
    {bound : ℕ} (h3 : G.CliqueFree 3) (hα : G.indepNum ≤ #fixed + bound)
    (hind : G.IsIndepSet (fixed : Set V)) (hdisj : Disjoint fixed (localPart ∪ outsidePart))
    (hanti : ∀ u ∈ fixed, ∀ v ∈ localPart ∪ outsidePart, ¬ G.Adj u v)
    (hpartition : Disjoint localPart outsidePart) (root : V) :
    #{v ∈ localPart | G.Adj root v} + #{v ∈ outsidePart | G.Adj root v} ≤ bound := by
  classical
  let lhs := localPart.filter (G.Adj root)
  let rhs := outsidePart.filter (G.Adj root)
  have hsub : lhs ∪ rhs ⊆ localPart ∪ outsidePart :=
    union_subset_union (filter_subset _ _) (filter_subset _ _)
  have hpart : Disjoint lhs rhs :=
    hpartition.mono (filter_subset _ _) (filter_subset _ _)
  have hnbr : (lhs ∪ rhs) ⊆ G.neighborFinset root := by
    intro v hv
    rw [mem_neighborFinset]
    rcases mem_union.1 hv with hv | hv
    · exact (mem_filter.1 hv).2
    · exact (mem_filter.1 hv).2
  have hind' : G.IsIndepSet ((lhs ∪ rhs : Finset V) : Set V) :=
    Set.Pairwise.mono (by simpa only [coe_subset] using hnbr) (isIndepSet_neighborFinset h3 root)
  have hind'' : G.IsIndepSet ((fixed ∪ (lhs ∪ rhs) : Finset V) : Set V) := by
    rw [coe_union, isIndepSet_iff, Set.pairwise_union]
    refine ⟨hind, hind', ?_⟩
    intro u hu v hv _
    have h := hanti u hu v (hsub hv)
    exact ⟨h, fun he => h he.symm⟩
  have hcard := hind''.card_le_indepNum
  rw [card_union_of_disjoint (disjoint_of_subset_right hsub hdisj),
    card_union_of_disjoint hpart] at hcard
  change #lhs + #rhs ≤ bound
  omega

/-- Mask projection row 6: a set larger than the codegree cap is contained in
at most one neighborhood, hence in at most one outside mask. -/
theorem card_filter_common_neighbors_le_one [DecidableRel G.Adj] {cap : ℕ}
    (h3 : G.CliqueFree 3)
    (hcap : ∀ left right, left ≠ right → ¬ G.Adj left right →
      #(G.neighborFinset left ∩ G.neighborFinset right) ≤ cap)
    (support outsidePart : Finset V) (hsize : cap < #support) :
    #{vertex ∈ outsidePart | support ⊆ G.neighborFinset vertex} ≤ 1 := by
  classical
  apply Finset.card_le_one.mpr
  intro left hleft right hright
  by_contra hne
  have hsub : support ⊆ G.neighborFinset left ∩ G.neighborFinset right :=
    subset_inter (mem_filter.1 hleft).2 (mem_filter.1 hright).2
  obtain ⟨common, hcommon⟩ := Finset.card_pos.mp (by omega : 0 < #support)
  have hadj := mem_inter.1 (hsub hcommon)
  have hnon : ¬ G.Adj left right := fun hedge =>
    h3 {left, right, common} (is3Clique_triple_iff.2
      ⟨hedge, (mem_neighborFinset _ _ _).1 hadj.1, (mem_neighborFinset _ _ _).1 hadj.2⟩)
  exact (not_le_of_gt hsize) ((card_le_card hsub).trans (hcap left right hne hnon))

/-- A complete bipartite subgraph forces the rest to split into two smaller
Ramsey residues, without a regularity or maximality hypothesis. -/
theorem card_add_two_le_of_biclique [DecidableRel G.Adj] {left right : Finset V}
    {leftSize rightSize leftOrder rightOrder : ℕ} (h3 : G.CliqueFree 3)
    (leftRamsey : Ramsey3Le leftSize leftOrder) (rightRamsey : Ramsey3Le rightSize rightOrder)
    (leftIndep : G.indepNum < #left + leftSize) (rightIndep : G.indepNum < #right + rightSize)
    (partsDisjoint : Disjoint left right) (leftNonempty : left.Nonempty) (rightNonempty : right.Nonempty)
    (hcross : ∀ u ∈ left, ∀ v ∈ right, G.Adj u v) :
    Fintype.card V + 2 ≤ #left + #right + leftOrder + rightOrder := by
  classical
  let rest := (left ∪ right)ᶜ
  let avoids := rest.filter (fun v => ∀ u ∈ left, ¬ G.Adj u v)
  let touches := rest \ avoids
  have hleft : G.IsIndepSet (left : Set V) := by
    obtain ⟨r, hr⟩ := rightNonempty
    refine Set.Pairwise.mono ?_ (isIndepSet_neighborFinset h3 r)
    intro u hu
    exact (mem_neighborFinset _ _ _).2 (hcross u hu r hr).symm
  have hright : G.IsIndepSet (right : Set V) := by
    obtain ⟨l, hl⟩ := leftNonempty
    refine Set.Pairwise.mono ?_ (isIndepSet_neighborFinset h3 l)
    intro v hv
    exact (mem_neighborFinset _ _ _).2 (hcross l hl v hv)
  have hdisjL : Disjoint left avoids := by
    apply Finset.disjoint_left.2
    intro v hv havoids
    exact (mem_compl.1 (mem_filter.1 havoids).1) (mem_union_left _ hv)
  have hantiL : ∀ u ∈ left, ∀ v ∈ avoids, ¬ G.Adj u v := by
    intro u hu v hv
    exact (mem_filter.1 hv).2 u hu
  have hdisjR : Disjoint right touches := by
    apply Finset.disjoint_left.2
    intro v hv htouches
    exact (mem_compl.1 (mem_sdiff.1 htouches).1) (mem_union_right _ hv)
  have hantiR : ∀ u ∈ right, ∀ v ∈ touches, ¬ G.Adj u v := by
    intro u hu v hv huv
    have hv' := mem_sdiff.1 hv
    apply hv'.2
    apply mem_filter.2
    refine ⟨hv'.1, ?_⟩
    intro w hw hwv
    exact h3 {w, u, v} (is3Clique_triple_iff.2 ⟨hcross w hw u hu, hwv, huv⟩)
  have havoid : #avoids < leftOrder := by
    simpa using (residue_order_row h3 leftIndep leftRamsey hleft
      (localPart := avoids) (outsidePart := ∅) (by simpa using hdisjL)
      (by simpa using hantiL) (disjoint_empty_right _))
  have htouch : #touches < rightOrder := by
    simpa using (residue_order_row h3 rightIndep rightRamsey hright
      (localPart := touches) (outsidePart := ∅) (by simpa using hdisjR)
      (by simpa using hantiR) (disjoint_empty_right _))
  have hpart : #touches + #avoids = #rest := card_sdiff_add_card_eq_card (filter_subset _ _)
  have htotal : #rest + (#left + #right) = Fintype.card V := by
    dsimp only [rest]
    rw [card_compl, ← card_union_of_disjoint partsDisjoint]
    exact Nat.sub_add_cancel (card_le_univ _)
  omega

theorem not_biclique36 {G : SimpleGraph (Fin 40)} [DecidableRel G.Adj]
    (h3 : G.CliqueFree 3) (halpha : G.indepNum ≤ 9)
    (h7 : Ramsey3Le 7 23) (h4 : Ramsey3Le 4 9) (left right : Finset (Fin 40))
    (hleft : #left = 3) (hright : #right = 6) (hdisj : Disjoint left right) :
    ¬ ∀ u ∈ left, ∀ v ∈ right, G.Adj u v := by
  intro cross
  have h := card_add_two_le_of_biclique h3 h7 h4 (by omega) (by omega) hdisj
    (card_pos.1 (by omega)) (card_pos.1 (by omega)) cross
  simp only [Fintype.card_fin, hleft, hright] at h
  omega

theorem not_biclique45 {G : SimpleGraph (Fin 40)} [DecidableRel G.Adj]
    (h3 : G.CliqueFree 3) (halpha : G.indepNum ≤ 9)
    (h6 : Ramsey3Le 6 18) (h5 : Ramsey3Le 5 14) (left right : Finset (Fin 40))
    (hleft : #left = 4) (hright : #right = 5) (hdisj : Disjoint left right) :
    ¬ ∀ u ∈ left, ∀ v ∈ right, G.Adj u v := by
  intro cross
  have h := card_add_two_le_of_biclique h3 h6 h5 (by omega) (by omega) hdisj
    (card_pos.1 (by omega)) (card_pos.1 (by omega)) cross
  simp only [Fintype.card_fin, hleft, hright] at h
  omega

end R310

namespace R310

open Finset SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V}

omit [Fintype V] in
/-- A four-step running intersection bound. At each step, six members of
the next nine-set have already appeared. -/
theorem card_union_four_le_eighteen (first second third fourth : Finset V)
    (hfirst : #first = 9) (hsecond : #second = 9)
    (hthird : #third = 9) (hfourth : #fourth = 9)
    (hfirstOverlap : #(first ∩ second) = 6)
    (hsecondOverlap : #(second ∩ third) = 6)
    (hthirdOverlap : #(third ∩ fourth) = 6) :
    #(first ∪ second ∪ third ∪ fourth) ≤ 18 := by
  have hfirstUnion := card_union_add_card_inter first second
  have hsecondUnion := card_union_add_card_inter (first ∪ second) third
  have hthirdUnion := card_union_add_card_inter (first ∪ second ∪ third) fourth
  have hsecondBound : #(second ∩ third) ≤ #((first ∪ second) ∩ third) := by
    apply card_le_card
    intro vertex hvertex
    obtain ⟨hsecondVertex, hthirdVertex⟩ := mem_inter.1 hvertex
    exact mem_inter.2 ⟨mem_union_right _ hsecondVertex, hthirdVertex⟩
  have hthirdBound : #(third ∩ fourth) ≤ #((first ∪ second ∪ third) ∩ fourth) := by
    apply card_le_card
    intro vertex hvertex
    obtain ⟨hthirdVertex, hfourthVertex⟩ := mem_inter.1 hvertex
    exact mem_inter.2 ⟨mem_union_right _ hthirdVertex, hfourthVertex⟩
  omega

/-- A small cover of the open neighbourhoods of an independent set violates
a Ramsey bound if sufficiently many vertices remain outside it. -/
theorem card_le_of_neighborhood_cover [DecidableRel G.Adj] {fixed near : Finset V}
    {k order : ℕ} (h3 : G.CliqueFree 3) (hα : G.indepNum < #fixed + k)
    (hR : Ramsey3Le k order) (hind : G.IsIndepSet (fixed : Set V))
    (hcover : ∀ u ∈ fixed, G.neighborFinset u ⊆ near) :
    Fintype.card V < #fixed + #near + order := by
  classical
  let residue := (fixed ∪ near)ᶜ
  have hdisj : Disjoint fixed residue := by
    apply Finset.disjoint_left.2
    intro vertex hfixed hresidue
    exact (mem_compl.1 hresidue) (mem_union_left _ hfixed)
  have hanti : ∀ u ∈ fixed, ∀ v ∈ residue, ¬ G.Adj u v := by
    intro u hu v hv hav
    exact (mem_compl.1 hv) (mem_union_right _ (hcover u hu ((mem_neighborFinset _ _ _).2 hav)))
  have hsmall : #residue < order := by
    simpa using (residue_order_row h3 hα hR hind
      (localPart := residue) (outsidePart := ∅) (by simpa using hdisj)
      (by simpa using hanti) (by simp))
  have hsize := card_union_add_card_inter fixed near
  dsimp [residue] at hsmall
  rw [card_compl] at hsmall
  omega

/-- A four-root codegree-six chain in Case R has adjacent endpoints once the
two diagonal nonedges are known. The published R(3,6) bound is a hypothesis. -/
theorem codegree_six_chain_endpoints_adj {G : SimpleGraph (Fin 40)} [DecidableRel G.Adj]
    (hTriangle : G.CliqueFree 3) (hIndep : G.indepNum ≤ 9) (hRamsey : Ramsey3Le 6 18)
    (hRegular : ∀ vertex, #(G.neighborFinset vertex) = 9)
    (first second third fourth : Fin 40) (hCard : #({first, second, third, fourth} : Finset _) = 4)
    (hFirstOverlap : #(G.neighborFinset first ∩ G.neighborFinset second) = 6)
    (hSecondOverlap : #(G.neighborFinset second ∩ G.neighborFinset third) = 6)
    (hThirdOverlap : #(G.neighborFinset third ∩ G.neighborFinset fourth) = 6)
    (hFirstSecond : ¬ G.Adj first second) (hSecondThird : ¬ G.Adj second third)
    (hThirdFourth : ¬ G.Adj third fourth) (hFirstThird : ¬ G.Adj first third)
    (hSecondFourth : ¬ G.Adj second fourth) : G.Adj first fourth := by
  by_contra hFirstFourth
  let roots : Finset (Fin 40) := {first, second, third, fourth}
  let near := G.neighborFinset first ∪ G.neighborFinset second ∪ G.neighborFinset third ∪
    G.neighborFinset fourth
  have hSize : #roots = 4 := hCard
  have hRootIndep : G.IsIndepSet (roots : Set (Fin 40)) := by
    intro left hLeft right hRight hDifferent
    simp only [roots, mem_coe, mem_insert, mem_singleton] at hLeft hRight
    rcases hLeft with rfl | rfl | rfl | rfl <;> rcases hRight with rfl | rfl | rfl | rfl
    all_goals first | exact (hDifferent rfl).elim | assumption
                    | (intro hedge; exact (by assumption : ¬ G.Adj _ _) hedge.symm)
  have hNear : #near ≤ 18 :=
    card_union_four_le_eighteen _ _ _ _ (hRegular _) (hRegular _) (hRegular _) (hRegular _)
      hFirstOverlap hSecondOverlap hThirdOverlap
  have hCover : ∀ vertex ∈ roots, G.neighborFinset vertex ⊆ near := by
    intro vertex hVertex neighbor hNeighbor
    simp only [roots, mem_insert, mem_singleton] at hVertex
    rcases hVertex with rfl | rfl | rfl | rfl <;> simp [near, hNeighbor]
  have hBound := card_le_of_neighborhood_cover hTriangle (by omega) hRamsey hRootIndep hCover
  simp only [Fintype.card_fin] at hBound
  omega

end R310
