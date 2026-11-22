# Round 22 — an order-25 puncture through e69 in every saturated 32/e108 graph

**Hand, pending critic.** Let `H` be saturated triangle-free on 32 vertices
with 108 edges and `alpha(H)<=8`. There is a degree-six vertex `v` such
that `H-N[v]` has **65..69** edges. In particular the possible saturated arm
of the missing-critical-key search needs no e70 source, now for **every**
degree distribution. This does not classify any of the five missing keys.

## Inherited constraints and contact inequality

By B-040 every `D6` puncture has 65..70 edges and `delta(H)=6`, where
`Di` denotes the degree-i layer. Suppose all these punctures have 70.
B-040/B-041 give the following conditions, recalled so the proof can be
checked without a generator. Put `S=D6`, `s=|S|`, `n7=40-2s` and
`n8=s-8`; in particular `8<=s<=20`. The neighbor degree sum at each
vertex of `S` is 38, so split `S=A ∪ B`:

- A site of `A` has four neighbors in `S` and two in `D7`.
- A site of `B` has five neighbors in `S` and one in `D8`.
- Every pair incident to a site of `S` has codegree at most two.

Write `a=|A|`, `b=|B|`; `2e(H[S])=4a+5b` gives even `b`. The internal
unordered wedges with endpoints in `S` number `6a+10b`. Triangle-freeness
and the codegree cap budget all wedges with endpoints in `S` at
`2(choose(s,2)-e(H[S]))`. The slack after the internal wedges is therefore
`F=s(s-16)+5a`. The `D7` centers use at least `max(0,2a-n7)` of this
slack, since `choose(t,2)>=t-1` and the incidence total is `2a`. If every
`D8` vertex has at least one `B` neighbor, the `D8` centers use at least
`b-n8` more units by the same inequality.

**Contact inequality.** If `W` is any independent eight-set and `I` is
an independent set outside `W`, then `|N(I)∩W| >= |I|`; otherwise
`I ∪ (W\N(I))` is an independent nine-set or larger. In particular, any
two distinct vertices outside `W` whose sole contact in `W` is the same
vertex are impossible: they are independent because they share that
neighbor. In the uses below `W=N(z)` for a degree-eight vertex `z`.

## At most four degree-eight vertices

B-041 rules out `s<=11` and at `s=12` forces `B` empty. Its forced
12-site low graph has codegree-one pairs forming four disjoint independent
triples; all other low nonedges have codegree two internally. A `D7`
vertex meeting low sites in two different triples would either make a
triangle or add a third common neighbor. Thus distinct triples have
disjoint contacts in `D7`. For any `z∈D8`, `N(z)` contains no low site and
each independent low triple requires three contacts in `N(z)` by the
contact inequality. They must be in `D7`, so this requires twelve sites
in `N(z)`, impossible.

## At least five degree-eight vertices and some unoccupied fibre

For `p∈D8`, call `B_p=N(p)∩B` its fibre. The fibres are disjoint and
partition `B`; no `D8` site has neighbors in `A`. In this section
`z∈D8` is *unoccupied*, meaning `B_z` is empty.

If `B` is empty and `p,q∈D8` are adjacent, every `A` site has a contact
in both `N(p)` and `N(q)` by saturation; both contacts must be in `D7`.
Those neighborhoods are disjoint by triangle-freeness. Every `A` site
then has a unique contact in `N(p)`, so their `s>=13` contacts must be
distinct by the contact inequality, which is impossible. Thus `D8` is
independent. Also `S` has an independent four-set (use `R(3,4)=9`),
giving an independent nine-set with five `D8` sites, a contradiction.

Suppose `B` is nonempty. The only possible contact of any `u∈B` in
`N(z)` is its `D8` neighbor. Saturation forces this contact, and the
contact inequality makes the contacts distinct. Therefore all occupied
fibres are singletons and their `D8` owners are adjacent to `z`, hence
mutually nonadjacent. For distinct owners `p,q`, the pair `p,u` with
`u∈B_q` must have a common neighbor by saturation. It must be the
unique low neighbor of `p`: the only non-low neighbor of `u` is `q` and
`p,q` are nonadjacent. Thus `B` is a clique. Since `b` is even and
positive, `b=2`.

Let `p` own one of these two sites, `u`. Exactly four of the five low
neighbors of `u` are in `A`, so `s-6>=7` sites of `A` avoid `u`.
Each such site has a `D7` contact in `N(p)` by saturation (it does not
meet the only low site of `N(p)`) and a `D7` contact in `N(z)` likewise.
Since `p,z` are adjacent, the two neighborhoods are disjoint, and each
of those `A` sites has just one contact in `N(z)`. These contacts must be
distinct, but the two owners in `N(z)` leave space for at most six
`D7` contacts. This is impossible.

## Every fibre occupied

If `p,q∈D8` are distinct and nonadjacent, **every site in each fibre has
a low neighbor in the other fibre**. For `u∈B_q`, the pair `p,u` is a
nonedge. Its common neighbor cannot be any non-low site other than `q`,
and cannot be `q` since `p,q` are nonadjacent. It must be in `B_p`. The
reverse direction swaps the roles.

If every fibre is a singleton, `b=n8` is even, hence `n8>=6` in this
section. A triangle-free graph on at least six owners has an independent
triple (`R(3,3)=6`). Their singleton lows then form a triangle by the
preceding condition, impossible.

