# Maximum-square rooted R(3) cover

This is an alternative to, not a deletion from, the 110 remaining
**minimum**-square root-swap representatives. No minimum-root clause
may be carried over without checking its premises.

## Hand reduction

For a regular triangle-free graph with degree `d`, order `n`, alpha at
most `d` and codegrees at most 3, put `h1(v)` equal to the number of
nonneighbors of `v` with codegree one. No nonneighbor has codegree zero:
otherwise that vertex together with `N(v)` is an independent `d+1`.
Writing `L = n-1-d`, the two-walk count and `h1+h2+h3=L` give

```
Q(v) = sum_nonadjacent_x binom(codeg(v,x), 2)
     = 2*d*(d-1) - 3*L + h1(v) = B + h1(v).
```

`Q(v)` counts squares through `v`. If `q(e)` is the number of squares
through edge `e`, then `sum_{e incident v} q(e)=2*Q(v)`.
Root at an edge `uv` where `q` achieves its global maximum `m`.
Then `m >= ceil(2*B/d)` and all vertices satisfy
`h1(v) <= floor(d*m/2)-B`. At `(40,9)`, `B=54`, so
`m` is in `12..16`. If `m=12`, all codegrees on nonedges are 2
or 3, and **every edge** is on exactly 12 squares. Each possible
`m` is a disjoint class of unrooted graphs. Different maximizing edges
can have nonisomorphic kernels; the kernels within a class are a
cover, not a disjoint partition of unrooted graphs.

As in Sec. 8, `F=G[N(u)-v,N(v)-u]` has `q(uv)` edges, max degree at
most 2, and a matching of size at least `d-2` since `alpha(F) <= d`.
Use the path/cycle component signatures in `ENCODING.md`. If
`n < 6d-12`, the incidence inequality in `SATURATED_BICLIQUE.md`
excludes `K3,3`, hence a square in `F`. The component generator lists
one signature modulo side swap. This is an exact finite cover of the
admissible rooted kernel types, not an assertion that they extend.

## Necessary mask rows

Fix the rooted graph `K`, write `X` for its complement, and `p_M` for
the multiplicity of outside mask `M=N(x) intersect K`. For a fixed
edge `ab` of `K`, set `A=N_K(a)-b`, `B'=N_K(b)-a` and
`Y=N_X(a)`, `Z=N_X(b)`. The outside sets are independent and disjoint.
Put `D=|E_K(A,B')|`. The full count is

```
q(ab) = D + sum_M p_M ([a in M]*|M intersect B'|
                        + [b in M]*|M intersect A|) + |E_X(Y,Z)|.
```

Bound the last term below by `max(0, |Y|+|Z|-d)`: deleting one endpoint
per `Y--Z` edge leaves an independent set. This is an exact linear
bound since the two endpoint degrees in `K` fix `|Y|,|Z|`. For a fixed
independent seed `I` in `K` omitting `a,b`, the same argument gives
`|E_X(Y,Z)| >= |(Y union Z)-N(I)| + |I|-d`. Encode that padded variant
only on seeds of size at least `d-1`. When one endpoint is a root the
last edge term is zero, so the two-root and root-to-anchor rows are
also exact lower bounds when every edge attains `m`. The roots'
singleton counts are exactly opposite isolates plus the multiplicity
of singleton masks on their respective side. For `h1(v)=0`, enforce
the floor 2 at every fixed nonedge. All rows are needed only for
graphs rooted at a maximizing edge, except when explicitly stated.

## Exact split inside a fixed max12 kernel (`hand`)

There are no isolated vertices in F; each side has four vertices of
each degree 1 and 2. The 22 outside vertices have 52 attachments per
side, all of sizes two or three. Thus exactly eight on each side
have size three. With `k` the number having size two on both sides,
the (22,23,32,33) mask counts are `(k,14-k,14-k,k-6)`, where
`6 <= k <= 14`. The degree counts `(d_X=3,4,5)` in X are
`(k-6,28-2k,k)` and `e(X)=47`.

