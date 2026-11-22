# Round 19 — private-cell matching and ledger

## H-034: Lean, pending critic review

`lean/R310/PrivateGrid.lean` implements the algebraic step of scout N's
one-defect restriction. The input matching is a finite set of **physical
sites** with an injective partner map into the noncross opposite anchors.
For matched sites that are singleton-supported on the opposite shore,
the partner must equal that site's unique opposite anchor. The image of
the matched singletons is therefore contained in the set of distinct
occupied noncross columns; injectivity bounds that part by `t`. All
other matched sites form a subset of the cell minus its singleton sites,
of size `4-s`. Thus the capacity bound is `matched ≤ t + (4-s)`.
This representation allows repeated physical cells, but not repeated use
of a physical site. The capacity lemma is valid for any cell size.

Specializing to a cell of four and a matching of size `≥ 3 + [i=0]`
gives `s−t ≤ 1−[i=0]`, where `s` counts all singleton/singleton sites of
the row, including those in the crossed column. The column theorem
applies the same row theorem after exchanging the two maps and crossed
anchors. The cell size, support compatibility, and matching lower
bound are explicit premises (for the graph application see G's
`rows/signature_matchings.md` and `rows/e170_equality_signatures.md`).
No MTF, triangle-free or codegree premise is needed for this counting
implication; the graph reductions supplying those premises are not
formalized here. No board/orbit count, SAT binding, or case exclusion.

The literal control exhausts 216 ordered three-site support arrays on
two noncross anchors and one crossed anchor, checking every partial
matching. The smaller tight example has singles at 1 and 0 and a
double at `{1,2}`, yielding `(s,t,max)=(2,1,2)`. A repeated-cell
offcross row has `(3,2,3)` and the crossed column has `(3,3,4)`, with
transpose recovering the same column instance. In the adverse row,
the three singles share one column and the double has two other
noncross anchors. True maximum 2; an anchor-only test reports three
size-three witnesses, each reusing the same double site twice.

Replay from the root (pre-fetched Mathlib binary cache; no source rebuild):

```sh
bash ralph/lanes/H/build_private_signature.sh --old build R310
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 -DElab.async=false ../ralph/lanes/H/AxiomsRound19.lean
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 -DElab.async=false scripts/Axioms.lean
python3 -SB ralph/lanes/H/check_private_grid.py
sha256sum -c ralph/lanes/H/ROUND19.sha256
```

Pinned Lean and Mathlib 4.35.0. The integrated build and strict checks
pass for 3 targeted and 356 project reports, with only standard axioms.
Total timed CPU 144.12 s (0.04003 core-h, including the development
probes), peak RSS 3,451,348 KiB. The historical round-18 root import and
axiom scripts are available at the round-18 flow revision; the new
freeze covers their changed round-19 bytes.

## Round 18 import

`ralph/critic/round_018.md` controls the accepted ledger. A-030 binds
physical old-margin IDs. C-044's 70 local failures include one old ID:
`2,542,514,492 − 47 − 69 = 2,542,514,376` not explicitly joint-tested.
R-006 separately vetoes 56 disjoint order-13 headers by structure,
leaving `2,542,514,320` neither joint-tested nor vetoed. The order-12
held-out bin is a new experiment, not an extension of that receipt.

G-054 closes the named `middle+middle.2` scheme with 15,684 incremental
labels, leaving `140,062` in 28 schemes. N-008 removes 60,990 disjoint
IDs against that historical roster, to `79,072` in 12 schemes. N-009
has `51/1,213` two-sided contexts at `h=7`, not 51 of the 81 sufficient
fixed-left contexts. Keep these denominators separate. G's round-19
middle test potentially intersects 57,947 of the 79,072, not yet a debit
in the accepted ledger.

D-045's 162 support types are necessary conditions for `m=15`, not
realized wings or an exclusion. E-042 has exactly 16 checked pilot IDs
on two routes, not 32 or a core closure. F-035 prices an unsigned
relaxation, not physical signing. H-033 is a scoped Lean implication.
B stays parked: floor 108, five criticals absent. No referee report or
T report in round 18; no independent GAP verdict. Accepted balance:
238 near-regular MTF distributions plus R, ten conditional U88 keys,
four mixed cores, no flow-verified candidate. G's one-receipt many-ID
transport is the strongest measured cost reduction, scoped to the
marked branch. No fresh literature screen per directive; `LIT.md`
retains the prior dated search rather than a new status claim.
