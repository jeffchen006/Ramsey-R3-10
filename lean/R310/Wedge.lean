/-
Degree-typed wedge identity, in directed-pair form. For distinct degree classes
each unordered pair has exactly one orientation in the indicated product. In a
single class both orientations are counted (hence h(h-1) rather than choose h 2).
-/
import R310.Basic

open Finset SimpleGraph
open scoped BigOperators

namespace R310

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

/-- A weighted codegree identity, including the diagonal pair contributions. -/
theorem weighted_sum_codegrees (left right : Finset V) :
    ∑ first ∈ left, ∑ second ∈ right, #(G.neighborFinset first ∩ G.neighborFinset second) =
    ∑ center, #(left ∩ G.neighborFinset center) * #(right ∩ G.neighborFinset center) := by
  let inc : V → V → ℕ := fun endpoint center => if G.Adj endpoint center then 1 else 0
  have hcodeg (first second : V) :
      #(G.neighborFinset first ∩ G.neighborFinset second) =
        ∑ center, inc first center * inc second center := by
    rw [show G.neighborFinset first ∩ G.neighborFinset second =
        univ.filter (fun center => G.Adj first center ∧ G.Adj second center) by
      ext center; simp]
    simp only [card_filter, inc]
    refine sum_congr rfl fun center _ => ?_
    by_cases hfirst : G.Adj first center <;> by_cases hsecond : G.Adj second center <;>
      simp [inc, hfirst, hsecond]
  have hdegree (endpoints : Finset V) (center : V) :
      #(endpoints ∩ G.neighborFinset center) = ∑ last ∈ endpoints, inc last center := by
    rw [show endpoints ∩ G.neighborFinset center = endpoints.filter (fun last => G.Adj last center) by
      ext last; simp [G.adj_comm]]
    rw [card_filter]
  simp_rw [hcodeg, hdegree, sum_mul_sum]
  calc ∑ first ∈ left, ∑ second ∈ right, ∑ center, inc first center * inc second center =
        ∑ first ∈ left, ∑ center, ∑ second ∈ right, inc first center * inc second center :=
          sum_congr rfl fun first _ => sum_comm
    _ = ∑ center, ∑ first ∈ left, ∑ second ∈ right, inc first center * inc second center := sum_comm

/-- For disjoint classes in a triangle-free graph, only nonedges contribute to the codegree sum. -/
theorem sum_codegrees_between_classes (h3 : G.CliqueFree 3)
    (left right : Finset V) (hdisj : Disjoint left right) :
    ∑ first ∈ left, ∑ second ∈ right.filter (fun second => first ≠ second ∧ ¬ G.Adj first second),
      #(G.neighborFinset first ∩ G.neighborFinset second) =
    ∑ center, #(left ∩ G.neighborFinset center) * #(right ∩ G.neighborFinset center) := by
  rw [← weighted_sum_codegrees left right]
  refine sum_congr rfl fun first hfirst => ?_
  rw [sum_filter]
  refine sum_congr rfl fun second hsecond => ?_
  have hne : first ≠ second := fun eq =>
    Finset.disjoint_left.1 hdisj hfirst (by simpa only [eq] using hsecond)
  by_cases hedge : G.Adj first second
  · have hempty : G.neighborFinset first ∩ G.neighborFinset second = ∅ := by
      apply eq_empty_iff_forall_notMem.2
      intro third hthird
      obtain ⟨hfirstThird, hsecondThird⟩ := mem_inter.1 hthird
      exact h3 {first, second, third} (is3Clique_triple_iff.2
        ⟨hedge, mem_neighborFinset.1 hfirstThird, mem_neighborFinset.1 hsecondThird⟩)
    simp [hempty]
  · simp [hne, hedge]

/-- Within one class, the diagonal of the codegree sum consists exactly of the degrees.
Dropping it leaves both orientations of every nonedge. -/
theorem sum_codegrees_within_class (h3 : G.CliqueFree 3) (vertices : Finset V) :
    (∑ first ∈ vertices,
      ∑ second ∈ vertices.filter (fun second => first ≠ second ∧ ¬ G.Adj first second),
        #(G.neighborFinset first ∩ G.neighborFinset second)) +
      (∑ first ∈ vertices, G.degree first) =
    ∑ center, #(vertices ∩ G.neighborFinset center) ^ 2 := by
  simp only [sq, ← weighted_sum_codegrees vertices vertices, ← sum_add_distrib]
  refine sum_congr rfl fun first hfirst => ?_
  let codeg := fun second => #(G.neighborFinset first ∩ G.neighborFinset second)
  have hcount : ∑ second ∈ vertices.filter (fun second => first ≠ second ∧ ¬ G.Adj first second),
      codeg second = ∑ second ∈ vertices.erase first, codeg second := by
    rw [show vertices.erase first = vertices.filter (fun second => first ≠ second) by
      ext second; simp [ne_comm]]
    rw [sum_filter, sum_filter]
    refine sum_congr rfl fun second _ => ?_
    by_cases hedge : G.Adj first second
    · have hempty : G.neighborFinset first ∩ G.neighborFinset second = ∅ := by
        apply eq_empty_iff_forall_notMem.2
        intro third hthird
        obtain ⟨hfirstThird, hsecondThird⟩ := mem_inter.1 hthird
        exact h3 {first, second, third} (is3Clique_triple_iff.2
          ⟨hedge, mem_neighborFinset.1 hfirstThird, mem_neighborFinset.1 hsecondThird⟩)
      simp [hedge, codeg, hempty]
    · simp [hedge]
  change (∑ second ∈ vertices.filter (fun second => first ≠ second ∧ ¬ G.Adj first second),
    codeg second) + G.degree first = ∑ second ∈ vertices, codeg second
  rw [hcount, ← sum_erase_add _ codeg hfirst]
  simp [codeg]

end R310
