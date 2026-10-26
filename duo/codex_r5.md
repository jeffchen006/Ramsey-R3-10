**I can justify one new candidate worth testing. I cannot yet justify two methods with a one-day runtime.**

First, the 7-regular, 27-vertex calibration is empty: \(27\cdot7\) is odd. Use the full 27-vertex census or the 7-regular, 28-vertex UNSAT case.

**1. Best candidate: enumerate sparse edge kernels, then complete by SAT**

Let \(G\) be \(d\)-regular, triangle-free, with \(\alpha(G)\le d\). For an edge \(uv\), define
\[
A=N(u)\setminus\{v\},\quad B=N(v)\setminus\{u\},\quad F=G[A,B].
\]
The kernel consists of \(u,v,A,B\). Let \(g=e(F)\), and let \(M\) bound every nonadjacent codegree.

Three necessary conditions are exact:
\[
\Delta(F)\le M-1,\qquad \nu(F)\ge d-2,
\]
and some edge satisfies
\[
g\le
\begin{cases}
\lfloor6+3M/2\rfloor &(n,d)=(35,8),\\
\lfloor(64+20M)/9\rfloor &(n,d)=(40,9).
\end{cases} \tag{*}
\]
Here \(\nu(F)\) is the maximum matching size.

**Proof sketch.** For \(a\in A\), its degree in \(F\) equals \(\operatorname{codeg}(a,v)-1\). König’s theorem gives
\(\alpha(F)=2(d-1)-\nu(F)\le d\).

For the last bound, let \(t_1\) count codegree-one pairs. Within each neighbourhood, these pairs form a matching. Otherwise two such pairs sharing an endpoint produce an independent \((d+1)\)-set. Thus
\[
t_1\le n\lfloor d/2\rfloor.
\]
Writing \(S=nd(d-1)/2\) and \(P=n(n-d-1)/2\), convexity gives
\[
4C_4=\sum_{\text{nonedges}}c(c-1)
 \le(M+1)S-2MP+(M-1)t_1.
\]
Also \(\sum_{uv\in E}e(F_{uv})=4C_4\). Average over edges to obtain (*).

This forces a small search object. It does not require the answer to be \(C_{35}\).

For 35 vertices, split:

- **Maximum codegree at most four:** enumerate bipartite \(7+7\) kernels with maximum degree three, 6–12 edges, and matching size at least six. I counted **3,305** with nauty.
- **Codegree five occurs:** choose that pair. Its common non-neighbourhood \(X\) has 22 vertices and
  \[
  e(X)=52+g,\qquad g\le9.
  \]
  Since \(e(3,7,22)=60\), only \(e(X)=60,61\) remain: **seven graphs**, already present in `data/graphs/mckay/r37_22.g6`. Codegree above five is impossible by \(R(3,7)=23\). These counts are in [GR2013, Table 12](./runs/lit/txt/arxiv_1210.5826.txt), [paper](https://arxiv.org/abs/1210.5826).

For each edge kernel, SAT decides 437 remaining edge variables. Fix the 16 kernel vertices individually in SMS; permit permutations of the 19 remaining vertices. This avoids invalid symmetry clauses.

**Cost:** a one-day classification needs roughly a 20-second mean per kernel, leaving five hours for the seven other cases. This runtime assumption is **unproved**. I tested the unseeded kernel \(6K_2+2K_1\): SMS returned UNSAT in **3.7 seconds**. One sample does not establish the mean.

The scaling rule is explicit:

| 40-vertex codegree cap | Kernel degree cap | Edge bound | Kernel count |
|---|---:|---:|---:|
| 3 | 2 | 13 | **238**, after matching |
| 4 | 3 | 16 | 160,729, before matching |
| 5 | 4 | 18 | 4,234,442, before matching |
| 6 | 5 | 20 | not counted |

Each completion has 583 free edge variables. Codegree seven also has the existing four-graph \(X\) reduction. **This could make \(R(3)\) cheap. It does not yet make the whole regular case feasible.**

**2. Second candidate: canonical incidence search, with SAT completion**

Fix \(v\), its independent neighbourhood \(A\), and \(H=G-N[v]\). Represent each \(y\in H\) by
\[
J_y=N(y)\cap A.
\]
Search the incidence matrix first, modulo permutations of \(A\) and \(H\). Its rows have sum \(d-1\), and
\[
J_y\ne\varnothing,\quad d_H(y)=d-|J_y|,\quad
yz\in E(H)\Rightarrow J_y\cap J_z=\varnothing.
\]
The independence condition is exactly
\[
\alpha(H)\le d-1,\qquad
|T|\le\left|\bigcup_{y\in T}J_y\right|
\quad\text{for every independent }T\subseteq H.
\]
The proof extends \(T\) by all unused vertices of \(A\).

This is an exact formulation. However, I reject **complete incidence enumeration** as a separate build. The crude unfiltered quotient scale grows from about \(10^{15}\) patterns at 35 vertices to \(10^{23}\) at 40. SAT must prune during generation. No evidence supports a one-day prediction.

Use it only as an alternative completion backend for method 1.

My judgments on your options:

- **(a): accept the bounded edge-kernel version above.** An arbitrary pair kernel lacks the crucial edge bound.
- **(b): reject enumeration over all \(H\).** The catalogue explosion remains.
- **(c): test as a branching order.** Codegree profiles do not reduce the isomorphism classes. A new canonical order must replace, or respect, the existing SMS order.
- **(d): reject scalar spectral cuts.** Hoffman does not exclude either calibration. I have no stronger proved spectral cut.
- **(e): the new ingredient is the forced sparse edge kernel.**

**Six-hour test on three CPUs**

Generate the kernel lists with:

```text
genbg -D3 7 7 6:12
genbg -D2 8 8 7:13
```

Filter by matching size at least six and seven. The counts must be **3,305** and **238**.

- **CPUs 1–2:** exhaust all 35-vertex kernels and the seven codegree-five cases. Enumerate all completions and deduplicate with nauty. Do not seed from `r39_35.g6`; compare only after exhaustion.
- **CPU 3:** first validate the implementation on the ten 6-regular, 22-vertex graphs. Then exhaust the 238 kernels for 40 vertices with codegree cap three.
- Use degree, MTF, triangle and lazy independent-set constraints. Keep fixed kernel labels outside SMS permutations.

**Pass threshold:** complete the 35-vertex classification within 12 CPU-hours, recover the ten smaller controls, and finish the 238 regular-case kernels within six CPU-hours—or find a valid 40-vertex graph.

That would demonstrate a useful reduction. If these completion searches remain hard, I would stop before building the larger kernel catalogues.