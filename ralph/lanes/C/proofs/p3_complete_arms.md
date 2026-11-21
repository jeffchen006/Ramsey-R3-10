# A three-root component cannot have both cross-edge counts nine

Use the notation and established partition of `path_three.md` for a
three-root path in R(6). In particular the three roots are independent,
their exterior diagonal has codegree s in {3,4,5}, and every common
neighbour of the two exterior roots lies in T, the intersection of
all three neighbourhoods. Write the three open neighbourhoods as

    N(v0) = T + Y + B0,
    N(v1) = T + B0 + B2 + B1,
    N(v2) = T + Z + B2.

Here the disjoint wings Y and Z each have size three, T has size s,
and B1 has size s-3. The residue X has 22 vertices. Suppose both
incident codegree-six pairs have cross-edge count nine. Then the two
3-by-3 blocks Y--(B2+B1) and Z--(B0+B1) are complete.

If s is four or five, a vertex of B1 sees all of Y and Z. Triangle
freeness leaves no Y--Z edges. Also T is independent and anticomplete
to both wings, since T+Y and T+Z lie in root neighbourhoods. Thus
T+Y+Z is an independent set of size s+6 >= 10, impossible.

Suppose s=3. Let D be the vertices of X with no neighbour in T. Every
vertex of T has only its three root neighbours in the boundary:
every other boundary vertex shares a root neighbour with it. Therefore
there are 3*(9-3)=18 edges from T to X, and |D| >= 22-18 = 4.

Every x in D avoids Y and Z as well. Indeed, if x sees Y, it avoids
B2 and B1 by triangle freeness. Since N(v2) is an independent
nine-set, x must hit it, hence must see Z. This forbids B0 as well.
Now x avoids the independent nine-set N(v1), a contradiction. The
opposite orientation gives the same conclusion for Z. This argument
works for any s, and only uses independence, not maximality.

The edge identity from `path_three.md` is e(X)=45+9+9+b with
b=e(Y,Z). By the critic-confirmed diagonal-three upper bound
e(X)<=64 (`ralph/critic/round_004.md`, based on the 35 checked e65/e66
residues), b<=1. Choose an independent five-set of Y+Z: if its only
possible edge is present, discard one of its endpoints; otherwise
discard any one vertex. Together with T this gives an independent
eight-set anticomplete to D. The triangle-free graph on at least
four vertices in D has a nonadjacent pair (indeed, three vertices
would suffice). Adding that pair gives an independent ten-set.

Thus **every P3 in R(6) has at least one incident pair with cross-edge
count at most eight**. In particular, in the global f*=9 subcase the
nonempty codegree-six graph has no P3 and is a matching (using the
accepted no-P4 result). This does not exclude that matching subcase.
The proof's new argument is hand; the R(6) corollary is composite
because it uses the accepted diagonal-three e65/e66 certificate.

## General complete-arm inequality and calibration

The argument applies if the roots have degree d, max degree is at
most d, alpha <= d, and the same seven-block form applies (B1 may be
empty). For any independent set W of the wings, D has independence
number at most d-|T|-|W|, since T+W is independent and anticomplete
to D. Also |D| >= |X|-(d-3)|T|. Both inequalities are exact integer
conditions. `p3_complete_arms_check.py` verifies the hypotheses and
inequalities on the known smaller regular graphs supplied, and on
positive and corrupted degree-four complete-arm controls for both
the zero-edge and one-edge wing cases.
