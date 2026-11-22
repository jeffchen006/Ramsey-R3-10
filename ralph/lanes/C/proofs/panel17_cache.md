# Exact independent-set witness reuse in the cap-five 17/17 terminal

Fix a single alignment. Label the 40 physical vertices as in the terminal.
The base lower graph `L` has forced edges, and the base upper graph `U`
has every edge still allowed by the base tests. For each three-site
group, a package is a choice of one **full** neighbour row for each
of the three labels. Its finite domain contains every package for any
physical target on this alignment, by `reciprocal_panel17.md`.

For group `D` and site `x` in its scope, let `T(D,x)` be the union of
the rows at `x` in all packages of `D`. For a site not in the group,
let `T(D,x)` be the whole vertex set. Form the undirected graph `P` by
keeping an edge `xy` of `U` exactly when, for every group `D`, we have
`y in T(D,x)` and `x in T(D,y)`.

For any joint package choice visited by the terminal, a selected row
is a subset of its group's union at that site. Assigning the rows
makes each selected row exact, simultaneously imposing symmetric
membership at the opposite endpoints. Thus the resulting upper graph
is a subgraph of `P`: an edge in it is in the base `U`, and at either
endpoint every group owning that site has selected a row including
the edge. The assignment only considers simultaneously compatible
packages, so it does not overwrite a selected row's edge restriction
with an inconsistent assignment. Subsequent propagation only deletes
upper edges. Hence an independent 10-set of `P` is independent in
the upper graph of every visited filling, and consequently in any
physical candidate extending such a filling.

When this common witness does not exist, one may instead cache a
concrete independent 10-set discovered in one particular filling.
It is **not** a witness for another filling until checking that each
of its ten labels has no current upper neighbour among those labels.
A hit gives exactly the same existence result as a fresh independence
search; if no hit occurs, the implementation performs the search.
The search by least set bit partitions all independent subsets by
their least label; after choosing that label only its non-neighbours
among the larger labels participate, with one fewer label needed.
This proves the recursion both ways by induction on the requested size.

The degree, triangle and codegree failures are always tested before
the cached independence test, and the propagation schedule for an
independence miss is unchanged. Thus neither the set of visited joint
choices nor the priority of the five terminal dispositions changes.
The C++ terminal is unaffected by this implementation and does not
call the new witness code. A common-witness hit is checked again
against the actual upper graph, so neither witness mechanism can
reject from a set containing an edge of that upper graph.
