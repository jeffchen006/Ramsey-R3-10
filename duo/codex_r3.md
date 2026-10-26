**The proposed degree/extension type is too coarse. I can rule it out exactly. A richer remainder type is still open.**

**1. Uniform weights: an obstruction and a precise synthesis LP**

Take
\[
H=C_{35}(1,7,11,16)-\{0,2,4,6,12\}-\{19,20\},
\]
using circulant labels. For independent \(T\), define
\[
\tau(T)=\bigl(|T|,\operatorname{sort}(d_H(T)),E_8(T)\bigr),
\]
where \(E_8(T)\) counts independent eight-sets containing \(T\).

I aggregated your rows of sizes \(4,\ldots,8\) by this type. The resulting relaxation is **feasible**, with:

- all 30 vertex degree equalities retained separately;
- all individual bounds \(0\le z_S\le1\) retained;
- 1,117 variables and 1,411 row types.

I reconstructed and checked an exact rational solution. It has 66 nonzero entries and common denominator
\[
84\,158\,218\,772\,527\,566\,240\,533\,544.
\]
Its mass is exactly nine.

**Consequence.** No certificate whose \(w_T\) depends only on this \(\tau(T)\) can exclude this \(H\). This remains true even if the certificate uses arbitrary vertex multipliers for the degree equalities.

**Proof.** The reconstructed vector satisfies, for each type \(\tau\),
\[
\sum_{T:\tau(T)=\tau}\sum_{S\cap T=\varnothing}z_S
\le (9-|T|)\#\{T:\tau(T)=\tau\}.
\]
Every weighting constant within each type is a nonnegative combination of these aggregate inequalities. The feasible vector prevents a contradiction.

**Reproduction:** construct the displayed \(H\), aggregate the rows from `adv6.build(H,(4,5,6,7,8))` by \(\tau\), and solve with the original degree equalities and bounds. For exact verification, recover the active basis and solve it over \(\mathbb Q\).

A stronger type worth testing is
\[
\tau(T)=\bigl(|T|,\operatorname{sort}(d_H(T)),[X_T,d_H|_{X_T}]\bigr),
\qquad X_T=H-N_H[T].
\]
The last entry is the isomorphism type of the remainder, with vertices coloured by their degrees in \(H\). For \(t=4,\ldots,8\), its maximum order is respectively
\[
13,\ 8,\ 5,\ 2,\ 0.
\]
Thus this uses bounded, small Ramsey remainders.

Here is the **shared-coefficient LP**. Define
\[
C_\tau(H,S)=\#\{T:\tau(T)=\tau,\ T\cap S=\varnothing\},\qquad
N_\tau(H)=\#\{T:\tau(T)=\tau\}.
\]
Choose shared coefficients \(w_\tau\ge0\), free degree coefficients \(a_d\), and upper-bound coefficients \(u_\sigma\ge0\), where \(\sigma(S)\) is a chosen type of eight-set. Require
\[
\sum_\tau C_\tau(H,S)w_\tau
+\sum_{y\in S}a_{d_H(y)}+u_{\sigma(S)}\ge0
\tag{A}
\]
for every \(S\), and
\[
\sum_\tau(9-t_\tau)N_\tau(H)w_\tau
+\sum_y(9-d_H(y))a_{d_H(y)}
+\sum_Su_{\sigma(S)}\le-1.
\tag{B}
\]

**Proof of sufficiency.** Sum the gluing inequalities, degree equalities, and \(z_S\le1\) bounds with these coefficients. Condition (A) makes the combined left side nonnegative. Condition (B) makes its upper bound negative.

**Test instructions:** impose (A)–(B) simultaneously on your 1,209 graphs, with one shared coefficient vector. Start with the eleven level-four hard graphs. An infeasible shared LP rejects that type choice. A feasible shared LP supplies only candidate weights: proving (A)–(B) for every admissible \(H\) remains the essential, unproved step. Testing a finite training family is not a uniform proof.

**2. Harder adversaries: dual neighbourhoods from almost regular 39-vertex graphs**

Use a known \((3,10;39)\)-graph \(G\) with degree pattern
\[
8^9\,9^{30},
\]
and choose a degree-eight vertex \(v\) whose eight neighbours all have degree nine. Set \(H=G-N[v]\).

Then
\[
|H|=30,\qquad e(H)=171-8\cdot9=99,\qquad \alpha(H)\le8.
\]

This family has an advantage over the \(C_{35}\) deletion family: it inherits **eight actual compatible independent eight-sets**
\[
S_x=N_G(x)-\{v\},\qquad x\in N_G(v).
\]
They satisfy every packing inequality at every level. Their coverage misses the target degree vector by exactly one on the eight other degree-eight vertices. Thus the target LP starts only one column short of an integral completion.

Concrete inputs already present:

- `known39/out/sample1000_39.g6`: **42 rooted instances**; first is **line 433, vertex 0**.
- `known39/out/r2_seeds.g6`: **52 rooted instances**; first is **line 5, vertex 0**.

Line numbers are one-based; vertex labels are zero-based. Deduplicate the resulting \(H\).

**Test instructions:** extract these neighbourhoods and run levels \(4,\ldots,8\). Prioritize graphs where the eight remaining degree-eight vertices span few edges. Then apply degree-preserving two-edge switches to \(H\), retaining triangle-freeness and \(\alpha(H)\le8\), to leave the original construction family.

I tested the first instance from each file. Line 433 was excluded at level four. The line-5 instance reached a 30-second LP limit without a conclusion. I have not found a level-four survivor.