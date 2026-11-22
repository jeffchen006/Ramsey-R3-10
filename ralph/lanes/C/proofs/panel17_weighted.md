# Weighted count for the one-neutral package filter

**Scope.** This is an exact count for a necessary filter, not for joint
packages or completions. All counts are of the labelled frame pairs of
`panel16_cover.md`. Fix the parameters (degree Δ, alpha cap b, and r
roots per shore) and both labelled host catalogues. An occurrence of a
host means one labelled catalogue record with one specified neutral z;
hosts on opposite sides refer to their respective catalogue.

## The predicate being counted

For a source singleton site x, let ε be 1 if x meets its own neutral,
and 0 otherwise. Count x's one root edge, its source-private neighbours,
and its remaining neighbours (all in the destination host, with the
one shared neutral). Its required row size is
`s = Δ − 1 − deg_source(x) + ε`, and the row must contain the destination
neutral exactly when ε=1. Use the integer type `2s+ε`.

For an individual group with k singleton sites, a package is a row for
each of its k slots. Each row has the required size and neutral state,
is independent in the destination host H, and for each nonempty subset
J of the k slots the deletion of the union of the J rows from H must
leave independence number at most `b−r+1−|J|` (restoration lemma in
`panel16_cover.md`). The only destination data in this predicate are
the adjacency matrix of H and the position of its neutral; its four
marks, their singleton labels, and degrees *outside* H are not read.
The only source data in the predicate are the row types in that group.
Permuting the types and rows together carries each tested subset to a
subset of the same size with exactly the same row union. This gives a
bijection of package assignments and in particular proves the multiset
key for existence. A group of size 2, 3 or 4 is checked by the same rule
on all nonempty subsets, not by a size-3 truncation.

The directional filter asks for nonemptiness of **every** group's
package domain, each alone. Let P be the multiset of the source's group
multisets; keeping repetitions is convenient for reconstructing the
size shape. Permuting the groups merely reorders the conjunction. Write
`F(P,H,z)` for its truth value. It does not say that packages for groups
on the same side, or opposite sides, can be chosen compatibly. In
particular this argument permits caching *truth values* only. For a
later join use the original frame, mark and site labels, orientation
of each rectangle, and physical neutral. No numeric equality of
residual degree sums or row types may identify distinct hosts or
different neutrals unless an explicit labelled transport is proved.

## Counting the intersection

Partition frames by `(D,d)`, the private degree sum and neutral degree
within their window. Only complementary strata are allowed, namely
`(D,d)` against `(D+Δ,d_bar=Δ−d)` for consecutive window orders.
Within one such pair of strata let `L_h(P)` and `R_k(Q)` be the numbers
of labelled frames with host/neutral h or k and profile P or Q. The
raw multiplicity for fixed h,k,P,Q is `L_h(P) R_k(Q)`, since there are
no further header-identification rules. Its contribution after both
directions pass is exactly

`L_h(P) R_k(Q) F(P,k) F(Q,h)`.

After fixing h,k, `F(P,k)` depends on P but not Q and `F(Q,h)` depends on
Q but not P. Finite distributivity therefore gives the exact both-pass
contribution of this host pair as

`[sum_P L_h(P) F(P,k)] [sum_Q R_k(Q) F(Q,h)]`.

The raw mass omits both predicates; one-direction passing masses omit
only the other predicate. Sum separately over the compatible host
pairs; their frame-pair sets are disjoint. The same argument applies
within any pair of shape strata, because each shape is a function of
its profile. Both-pass is an intersection, not the raw mass minus the
sum of the two rejected masses (which would double-count headers
rejected in both directions). No probability or independence assumption
about different host pairs is used. This is a weighted count without
iterating the ordered labelled headers or their terminal assignments.

## Computation of a group truth value

Enumerate all independent subsets of H with the required row size and
neutral state. Independently test every subset union as soon as all
its row slots have been chosen. If any subset union fails, no extension
of those rows can repair that tested subset. Otherwise a fully filled
tuple witnesses true; exhaustive failure witnesses false. In the bitmask
implementation alpha of any induced subset S is computed by the
recurrence `max(alpha(S−v), 1+alpha(S−N[v]))` for the lowest site v of
nonempty S, using `alpha(empty)=0`. These are precisely the independent
sets omitting and containing v. Candidate order, or a permutation of
the row slots to visit the most restrictive domain first, does not
change the answer. The separate Python check uses hitting every
independent set of forbidden size instead of this recurrence.
