import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Combinatorics.SimpleGraph.Finite

namespace R310

open Finset SimpleGraph
open scoped BigOperators

/-- Lower bounds for incidences into disjoint physical groups add, but only after
removing every prescribed incidence. The minima need not be jointly attained. -/
theorem disjoint_added_incidence_budget {Index Vertex : Type*} [DecidableEq Vertex]
    {indices : Finset Index} {actual prescribed : Finset Vertex}
    (group : Index → Finset Vertex) (minimum : Index → ℕ)
    (hPrescribed : prescribed ⊆ actual)
    (hDisjoint : (indices : Set Index).PairwiseDisjoint group)
    (hMinimum : ∀ index ∈ indices, minimum index ≤ #((actual \ prescribed) ∩ group index)) :
    (∑ index ∈ indices, minimum index) ≤ #actual - #prescribed := by
  let added (index : Index) := (actual \ prescribed) ∩ group index
  have hAddedDisjoint : (indices : Set Index).PairwiseDisjoint added := by
    intro first hFirst second hSecond hNe
    exact (hDisjoint hFirst hSecond hNe).mono inter_subset_right inter_subset_right
  have hUnion : indices.biUnion added ⊆ actual \ prescribed := by
    intro vertex hVertex
    obtain ⟨index, _, hAdded⟩ := mem_biUnion.mp hVertex
    exact (mem_inter.mp hAdded).1
  have hCount : #(actual \ prescribed) = #actual - #prescribed := by
    have := card_sdiff_add_card_eq_card hPrescribed
    omega
  calc
    (∑ index ∈ indices, minimum index) ≤ ∑ index ∈ indices, #(added index) := sum_le_sum hMinimum
    _ = #(indices.biUnion added) := (card_biUnion hAddedDisjoint).symm
    _ ≤ #(actual \ prescribed) := card_le_card hUnion
    _ = #actual - #prescribed := hCount

/-- Graph version for one fixed core vertex. The card projections supply the
valid lower bounds on that physical vertex's added incidences. -/
theorem shared_core_degree_budget {Index Vertex : Type*} [Fintype Vertex] [DecidableEq Vertex]
    (Graph : SimpleGraph Vertex) [DecidableRel Graph.Adj] (site : Vertex)
    {indices : Finset Index} {prescribed : Finset Vertex}
    (group : Index → Finset Vertex) (minimum : Index → ℕ)
    (hPrescribed : prescribed ⊆ Graph.neighborFinset site)
    (hDisjoint : (indices : Set Index).PairwiseDisjoint group)
    (hMinimum : ∀ index ∈ indices,
      minimum index ≤ #((Graph.neighborFinset site \ prescribed) ∩ group index)) :
    (∑ index ∈ indices, minimum index) ≤ Graph.degree site - #prescribed := by
  exact disjoint_added_incidence_budget group minimum hPrescribed hDisjoint hMinimum

end R310
