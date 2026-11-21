# Extreme fixed-set windows for involutions with 30 fixed points

Let `a` be the largest fixed attachment size, and `W` the fixed vertices
with no moved neighbors. For `f=30` and `a∈{4,5}`, the quotient is a
five-pair crown by `involution.md` (internal pair edges allowed). A full
side is independent; hence `α(W)≤4`, and `|W|≤13` by `R(3,5)=14`.
For an attachment `A_i`, the four moved vertices on one side *other than*
its own pair are independent and anticomplete to `W∪A_i`. Therefore
`α(W∪A_i)≤5`. These bounds require neither maximality nor a min-degree
lower bound.

- **`hand`: `a=5` implies `|W|≤12`.** Otherwise `W` and some size-five
  attachment would induce 18 triangle-free vertices with `α≤5`, violating
  `R(3,6)=18`.
- **`enum`: the single-window check gives `|W|≤11` at `a=5` and
  `|W|≤12` at `a=4`.** At the
  remaining maximum `|W|=12` or 13, respectively, `W∪A_i` for an attachment
  of maximum size would belong to the complete seven-graph `(3,6;17)`
  class. In every one of those graphs, deleting any independent set of
  size four or five leaves independence number at least five. This is
  incompatible with `α(W)≤4`.

## Stronger multi-window sieve

**`enum`: ultimately `|W|≤10` at `a=5` and `|W|≤11` at `a=4`.**
For a choice of `j` attachments, the other `5−j` members of a side give
the necessary bound `α(W∪⋃ A_i)≤4+j`. Two vertices from different
attachments can be adjacent only if their neighbor masks into `W` are
disjoint (otherwise there is a triangle). Adding *all* these possible
cross edges gives a supergraph of the true window, so an independent set
in the supergraph rules out the masks. The supergraph itself need not be
triangle-free. Multisets, including repeated masks or repeated attachment
profiles, are allowed throughout. We also check the degree cap at `W`.

At `a=4, |W|=12` the five attachments have total size 18, so at least
three are full (size four). The 12 `(3,5;12)` cores give 33 individual
four-vertex profiles, four viable profile pairs, and zero triples.
At `a=5, |W|=11` the attachment sum is 19. An independent moved pair must
have at least three fixed neighbors (otherwise its fixed antineighborhood
has order at least 28 and `α≤7`); an adjacent moved pair has zero. The
sorted possibilities at maximum 5 are `(0,4,5,5,5)`, `(3,3,3,5,5)`, and
`(3,3,4,4,5)`. Thus either two full five-sets or a five-set and two four-sets
are necessary. The 105 `(3,5;11)` cores give 117 size-five profiles in
12 cores. There is no viable `(5,5)` pair, one viable `(5,4)` pair, and
no `(5,4,4)` triple (including the case where the two four-sets have the
same profile). This exhausts the former maximum `|W|=11` at `a=5`.

## Evidence

`crown30_windows.py` checks all independent deletion sets on the seven
graphs of order 17. It independently runs the converse search: start
with all 12 `(3,5;12)` graphs, or the unique `(3,5;13)` graph, and try
all ways of attaching an independent set of size five or four,
respectively. In either search, zero candidates survive. The converse
search uses a canonical multiset of independent neighbor masks into `W`;
every subset of added vertices is checked against the independence number
of its antineighborhood in `W`. This is exhaustive for this extension,
irrespective of the rest of a possible order-40 graph.

Controls: remove an independent four-set from the known `C13(1,5)`, then
recover its neighborhood masks (one checked completion); attaching one
vertex to `C13(1,5)` while preserving `α≤4` returns none, as expected by
`R(3,5)=14`. The code checks validity of all small input graphs. The
graph6 lists are McKay's (D-G3 / McKayWeb), hashes in
`scratch/E/crown30.manifest`; `shortg` gives the same 105, 12, 1 and 7
counts after canonicalization. The
order-17 count is D-G3 (`notes/DEPENDENCIES.md`); the 12 and 1 order-12/13
counts, and the 105 order-11 count, are independently recorded in
`notes/gluing.md`. The optimistic-graph routine has explicit small
brute-force controls with repeated and overlapping neighborhood masks.

Replay from `scratch/E`:

```sh
sha256sum -c crown30.manifest
for catalogue in r35_11 r35_12 r35_13 r36_17; do
  ../../opt/bin/shortg -q -T"$PWD" "$catalogue.g6" "$catalogue.canon.g6"
  wc -l "$catalogue.g6" "$catalogue.canon.g6"
done
nice -n 5 timeout 210 bash ../../ralph/lanes/E/limited.sh 130 \
  python3 -u ../../ralph/lanes/E/crown30_windows.py . --a4-w12 --probe11
```

Evidence `scratch/E/crown30_windows.log` (1.68 CPU s),
`scratch/E/crown30_a4_w12.log` (2.97 CPU s), and
`scratch/E/crown30_probe11.v3.log` (89.51 CPU s). Smaller `|W|`
remains open; this does not exclude either `a` value or the full `(2,30)`
case. McKay's `r36_15.g6` and `r36_16.g6` downloads contain only 1,592
and 121 representatives; **not** the all-graphs censuses (64,732 and
2,576), so they must not be used as complete anchors for smaller `|W|`.
