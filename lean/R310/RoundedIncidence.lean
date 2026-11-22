import R310.Basic

namespace R310

open Finset

variable {Row Column : Type*}

/-- Number of selected columns incident to a row. -/
def incidenceCount (columns : Finset Column) (incident : Row → Column → Prop)
    [DecidableRel incident] (row : Row) : ℕ := #(columns.filter (incident row))

/-- Number of rows of a given incidence multiplicity. -/
def incidenceFiber (rows : Finset Row) (multiplicity : Row → ℕ) (count : ℕ) : ℕ :=
  #(rows.filter fun row => multiplicity row = count)

theorem incidence_sum_comm (rows : Finset Row) (columns : Finset Column)
    (incident : Row → Column → Prop) [DecidableRel incident] :
    (∑ row ∈ rows, incidenceCount columns incident row) =
      ∑ column ∈ columns, #(rows.filter fun row => incident row column) := by
  simp only [incidenceCount, card_filter]
  exact sum_comm

theorem incidence_histogram (rows : Finset Row) (multiplicity : Row → ℕ) (weight : ℕ → ℕ)
    (hBound : ∀ row ∈ rows, multiplicity row ≤ 4) :
    (∑ row ∈ rows, weight (multiplicity row)) =
      weight 0 * incidenceFiber rows multiplicity 0 + weight 1 * incidenceFiber rows multiplicity 1 +
      weight 2 * incidenceFiber rows multiplicity 2 + weight 3 * incidenceFiber rows multiplicity 3 +
      weight 4 * incidenceFiber rows multiplicity 4 := by
  have hMaps : ∀ row ∈ rows, multiplicity row ∈ range 5 := by
    intro row hRow
    exact mem_range.mpr (Nat.lt_succ_of_le (hBound row hRow))
  rw [← sum_fiberwise_of_maps_to' hMaps weight]
  have hFib (count : ℕ) : (∑ _row ∈ rows.filter (fun row => multiplicity row = count),
      weight count) = weight count * incidenceFiber rows multiplicity count := by
    rw [sum_const, smul_eq_mul, mul_comm]
    rfl
  simp only [hFib, sum_range_succ, sum_range_zero, zero_add]

/-- The 22-row, four-column diagonal-four identity, with six incidences in each column. -/
theorem p3_incidence_identity (rows : Finset Row) (columns : Finset Column)
    (incident : Row → Column → Prop) [DecidableRel incident] (hRows : #rows = 22)
    (hCols : #columns = 4) (hColDegree : ∀ column ∈ columns,
      #(rows.filter fun row => incident row column) = 6) :
    let freq := incidenceFiber rows (incidenceCount columns incident)
    freq 1 + 2 * freq 0 = 20 + freq 3 + 2 * freq 4 := by
  dsimp only
  have hBound : ∀ row ∈ rows, incidenceCount columns incident row ≤ 4 := by
    intro row _
    exact hCols ▸ card_filter_le _ _
  have hRaw := incidence_sum_comm rows columns incident
  have hTotal : (∑ column ∈ columns, #(rows.filter fun row => incident row column)) = 24 := by
    calc
      _ = ∑ _column ∈ columns, (6 : ℕ) := sum_congr rfl hColDegree
      _ = 24 := by simp [hCols]
  rw [hTotal] at hRaw
  have hCount := incidence_histogram rows (incidenceCount columns incident) (fun _ => 1) hBound
  have hWeight := incidence_histogram rows (incidenceCount columns incident) id hBound
  simp only [sum_const, smul_eq_mul, hRows, Nat.mul_one, one_mul] at hCount
  simp only [id_eq, hRaw, zero_mul, zero_add, one_mul] at hWeight
  omega

/-- Sum the integral capacity witnesses. Coverage is checked on each mask, not on an LP optimum. -/
theorem rounded_capacity_le {Constraint Mask : Type*} (constraints : Finset Constraint)
    (masks : Finset Mask) (coefficient : Constraint → Mask → ℕ) (bound weight : Constraint → ℕ)
    (multiplicity : Mask → ℕ) (selected : Mask → Prop) [DecidablePred selected] {scale : ℕ}
    (hRows : ∀ constraint ∈ constraints,
      (∑ mask ∈ masks, coefficient constraint mask * multiplicity mask) ≤ bound constraint)
    (hCovers : ∀ mask ∈ masks, selected mask →
      scale ≤ ∑ constraint ∈ constraints, weight constraint * coefficient constraint mask) :
    scale * (∑ mask ∈ masks.filter selected, multiplicity mask) ≤
      ∑ constraint ∈ constraints, weight constraint * bound constraint := by
  calc
    _ = ∑ mask ∈ masks, if selected mask then scale * multiplicity mask else 0 := by
      rw [mul_sum, sum_filter]
    _ ≤ ∑ mask ∈ masks,
        (∑ constraint ∈ constraints, weight constraint * coefficient constraint mask) *
          multiplicity mask := by
      refine sum_le_sum fun mask hMask => ?_
      split_ifs with hSelected
      · exact Nat.mul_le_mul_right _ (hCovers mask hMask hSelected)
      · exact Nat.zero_le _
    _ = ∑ constraint ∈ constraints, weight constraint *
        (∑ mask ∈ masks, coefficient constraint mask * multiplicity mask) := by
      simp only [sum_mul, mul_sum, mul_assoc]
      exact sum_comm
    _ ≤ _ := sum_le_sum fun constraint hConstraint =>
        Nat.mul_le_mul_left _ (hRows constraint hConstraint)

/-- Division rounds down the integer witness, with positivity of its scale explicit. -/
theorem rounded_capacity_floor {scale singles weightedBound : ℕ} (hScale : 0 < scale)
    (hWitness : scale * singles ≤ weightedBound) : singles ≤ weightedBound / scale := by
  apply (Nat.le_div_iff_mul_le hScale).mpr
  rwa [Nat.mul_comm]

/-- State the implications without relying on truncated natural subtraction at large `zeroes`. -/
theorem p3_incidence_rounding {zeroes singles triples quadruples : ℕ}
    (hIdentity : singles + 2 * zeroes = 20 + triples + 2 * quadruples) :
    20 ≤ singles + 2 * zeroes ∧
      (singles + 2 * zeroes ≤ 20 → triples = 0 ∧ quadruples = 0) ∧
      (singles + 2 * zeroes ≤ 21 → triples ≤ 1 ∧ quadruples = 0) := by
  omega

/-- Exact integer floor of the two q=1 witnesses with scaled RHS 56 and 55. -/
theorem p3_one_zero_tight {singles doubles triples quadruples : ℕ}
    (hCount : 1 + singles + doubles + triples + quadruples = 22)
    (hIdentity : singles + 2 = 20 + triples + 2 * quadruples)
    (hWitness : 3 * singles ≤ 56) :
    singles = 18 ∧ doubles = 3 ∧ triples = 0 ∧ quadruples = 0 := by
  omega

end R310
