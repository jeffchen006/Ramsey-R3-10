# Literature scout — 2026-11-21

## Status and data

- **Open in the sources found:** the best established bounds are **40 ≤ R(3,10) ≤ 41**. See Radziszowski, *Small Ramsey Numbers*, EJC DS1 rev. 18, **April 24, 2026**, Table Ia and §2.1, DOI `10.37236/21` ([current survey PDF](https://www.combinatorics.org/ojs/index.php/eljc/article/download/DS1/pdf/0)). Searches through November 21 found no later resolution. The November 5 TCSExam preprint independently gives a recent dated snapshot at the same interval, not a new mathematical proof.
- **39-vertex census is partial, and I found no public bulk download.** Angeltveit journal §7 reports 39,745,077 from his initial project/one-point expansions, 43,117,868 supplied by GR, 43,146,537 after union and one-point expansion, and **at least 43,225,483** after two-/three-point expansions. The last is the journal figure; arXiv v2 §7 stops at 43,146,537. The acknowledgements describe a file shared with Angeltveit, not a public deposit. Checked the journal article/PDF, arXiv metadata, McKay and HoG catalogs, and exact-count/graph6 searches. Neither GR's claim about its earlier 37M+ graphs (Berlin 2012 talk, slide 17) nor Angeltveit's §6 gluing run certifies the non-extendibility of the entire journal census. Even a check of that census would not imply nonexistence at 40.
- **No new exact count located for `R(3,9;30,e)`, `e ≥ 88`** in the relevant range through 99. GR Table 14 gives 1,800 at 86 and 147,335 at 87, and no 30-vertex count at 88. Angeltveit's new complete input classes are at *32, 33, 34*, not 30. His statement about `(30,99)` is qualitative; the repo's sampling estimates are not enumeration. The report's `t9_88` work in progress is not a published count.
- **Public calibrations:** [McKay's Ramsey data](https://users.cecs.anu.edu.au/~bdm/data/ramsey.html) links `r37_22.g6` (191), `r38_27.g6.gz` (477,142), and `r39_35.g6` (1), but no 39-vertex `(3,10)` bulk class. [House of Graphs minimum-edge catalog](https://houseofgraphs.org/meta-directory/minimal-ramsey) links `data/ramsey/minramsey/Ramseygraphs_3_9_30_e86.g6` (1,800), `Ramseygraphs_3_8_27_e85.g6` (4), and other minimum classes. It does not list 30/87 or 30/88. Exoo's [39-vertex witness file](https://cs.indstate.edu/ge/RAMSEY/r3.10.39) is the **complement** adjacency matrix (`notes/known39.md`); a single reproducible seed, not a census.

## Primary papers, artifacts, and scope

| Source | Result relevant here; what it does **not** prove |
|---|---|
| Geoffrey Exoo, *On Two Classical Ramsey Numbers of the Form R(3,n)*, SIAM J. Discrete Math. **2**(4), 488–490 (1989), DOI `10.1137/0402043`, Thm. 1 | Explicit `(3,10;39)` construction; still the established lower bound 40. |
| Jan Goedgebeur and Stanisław P. Radziszowski, *New Computational Upper Bounds for Ramsey Numbers R(3,k)*, EJC **20**(1), #P30 (2013), [arXiv:1210.5826v4](https://arxiv.org/abs/1210.5826v4), Tables 5, 12–15 and §6 | Minimum-edge tables, isomorphism class counts, and `R(3,10) ≤ 42` replaced by Angeltveit. The gluing proof checks the 2,104,151 `(3,9;32,108)` inputs for regular 42-vertex extensions. [Berlin 2012 slides](https://www.cs.rit.edu/~spr/PUBL/ber12.pdf) give the earlier 39-vertex extension test. |
| Vigleik Angeltveit, *R(3,10) ≤ 41*, EJC **32**(4), #P4.30, **November 3, 2025**, DOI `10.37236/12936`, [arXiv:2401.00392](https://arxiv.org/abs/2401.00392) (v1 Dec 31, 2023; v2 Apr 8, 2024; no v3 located) | Prop. 2 and §§3–6 reduce 41 vertices to glued classes of `(3,9;32,≤112)` **1,554,928,360**, `(3,9;33,≤121)` **14,395**, `(3,9;34,≤130)` **5**. McKay independently checked completeness of the first class. §7 and Table 1 update the 39-vertex census. The odd-order argument used at 41 does not remove 9-regular 40. |
| Markus Kirchweger and Stefan Szeider, *SAT Modulo Symmetries for Graph Generation and Enumeration*, ACM TOCL **25**(3), Article 18, 1–30 (2024), DOI `10.1145/3670405` | Dynamic lexicographic symmetry breaking for isomorph-free graph generation; solver architecture, not a new `(3,9;30,e)` count. |
| Zhengyu Li, Conor Duggan, Curtis Bright, Vijay Ganesh, *Verified Certificates via SAT and Computer Algebra Systems for the Ramsey R(3,8) and R(3,9) Problems*, IJCAI 2025, 2619–2627, DOI `10.24963/IJCAI.2025/292`, [arXiv:2502.06055v2](https://arxiv.org/abs/2502.06055v2), [code](https://github.com/ConDug/MathCheckRamsey) | Checked UNSAT for `R(3,8) ≤ 28`; for `R(3,9) ≤ 36`, Graver–Yackel reduces to excluding a 27-vertex `(3,8)` graph of 80 edges (271 in complement) with the stated degree bounds. Table 3: 19,811 and 697,575 CPU s solving, 22,328 and 473,874 CPU s checking. CAS clause checker and encoding not formally verified end to end. No `R(3,10)` decision. |
| Vigleik Angeltveit and Brendan D. McKay, *R(5,5) ≤ 46*, J. Graph Theory **112**(3), 198–208 (July 2026), DOI `10.1002/jgt.70029`, [arXiv:2409.15709v2](https://arxiv.org/abs/2409.15709v2) (Sep 1, 2025) | Independently implemented joins of local neighborhoods, LP and global gluing; methodological precedent, not a triangle-free census or bound on `R(3,10)`. |
| Dinesh Pandey and Peruvemba Sundaram Ravi, *On structural properties of some probable R(3,10)-critical graphs*, [arXiv:2601.03572v1](https://arxiv.org/abs/2601.03572v1), Jan 7, 2026 | §2 concerns the superseded possibility of order 41; §3 **does** address order 40. Claims diameter 2 or 3 and connectivity/min-degree properties at diameter 2 without deciding existence. The `|N(u)∪N(w)|≥11` condition for two distinct neighbors is already contained in the pair lemma. Use `notes/DEPENDENCIES.md` §7 for precise hypotheses, not the abstract alone. |
| Bernard Lidický and Florian Pfender, *Bounds on Small Ramsey Numbers by Semidefinite Programming*, SIAM Review **68**(2), 385–403 (2026), DOI `10.1137/25M1827554` | SIGEST presentation of finite flag-algebra/PSD upper bounds for small Ramsey problems. No `R(3,10)` decision or exact input census; relevant as a finite-SDP certificate template, not evidence the present LP is sufficient. |
| Ansh Nagda, Prabhakar Raghavan, Abhradeep Thakurta, *Reinforced Generation of Combinatorial Structures: Ramsey Numbers*, [arXiv:2603.09172v5](https://arxiv.org/abs/2603.09172v5), Apr 21, 2026, Table 1 and Algorithm 18 | Reports matching 40, not improving it. Algorithm 18 grows from `P29`, tries empty/complete/random new-vertex incidence, and globally anneals `#K3+#I10`. Possible cheap construction calibration; not a census or a reason to budget long replications. |
| Markus Kirchweger, Pablo Manrique Merchan, Stefan Szeider, *Formally Verified Graph Generation with SAT Modulo Symmetries and Lean*, IJCAR 2026, LNCS **16688**, 117–135, DOI `10.1007/978-3-032-32589-1_8` (July 24, 2026) | End-to-end SMS/Lean framework for diameter-2-critical graphs, Turán numbers and cages. Useful for checking invariance and integrating certificates; no smaller-Ramsey census reported. |
| Stefano Coniglio, Fabio Furini, Ivana Ljubić, Pablo San Segundo, Johannes Thüerauf, Emiliano Traversi, *An Integer Programming Approach to Compute Lower Bounds for Ramsey Numbers Using Circulant Graphs*, [arXiv:2608.18769](https://arxiv.org/abs/2608.18769), Aug 19, 2026, §7.4; [author results and certificates](https://fabiofurini.github.io/ramsey-number-lower-bounds/known-numbers.html) | Reproduces **circulant** `R_C(3,10)=39` (38-vertex witness and search of remaining orders); this is not classical `R(3,10)=39`. Distance-projected IP and clique separation, with downloadable construction data. 38-vertex circulant graph can seed a bounded symmetry-breaking extension, but another full cyclic search duplicates prior work. |
| Yaqiao Li and Junyi Lin, *Online geometric matching and segments block points*, [arXiv:2610.23130v1](https://arxiv.org/html/2610.23130v1#S3.SS4), Oct 16, 2026, §3.4/Table 1 (accepted by IJTCS–FAW 2026) | Explicitly takes the two possible classical Ramsey values 40/41 as inputs and proves segment-blocking bounds in both cases. The segment count is not a new Ramsey graph construction. |
| Johannes K. Fichte and Stefan Szeider, *count-catcher: Lean Theorems from Model Counting Certificates*, [arXiv:2610.36196v1](https://arxiv.org/abs/2610.36196v1), Oct 26, 2026, §§1, 5.2; [code](https://github.com/leansolving/count-catcher), DOI `10.5281/zenodo.2330475` | Formally proves uniqueness of the `(3,5;13)` circulant and counts triangle-free graphs on ten vertices up to isomorphism via CPOG exact counts and Burnside. Relies on Lean native evaluation/compiler/runtime in addition to kernel. Useful independent small-case census calibration or count certification template; no `(3,9;30,e)` counts and not an immediate replacement for the R(7) proof trees. |
| Yifan Luo, Zhengying Liu, Yang Yuan, Zhilin Yang, Andrew Chi-Chih Yao, *TCSExam: Evaluating Frontier LLMs on the Full Range of TCS Research*, [arXiv:2611.07962v1](https://arxiv.org/abs/2611.07962v1), Nov 5, 2026; [task/results](https://moonshotai.github.io/TCSExam/tasks/ramsey-r3-10/) | Public construction task/checker for `(3,10)`; 100% is the order-39 reference, not a solution at 40. Paper table and task page report no gain for this problem. |

Asymptotic context only: Campos, Jenssen, Michelen and Sahasrabudhe, *A new lower bound for the Ramsey numbers R(3,k)*, [arXiv:2505.13371](https://arxiv.org/abs/2505.13371), improves the asymptotic constant to `1/3 + o(1)` in `k²/log k`. It gives no improved bound at `k=10` or finite input list.

Two later unrefereed reports are **leads only**: Unsolved Lab's [R(3,10) report](https://unsolvedlab.com/problems/ramsey-r310) (run closed Oct 1, 2026) describes symmetry cases, pentagon-matchings, degree-4 exclusion and counts estimated by sampling; `hraness/algal-lab` (Sep 28, 2026) is linked there for degree-4 and transitivity. The local report already tracks these, and no unverified web outcome is counted in this run.

## Implications for the lanes

| Lane | Action / boundary |
|---|---|
| A | IJCAR 2026 is the closest independent architecture for an end-to-end split/encoding/SB proof. `count-catcher` provides a checked small Ramsey census and a count/encoding separation example. Keep independent-set and cube-cover validation separate. |
| B | No new public 30/88 class or exact count to substitute. Use HoG 30/86 and GR 30/87 calibration, not an MCMC estimate. |
| C | Pair/diameter results mostly overlap local MTF/pair constraints; Angeltveit's 41-vertex argument cannot close regular 40. Sparse exact mask-count projection is a different test. |
| D | No public dense 30-vertex catalogue for an alternative to kernels. The SAT+CAS small-case certificates give an independent pipeline baseline, not coverage of any R(3) kernel list. |
| E | New independent IP confirmation excludes cyclic only; does not settle any noncyclic prime-action branch. Unsolved Lab runs are leads, not closures. |
| F | No 43M-file path identified. Test bounded diverse seeds (Exoo, distance-certified 38, or reported Paley-then-growth) rather than rerunning generic annealing at scale. TCSExam's perfect reports mean matching order 39. |
| G | Angeltveit–McKay's local join and finite flag-SDP papers suggest constraints that correlate more than one local view; neither supplies a separating row for our regular case. |

Search scope: arXiv and exact DOI/title lookups; EJC/DS1, ACM, IJCAI, Springer and Wiley references; McKay/HoG plus targeted `(3,10,39)` count and graph6 searches and `(3,9;30,88)` through dense-class searches. An absent find is not proof that no release exists. No mail, posting, or dataset requests were made.

## Round 2 cross-check and adjacent results

- Rechecked the journal §7 and Radziszowski DS1.18 §2.1(d). The exact
  published figure is still Angeltveit's *partial* count 43,225,483;
  the survey rounds it to at least 43 million. [McKay's current index](https://users.cecs.anu.edu.au/~bdm/data/ramsey.html)
  still does not expose the GR–Angeltveit file. A candidate third-party
  mirror, [`linxy/RamseyGraph` at `7ca0863`](https://huggingface.co/datasets/linxy/RamseyGraph/tree/7ca0863),
  repackages smaller graph classes; its raw and processed indexes are not
  a new source for B's order-30 dense levels or F's order-39 seeds.
- Marcelo Campos, Matthew Jenssen, Marcus Michelen, and Julian Sahasrabudhe,
  *A new lower bound for the Ramsey numbers R(3,k)*, [arXiv:2505.13371](https://arxiv.org/abs/2505.13371)
  (May 19, 2025), gives asymptotic constant 1/3; Zion Hefty, Paul Horn,
  Dylan King, and Florian Pfender, *Improving R(3,k) in just two bites*,
  [arXiv:2510.19718v3](https://arxiv.org/abs/2510.19718v3) (February 19,
  2026), raises it to 1/2 with a random blow-up/filter construction. Samuel
  Harris et al., [arXiv:2609.01782v1](https://arxiv.org/abs/2609.01782v1)
  (September 1, 2026), gives a short alternative with a weaker constant.
  Their asymptotic statements cannot be substituted at k=10; a possible
  seed generator for F would first have to beat a smaller finite control.
- Milos Tatarevic, *An upper bound of 60 for the Ramsey number R(3,3,3,3)*,
  [arXiv:2610.36648v2](https://arxiv.org/abs/2610.36648v2) (November 6,
  2026), uses global incidence counting, local neighbourhood classifications,
  Lean reductions and two independent SAT solvers. The v1 bound was 61;
  neither version concerns the two-colour R(3,10), and the two-solver step
  is not an end-to-end Lean proof. This is an architecture precedent for
  A/C/D/G, not a new count, closure, or gluing floor.
