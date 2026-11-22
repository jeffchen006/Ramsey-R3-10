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

## Round 3: targeted catalogue check

- Jan Goedgebeur and Stanisław P. Radziszowski, *New Computational Upper
  Bounds for Ramsey Numbers R(3,k)*, EJC **20**(1), P30 (2013),
  DOI `10.37236/2824`, [arXiv:1210.5826v2](https://arxiv.org/abs/1210.5826v2),
  Tables 4 and 14: the two lowest `(3,9;33)` levels have 5 classes at
  118 edges and 69 classes at 119. These are published counts, not a
  graph6 appendix. The paper marks the history of its edge-table
  calculation: the old lower bound 117 was superseded by the exact 118.
- The [House of Graphs minimum-edge index](https://houseofgraphs.org/meta-directory/minimal-ramsey)
  lists the 33/118 level; its file `Ramseygraphs_3_9_33_e118_some.g6`
  is already pinned by G, whose validation against GR confirms all five
  despite `_some`. The [McKay Ramsey data index](https://users.cecs.anu.edu.au/~bdm/data/ramsey.html)
  provides neither 33/119 nor the 39-vertex partial census. I found no
  public 33/119 file via the authors' paper, indexes, or exact-name
  searches. G's new local hits are not evidence of a public census.
- Jonas Backelin's *The (3,t) Ramsey graph enumeration project* (undated
  public report, Stockholm University author site, `enumrep_1.pdf`)
  is a further catalogue lead, but I located no indexed post-2024 count
  for the 33/119 or dense order-30 levels from it. No change to lanes
  A–G's data inputs or claimed coverage.
- Rechecked the publisher's current DS1 revision date and the recent
  construction reports; no classical 40/41 resolution, 39-vertex bulk
  file, or exact 30/88-and-up order-30 count located. The three negative
  search results are not completeness claims.

## Round 4: primary count audit and current status

- Rechecked the [current DS1 release](https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS1)
  (April 24, 2026) and [Angeltveit's journal paper](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v32i4p30)
  (November 3, 2025; arXiv v2 remains the latest preprint version). The
  November 21 search did not locate a later exact result. No newly public
  GR–Angeltveit 39-vertex census or exact dense order-30 count was located.
  This gives no new input batch for B or F, and no coverage change elsewhere.
- [GR v4](https://arxiv.org/abs/1210.5826v4), March 20, 2013, Tables 4 and
  14: the 33/118 and 33/119 counts 5 and 69 are exact, but 33/120 has
  lower bound **1,223**, 33/121 lower bound **13,081**. Together with
  Angeltveit's exact 14,395 total through 121 (arXiv v2, §3.3), the unknown 33/120
  count is between **1,223 and 1,240**. No graph6 download for that
  complete level was located. G can use the interval to rule out
  completeness of a sub-1,223 set, not to certify a set of size 1,223;
  A can audit supplied proofs separately. GR also gives the exact
  order-32 counts 39, 952, 18,598, 234,681 at e=104..107.

## Round 5: current search and construction comparator

- Re-ran November 21 searches for a settled classical value, the
  43,225,483 graph bulk set, exact order-30/88+ levels and an order-33/120–121
  bulk release. No additional primary result or deposit was located. The
  EJC survey and journal references at the top remain the status basis;
  this negative search does not establish nonexistence of a private set.
  There is no new public substitute for B's e88 inputs or G's six unresolved
  combined classes. The run's own 14,389 are not a published exact census.
- Ansh Nagda, Prabhakar Raghavan and Abhradeep Thakurta, *Reinforced
  Generation of Combinatorial Structures: Ramsey Numbers*,
  [arXiv:2603.09172v5](https://arxiv.org/abs/2603.09172v5), April 21, 2026,
  Algorithm 18 and Table 1. The reported R(3,10) lower-bound result matches
  40, not a 40-vertex witness. The construction grows Paley(29) one vertex
  at a time, with greedy incident-edge initialization and global annealing
  on triangle and independent-10 defect counts. This is a comparator for
  F's different exact local-repair strategy, not a nonexistence argument
  or a new catalogue. The other improved Ramsey lower bounds are for
  different parameter pairs. Pinned primary text: `scratch/H/lit/ae.txt`.

## Round 6: publisher and catalogue recheck

- On November 21, 2026, the live EJC landing pages again gave DS1
  revision April 24, 2026 and Angeltveit's journal date November 3,
  2025; arXiv still gave v2, April 8, 2024. The exact-title/bound and
  recent-enumeration searches found no primary source superseding
  the classical interval **40–41**. This is a search result, not a
  proof that an unpublished resolution does not exist.
- Reopened McKay and House of Graphs and searched the exact journal
  count 43,225,483 and order-30 graph6 catalogue names. No new bulk
  order-39 source for F or exact 30/88–99 count for B–D was located.
  There is likewise no basis to replace G's six missing order-33
  e120/e121 classes by a public file. The new local 984-class
  minimum-degree-five census is a different scope (e123–130), not
  a publication and not an e120–121 fix. Pinned landing pages and
  search metadata: `scratch/H/lit/r6-*.data`;
  `scratch/H/literature-recheck-r6.log`.

## Round 7: dated cross-check and smaller-window sources

- On November 21, 2026, both EJC pages were refetched with unchanged
  bibliographic fields (DS1 rev. 18, Apr 24, 2026; Angeltveit
  EJC **32**(4), #P4.30, DOI `10.37236/12936`, Nov 3, 2025).
  Angeltveit arXiv:2401.00392 and the McKay and HoG catalogue
  landing pages matched the round-6 bytes. The journal's §7
  count remains a lower bound of 43,225,483 known order-39
  classes, not a complete census; no public bulk file, superseding
  `R(3,10)` bound, or exact count at 30/88–99 was found. This is
  a scoped search result. The Pandey–Ravi exact-title Crossref
  returned no matching journal entry among the top five results;
  their primary arXiv:2601.03572 landing page still serves v1.
  Pinned pages and queries: `scratch/H/lit/r7-*.data` and
  `scratch/H/lit/r7-pandey.json`.
- For A/E/G, GR Table 13 has exact order-26 `(3,8)` counts
  at e73–77 of 62, 1,625, 23,409, 216,151 and 1,526,296;
  e78–84 is uncounted in that table. The full McKay order-27
  catalogue of 477,142 is a valid source for the paired strip
  with center codegree three only. For the one-center strip,
  the new upper caps 82/84 narrow but do not bound the search to
  published counts or available files. The separate E reverse
  window still depends on the missing e74 class. Source: GR DOI
  `10.37236/2824`, Table 13; McKay Ramsey data as above.

## Round 8: November 22, 2026 check

- Read-only refetch: DS1 rev. 18 (April 24, 2026, DOI `10.37236/21`),
  Angeltveit EJC **32**(4) #P4.30 (November 3, 2025, DOI
  `10.37236/12936`), and GR EJC **20**(1) #P30 (DOI `10.37236/2824`)
  differ from yesterday's landing pages only in transient form tokens.
  The arXiv:2401.00392 v2 (April 8, 2024), McKay and HoG bytes match.
  The TCSExam author task remains a match to the order-39 reference,
  not an order-40 result. No newer published bound, public bulk list of
  the 43,225,483 known order-39 classes, or exact 30/88–99 count found.
  The Crossref broad title search surfaced no pertinent result and the
  narrower enumeration query hit HTTP 429. This is a limited dated
  search, not proof of nonpublication. Snapshots: `scratch/H/lit/r8-*`;
  request outcomes: `scratch/H/round8-literature.log`.
- For A/G the published complete order-22 `(3,7)` list (McKay, 191)
  supplies the two exact rooted low-degree slices only. The order-27
  `(3,8)` list (McKay, 477,142) supplies the separate order-27 marks;
  there is no licence to pad a general order-25/26 window to order 27.
  C's individual P3 layout binds McKay's 30 e62 and 60 e63 rows, not
  another layout at either level. B's **124 missing** is against GR's
  order-32/e108 count, not a revised D-C9a order-30 count. E/F have no
  substituted public e74 list or order-39 bulk source. D has no new
  published replacement for a covered rooted template family.
## Round 9: no new premise imported

Narrow recent-preprint and data-repository discovery queries did not
supply a new usable premise. Did not repeat the publisher/catalogue
refetches in round 8. The public evidence cited above still supports
40–41, not a decision or a claim of universal nonavailability of the
dense order-30 or order-39 files. For the current mixed pilot use the
existing 191-class order-22 source via rooted gluing, not an assumed
published full order-26 census; see `ROUND9_REVIEW.md`.

## Round 10: November 22, 2026 refresh

- Refetched Radziszowski DS1 (`10.37236/21`, displayed revision April 24,
  2026) and Angeltveit EJC 32(4) #P4.30 (`10.37236/12936`, November 3,
  2025); bibliographic fields unchanged. The arXiv:2401.00392 landing page
  is byte-identical to the round-8 snapshot (v2 April 8, 2024). Targeted
  bound and census searches returned no usable newer primary result; a
  limited Crossref title lookup since April 24 yielded no superseding
  exact R(3,10) result. The evidence still supports **40–41**. The
  TCSExam author task likewise has unchanged bytes; matching its
  order-39 reference is not progress at order 40.
- McKay's and House of Graphs' indexes are byte-identical to round 8.
  Still no public bulk file located for Angeltveit §7's partial census
  of at least 43,225,483 order-39 classes, and no new exact public count
  located for `R(3,9;30,e)` at `88 ≤ e ≤ 99`. These are limited dated
  searches, not a claim that the data cannot exist. Primary source
  snapshots and request outcomes: `scratch/H/lit/r10-*.data`,
  `scratch/H/round10-literature.log`.
- No lane changes its published input: A/G retain the marked gluing
  sources, C/D the calibrated small classes, E its explicit E-021
  premise, F its individually verified seeds. B's reduction from 124
  to 63 missing uses local order-32/e108 keys against GR Table 14, not
  a published order-30 enumeration or a new residue floor.

## Round 11: November 22, 2026 verification and two adjacent methods

- The current established interval is still **40–41** in the sources
  found: Radziszowski DS1.18 (April 24, 2026), Table Ia and §2.1, DOI
  `10.37236/21`; Angeltveit EJC 32(4) #P4.30 (November 3, 2025),
  Theorem 1, DOI `10.37236/12936`; public arXiv copy `2401.00392v2`
  (April 8, 2024). Exact-title/count searches and dated discovery
  queries (arXiv November titles and Crossref/OpenAlex since April 24)
  yielded no superseding decision. These queries are not exhaustive.
- No public bulk file located for the **partial** order-39 journal §7
  count ≥43,225,483. McKay's index is unchanged. HoG's public page was
  refetched, but its byte match alone only authenticates the JS shell;
  the previously audited links and the targeted e88–99 queries did not
  identify any new exact `R(3,9;30,e)` count. GR Table 14 still has
  1,800 at 86, 147,335 at 87, question marks at 88–94; the relevant
  **2,104,151** is at **32/108**, not order 30. B supplies 2,104,146
  local rows pending critic; that is not an external data release or
  a residue-floor change. Raw sources: `scratch/H/lit/r11-*.data`;
  request outcomes: `scratch/H/round11-literature.log`.
- Hanxin Jiang and Zehui Shao, *An 8+9 gluing computation for the Ramsey
  number R(F₃,F₄)*, [arXiv:2610.26109v1](https://arxiv.org/abs/2610.26109v1),
  October 19, 2026, §2.5, §4 and Appendix A.9–A.12; artifact DOI
  `10.5281/zenodo.23119016`. Reports `R(F₃,F₄)=17`; the maximum-red-cut
  swap rows and joint support profiles give 88,294,674 ordered pairs.
  Bulk UNSAT decisions for 88,294,634 are separated from 34 counting
  exclusions and six independently checked finite-domain tail cases.
  Useful for A/B/G's manifest and tail-proof architecture; a max-cut
  selector cannot replace a prescribed pivot cut without a rerooting
  cover. No `(3,k)` census or end-to-end bulk propositional certificate.
- Milos Tatarevic, *An upper bound of 60 for the Ramsey number
  R(3,3,3,3)*, [arXiv:2610.36648v2](https://arxiv.org/abs/2610.36648v2),
  November 6, 2026 (v1 on October 27 had 61), §§2–6, Thm. 1.1.
  Directed incidence counting forces a rooted marked violation or
  global equalities; compatibility views share physical edge variables.
  Relevant to C/D/G's joint-versus-marginal root tests and A/H's exact
  CNF interface: Lean checks 55 classification certificates and the
  mathematical reduction; the 296,081 large-formula UNSAT results
  from two solvers remain a premise of the final Lean theorem. Neither
  this nor the fan result changes any A–G premise, order-39 seed or
  involution scope. No artifact campaign was launched.

## Round 12: November 22, 2026 primary-source refresh

- Radziszowski, *Small Ramsey Numbers*, EJC DS1.18 (April 24, 2026),
  Table Ia and §2.1, DOI `10.37236/21`, and Angeltveit, EJC **32**(4)
  #P4.30 (November 3, 2025), Theorem 1 and §7, DOI `10.37236/12936`,
  still support **40–41**. Journal metadata is unchanged, and the
  `2401.00392` arXiv landing page (v2 April 8, 2024) is byte-identical
  to round 11. IJCAI `10.24963/IJCAI.2025/292` and Springer
  `10.1007/978-3-032-32589-1_8` primary pages were refreshed: their
  SAT+CAS and Lean/SMS applications are as scoped in the table above.
  The limited Crossref result set had no exact decision or census;
  arXiv keyword HTTP 400 and Zenodo HTTP 403 are **failed requests**,
  not negative search results. See `scratch/H/round12-literature.log`.
- Benjamin Przybocki, John Mackey, Marijn J. H. Heule and Bernardo
  Subercaseaux, *Doubly Saturated Ramsey Graphs: A Case Study in
  Computer-Assisted Mathematical Discovery*,
  [arXiv:2604.21187v1](https://arxiv.org/abs/2604.21187v1), April 23,
  2026, §§1.2, 2, 4.1. Section 4.1 reports **over 100** doubly
  saturated order-39 `(3,10)` examples, not a new bound or the
  Angeltveit/GR census. The linked author artifact at tree
  `389d344cce15b594710c03496eafb069a3646a1e` has 18 paths (complete
  tree) and no releases; it contains Lean and SAT code, no example
  graph list. Useful for B's edge-private plus nonedge-witness
  constraints and F's diversity-of-seeds question, but double
  saturation cannot be assumed for all B residues or all full targets.
  A/C/D/E/G have no replacement catalogue or stronger closure premise.
- McKay and HoG index bytes match round 11 (HoG's match is for the
  shell only). I found neither a public bulk file for the journal
  §7 partial census of at least **43,225,483** order-39 graphs nor a
  new public exact count at order 30 / `88≤e≤99`. The exact
  `2,104,151` denominator is still GR Table 14 at **32/108**. B's
  new local search yielded zero novel keys on the named 7,954-parent
  list; neither that result nor the literature supplies the last five.
  These are dated findings, not claims of exhaustive nonavailability.

## Round 13 refresh — November 22, 2026

- **No superseding decision located.** The current EJC DS1 entry is
  Radziszowski's revision 18, April 24, 2026, DOI `10.37236/21`; Table Ia
  and §2.1 give 40–41. The Angeltveit journal article remains EJC **32**(4)
  #P4.30, November 3, 2025, DOI `10.37236/12936`; its `2401.00392` arXiv
  landing page still has v2 (April 8, 2024). The public November TCSExam
  `ramsey-r3-10` page still uses Exoo's order 39 as the reference. The
  circulated exact value 39 is *circulant* `R_C(3,10)`, not classical.
- **Exact archival citation for the round-12 find:** Benjamin Przybocki,
  John Mackey, Marijn J. H. Heule and Bernardo Subercaseaux, *Doubly
  Saturated Ramsey Graphs: A Case Study in Computer-Assisted Mathematical
  Discovery*, in Naumowicz and Seidl (eds.), *Intelligent Computer
  Mathematics* (CICM 2026), LNAI **16907**, pp. 300–318, Springer volume
  dated 2027, **first online September 29, 2026**, DOI
  `10.1007/978-3-032-38214-6_18`, §4.1. The full publisher text retains
  the report of over 100 order-39 doubly saturated examples, distinct
  from the Angeltveit/GR collection. The publisher code link points to
  the already checked author artifact, not a second graph deposit.
- **Data:** no public bulk Angeltveit/GR order-39 file or exact new
  `R(3,9;30,e)` count at `88≤e≤99` located. McKay index and the HoG shell
  are unchanged. Targeted searches and OpenAlex/Crossref discovery
  results (including enumerations, exact-bound titles and data queries)
  did not yield an applicable release. The failed arXiv discovery
  request yields no negative evidence. Provenance: `scratch/H/lit/r13-*.data`
  and `scratch/H/round13-literature.log`.
- **For A–G:** A/Cert and E can reuse the prior SAT-artifact references
  as methodology, not graph coverage. B must still separate the
  **2,104,151** `32/108` denominator from the **14,395** all-graph
  `33/≤121` denominator used in the now-audited degree-six floor; neither
  supplies e88, floor 109, or a complete `33/122` family. C/D have no
  new published replacement for their rooted controls; F can price the
  reported double saturation as a construction bias only, not assume it
  or reproduce those seeds without an artifact. G's new d6 floor and
  conditional thresholds are local results, not new published numbers.

## Round 14 targeted check — November 22, 2026

- The EJC page still identifies the current DS1 as **April 24, 2026**;
  Radziszowski, *Small Ramsey Numbers*, revision 18, Table Ia/§2.1,
  DOI `10.37236/21`, remains the cited 40–41 source. Checked again:
  Angeltveit, EJC **32**(4) #P4.30, DOI `10.37236/12936`; arXiv still
  has `2401.00392v2` dated April 8, 2024. No superseding resolution
  located. This is a dated search finding, not a proof of absence.
- The public McKay index still has the smaller `r35_13.g6`, `r36_17.g6`,
  `r37_22.g6`, `r38_27.g6.gz` and `r39_35.g6` controls. The fetched
  House of Graphs route is the site shell, not independent new class
  data. No new public Angeltveit/GR order-39 bulk file or exact dense
  `R(3,9;30,e)` count was located; no second catalogue search/rebuild.
  Responses and HTTP receipt: `scratch/H/lit/r14-*.data` and
  `scratch/H/round14-literature.log`.
- Implications for A–G remain as above. In particular C's cap-five
  header census and B's reducible extensions are team computations,
  not public Ramsey catalogues; F's necessary words are not new
  order-39 constructions. No evidence changed lane scope.

## Round 15 status check — November 22, 2026

- The current EJC PDF re-fetch at DS1's publisher page is revision
  18, **April 24, 2026**, Table Ia, explicitly **40–41** in the
  `K10` row and `K3` column (Exoo/Angeltveit), Radziszowski,
  *Small Ramsey Numbers*, DOI `10.37236/21`. Angeltveit's EJC
  **32**(4) #P4.30 (November 3, 2025), DOI `10.37236/12936`, and
  arXiv:2401.00392v2 (April 8, 2024) are unchanged. No newer
  exact classical result was located. Evidence: `scratch/H/round15-literature.log`
  and `scratch/H/lit/r15-ds1.{pdf,txt}`.
- Per the critic, no independent catalogue census or frame regeneration
  this round. The order-39 bulk and order-30 dense exact-count answers
  remain “not located in the sources checked above,” not a nonavailability
  theorem. No new input for A–G. The marked 17/17 proof uses the
  published upper bound `R(3,6) ≤ 18` explicitly; that is not a new
  enumeration or a Lean proof of the published Ramsey number.
