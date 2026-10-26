The bounds improve to
\[
\boxed{54\le Q\le87,\qquad 540\le C_4\le860.}
\]
These are necessary bounds. Attainability of the endpoints remains unproved.

**1. Histogram bounds**

Write \(h=(h_1,\ldots,h_7)\). Then
\[
q(v)=54+h_1+h_4+3h_5+6h_6+10h_7. \tag{1}
\]

The private-vertex argument gives **\(h_1\le9\) per vertex**, not eight. The matching argument inside each neighbourhood gives the separate global bound
\[
\sum_v h_1(v)\le320.
\]

Applying the trusted Ramsey bounds inside \(H_v\) gives stronger restrictions:
\[
h_7\le1,\qquad h_6\le2,\qquad
h_7>0\Rightarrow h_6=0,\ h_1\le7. \tag{2}
\]

Proof sketches:

- Vertices with root codegrees at least five are mutually nonadjacent: their neighbourhoods in \(N(v)\) intersect.
- Two degree-two vertices in \(H_v\), or degrees two and three, would leave at least 23 common non-neighbours. These would form a \((3,7)\)-graph, contradicting \(R(3,7)=23\).
- Two degree-three vertices in \(H_v\) must have disjoint neighbourhoods. Three would therefore leave 18 common non-neighbours, contradicting \(R(3,6)=18\). Thus \(h_6\le2\).
- If \(c(v,w)=7\), Lemma R7 makes the exclusive \(2\times2\) bipartite graph complete. Neither exclusive neighbour of \(v\) can own a private vertex: that vertex, the two exclusive neighbours of \(w\), and the seven common neighbours would give an independent 10-set. Hence \(h_1\le7\).

Here is an exact parameterization of the remaining histogram candidates:
\[
\begin{aligned}
h_3&=12+h_1-2h_4-3h_5-4h_6-5h_7,\\
h_2&=18-2h_1+h_4+2h_5+3h_6+4h_7.
\end{aligned}
\]
Enumerate \(0\le h_1\le9\), \(0\le h_6\le2\), \(0\le h_7\le1\), and nonnegative \(h_4,h_5\). Impose (2) and discard negative entries.

I verified **769 candidates** by integer arithmetic. They satisfy \(q\le78+h_1\), which proves \(Q\le87\) and
\[
4C_4=\sum_vq(v)\le40\cdot78+320=3440.
\]
These candidates are **not proved graph realizations**.

The smallest and largest lists are:

| \(Q\) | Candidate histograms |
|---:|---|
| 54 | \((0,18,12,0,0,0,0)\) |
| 85 | \((9,14,0,1,5,1,0)\), \((9,13,2,1,3,2,0)\) |
| 86 | \((8,16,0,0,4,2,0)\), \((9,14,0,2,3,2,0)\) |
| 87 | \((9,14,1,0,4,2,0)\) |

**2. The endpoint cubes have structure**

If **\(Q=54\)**, every vertex has the first histogram. Thus all nonadjacent codegrees are two or three, \(q\) is constant, and \(C_4=540\).

Every edge kernel then has minimum degree one and maximum degree two. Choosing a minimum incident kernel gives \(e(F)\le12\). Nauty produces only **49** bipartite \(8+8\) kernels satisfying these bounds and matching size at least seven. Reproduce with:

```text
genbg -d1 -D2 8 8 8:12
```

Then apply the matching filter. This is a modest reduction from 238 kernels, not a counting contradiction.

If **\(Q=86\) or \(87\)**, the root has two codegree-six partners \(a,b\). Their degree-three neighbourhoods inside \(H_0\) are disjoint. Therefore
\[
G-N[\{0,a,b\}]
\]
has exactly 22 vertices and independence number at most six. It belongs to the **191-graph \(R(3,7;22)\) catalogue**.

This is a genuine forced small seed class. Its extension space remains unbounded by this argument.

Maximum \(q\) does **not** imply constant \(q\). In particular, \(Q=87\) cannot be constant because the mean is at most 86. If \(C_4=860\), equality forces every vertex to have
\[
h=(8,16,0,0,4,2,0),\qquad q=86.
\]

**3. Compatibility with the edge kernel**

The exact identity is
\[
\boxed{\sum_{w\in N(u)}e(F_{uw})=2q(u).}
\]
Each 4-cycle through \(u\) contributes to its two incident edges.

Consequently, after choosing a maximum-\(q\) root,
\[
\boxed{\min_{w\in N(u)}e(F_{uw})\le\lfloor2Q/9\rfloor.}
\]

You may impose “maximum-\(q\) root, then minimum incident kernel.” You cannot also claim that this edge minimizes kernels globally.

For example, in \(R(3)\), \(Q=63\) gives incident bound 14, whereas the global minimum-edge bound is 13. Taking their minimum at the same anchored edge is unjustified. Alternatively, retain a separate maximum-\(q\) vertex and global minimum edge.

For \(Q=87\), \(h_1=9\) also forces exactly one isolated vertex on the \(N(w)\setminus\{u\}\) side of every incident kernel.

**4. The 35-vertex benchmark**

For the known graph:
\[
h=(8,12,0,6,0),\qquad q=48,\qquad C_4=420.
\]
Every edge has \(e(F)=12\). Each kernel side has degrees
\[
(0,1,1,1,3,3,3).
\]

Without assuming uniqueness, analogous local arguments give \(35\le Q\le48\). The lower endpoint 34 is impossible: it would force every \(q=34\), but \(35\cdot34\) is not divisible by four.

The known graph therefore lies only in cube \(Q=48\). Maximum-\(q\) root selection removes no root choices because all vertices tie. The other cubes still require refutation.

The recorded hour-long kernel timeouts remain decisive: none of these smaller lists yet establishes a practical runtime cut.