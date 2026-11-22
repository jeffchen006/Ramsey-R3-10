# Any remaining R(3) graph has an induced P8 in an edge kernel

`hand + enum`, submitted for independent review. Not a certificate for
R(3). This is a third argument, **after** `GRAFT.md` (global L=6) and
`P7_COVER.md` (global L=7). Let a graph have a simple kernel P8, but
suppose **no edge kernel anywhere contains an induced P8**. Degree at
most two means the only possible chord of any simple P8 joins its two
endpoints. Hence every such path closes to a C8 component. There is no
P9: the first eight vertices of a P9 could not have that chord, since
the eighth still has its ninth neighbor. Thus global L=8 under this
assumption, but not every P7 is part of a C8. In particular we never
require that all edge kernels are acyclic or that other graphs lack C8.

## Cover by deleting adjacent cycle vertices

Mark any C8 on an edge `0,1`, putting the path vertices in cyclic
order at `2..9` (even labels neighbor 0). Omitting position 9 yields
one nine-star P7 with a **unique** exterior occurrence of mask 262:
the omitted vertex sees exactly root 1 and positions 2 and 8. Two such
extensions would give a kernel vertex of degree three. The same holds
for all eight omissions, allowing root swap and path reversal.

From the *unrestricted* P7 file retain the rows that pass the general
cap/regularity/domination/independence screen, have forced length at
most 8, and have the closing mask. This gives 24,962 representatives.
Any mandatory eight-vertex kernel path must have its closing edge in the
upper graph. Force it, or reject the state if impossible. Test optional
edges likewise, to rule out those creating a path with an impossible
closing edge. These clauses are necessary **only under no induced P8**.
The other cap/alpha/degree tests are those of `P7_COVER.md`.
17,898 nine-star views remain.

To reconstruct all ten-star masks, omit a vertex from either end of a
selected cycle edge. Orient both P7s, remove the omitted vertex from each
exterior table, and compare on the eight shared stars. In a shared cell
of size n where the two extra anchors have counts a,b, no exterior vertex
can see them both: the extra anchors are adjacent. Thus require a+b<=n
and the entire ten-star cell is **uniquely determined** as sizes a, b,
n-a-b. Keep a row only if all eight single-deletion views are in the
library. Quotient by rotations and reversal, swapping the two roots when
the parity changes. This is a cover of *marked cycle neighborhoods*, not
a partition of graphs.

| Stage | Count |
|---|---:|
| oriented deletion views | 35,498 |
| matching eight-star parent pairs | 1,200,842 |
| pairs allowing disjoint attachments | 53,564 |
| labelled ten-star profiles with all eight views | 51,041 |
| complete ten-star dihedral representatives | **3,391** |

`oct_audit.cpp` obtains the same 51,041 labelled patterns by a different
algorithm: explicitly choose the six unfixed neighbors of the tenth anchor
in the nine-star cells, check triangle and already-fixed pair capacities,
then check the eight rolls. It tried 80,560 candidate rows and consumed
every expanded representative exactly once. This test does not use the
adjacent-deletion join to enumerate candidates.

## Exhaustion and signed controls

Compile `long_search.cpp` with `-DOCTAGON_ROOT`. Lower and upper graphs
start with ten complete stars. As before, only equivalent exterior labels
within the current frozen cells may be permuted. The first 500-node pass,
**no profile library**, exhausts 3,369 of 3,391 (116,633 nodes, 155.2
CPU-s). The 22 node caps yield 86 nine-star deletion profiles. Under the
no-induced-P8 hypothesis a *known C8* must have every deletion view in
this library. The other P7s **may not** be restricted to these keys. Rule
`44 = 32+8+4` explicitly checks for a lower-graph C8 closing vertex
before applying the joint reroot library. Requiring profiles on arbitrary
P7s instead would be unsound. This pass exhausts **22/22**, 53,662 nodes,
53.5 CPU-s. No cap remains in the terminal union. This does not refute
an arbitrary marked C8 or any graph containing both a C8 and an induced P8.

**Simpler audit route:** rerunning the last 22 with **no reroot library at
all** also exhausts 22/22, in 56,324 nodes / 65.4 CPU-s. Thus the 86-view
implication is unnecessary for this third result. Use `40 9 8 30000 none 8`
on the same 22 `.in` files: `eight/no-library/{all.out,hist}`. Each alternate
receipt is independently bound to its ten-star profile in `eight/terminal.tsv`.

C22 controls: of the 12 nine-star marks, the local closure rule on the
marked edge accepts exactly the five non-induced-P8 cases and rejects
the other seven. The global rule rejects all marked C22 graphs as expected
from the source. Real C22 cyclic deletion views give one ten-star orbit,
eight labelled views; exact search with closure imposed only on the marked
edge (`16`) produces the planted graph. Real cyclic-library mode passes and
an empty library fails. Do not treat a known graph with an induced P8 on
another edge as a positive for the *global* closure condition.

Replay in `scratch/D/joint9`, with the usual limits. `eight/filter 40 9 8 1`
on `eight/cyclic.tsv`; `cycle8_join.py eight/views.tsv --out NEW`;
`eight/oct-audit 9 40 eight/views.tsv eight/oct.tsv`. Native search
arguments: `40 9 8 500 none 8` for `eight/stage1/a??.in` and
`40 9 8 25000 eight/stage1/views.tsv 44` for `eight/stage2/b??.in`.
`oct_receipts.py` binds all 3,391 terminal statuses and the exact late
library; `eight/terminal.tsv` maps hashes and ordinals. All proof work in
this third step is **enum**, with a separately generated source cover.

Combining the three steps gives an **induced P8** root for every R(3)
graph. R(3), R(4), and R(3,10) are open. The four unrestricted C6
eight-star roots hit 10,000 nodes each in a separate pilot: no general
no-C6 or no-C8 assumption is justified.
