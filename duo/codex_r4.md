I can prove a stronger conditional result: **every nonregular `sel` case has at least 13 degree-9 vertices with \(e(H_v)\le98\)**. This forces adjacent roots. It does not produce a small catalogue.

Degree 10 is impossible: its neighbourhood would be an independent 10-set.

**1. Excess forcing**

Assume \(e(G)\ge167\), degrees lie in \(6,\ldots,9\), and the `sel` exclusions give
\[
e(H_v)\ge L_{d(v)},\qquad
(L_6,L_7,L_8,L_9)=(122,113,100,91).
\]
Thus, the result is conditional on those exclusions.

Put
\[
(a,b,c)=(n_8,n_7,n_6),\quad
N=a+2b+3c=360-2e,\quad q=N/2,\quad n=n_9.
\]
Let \(m=\#\{v:d(v)=9,\ e(H_v)\le98\}\).

The excess identity gives
\[
\boxed{\quad
m\ge
\left\lceil\frac{4a+22b+38c}{\min(8,q)}\right\rceil .
\quad} \tag{1}
\]
Indeed, an 8-, 7-, or 6-vertex contributes at least \(4,22,38\) to
\(e(H_v)-d(v)(20-d(v))\). A degree-9 vertex contributes at least
\(-\min(8,q)\). Only the \(m\) selected vertices can contribute negatively.

Here is the additional structure that strengthens (1). Let \(D\) contain all vertices of degree below 9. Since \(\alpha(G[D])\le9\),
\[
e(G[D])\ge\max(0,a+b+c-9).
\]
Consequently,
\[
e(G[C_9])\ge
E_0:=\frac{9n-8a-7b-6c}{2}+\max(0,a+b+c-9). \tag{2}
\]

Call a degree-9 vertex *bad* if \(e(H_v)\ge99\). Its neighbours in \(D\) have total deficiency at least \(q\). Let \(k\) be the smallest number of entries from
\[
\underbrace{3,\ldots,3}_{c},
\underbrace{2,\ldots,2}_{b},
\underbrace{1,\ldots,1}_{a}
\]
whose sum reaches \(q\). Each bad vertex has at most \(r=9-k\) neighbours in \(C_9\).

Mantel’s bound, applied to the \(m\) selected vertices, now gives
\[
e(G[C_9])\le
\min\left\{
\left\lfloor\frac{9m+r(n-m)}2\right\rfloor,\,
\left\lfloor\frac{m^2}4\right\rfloor+r(n-m)
\right\}. \tag{3}
\]
If \(r<0\), no bad vertex exists. If \(r=0\), at most nine bad vertices exist.

**Exact finite check.** Enumerate \(0<N\le26\), with \(N\) even. Equations (1)–(3), with \(m\le12\), leave only \(m=12\) and
\[
(a,b,c)\in
\{(12,1,0),(14,1,0),(16,1,0),(18,1,0),
(10,2,0),(12,2,0),(11,0,1),(13,0,1)\}.
\]

These eight cases also fail:

- For \(b=1,\ a=12,14,16\), the 7-vertex has at least \(q-4\) neighbours in \(D\). The bound
  \(\alpha(D)\ge |D|-1-e(D)+d_D(v)\)
  improves \(e(D)\) to at least \(a+q-13\). Equation (2) then gives \(76,62,48\) edges in \(C_9\). If \(m=12\), the bad vertices themselves need at least \((n-m)-9\) edges. Subtracting these from the second bound in (3) gives upper bounds \(75,58,45\): contradictions.
- For \(b=2,\ a=10,12\), the two 7-vertices force
  \[
  \sum_{x\in D}(9-d(x))d_D(x)\ge6q-32.
  \]
  Count their required deficiency, allowing their mutual edge. The total deficiency received by \(C_9\) then bounds \(m\) below by \(14,13\).
- For \(c=1,\ a=11,13\), the 6-vertex similarly forces the displayed sum to be at least \(4(q-4)\). This gives \(m\ge15,13\).
- For \((a,b,c)=(18,1,0)\), every bad vertex must meet the 7-vertex. That vertex needs six neighbours in \(D\), so it has at most one degree-9 neighbour. Hence \(m\ge20\).

I verified this complete check with integer arithmetic in a read-only script. It proves **\(m\ge13\)**; I do not claim optimality.

Among any 13 selected vertices, at least four edges exist: otherwise deleting one endpoint per edge leaves an independent 10-set. Triangle-freeness also guarantees a nonadjacent pair.

The catalogue remains large. GR2013 gives minimum edge counts \(86,95,104,118\) for orders \(30,31,32,33\). Its small catalogues include:

| Order, edges | Count |
|---|---:|
| 30, 86 | 1,800 |
| 30, 87 | 147,335 |
| 31, 95 | 560 |
| 31, 96 | 35,154 |
| 32, 104 | 39 |
| 33, 118 | 5 |

Source: [local GR2013 text, Tables 4 and 14](./runs/lit/txt/arxiv_1210.5826.txt), [paper](https://arxiv.org/abs/1210.5826). The `sel` assumptions exclude these catalogues. The forced catalogue \(R(3,9;30,\le98)\) has an **estimated** \(2\times10^{17}\) graphs.

**2. The forced adjacent overlay**

Choose adjacent selected vertices \(u,v\). Set
\[
A=N(u)\setminus\{v\},\quad B=N(v)\setminus\{u\},\quad
X=V(G)\setminus(N(u)\cup N(v)).
\]
Then \(|A|=|B|=8\), \(|X|=22\), and
\[
H_u=G[B\cup X],\qquad H_v=G[A\cup X].
\]
The shared graph \(G[X]\) has independence number at most **8**.

An overlay fixes all 40 vertices and every edge except the **64 possible \(A\)-\(B\) edges**. SAT must enforce degrees and exclude independent 10-sets. Triangle-freeness simply forbids \(ab\) whenever \(a,b\) have a common neighbour in \(X\). Check degree feasibility by flow before SAT.

For catalogue size \(K\), the raw unordered graph-pair count is approximately \(K^2/2\):

- \(K=1800\): \(1.6\times10^6\).
- \(K=149135\): \(1.1\times10^{10}\).
- \(K\approx2\times10^{17}\): \(2\times10^{34}\).

These are **raw counts**, not overlay estimates. One must select independent 8-sets, match the remaining 22-vertex graphs, and quotient the matches by automorphisms. Published counts do not give those overlap multiplicities. Symmetry supplies no guaranteed large divisor.

**Cheap test:** hash each pointed record \((H,B)\) by the canonical form of \(H-B\). Count matching pairs within each hash bucket. Decide a sample using the 64-variable completion. This measures both costs directly. The team’s present bottleneck is catalogue generation, so fast completion alone does not solve it.

**3. The regular case**

Two relevant identities are
\[
\sum_{\{u,v\}\notin E}e(G-N[u]-N[v])=35280-4C_4,
\]
and
\[
\sum_v i_8(H_v)=9i_9(G).
\]
Here \(C_4\) counts 4-cycles and \(i_s\) counts independent \(s\)-sets. The second identity counts an independent 9-set with one distinguished vertex.

Neither right-hand side is fixed by regularity. The existing pair LP already permits broad codegree distributions. These identities therefore provide no proved forcing into a small catalogue.

The new 13-vertex bound makes an adjacent overlay available in every nonregular `sel` case. **It does not remove orders of magnitude from the current search. The 9-regular case remains beyond the methods established here.**