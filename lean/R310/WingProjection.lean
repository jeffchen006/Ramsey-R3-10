import Mathlib.Combinatorics.SimpleGraph.Finite

namespace R310

open Finset
open scoped Finset

variable {Vertex : Type*} [DecidableEq Vertex]
variable (graph : SimpleGraph Vertex) [DecidableRel graph.Adj]

/-- The common neighbors of a pair among physical sites in the given set. -/
def wingCommon (sites : Finset Vertex) (first second : Vertex) : Finset Vertex :=
  sites.filter fun site => graph.Adj first site ∧ graph.Adj second site

theorem wing_common_partition {kept hidden : Finset Vertex} (first second : Vertex)
    (hDisjoint : Disjoint kept hidden) :
    #(wingCommon graph (kept ∪ hidden) first second) =
      #(wingCommon graph kept first second) + #(wingCommon graph hidden first second) := by
  unfold wingCommon
  rw [filter_union, card_union_of_disjoint]
  exact hDisjoint.mono (filter_subset _ _) (filter_subset _ _)

/-- A lost-neighbor allowance weakens the lower bound; it is not subtracted
from the upper bound on visible common neighbors. -/
theorem wing_visible_common_bounds {kept hidden : Finset Vertex} {first second : Vertex}
    {lower upper allowance : ℕ} (hDisjoint : Disjoint kept hidden)
    (hLower : lower ≤ #(wingCommon graph (kept ∪ hidden) first second))
    (hUpper : #(wingCommon graph (kept ∪ hidden) first second) ≤ upper)
    (hHidden : #(hidden.filter (graph.Adj first)) ≤ allowance) :
    lower - allowance ≤ #(wingCommon graph kept first second) ∧
      #(wingCommon graph kept first second) ≤ upper := by
  have hCount := wing_common_partition graph first second hDisjoint
  have hSub : wingCommon graph hidden first second ⊆ hidden.filter (graph.Adj first) := by
    intro site hSite
    have hInfo := mem_filter.mp hSite
    exact mem_filter.mpr ⟨hInfo.1, hInfo.2.1⟩
  have hAllowance := (card_le_card hSub).trans hHidden
  omega

/-- If the cycle has no hidden wing neighbors after retaining the unique flap
endpoint, no common-neighbor term involving a cycle site is lost. This applies
also when the other selected site is the flap endpoint. -/
theorem wing_cycle_common_exact {kept hidden cycle : Finset Vertex} {first second : Vertex}
    (hDisjoint : Disjoint kept hidden) (hFirst : first ∈ cycle)
    (hNoHidden : ∀ site ∈ cycle, ∀ other ∈ hidden, ¬graph.Adj site other) :
    #(wingCommon graph (kept ∪ hidden) first second) =
      #(wingCommon graph kept first second) := by
  have hEmpty : wingCommon graph hidden first second = ∅ := by
    apply eq_empty_iff_forall_notMem.mpr
    intro site hSite
    have hInfo := mem_filter.mp hSite
    exact hNoHidden first hFirst site hInfo.1 hInfo.2.1
  rw [wing_common_partition graph first second hDisjoint, hEmpty, card_empty, Nat.add_zero]

omit [DecidableRel graph.Adj] in
/-- Retaining the unique off-cycle flap endpoint removes all hidden neighbors
of cycle sites; the empty-flap case is included. -/
theorem wing_one_flap_retained {cycle wing : Finset Vertex} {endpoint : Vertex}
    (hFlap : ∀ site ∈ cycle, ∀ other ∈ wing \ cycle,
      graph.Adj site other → other = endpoint) :
    ∀ site ∈ cycle, ∀ other ∈ wing \ (insert endpoint cycle), ¬graph.Adj site other := by
  intro site hSite other hOther hAdj
  obtain ⟨hWing, hOutside⟩ := mem_sdiff.mp hOther
  have hNoCycle : other ∉ cycle := fun h => hOutside (mem_insert_of_mem h)
  have hEndpoint := hFlap site hSite other (mem_sdiff.mpr ⟨hWing, hNoCycle⟩) hAdj
  exact hOutside (mem_insert.mpr (Or.inl hEndpoint))

end R310
