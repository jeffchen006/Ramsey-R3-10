# Round 18: marked aligned `middle+middle.2`

## Scope and physical census

This is the marked **e170 adjacent degree-six equality pair**, with
coincident double sites (`h=8`) and left holes `L0L3,L0L4`, right holes
`R0R1,R0R2`. The local reduction is in `rows/e170_aligned_grid.md` and
the action and proof transport are justified in
`rows/e170_middle_2_stabilizer.md`. No claim about `h<8`, any other hole
scheme, an e170 distribution, the residue floor, `t9` or U88 follows.

- A set-of-literal-anchors forward enumeration and the inherited
  inverse roster agree in exact sorted order on all **16,350** IDs.
  The eight stabilizer actions preserve crossing, holes, grid, and
  paired doubles. Their full orbit counts by size are 7 (two), 130
  (four), and 1,977 (eight). The nonidentity fixed-point counts are
  256, 256, 50, and four zeros; the resulting Burnside count is 2,114.
- The calibration rebuilt both complete smaller canonical sets,
  agreeing class for class with the earlier sets: **24** at order 15
  and **0** at order 16, including 26 physically marked order-15 root
  pairs and their 104 action images. The asymmetric transpose control
  moves both halves of a double mask.
- The exact previously covered set of **660** was reconstructed from
  eight applicable scout receipts, rebound against both LRAT checkers.
  None of the round-16 transfer supports hit this scheme. The six
  round-17 direct receipts each generate an eight-element orbit and
  their 48 distinct labelled images include **42** new transports.
  The resulting queue was **2,024** representative IDs of total weight
  **15,642**: 7/127/1,890 by orbit size two/four/eight. No other scheme
  was processed. See `ROUND18_PREREG.md` for the price before launch.

## Result

**Hand + enum + cert (local, pending critic).** All 2,024 new ordinary
LRATs pass both checkers after unpacking, in both the checkpoint replay
and a clean run. The latter explicitly checked **2,928,046** transported
independent-ten witness blocks, in addition to the inherited receipt
audit. All **16,350/16,350** labelled IDs reconcile to one named proof
and oriented move, with zero open or staged-only IDs. This excludes
`middle+middle.2` in the stated marked slice only. Accounting against
G-053: subtract **15,684** (42 inherited transports and 15,642 covered by
new certificates), leaving **140,062** untested labelled IDs in 28 other
aligned schemes. The six round-17 direct IDs were already counted.

Production through first replay and reconciliation used 274.73 CPU-s;
the clean run took another 144.66 CPU-s. End to end: **419.39 CPU-s
(0.11650 core-h)**, about **94 MiB additional scratch** and peak
reported RSS 102,580 KiB including compilation. The 2,024 receipts hold
255,368,722 ordinary bytes compressed to 85,713,624 bytes. The largest
combined raw and packed staging charge was 966,656 bytes. There were no
local models or solver caps; the first sample replay's allocation
metadata issue, fixed before production, is included in the CPU total.
No jobs remain.

## Reproduction

From the workspace root, with a fresh replay directory under the
reviewer's own `scratch/`:

```bash
sha256sum -c --quiet ralph/lanes/G/ROUND18_FREEZE.sha256
sha256sum -c --quiet scratch/G/round18/dependencies.sha256
(cd scratch/G/round18 && sha256sum -c --quiet receipts.sha256)
bash ralph/lanes/G/round18_review.sh scratch/G/round18-clean-second
```

The replay runs no proof search. It regenerates the small controls and
the orbit/price sample manifests in its own directory, unpacks one
receipt at a time, checks all three byte hashes, recomputes the complete
ordinary CNF clause multiset (including every literal witness), and
requires exact successful lines from both LRAT checkers. It then moves
every retained witness block along each credited new oriented image,
verifying physical incidence and the wing crossing at the destination.
The independent owner map must match `reconciliation.json` for every
original labelled ID; no credit is based on an UNSAT exit status alone.