Let `z` be the sum of outside codegrees of pairs of anchors on the
same side that have a common F-neighbor. There are eight such pairs
in total and `0 <= z <= 8`. Then the exact number of squares in X is
`2k-4-z`. To see this, give an edge of G weight +1 inside K or X
and -1 across the cut. The sum of weight times square count is
`4*(C4(K)+C4(X)-C_alt)`, since a square contributes +4 if internal,
-4 if alternating between K and X, and zero otherwise. Here it is
`12*(29+47-104)=-336`. The kernel has 20 squares: 12 through the
old root edge and eight through one root and two neighbors of a
degree-two F vertex, with none contained in F.

Count `C_alt` by its two opposite vertices in K. Opposite-side
nonedges between anchors number 52 and have no common K neighbor.
Each has two or three common X neighbors, so the contributions are
twice their outside codegree minus three. Their outside-codegree
sum is `sum |M_left|*|M_right|=114+k` and they contribute `72+2k`.
For same-side anchor pairs, 48 have exactly one common K neighbor
and eight have two; the latter contribute zero. The same-side
outside-codegree sum is 76, giving contribution `76-z-48=28-z`.
No pair including a root can contribute. The equality follows.
The signed counting identity is independently replayed on all 13
labelled smaller outputs by `check_max_root.py`.

## Pilot budget

An 11-key stride sample took 12.88 CPU-s for the base projection and
14.87 CPU-s with the matching rows (2 exact infeasible, 9 feasible).
Linear extrapolation for the 111 matching keys is about 150 CPU-s;
this is only a projection-cost estimate. Cap the finite scan at 330
CPU-s and wall at 900 s. The original all-seed padding sample reached
its wall cap without completing even one key, so do not scale it.
The projection's feasibility does not imply a graph. Exact integer
Farkas arithmetic is rechecked separately; report new projection
exclusions as enum pending an independent audit of the rows and cover.

## Outside-star pilot budget

Two matched stride samples reject 19/36 and 11/41 masks on keys 22
and 34. Extra independent-seed rows reject none beyond the base test
on these samples and take 24.79/19.86 CPU-s instead of 11.83/6.35.
Do not scale the seed rows. Without symmetry, first-pass extrapolation
is about 366/196 CPU-s; exact color-preserving orbits reduce the
number of solved representatives. For the two-key pilot, bound each
full orbit and fixed-point run at 450 CPU-s and 1,020 wall seconds.

The full key-22 and key-34 passes used 57.0 and 17.9 CPU-s for 147 and
81 initial orbits, including the final LP. Use 0.40 CPU-s/orbit as a
linear planning estimate, not a guarantee. The next six distinct keys
(19, 20, 21, 23, 25, 33) total 1,437 initial orbits (~575 CPU-s);
cap each at 270 CPU-s and 600 wall seconds. Do not count incomplete
orbit traces as coverage. Evidence logs: `scratch/D/outer_star_batch/`.

Key 22's exact trace eliminates 105 orbit representatives. The C16
proof replay checked both smaller UNSAT orbits. For key 22, allow
360 CPU-s in the replay driver, 23 CPU-s per solver/checker child,
900 wall seconds total and 16 MiB per generated proof. The 54.26 CPU-s
SAT scan (including viable orbits) is the scale anchor; checking and
solver-version changes could increase it. This checks local DIMACS
refutations, not the missing Sec. 7 input-encoding bridge.

The six-key scan completed in 367.3 CPU-s for 1,437 initial orbits.
Scanning the remaining eight keys (4,701 initial orbits) therefore
projects to about 1,200 CPU-s. Cap each key at 320 CPU-s and 480 wall
seconds, one worker initially. A target LP pilot on 19, 21, 34 shares
the other slot, limited to 70 CPU-s per matched probe.

The matched LP pilot took 2--3 CPU-s at the two highly symmetric keys
and hit its internal 15-second LP limit at key 21. Unfiltered transport
with rounded duals safely checked key 19; the extra star-cap rows put
two of four probes over the LP cap, so use the simpler variant in the
first unfiltered sweep. Plan ~320 CPU-s for 16 keys, 70 CPU-s and 100
wall seconds per key (LP-internal limits still apply).
