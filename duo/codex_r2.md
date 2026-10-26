I have one concrete new LP experiment. It detects an obstruction that the multicover test misses. I still cannot prove that it excludes every \(H\), or force a small published class.

**1. Test fractional gluing with seven-set and eight-set constraints.**

For \(H\in R(3,9;30,99)\), let \(\mathcal F\) be its independent eight-sets. Introduce \(0\le z_S\le1\), for \(S\in\mathcal F\). Require
\[
\sum_S z_S=9,\qquad
\sum_{S\ni y}z_S=9-d_H(y)\quad(y\in V(H)),
\]
and, for every independent \(T\subseteq V(H)\) of size seven or eight,
\[
\boxed{\sum_{S\cap T=\varnothing}z_S\le9-|T|.}
\tag{*}
\]

This is a necessary condition for every root of a nine-regular candidate.

**Proof.** The nine neighbours of the root give nine distinct independent eight-sets \(S_i\). Their incidences give the degree equations. If more than \(9-|T|\) selected sets avoid \(T\), their corresponding root-neighbours, together with \(T\), form an independent ten-set. Thus their indicator vector satisfies \((*)\).

The proposed research target is:

> **Unproved:** No \(H\in R(3,9;30,99)\) satisfies this LP.

A proof would close case R. It would require no integrality argument and no SDP solver.

I ran these read-only tests:

- On the first 40 graphs in `gluing/samp30_99.g6`, the eight-set inequalities alone bounded \(\sum z_S\) between **6.65048 and 7.92221**, even without degree equations.
- I converted all 40 dual solutions into integer certificates. For sample 0, nonnegative integer weights \(w_T\) satisfy
  \[
  \min_{S\in\mathcal F}\sum_{T\cap S=\varnothing}w_T=1\,000\,003,
  \qquad \sum_Tw_T=7\,467\,419.
  \]
  Nine selected sets would imply \(9\,000\,027\le7\,467\,419\), a contradiction.
- The analogue from \(C_{35}\), namely \(H\) on 26 vertices with 76 edges and independent seven-sets, gives optimum **8**, as required.
- A suitable root of a known 39-vertex graph gives an eight-set packing optimum **10.37745**, which permits the required nine.

These are sample results, not a bound on the number of surviving \(H\).

I also constructed an adversarial example. Using the labels in `data/graphs/mckay/r39_35.g6`:

1. Delete vertices \(\{0,9,12,19\}\).
2. Delete edge \(\{2,31\}\).
3. Delete vertex \(20\).

The resulting \(H\) has 30 vertices, 99 edges and \(\alpha(H)\le8\). It **passes the fractional multicover plus eight-set inequalities**. Its disjointness graph has ten isolated vertices. Thus a universal claim based only on the eight-set packing bound is false.

However, adding the seven-set inequalities excludes it. With vertex capacities \(\sum_{S\ni y}z_S\le9-d_H(y)\), the maximum selected mass is **8.94526309**. I obtained an integer dual certificate giving
\[
\sum_S z_S\le \frac{8\,945\,370}{1\,000\,007}<9.
\]

This example separates the proposed test from the pair constraints.

There is a useful reduction in the seven-set rows. If \(T\) has two extensions \(a,b\) to maximum eight-sets, then \(ab\) is an edge. Every independent \(S\) avoids at least one endpoint. Adding the rows for \(T+a\) and \(T+b\) proves the row for \(T\). Those rows are redundant.

Do **not** retain only maximal seven-sets. The adversarial example has eight such sets, and their rows do not exclude it. Its seven-sets with a unique extension matter.

**Test for CPUs 68–71.** Generate several hundred adversarial \(H\) from deletions and edge deletions of \(C_{35}\). Test \((*)\), then add six-set rows with right-hand side three if needed. Search actively for a fractionally feasible example.

With all independent \(T\) and binary \(z\), these constraints describe exact regular gluing. The question is whether the fractional relaxation already fails universally at the seven-set level, or shortly below it.

This LP is slower than the 3 ms gluer. Its potential value is a uniform weighted inequality that proves non-gluability. It is not a faster enumeration filter.

**2. The overlap method has an exact degree equation, but it loses Angeltveit’s exact hash match.**

For a nonadjacent pair, retain \(C,A,B,X\) and \(c=|C|\). Let \(h_1(x),h_2(x)\) be the degrees of \(x\in X\) in the two proposed dual neighbourhoods. Then the missing number of \(C\)-neighbours is
\[
\boxed{q_x=9+d_X(x)-h_1(x)-h_2(x).}
\]
Necessarily,
\[
0\le q_x\le c,\qquad \sum_{x\in X}q_x=7c.
\]

Moreover, \(q\) must be the incidence sum of **\(c\) independent seven-sets of \(X\)**. These are the neighbourhoods in \(X\) of the vertices of \(C\).

This explains the difficulty with copying [Angeltveit’s §5 method](https://arxiv.org/html/2401.00392v2). When \(c=0\), the degree vector determines its compatible partner exactly. Here, the partner depends on an unresolved incidence vector \(q\).

There is a stronger restriction for \(c=6\). Let \(U\) be the union of those six seven-sets. Since \(C\) is independent,
\[
X_C=A\cup B\cup(X-U),\qquad \alpha(X_C)\le3.
\]
Hence \(|X_C|\le8\), so
\[
|U|\ge24.
\]
Thus at most two coordinates of \(q\) can be zero. This is substantially stronger than merely checking \(q_x\in[0,6]\).

The input counts remain problematic:

| Pair type | Necessary \(X\) | Input count |
|---|---|---:|
| \(c=7\) | \(R(3,8;27,85)\) | 4 |
| \(c=6\) | \(R(3,8;26,75\ldots81)\) | 1,765,856 at edges 75–77; about \(1.9\times10^9\) including 78–81 |
| \(c\le5\) | Smaller, less restricted overlaps | Large ranges lack published counts |

The 75–77 counts are published in GR2013. The estimate through 81 is the team’s MCMC estimate. Exact counts at 78–81 and extension counts \(X\to H\) are missing.

Nothing established forces \(c\ge6\). A feasible pair-count assignment is
\[
n_2=360,\quad n_3=240,\quad C_4=540,\quad
g_2=18,\quad g_3=12.
\]
It places the overlaps at \((22,54)\) and \((23,57)\), outside the small published ranges. This is a feasible counting profile, not a graph.

A useful cost test is therefore to sample \(X\) at edges 75–81 and measure extension-bin sizes **after requiring realization of \(q\)** by six independent seven-sets covering at least 24 vertices. Counting degree-vector matches alone will underestimate the work.

Finally, I strengthened the global profile LP using all **1,030 exact \(R(3,5)\) types, including the empty graph**, and the identities
\[
\sum_S i_t(X_S)=\binom{5+t}{t}I_{5+t},\qquad t=1,\ldots,4.
\]
It remained feasible when all four proposed tight types were forbidden, for each codegree cap 3–7, even with the pair constraints and \(n_1\le160\).

The analogue tests also caution against forcing the larger tight sets: \(C_{35}\) has 210 tight four-sets with remainder \(C_{13}\), but its three-set remainder reaches only 16, below 17. None of the ten regular 22-vertex examples has the tight \(C_{13}\) analogue.

I would spend the next few CPU-hours trying to refute the fractional-gluing target in item 1. It has exact sample certificates, valid controls, and a structured example that requires the next level of constraints.
