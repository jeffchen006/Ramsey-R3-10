import R310.MinDegree
import R310.ReciprocalWindow

namespace R310

open Finset SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

/-- The neutral sites avoid the union of the two root sets. -/
theorem reciprocal_windows_inter (left right : Finset V) :
    rootsWindow G left ∩ rootsWindow G right = rootsWindow G (left ∪ right) := by
  ext vertex
  simp only [mem_inter, mem_rootsWindow, mem_union, not_or]
  constructor
  · rintro ⟨⟨hLeftOut, hLeftAvoid⟩, ⟨hRightOut, hRightAvoid⟩⟩
    exact ⟨⟨hLeftOut, hRightOut⟩, fun root hIn => hIn.elim (hLeftAvoid root) (hRightAvoid root)⟩
  · rintro ⟨⟨hLeftOut, hRightOut⟩, hAvoid⟩
    exact ⟨⟨hLeftOut, fun root hIn => hAvoid root (Or.inl hIn)⟩,
      ⟨hRightOut, fun root hIn => hAvoid root (Or.inr hIn)⟩⟩

/-- An independent root set can be adjoined to an independent set in its window. -/
theorem indepNum_rootsWindow_add_le {roots : Finset V} (hRoots : G.IsIndepSet (roots : Set V)) :
    (G.induce (rootsWindow G roots : Set V)).indepNum + #roots ≤ G.indepNum := by
  obtain ⟨seed, hSeed⟩ := (G.induce (rootsWindow G roots : Set V)).exists_isNIndepSet_indepNum
  let sites : Finset V := seed.map (Function.Embedding.subtype _)
  have hSites (vertex : V) : vertex ∈ sites ↔ ∃ site ∈ seed, (site : V) = vertex := by
    simp [sites]
  have hDisjoint : Disjoint sites roots := by
    rw [Finset.disjoint_left]
    intro vertex hSite hRoot
    obtain ⟨site, _, rfl⟩ := (hSites vertex).mp hSite
    exact (mem_rootsWindow.mp site.2).1 hRoot
  have hIndep : G.IsIndepSet ((sites ∪ roots : Finset V) : Set V) := by
    intro vertex hVertex other hOther hNe
    rcases mem_union.mp hVertex with hSite | hRoot
    · obtain ⟨site, hSiteIn, rfl⟩ := (hSites vertex).mp hSite
      rcases mem_union.mp hOther with hOtherSite | hOtherRoot
      · obtain ⟨second, hSecondIn, rfl⟩ := (hSites other).mp hOtherSite
        exact hSeed.isIndepSet hSiteIn hSecondIn (fun hEq => hNe (congrArg Subtype.val hEq))
      · exact fun hAdj => (mem_rootsWindow.mp site.2).2 other hOtherRoot hAdj.symm
    · rcases mem_union.mp hOther with hOtherSite | hOtherRoot
      · obtain ⟨site, _, rfl⟩ := (hSites other).mp hOtherSite
        exact (mem_rootsWindow.mp site.2).2 vertex hRoot
      · exact hRoots hRoot hOtherRoot hNe
  calc
    (G.induce (rootsWindow G roots : Set V)).indepNum + #roots = #sites + #roots := by
      change _ + #roots = #(seed.map (Function.Embedding.subtype _)) + #roots
      rw [card_map, hSeed.card_eq]
    _ = #(sites ∪ roots) := (card_union_of_disjoint hDisjoint).symm
    _ ≤ G.indepNum := hIndep.card_le_indepNum

/-- Apply a Ramsey upper bound to the induced antineighborhood, not to the ambient graph. -/
theorem card_rootsWindow_lt_of_ramsey {roots : Finset V} {target order : ℕ}
    (hTriangle : G.CliqueFree 3) (hRoots : G.IsIndepSet (roots : Set V))
    (hIndep : G.indepNum < target + #roots) (hRamsey : Ramsey3Le target order) :
    #(rootsWindow G roots) < order := by
  by_contra! hOrder
  have hInduced := hTriangle.comap (Embedding.induce (rootsWindow G roots : Set V)).isContained
  have hLower := hRamsey.le_indepNum (by simpa using hOrder) _ hInduced
  have hUpper := indepNum_rootsWindow_add_le hRoots
  omega

/-- Two completely joined nonempty root sets partition the exterior into private and neutral
sites. Inclusion-exclusion counts the actual neutral sites once on the right. -/
theorem reciprocal_windows_card_add (hTriangle : G.CliqueFree 3) {left right : Finset V}
    (hLeft : left.Nonempty) (hRight : right.Nonempty)
    (hCross : ∀ vertex ∈ left, ∀ other ∈ right, G.Adj vertex other) :
    #(rootsWindow G left) + #(rootsWindow G right) =
      #(univ \ (left ∪ right)) + #(rootsWindow G (left ∪ right)) := by
  rw [← reciprocal_windows_union hTriangle hLeft hRight hCross,
    ← reciprocal_windows_inter (G := G) left right, card_union_add_card_inter]

/-- The two-neutral marked-biclique cover used by C. `Ramsey3Le 6 18` is an explicit
published input. Neither regularity nor a codegree cap is needed for this implication. -/
theorem biclique_four_neutral_iff_windows_seventeen (hOrder : Fintype.card V = 40)
    (hTriangle : G.CliqueFree 3) (hIndep : G.indepNum ≤ 9) (hRamsey : Ramsey3Le 6 18)
    {left right : Finset V} (hLeft : #left = 4) (hRight : #right = 4)
    (hLeftIndep : G.IsIndepSet (left : Set V)) (hRightIndep : G.IsIndepSet (right : Set V))
    (hCross : ∀ vertex ∈ left, ∀ other ∈ right, G.Adj vertex other) :
    #(univ \ (left ∪ right)) = 32 ∧
      #(rootsWindow G left) ≤ 17 ∧ #(rootsWindow G right) ≤ 17 ∧
      #(rootsWindow G (left ∪ right)) ≤ 2 ∧
      (#(rootsWindow G (left ∪ right)) = 2 ↔
        #(rootsWindow G left) = 17 ∧ #(rootsWindow G right) = 17) := by
  have hDisjoint : Disjoint left right := by
    rw [Finset.disjoint_left]
    exact fun vertex hInLeft hInRight => (hCross vertex hInLeft vertex hInRight).ne rfl
  have hExterior : #(univ \ (left ∪ right)) = 32 := by
    rw [card_sdiff_of_subset (subset_univ _), card_univ, card_union_of_disjoint hDisjoint,
      hOrder, hLeft, hRight]
  have hLeftNonempty : left.Nonempty := card_pos.mp (by omega)
  have hRightNonempty : right.Nonempty := card_pos.mp (by omega)
  have hAdd := reciprocal_windows_card_add hTriangle hLeftNonempty hRightNonempty hCross
  rw [hExterior] at hAdd
  have hLeftCap := card_rootsWindow_lt_of_ramsey hTriangle hLeftIndep (by omega) hRamsey
  have hRightCap := card_rootsWindow_lt_of_ramsey hTriangle hRightIndep (by omega) hRamsey
  refine ⟨hExterior, by omega, by omega, by omega, ?_⟩
  constructor
  · intro hNeutral
    exact ⟨by omega, by omega⟩
  · rintro ⟨hLeftFull, hRightFull⟩
    omega

end R310
