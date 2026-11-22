import R310.Pair

open Finset SimpleGraph

namespace R310

/-- A simultaneous solution survives any shrink step that deletes a value only
when it has no support in some other current domain. Iterating this statement
does not require a particular arc order, symmetry of the relations, or nonempty
domains at indices not used as witnesses. -/
theorem preserves_arc_shrink {Index Value : Type*} {compatible : Index → Index →
    Value → Value → Prop} {before after : Index → Finset Value} {solution : Index → Value}
    (hBefore : ∀ index, solution index ∈ before index)
    (hCompatible : ∀ first second, first ≠ second →
      compatible first second (solution first) (solution second))
    (hDelete : ∀ index value, value ∈ before index → value ∉ after index →
      ∃ other ≠ index, ∀ witness ∈ before other, ¬ compatible index other value witness) :
    ∀ index, solution index ∈ after index := by
  intro index
  by_contra hMissing
  obtain ⟨other, hOther, hUnsupported⟩ := hDelete index _ (hBefore index) hMissing
  exact hUnsupported _ (hBefore other) (hCompatible index other hOther.symm)

/-- Every round of a sequence of supported-domain shrinks preserves the
assignment of an actual simultaneous completion. -/
theorem preserves_arc_sequence {Index Value : Type*} {compatible : Index → Index →
    Value → Value → Prop} {domains : ℕ → Index → Finset Value} {solution : Index → Value}
    (hInitial : ∀ index, solution index ∈ domains 0 index)
    (hCompatible : ∀ first second, first ≠ second →
      compatible first second (solution first) (solution second))
    (hStep : ∀ round index value, value ∈ domains round index →
      value ∉ domains (round + 1) index →
      ∃ other ≠ index, ∀ witness ∈ domains round other,
        ¬ compatible index other value witness) :
    ∀ round index, solution index ∈ domains round index := by
  intro round
  induction round with
  | zero => exact hInitial
  | succ round ih => exact preserves_arc_shrink ih hCompatible (hStep round)

section Graph

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

/-- Open-neighbourhood codegree controls the size of the paired window.
The second pivot can have degree seven (paired) or eight (mixed). This
does not assert that any two pivots of those degrees have the required roles. -/
theorem paired_window_order_alpha (hTriangle : G.CliqueFree 3) (hAlpha : G.indepNum ≤ 9)
    {first second : V} (hDistinct : first ≠ second) (hNonadj : ¬ G.Adj first second) :
    Fintype.card (outside2 G first second : Set V) + G.degree first + G.degree second + 2 =
        Fintype.card V + #(G.neighborFinset first ∩ G.neighborFinset second) ∧
      (G.induce (outside2 G first second : Set V)).CliqueFree 3 ∧
      (G.induce (outside2 G first second : Set V)).indepNum ≤ 7 := by
  have hSize := card_outside2_add (G := G) hDistinct hNonadj
  have hIndep := indepNum_outside2_add_two_le (G := G) hDistinct hNonadj
  exact ⟨by simpa only [Finset.coe_sort_coe, Fintype.card_coe] using hSize,
    hTriangle.comap (Embedding.induce _).isContained, by omega⟩

/-- The order-25 degree-two and order-26 degree-three slices use order-22
`(3,7)` cores. The size premise is exact, so this bridge does not put the
higher minimum-degree cases into the same catalogue. -/
theorem window_root_core22 (hTriangle : G.CliqueFree 3) (hAlpha : G.indepNum ≤ 7)
    (root : V) (hSize : Fintype.card V = 23 + G.degree root) :
    Fintype.card (outside G root : Set V) = 22 ∧
      (delNbhd G root).CliqueFree 3 ∧ (delNbhd G root).indepNum ≤ 6 := by
  have hCount := card_delNbhd_verts (G := G) root
  exact ⟨by omega, cliqueFree_delNbhd hTriangle root,
    indepNum_delNbhd_le (k := 8) hAlpha root⟩

end Graph

end R310
