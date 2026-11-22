import R310.FoldedSlot

namespace R310

namespace SelectedWitness

variable {Var Site Vertex : Type*}

/-- False polarity for a selector guard; true polarity for a possible edge.
`none` means that there is no positive literal for this physical pair. -/
def row (guards : List Var) (pairs : List (Site × Site))
    (edgeVar : Site × Site → Option Var) : List (Var × Bool) :=
  guards.map (fun guard => (guard, false)) ++
    (pairs.filterMap edgeVar).map (fun edge => (edge, true))

def Holds (assignment : Var → Bool) (clause : List (Var × Bool)) : Prop :=
  ∃ literal ∈ clause, assignment literal.1 = literal.2

def AllSelected (assignment : Var → Bool) (guards : List Var) : Prop :=
  ∀ guard ∈ guards, assignment guard = true

theorem row_holds_iff (assignment : Var → Bool) (guards : List Var)
    (pairs : List (Site × Site)) (edgeVar : Site × Site → Option Var) :
    Holds assignment (row guards pairs edgeVar) ↔
      (∃ guard ∈ guards, assignment guard = false) ∨
      (∃ pair ∈ pairs, ∃ edge, edgeVar pair = some edge ∧ assignment edge = true) := by
  constructor
  · rintro ⟨literal, hmem, hValue⟩
    rcases List.mem_append.mp hmem with hGuard | hEdge
    · rcases List.mem_map.mp hGuard with ⟨guard, hGuardMem, rfl⟩
      exact Or.inl ⟨guard, hGuardMem, hValue⟩
    · rcases List.mem_map.mp hEdge with ⟨edge, hEdgeMem, rfl⟩
      rcases List.mem_filterMap.mp hEdgeMem with ⟨pair, hPair, hVar⟩
      exact Or.inr ⟨pair, hPair, edge, hVar, hValue⟩
  · rintro (⟨guard, hmem, hValue⟩ | ⟨pair, hmem, edge, hVar, hValue⟩)
    · exact ⟨(guard, false), List.mem_append_left _ (List.mem_map_of_mem hmem), hValue⟩
    · exact ⟨(edge, true), List.mem_append_right _
        (List.mem_map_of_mem (List.mem_filterMap.mpr ⟨pair, hmem, hVar⟩)), hValue⟩

/-- Graph-to-row soundness for an explicit physical witness of size `bound`
(ten in the target). The active guards must imply genuine injective names and
honest pair incidence. A single orientation of each unordered pair suffices.
In particular a pair with no variable must be a physical nonedge under the
guards. There is no assertion that a SAT assignment decodes to a graph. -/
theorem row_sound [Finite Vertex] [DecidableEq Vertex] (Graph : SimpleGraph Vertex)
    (assignment : Var → Bool) (guards : List Var) (sites : Finset Site)
    (vertex : Site → Vertex) (pairs : List (Site × Site))
    (edgeVar : Site × Site → Option Var) {bound : Nat}
    (hSize : bound ≤ sites.card) (hAlpha : Graph.indepNum < bound)
    (hDistinct : AllSelected assignment guards → Set.InjOn vertex (sites : Set Site))
    (hPairs : ∀ first ∈ sites, ∀ second ∈ sites, first ≠ second →
      (first, second) ∈ pairs ∨ (second, first) ∈ pairs)
    (hEdge : AllSelected assignment guards → ∀ pair ∈ pairs,
      Graph.Adj (vertex pair.1) (vertex pair.2) →
      ∃ edge, edgeVar pair = some edge ∧ assignment edge = true) :
    Holds assignment (row guards pairs edgeVar) := by
  classical
  by_cases hSelected : AllSelected assignment guards
  · by_contra hRow
    have hNoEdge : ∀ pair ∈ pairs, ¬ Graph.Adj (vertex pair.1) (vertex pair.2) := by
      intro pair hPair hAdj
      obtain ⟨edge, hVar, hValue⟩ := hEdge hSelected pair hPair hAdj
      exact hRow ((row_holds_iff assignment guards pairs edgeVar).mpr
        (Or.inr ⟨pair, hPair, edge, hVar, hValue⟩))
    have hIndep : Graph.IsIndepSet ((sites.image vertex : Finset Vertex) : Set Vertex) := by
      intro lhs hLhs rhs hRhs hNe hAdj
      obtain ⟨first, hFirst, rfl⟩ := Finset.mem_image.mp hLhs
      obtain ⟨second, hSecond, rfl⟩ := Finset.mem_image.mp hRhs
      rcases hPairs first hFirst second hSecond (fun hEq => hNe (congrArg vertex hEq)) with
        hForward | hBackward
      · exact hNoEdge (first, second) hForward hAdj
      · exact hNoEdge (second, first) hBackward hAdj.symm
    have hCard : (sites.image vertex).card = sites.card := Finset.card_image_of_injOn (hDistinct hSelected)
    exact (not_le_of_gt hAlpha) (hSize.trans (hCard ▸ hIndep.card_le_indepNum))
  · have hGuard : ∃ guard ∈ guards, assignment guard = false := by
      simpa [AllSelected, Bool.not_eq_true] using hSelected
    exact (row_holds_iff assignment guards pairs edgeVar).mpr (Or.inl hGuard)

