# Round 10 — reciprocal windows, integer incidence, and ledger

No verified graph, distribution subtraction, or new literature premise.
The critic's round-009 cutoff is **278 near-regular MTF distributions
plus Case R**, ten conditional U88 keys, and twenty open e168 degree-six
distributions. `ralph/CLAIMS.md` imports the confirmed scopes and marks
round-010 work pending. Scout T and the referee had no round-009 report.

## Lean interfaces

- `R310.ReciprocalWindow`: degrees in the induced subgraphs are proved
  equal to the cardinalities of the intersections of the full neighbour
  set with the three windows. If the union of two windows covers the
  full neighbour set, set inclusion–exclusion gives
  `d_left(z)+d_right(z)=d_G(z)+d_overlap(z)`. Coverage is essential;
  membership of `z` in both windows alone does not imply it. For two
  nonempty completely joined root sets in a triangle-free graph, the
  windows cover exactly the nonroots, and a common-window vertex does
  not see any root. The specialization gives order ten for either
  independent pair of degree-six roots at codegree two and order two
  for their overlap under the square's cross edges. It also gives the
  opposite degree `6+d_overlap−d_left`.
- `R310.RoundedIncidence`: double-counts a decidable incidence matrix on
  22 rows and four columns of size six; the five fibres give
  `S+2q=20+U+2V`. Weighted capacity rows imply
  `scale*S ≤ weightedBound` given column-wise coverage of all selected
  masks. A positive scale permits flooring. Thresholds 20 and 21 on
  `S+2q` give no triples/quadruples and at most one triple/no quadruples,
  respectively. The `q=1, 3S≤56` specialization also covers RHS 55 and
  forces 18 singleton and three double rows.

The Lean results do **not** prove the geometric C boundary cover,
individual capacity witnesses, source completeness, or any SAT/enum
verdict. The generic weighted lemma assumes input row bounds and
pointwise marginal coverage; it does not trust LP floats. Stating
thresholds on `S+2q` avoids natural truncated subtraction.

The independent control extracts all ten 6-regular graphs from the
191-class order-22 file, checks triangle-freeness and alpha six, then
counts **334** equal and **395** asymmetric planted marks. It checks
1,853 shared-vertex degrees and 4,978 adverse deletions of a covered
neighbour from one window. The incidence control exhausts 50,625
smaller matrices (six rows, four columns of size two), including exact
thresholds and larger excess, and distinguishes a positive integer
witness from a deliberately insufficient coefficient column. See
`check_round10_controls.py` and `scratch/H/round10-controls.log`.

## Evidence scopes and dependency checks

- A-015 is the cover used by G-033 (noncross d8 j=3, δ(T)=3). G-032 is
  the separate noncross d9 j=5 with no δ restriction. These are **two**
  mixed exclusions, not three, and neither closes the e168 distribution.
  For older c1 receipts do not interchange the 32 distinct eager vs
  non-eager CNF hashes (A-016).
- D-017 → D-018 → D-019: first global L=6, then global L=7, then the
  cyclic-only consequence of assuming no induced P8. Some kernel has
  induced P8 in R(3), not all kernels; C6/C8 can still occur. No general
  Section 7 cert. E-024 is one conditional core under E-021 and δ(G)≥5;
  F-012 is the weighted unsigned quotient only, with signs unrestricted.
- N-001 supplied 61 class keys; B-023 is the later scoped extension
  replay on those keys. Independently checked the 57/4 ID partition,
  all four residual graph6 rows and stored proof hashes. R-001's complete
  cap-six 22/22 marked scope does not extend to R-002's sampled 22/21
  source. Neither a successful sample nor a key match is an exclusion.
- For the round-10 mixed d9 j=4, δ(T)=3 claim G-034, the full ordered
  215 source rows including graph6 are equal in A and G. All 215 IDs
  match checked receipts and all compressed trace lengths/hashes agree;
  H did not regenerate the formulas or run either checker. See
  `check_round10_receipts.py` and `scratch/H/round10-receipts.log`.

Best finite path to distribution-level impact is the e108 work: after
the import B reports five additional e98-lift keys and six repuncture
keys, each with scoped checks (B-024, pending), leaving 52 absent. The
122 untested e98 deck keys are parents, not target classes. Even full
class supply needs scoped extension coverage. The marked e168 windows have the strongest current repeated
cover-plus-proof evidence, but each targets a narrow mark. The induced-P8
and asymmetric reciprocal routes should be priced against their actual
sources and aligned maps; neither establishes a new general exclusion.