Now fix a nonsingleton owner `p`. It is nonadjacent to **at most one**
singleton owner: two such owners would give two distinct singleton low
neighbors common to every pair in `B_p`, in addition to their common
owner `p`. It is adjacent to **at most two** singleton owners: these
owners form an independent set, so their singleton lows are a clique.
Hence the total `t` of singleton fibres is at most three, and
`b>=2n8-t`. Together with `b` even, `a=s-b`, `s=n8+8` and

```
max(0, 2a-n7) + b-n8 <= s(s-16)+5a,
```

this leaves exactly the rows below in the relaxed arithmetic. All
listed rows have `b=2n8-2`; in particular `t` is two or three.

| n8 | a | b | t |
|---:|---:|---:|---:|
| 8 | 2 | 14 | 2 or 3 |
| 9 | 1 | 16 | 2 or 3 |
| 10 | 0 | 18 | 2 or 3 |

**Three singleton fibres.** Each nonsingleton owner is adjacent to
exactly two of the three singleton owners. Any two nonsingleton owners
share such a neighbor and are therefore nonadjacent. Every low site in a
nonsingleton fibre needs one low neighbor in each other nonsingleton
fibre and one in the unique singleton fibre whose owner it misses. This
requires at least `n8-3` low neighbors, impossible if `n8>=9` since a
`B` site has just five low neighbors. At `n8=8` it requires exactly one
neighbor in every other nonsingleton fibre. There are four size-two
fibres and one size-three fibre since `b=14`. The bipartite edges between
two unequal nonsingleton fibres cannot give degree one to every site on
both sides.

**Two singleton fibres.** All other fibres have size two. Call the
singleton owners `q1,q2`. Each double owner is adjacent to at least one
of them. There is at most one double owner adjacent only to `q1`: two
such owners would be nonadjacent (share `q1`) but all their low sites
would be adjacent to the singleton low in `B_q2`, preventing any edge
between their fibres. This violates the condition for nonadjacent
owners. The same argument bounds the group adjacent only to `q2`.

Let `m=n8-2` be the number of double owners and `r>=m-2` the number
adjacent to both singletons. Any owner adjacent to both shares a high
neighbor with every other double owner, so it is nonadjacent to all
others. Its low sites need at least `m-1` low neighbors in other double
fibres, impossible if `n8>=9`. It remains to handle `n8=8`, `m=6`, `r>=4`.

Pick an owner adjacent to both singletons as an anchor. Each of its
two low sites has exactly one neighbor in each other double fibre (five
fibres and only five low neighbors). All sites in those other fibres
have at least one neighbor in the anchor fibre, so all five joins are
matchings. Label the two low sites in each fibre with opposite signs,
choosing signs to make the anchor matchings cross. Two same-sign sites
in different nonanchor fibres share an anchor neighbor and cannot be
adjacent. A same-sign pair involving the anchor is nonadjacent by
construction. The two six-site shores are therefore independent.

Add `q1,q2` to one shore: they share the anchor owner, hence are
nonadjacent, and neither has a neighbor in any double fibre. Every
`D7` site is outside this independent eight-set and has no neighbor
among its six low sites (`D7` contacts in `S` lie only in `A`). It must
therefore meet `q1` or `q2`. But `q1,q2` have two low contacts in total
and `2r+(m-r)=6+r` incidences with double owners, leaving only
`16-2-(6+r)=8-r` contacts for the eight `D7` sites. Contradiction.

This exhausts the all-e70 premise. B-040 supplies the lower bound of 65.

**If the selected puncture is e69.** There are 33 incidences in its
25 nonzero columns on the six neighbors of the root. Let `p` count the
singleton columns. B-040 gives `p<=18` and at most three in each row.
The excess over singleton/double sizes is `33-(50-p)=p-17`, so the
column sizes are either 17 singletons and eight doubles, or 18 singletons,
six doubles and one triple. Doubles cannot repeat: in either case at least
one of the two rows of a repeated double has three singleton columns;
these three, the repeated columns and the other four rows are an
independent nine-set. This local restriction does not price the lift.

## Controls, pricing and independent-source handoff

- `src/r22_low_replay.sh` first recovers `C5` in two independent
  generators, checks the contact inequality by literal subsets at every
  root of `C5` and `C13(1,5)`, and exposes a specific nine-set analogue
  `{1,4,5}` in an adverse augmented `C5`. It checks the integer envelope
  above and reproduces the B-041 low layer by both a rooted
  exhaustive column generator and nauty geng, then checks its triples
  by literal pair intersections. The C13 low census is an extra
  smaller check, not a dependency of the hand proof. See
  `scratch/B/work/e108_r22/low.log` and `low.time` in that directory.
- The confirmed N→B e96 source from `ralph/critic/round_021.md` comprises
  1,842 critical and 33,312 reducible parents (GR Table 14 total
  35,154). Its full degree-4..8 critical inverse lift yields 23 distinct
  outputs, all old. By N-001 and B-029, a thinner puncture cannot exist
  at e95 for a missing key. Any reducible e96 puncture would thin to e95,
  so **for each missing key and every vertex deletion, every spanning
  (3,9) graph of that puncture has at least 97 edges**. This bound is
  independent of the saturation argument. e96 and the measured e98
  waves are retired. `source.log` binds the scout evidence without
  rescanning the 2.1M-key archive or rerunning those lifts.
- The e69-only tightening is a coverage result, not an end-to-end
  search price. The published e65..68 levels total 12,581,543, with no
  e69 count in GR Table 13; D-C8c counts 2,120,846,970 at e<=70 in all.
  The prior e65 pilot was not representative of e69 and is not a basis
  for scaling. No new saturated source was produced. No candidate,
  solver job, floor-109 claim, U88 or distribution debit.
