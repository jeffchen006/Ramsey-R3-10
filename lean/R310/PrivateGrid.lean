import Mathlib.Data.Finset.Card
import Mathlib.Data.Finset.Image

open Finset

namespace R310

variable {Site Row Column : Type*} [DecidableEq Site] [DecidableEq Row] [DecidableEq Column]

/-- Bound the size of a site-to-anchor matching by the distinct noncross columns of
the singleton-supported sites plus the number of remaining physical sites. -/
theorem private_cell_matching_capacity
    {cell singles matched : Finset Site} {uniqueAnchor partner : Site → Column}
    {crossColumn : Column}
    (hSingles : singles ⊆ cell) (hMatched : matched ⊆ cell)
    (hDistinct : Set.InjOn partner (matched : Set Site))
    (hNoncross : ∀ site ∈ matched, partner site ≠ crossColumn)
    (hSinglePartner : ∀ site ∈ matched, site ∈ singles → partner site = uniqueAnchor site) :
    #matched ≤ #((singles.image uniqueAnchor).erase crossColumn) + (#cell - #singles) := by
  have hImage : (matched ∩ singles).image partner ⊆ (singles.image uniqueAnchor).erase crossColumn := by
    intro anchor hAnchor
    obtain ⟨site, hSite, rfl⟩ := mem_image.mp hAnchor
    obtain ⟨hInMatched, hInSingles⟩ := mem_inter.mp hSite
    exact mem_erase.mpr ⟨hNoncross site hInMatched,
      mem_image.mpr ⟨site, hInSingles, (hSinglePartner site hInMatched hInSingles).symm⟩⟩
  have hImageCount := card_le_card hImage
  rw [card_image_of_injOn (hDistinct.mono (fun _ hSite => (mem_inter.mp hSite).1))]
    at hImageCount
  have hRemainder : matched \ (matched ∩ singles) ⊆ cell \ singles := by
    intro site hSite
    obtain ⟨hInMatched, hOutInter⟩ := mem_sdiff.mp hSite
    exact mem_sdiff.mpr ⟨hMatched hInMatched, fun hInSingles =>
      hOutInter (mem_inter.mpr ⟨hInMatched, hInSingles⟩)⟩
  have hMatchedSplit := card_sdiff_add_card_eq_card
    (inter_subset_left : matched ∩ singles ⊆ matched)
  have hRemainderCount := card_le_card hRemainder
  rw [card_sdiff_of_subset hSingles] at hRemainderCount
  omega

/-- A row margin counts physical sites; its occupancy counts distinct noncross columns.
The lower matching bound is a premise, to be supplied by the graph reduction. -/
theorem private_grid_row_bound
    {gridSites cell matched : Finset Site} {rowOf : Site → Row} {columnOf partner : Site → Column}
    {row crossRow : Row} {crossColumn : Column}
    (hSingles : (gridSites.filter fun site => rowOf site = row) ⊆ cell)
    (hCellCount : #cell = 4) (hMatched : matched ⊆ cell)
    (hDistinct : Set.InjOn partner (matched : Set Site))
    (hNoncross : ∀ site ∈ matched, partner site ≠ crossColumn)
    (hSinglePartner : ∀ site ∈ matched, site ∈ gridSites → rowOf site = row →
      partner site = columnOf site)
    (hLower : 3 + (if row = crossRow then 1 else 0) ≤ #matched) :
    #(gridSites.filter fun site => rowOf site = row) -
        #(((gridSites.filter fun site => rowOf site = row).image columnOf).erase crossColumn) ≤
      1 - (if row = crossRow then 1 else 0) := by
  have hCapacity := private_cell_matching_capacity hSingles hMatched hDistinct hNoncross
    (fun site hMatch hSolo => hSinglePartner site hMatch (mem_filter.mp hSolo).1 (mem_filter.mp hSolo).2)
  have hSoloCard := card_le_card hSingles
  by_cases hCross : row = crossRow
  · rw [ite_eq_left hCross] at hLower ⊢
    omega
  · rw [ite_eq_right hCross] at hLower ⊢
    omega

/-- The column bound is the row bound with the two anchor maps transposed. -/
theorem private_grid_column_bound
    {gridSites cell matched : Finset Site} {columnOf : Site → Column} {rowOf partner : Site → Row}
    {column crossColumn : Column} {crossRow : Row}
    (hSingles : (gridSites.filter fun site => columnOf site = column) ⊆ cell)
    (hCellCount : #cell = 4) (hMatched : matched ⊆ cell)
    (hDistinct : Set.InjOn partner (matched : Set Site))
    (hNoncross : ∀ site ∈ matched, partner site ≠ crossRow)
    (hSinglePartner : ∀ site ∈ matched, site ∈ gridSites → columnOf site = column →
      partner site = rowOf site)
    (hLower : 3 + (if column = crossColumn then 1 else 0) ≤ #matched) :
    #(gridSites.filter fun site => columnOf site = column) -
        #(((gridSites.filter fun site => columnOf site = column).image rowOf).erase crossRow) ≤
      1 - (if column = crossColumn then 1 else 0) :=
  private_grid_row_bound hSingles hCellCount hMatched hDistinct hNoncross hSinglePartner hLower

end R310
