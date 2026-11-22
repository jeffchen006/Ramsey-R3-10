# Round 23 — necessary two-window overlap for E's saturated crown

**Scope:** `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=8`, `P=0`, with
the saturated fixed degrees and crown assumptions of E-018. Neither
Case R nor an involution type, degree distribution, or the whole
`e(W)=8` branch is closed. No candidate graph.

## Hand results, pending review

- **C-055.** In each physical two-window join, the degree colors on
  the common part must be complementary. Once the marks and overlap
  isomorphism are fixed, the only unknowns are the two omitted
  wings' crossing pairs. A capacitated bipartite Hall test is
  equivalent to degree- and triangle-preserving restoration. A
  failed cut is a physical subset with checkable demand and capacity.
  The degree factor is not a Ramsey completion. The exact independent
  set obligation is the four-role capped mask condition; equivalently
  it can be tested through scoped bipartite matching demands. The
  latter give a genuinely joint obstruction when supported individual
  edges cannot coexist in one degree factor. Full derivations:
  `proofs/crown23_two_window_factor.md`.
- **C-056.** Each saturated attachment pair has at least six
  crossing edges, with equality only for `6K2`. Three specific
  non-perfect seven-edge shapes are excluded as well. For two
  omissions with `b_i,b_j≤12`, the overlap has
  `e(X)≥62−(b_i+b_j)`; equality requires the *other*, already present
  pair to be `6K2`. This uses the crown and card independence caps,
  not the incomplete e74 list, and does not require all four
  windows to be the same missing class. Proof:
  `proofs/crown23_sparse_rectangle.md`.

## Exact controls (C-057, enum; no target performance result)

| Control | Literal or independently reconstructed result |
|---|---|
| All allowed matrices and capacity-respecting demand tuples at widths 2×3 and 3×3 | 177,856 cases; 18,544 factors feasible, 15,264 deficient cuts with correct capacities, 144,048 unequal totals. Every supported-edge union agrees with the enumerated feasible factors. |
| Same-class `C13(1,5)` translated deletion decks at widths 3 and 4 | 364 planted graph restorations retained. All 1,196 physical overlap automorphisms checked; exactly 832 wrong-degree alignments rejected by complementary colors. All 364 surviving restorations are checked induced completions isomorphic to `C13(1,5)`; no additional positive alignments. |
| Adverse degree-balanced deck, with two isomorphic cards and all one-coordinate capacities passing at the failing alignment | All 120 shared permutations and literal rectangles checked. 16 have a deficient cut, 104 have a degree factor. The pinned example has subset mask `3`, demand `2`, capacity `1`. These are triangle/degree positives, not Ramsey positives. |
| Scoped matching with two literal `C9` factors | All 256 scopes/sizes agree. The supported union has a two-edge matching on `0b011 × 0b101` but neither factor realizes both. |
| Crown padding and sparse components | All 16 touched-role subsets match literal moved-set enumeration. At widths 3–6, 76 total base/one-extra patterns match independently enumerated maximum independent-set blocker families. The three seven-edge exclusions also match literal blockers at a smaller width and width six. |
| Width-six geometry-only plant | Six physical role pairs from four explicitly isomorphic 26/e74 cards. Two are six-edge matchings and four have 12 crossing edges. Exact factor reconstruction and six shared-sign mutations agree. The bipartite plant fails the crown independence cap in every alignment and is not a Ramsey input. |

The C13 oracle checks 5,981,768 literal total-size rectangles using
sets, then checks complete graphs and their independence directly.
In the clean run its completion work took 26.49 CPU-s; Hall and the
supported-edge filter took 0.16 CPU-s on the same alignments. The
oracle deliberately includes obviously wrong shared degrees and
forbidden crossings; **this is a control, not a claimed speedup
over E's row-pruned terminal or a price for target production.** No
concrete target marked deck reached our completion screen. No E
partition was enumerated in this lane and no E artifacts were changed.

C-050 remains retired. As confirmed by the round-22 critic, the
eight old exclusions were due only to the existing signed join.
No frame repeated, no re-credit, no new count against the marked
16/17 residual. The critic's alternative E directive was used because
the recent C pilots reached no target terminal and there was no
priced target joint obstruction to run against them.

## Replay and accounting

```sh
sha256sum -c ralph/lanes/C/ROUND23_FREEZE.sha256
mkdir scratch/C/r23-review
bash ralph/lanes/C/replay_crown23.sh scratch/C/r23-review
cmp scratch/C/r23-clean/replay.log scratch/C/r23-review/replay.log
```

The code performs literal set/graph comparison separately from the
bitmask Hall implementation. In the original and clean passes the
first 15 deterministic rows were byte-identical; the seven added
checks also matched their separately run output. Clean replay used
30.17 CPU-s, 15,740 KiB peak RSS. Total charged checks, including the
two earlier progressively expanded passes and the small exploratory
seven-edge pattern count, took **89.93 CPU-s / 0.02498 core-h**.
All runs were foreground, one worker, 512 MiB VM, bounded CPU/wall;
no detached jobs, proof archive or target queue. A production request
needs a bound concrete survivor and a matched terminal price.
