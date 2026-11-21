# A degree-three anchor for an isolated codegree-six e80 pair

Use `isolated_pair.md` and its notation. Suppose the private wings Y,Z
lack exactly the single edge yz. With m=d-k, let x in the pair residue
X have d_X(x)=m. Then x sees y,z and exactly k-2 vertices of C, denoted
C_x. Write C_o=C\C_x, Y'=Y\{y}, Z'=Z\{z}, W=N_X(x), and
X'=X-(W+{x}). The roots u,v,x are independent. In particular
alpha(X')<=d-3. In the target, |X|=26, m=3 and |X'|=22, so the
same complete 191-class census applies, but this is not a P3 boundary.

For w in W, triangles at x forbid neighbours in C_x+{y,z}, and w
avoids u,v by belonging to X. The only possible neighbours of w
outside X are therefore in C_o+Y'+Z'. Here |C_o|=2 and each of
Y',Z' has size m-1. Since Y'--Z' is complete and a triangle is
forbidden, at most one wing contributes neighbours. Consequently

    d_X(w) >= d - 2 - (m-1) = k-1.

The removed vertices W+{x} contribute exactly sum(d_X(w), w in W)
to the number of edges lost from X: each edge xw is counted once,
and W is independent. Hence e(X')<=e(X)-m(k-1). At equality each w
has all two C_o neighbours and all neighbours in exactly one of
Y',Z'. All other boundary edges are now fixed: u,v meet their known
neighbourhoods, x meets C_x+{y,z}+W, the given Y--Z is complete
except yz, C has no edge to Y+Z, and W has the just-derived edges.
For m>=2, only the W split between the two wing types is undetermined.
Permutations in W and reversal of u,v identify splits kW and m-kW,
with no relabelling of the 22-vertex residue.

In the target (d,k,m)=(9,6,3) and e(X)=80. Thus e(X')<=65 and
there are exactly two allowed boundary templates at equality, three
same-side W vertices or a 2+1 split. The same-side template is
impossible: its two unmarked vertices of that wing have at least
seven common neighbours, namely their root, all three vertices of
the opposite wing, and all three W vertices. The missing edge yz
does not touch these unmarked vertices. Only the 2+1 template needs
checks against the e65 census. This does not apply to e80
pair residues without a degree-three vertex, to f=9, or to an edge
of a P3 component. The two roots u,v have codegree at most five
with all of X', but x need not: its cap is still six. The fixed
boundary Lite6 relaxation is valid with just that one cap override.

Calibration and exact scope:
- The 331 regular 21-vertex controls are filtered from lane B's
  checked (3,7;21) census with `pickg -q -d6 -D6`. On these controls
  (d,k,m)=(6,4,2) the same bound and equality shape can be compared
  pointwise to the actual induced graphs.
- `p2_anchor.py --control` checks the triangle/alpha premise, all
  matching isolated roots and low-degree anchors, and the actual
  equality boundaries. For maximal controls it checks the entire
  attachment assignment and a one-edge corruption.
