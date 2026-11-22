# Round 23 — physical deck addbacks and degree-roster projections

## Scope and inherited premises

Throughout: order-two automorphism fixing 32 vertices, four independent
six-site attachments, universal `δ(G)≥5`, `δ(W)≥2`. No MTF assumption.
E-018/`window73.md` gives `d_F(W)=8`; `P=0` gives `d_F(A_i)=7`. Every
deletion card `H_i=F\A_i` has 26 vertices, 74 edges and independence
number at most 7. Each `w` hits each attachment. Its one-wing window
must have independence number at most 6, and `b_i=e(W,A_i)≥10`.
The 1,624 known distinct classes and the premise that there is exactly
one missing class are E-021. No inference that the missing class is
absent is drawn from the failure of known-card extensions.

## Two-copy join (calibrated; not a target census)

Take separate marks of two copies of a single uncolored card class,
with respective omitted roles `i,j`. Each mark consists of an actual
eight-set and three independent six-sets assigned to roles. Delete
the other omitted role in each card. Key by a colored canonical form
on the actual 20 shared sites, with `W` and the two retained wings
distinct colors. Enumerate **all** color-preserving isomorphisms of
the two restrictions, including when the source and target uncolored
card are identical. The union determines all edges except between
the two nonshared six-sets; validate residual degrees and enumerate
that bipartite block with triangle and independence tests. Both
occurrences of a mark remain distinct until the physical overlap map
is chosen. This agrees with C-055's complementary-degree refinement;
the latter is a prospective cheap color filter, not an assumption
that a card isomorphism preserves W or any wing.

`deck23.py control --cards` tests every pair of omitted roles of a
15-site smaller planted deck. Its two uncolored cards are isomorphic,
but permuted, and the actual overlap map is found in all six cases.
Every planted addback agrees with literal enumeration of the nine
allowed-position bits, with a one-edge overlap and a degree-demand
mutation rejected separately. There is no supplied target missing
card to join: the reverse-search approaches in `m11.md` could not
produce it. The round used the priced disjoint fallback below, not a
false completion of the 1,624-class deck.

## Known-card arms (hand + enum + local cert)

In a known 26/e74 card, mark a physical eight-set W and three disjoint
independent six-sets that exactly partition the remainder. Every W
vertex has degree at least `d_W(w)+3` in the card, and its degree sum
over W is `64-b_omitted`. Thus each census below only uses necessary
conditions. Retained groups must hit every row and obey
`α(W∪A_i)≤6`. The primary scan tests the latter by the W-side Hall
criterion on independent subsets; the independent C audit tests an
actual independent seven on all 14 sites. The two enumerators agree
on every uncompressed W mask and every unordered marked partition:

| Arm | W masks | Unordered marks | Known cards with marks |
|---|---:|---:|---:|
| e8/P0, omitted `b=13..18` at **any** sorted profile of total 48 | 351,794 | 134 | 49 |
| e10 `(10,10,10,14)`, omitting the 14 group | 420,492 | 126 | 86 |

`lift_deck23.py` fixes all edges of each marked card. The only
extension bits meet the new independent six-set; it encodes exact
degrees, triangles, and witnessed necessary independence clauses.
In particular each blocked physical I8 in an omitted card can add
both members of its moved pair; witnessed I7 in `W∪A_new` can add
three same-side moved vertices, witnessed I6 in W four, and I10 in
F needs no padding. The independent rebind reconstructs the CNF
from the graph6, physical mark and each exact independent-set mask,
byte-checks both digests, and replays CakeLRAT and `lrat-check`.
All 260 IDs checked twice, zero open, zero model. Smaller full
addback controls recover the planted star and dual-certify the
stronger impossible independence requirement. Early tool-memory
and control threshold problems are logged and earn no debit.

Together with the round-22 confirmed exclusion of a known b≤12 card,
**all four e8/P0 cards must be copies of the missing class**. The three
size-ten omissions of e10 have six W d7 sites (outside known roster),
so all four e10 cards in this profile must also be copies of it. These
all-missing conditions are not themselves closures.

## Conditional high-degree roster

For every omission, an exterior d7 vertex has no neighbors in A_i
because its full fixed degree is seven. Two such exterior vertices
must be adjacent: otherwise they and A_i would make an independent
eight in one of the other cards (choose an omitted role different
from their at most two roles and i). Thus they form a clique and
there are at most two. This is the earlier roster fact reused here.
Let `K` be the common number of d7 vertices of the missing class.

For the e10 `(10,10,10,14)` profile, each small omission has six
singleton W rows and so `K≥6`. In the large omission a W row takes
1, 2, or 3 edges into the omitted group and there are six surplus
incidences. Four or more singletons are necessary (`K−2≥4`). Hence
there are two triples plus two doubles or three triples. Thus:

- Two triples: four W d7, exactly two outside d7, `K=6`.
- Three triples: five W d7, one or two outside d7, `K=6` or 7.
- At `K=6` no exterior d7 in any size-ten omission. The three
  induced W six-vertex d7 graphs must be isomorphic. Each retained
  wing site must meet both other small wings. At `K=7`, for each
  small wing, among the sites of the other two small wings at most
  one can fail to meet it.

The three pinned small wings determine all omitted W row degrees by
residual arithmetic. Canonicalize their support columns, equal-size
wing permutations, and W automorphisms. `residue23.py` independently
checks the 20 W keys against all 7,740 normalized labelled cores,
and proves exact agreement of the two local support generators and
two triple-enumeration orders. All 8,157 retained `(W,3 supports,r,K)`
records match byte-for-byte, including empty fibers. Each base CNF
has the pinned W, actual slots, triangle/edge/degree rows, width-three
necessary I8 cuts, exact d7 exterior count/clique, and the above
partial cross-contact budgets. Additional physical I8 cuts would be
sound, but only checked terminal rows count. The 13 pilot IDs are
bound by literal plan-row equality to global IDs. The exact ledger
is 13 + 8,144 production = **8,157 CHECKED, 0 open**. Fresh independent
CNF replay (`rebind_projection23.py`) byte-bound and dual-checked
all 8,157 proof bundles: 3,390 at K=6 and 4,767 at K=7. Together with
the known-card arm this excludes the **whole listed e10 profile**,
conditional on the E-021 premise and the opening assumptions.

## e8 largest omissions (hand and queued follow-up)

If `b_max≥16`, total 48 and minimum 10 force `b_min=10`, hence `K≥6`.
Each W row has at most three neighbors in a given wing; a `b` wing
therefore has at least `ceil((b−8)/2)` nonsingleton rows. Adding at
most two outside d7 gives `K≤10−ceil((b−8)/2)`. Thus `b_max=17,18`
are excluded conditional on the all-missing result. For `b_max=16`
only `(10,10,12,16)` and `(10,11,11,16)` are possible, with `K=6`,
four triple rows in the omitted group, and exactly two adjacent
exterior d7 vertices in the large omission. `residue8_23.py` indexes
the third small support by its exact forced row vector. The first
naive full census was killed at its CPU cap, not an exclusion. The
completed indexed census produces 15,350 2C4 and 243,162 C8 rows.
Only the first core has been dispatched, after six checked pilots.

## Artifacts

All logs and compact receipts are in `scratch/E/r23_deck/`. `jobs.tsv`
has every detached wrapper including dates, limits, commands and logs;
`exits.tsv` records completions. Original catalogue source is
`scratch/E/r6_e11/addswap2.g6`. The round does not close an entire
involution, e8/P0 overall, other e10 profiles, or any degree
distribution. It produced no flow candidate.