/-- Dropping edge variables already forced false when all selectors are true
preserves the row under the projection. This does not justify dropping any
selector guard or any free optional/optional edge. -/
theorem compact_iff_full (assignment : Var → Bool) (guards : List Var)
    (pairs : List (Site × Site)) (full compact : Site × Site → Option Var)
    (hKept : ∀ pair ∈ pairs, ∀ edge, compact pair = some edge → full pair = some edge)
    (hDropped : AllSelected assignment guards → ∀ pair ∈ pairs, ∀ edge,
      full pair = some edge → compact pair = none → assignment edge = false) :
    Holds assignment (row guards pairs compact) ↔ Holds assignment (row guards pairs full) := by
  rw [row_holds_iff, row_holds_iff]
  constructor
  · rintro (hGuard | ⟨pair, hmem, edge, hVar, hValue⟩)
    · exact Or.inl hGuard
    · exact Or.inr ⟨pair, hmem, edge, hKept pair hmem edge hVar, hValue⟩
  · rintro (hGuard | ⟨pair, hmem, edge, hVar, hValue⟩)
    · exact Or.inl hGuard
    · by_cases hSelected : AllSelected assignment guards
      · cases hCompact : compact pair with
        | none => exact Bool.noConfusion (hValue.symm.trans (hDropped hSelected pair hmem edge hVar hCompact))
        | some kept =>
          have hMatch : kept = edge := Option.some.inj ((hKept pair hmem kept hCompact).symm.trans hVar)
          exact Or.inr ⟨pair, hmem, kept, hCompact, hMatch.symm ▸ hValue⟩
      · exact Or.inl (by simpa [AllSelected, Bool.not_eq_true] using hSelected)

/-- An actual channel clause can discharge a deletion, without assuming a
graph decoding for the assignment. Each such clause uses only the guard(s)
for its own endpoint pair, which must occur in the outer witness row. -/
theorem compact_iff_full_of_channels (assignment : Var → Bool) (guards : List Var)
    (pairs : List (Site × Site)) (full compact : Site × Site → Option Var)
    (hKept : ∀ pair ∈ pairs, ∀ edge, compact pair = some edge → full pair = some edge)
    (hChannels : ∀ pair ∈ pairs, ∀ edge, full pair = some edge → compact pair = none →
      ∃ localGuards : List Var, (∀ guard ∈ localGuards, guard ∈ guards) ∧
        Holds assignment (localGuards.map (fun guard => (guard, false)) ++ [(edge, false)])) :
    Holds assignment (row guards pairs compact) ↔ Holds assignment (row guards pairs full) := by
  refine compact_iff_full assignment guards pairs full compact hKept ?_
  intro hSelected pair hPair edge hFull hCompact
  obtain ⟨localGuards, hLocal, literal, hMem, hValue⟩ := hChannels pair hPair edge hFull hCompact
  rcases List.mem_append.mp hMem with hGuard | hEdge
  · obtain ⟨guard, hGuardMem, rfl⟩ := List.mem_map.mp hGuard
    exact Bool.noConfusion ((hSelected guard (hLocal guard hGuardMem)).symm.trans hValue)
  · rw [List.mem_singleton] at hEdge
    simpa [hEdge] using hValue

/-- An asymmetric channel clash can remove a full-row literal if the shared
anchor is a real contact and the literal faithfully represents physical edges
under the selected guards. -/
theorem edge_false_of_shared_anchor (Graph : SimpleGraph Vertex) (hTriangle : Graph.CliqueFree 3)
    (assignment : Var → Bool) {edge : Var} {first second anchor : Vertex}
    (hFirstContact : Graph.Adj first anchor) (hSecondContact : Graph.Adj second anchor)
    (hProjected : assignment edge = true → Graph.Adj first second) :
    assignment edge = false := by
  have hNot : assignment edge ≠ true := by
    intro hTrue
    have hAdj := hProjected hTrue
    exact (Graph.isIndepSet_neighborSet_of_triangleFree hTriangle anchor)
      hFirstContact.symm hSecondContact.symm hAdj.ne hAdj
  simpa [Bool.not_eq_true] using hNot

end SelectedWitness

end R310
