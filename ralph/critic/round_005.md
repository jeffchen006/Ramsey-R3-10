# Round 005 critic review — November 21, 2026

No order-40 graph passed the flow gate. The accepted MTF distribution
baseline goes **368 → 283 → 278 near-regular distributions, plus Case R**.
The first step uses G's independently enumerated cover (not an end-to-end
certificate), the second uses B's certified degree-seven residue floor
and exact distribution replays. Previously accepted gluing premises still
apply where indicated. The remaining **10 conditional U88 keys** are not
excluded. No scheduled four-round deep audit this turn.

## Claim verdicts

Paths in the lane column are relative to `ralph/lanes/`. The critic's
bounded replay logs are `scratch/critic/r5-*.log`. A retained full replay
plus an exact index and fresh spot checks are explicitly distinguished
below from a second full replay by the critic.

| Lane / claim | Verdict, evidence and limits |
|---|---|
| A — supplied order-33 proof rows | **CONFIRMED, cert, supplied rows only.** `A/HIGH_RESIDUE_AUDIT.md` and `scratch/A/residue5/{index-full.tsv,proof-full.log}` bind 11,425 checked cliques and 2,890 rebuilt LRATs. The 11 e169-only proofs use the exact 42-cross-edge/private-cell equality; they cannot be used at larger total e. All 11 weaker unpinned cores have verified SAT assignments, not completions. The critic's bounded repeat checked the incidence and negative controls and matched a 6,114-line proof-index prefix before stopping; full proof counts use the retained A replay and the round-4 independent checks. |
| A — order-33 incidence | **CONFIRMED, enum + hand.** `r5-A-out/moves-full.log` reproduces exact bidirectional incidence sets: 1,523 and 24,794, with deletion-critical e120/e121 counts 230/803 on supplied rows. Published combined count 14,395 versus 14,389 valid distinct supplied keys leaves six omissions. The exact e119 source means an omitted e120 class cannot have a legal deletion. A legal addition cannot hit a supplied e121 class (exact down test), leaving at most five distinct possible children; zero is not ruled out. No global floor 121 or 122. |
| B — direct e162 `(0,2,32,6)` | **CONFIRMED, cert conditional on published census and floor 107.** `B/E162_E107.md`: at either d7 root `Z≤55` forces the d7 adjacency and no d9 neighbour, so the seven row sizes are six or seven. A distance-≥3 exterior pair must occur in a row; triangle-freeness and maximality make that row independent dominating. Replayed the complete 234,681 pair witnesses and the 64×2 independent forced-row checks (`r5-B-direct.log`); the recursion covers the first eligible choice in each dominating row. Same key as the later floor-108 consequence; count once. |
| B — degree-seven floor 108 | **CONFIRMED, cert (MTF; neither gluing floor required).** `B/FLOOR7_108.md`: verified catalogue digest, all graph properties, exact 234,681 nonisomorphic classes matching GR Table 14, and ordered 231,455/3,226 partition (`r5-B.log`). Singleton demands need attachments, and pairs at distance ≥3 need a shared attachment. Incompatibility prevents a row from covering two clique members. A seven-clique bijects to the seven rows after selecting one witness row per demand; row renaming is valid because the CNF has no prior asymmetric row pins. Rebuilt and replayed **all 3,226 LRATs with both checkers** and matched the production digest index byte-for-byte. This with G-011 excludes all smaller levels. The logged all-input MTF gluer is a separate **CONFIRMED, enum** cross-check; its SAT corroboration covers only 64 sample inputs. |
| B — e108 and U88 | **CONFIRMED, enum (partial) / open.** `scratch/B/logs/e108_r5_{reducible,followup,critical_audit}.log`: 2,102,271 reducible keys and seven verified critical keys leave 1,873 short of 2,104,151. The pilot proof-rate/cost projection is an **estimate** from predominantly reducible inputs, not a guaranteed ceiling for the critical slice. Prefix/e43/tail were still running or queued at the resource snapshot; no U88 closure. |
| C — P3 residue caps | **CONFIRMED, cert.** Rebuilt all exact coverage indexes and retained proof hashes (`r5-C.log`, `C/ROUND5_REPLAY.md`): diagonal 5 e62 has 44 boundary orbits × 30 residues = 1,320, and diagonal 3/4 e64 has 59+59 = 118. These really remove the top remaining layers in conjunction with prior caps, not just 1,438 arbitrary rows. The full retained CakeLPR replay has no missing/capped rows; the fresh index check was not a second run of all 1,438 checkers. Only P3-associated residue edges are bounded by 61 or 63. |
| C — complete and mixed arms | **CONFIRMED, hand + cert.** `C/proofs/p3_complete_arms.md`, `C/proofs/p3_mixed_arms.md`: at s=4/5 the shared B1 vertex makes the wings anticomplete; at s=3 at least four T-avoiders in X avoid both wings by the full-arm triangles and the requirement to hit each independent nine-neighbourhood. Adding two nonadjacent T-avoiders to T plus five independent wing vertices contradicts alpha≤9. For 9/8, reversal and the hole-row distinction cover s=3; the B1 hole and one wing edge are forced at s=4. The three small antineighbour LRATs and one fixed Lite6 row per diagonal replayed freshly. The exact retained 60+60 matches cover both remaining layouts. Thus at global minimum `f*≥8` both P3 arms are 8, s=3/4; at `f*=9`, with no P4 or triangles in J, J is a nonempty matching. No isolated-pair exclusion. |
| C — isolated-wing reduction | **CONFIRMED, hand + enum (necessary filter).** `C/proofs/p2_full_wings.md`: 42 common-support incidences and no more than 12 singleton-support vertices imply excess ≤2. A wing-sibling codegree-six pair would itself be full and violate that budget, with two distinct exterior vertices contributing 3. Inclusion-exclusion gives each wing footprint ≥12, and the smaller is 12 or 13. Replayed the matched C22 controls and exact terminal lists of 35,099 marked order-21 windows and 246,483 order-13 cores (`r5-C.log`). They are not completions or equivalent lists. |
| D — alternative maximum-root cover | **CONFIRMED, hand/enum.** `D/MAX_ROOT.md`, `scratch/D/{max_root_genbg,forest_cover}.log`: 111 keys in strata 35/39/26/8/3, not 111 disjoint unrooted cases. The global maximum m=12 forces h1(v)=0 and every edge square count 12; a side isolate contradicts codegree at least two with the opposite root. Thus 19 isolate keys are out by hand. Unfiltered exact Farkas replay for 19/20/22 passed (`r5-D.log`); distinct masks, triangle-disjoint arcs, exact outside valence, remaining codegrees and square transport are necessary, and verified subgroup averaging preserves the linear rows. This leaves 13 forest keys in max12 and 76 above it; no change to the 110 minimum-root keys. Forest/reroot/rank consequences are **CONFIRMED, hand** only in max12. |
| D — key 34 count and calibration | **CONFIRMED, enum.** `D/TRANSPORT.md`, `scratch/D/transport40/split-index.log`: `k` tracks `(2,2)` masks, and the four mask-pattern totals from exact side counts give `6≤k≤14`. The k=6 proof replays even without the forest rows; k=7–14 only pass the LP. Replayed the 13 smaller exact rational averages and inspected both fixed/eager smaller complete labeled matches from 16 keys and five known graph classes. This does not certify any larger local-star SAT encoding still awaiting its separate input bridge. |
| E — saturated 12-edge core at f=32 | **CONFIRMED, cert, scoped.** `E/cubic32.md`: with four size-six attachments and δ(W)≥2, fixed degrees in W are at most 8; at e(W)=12 the incidence sum is ≤40, and the forced singleton/double rows give ≥40. Equality forces the counted support profiles, including repeated double pairs where legal. Crown window sum ≤296 guarantees a window with at most 74 edges. The omitted group is used only as a necessary support feasibility check. Manifests bind 1,058 cubic and 6,904 noncubic windows, no terminal SAT/limit; replayed canonical census equality, all bundle hashes and regenerated CNFs/checked LRATs for six cubic and 35 noncubic indices (`r5-E.log`). The bounded-clause noncubic variant only drops constraints. Retained full producer replay covers the rest. No t=2,3, leaves/isolates or e(W)≤11 closure. |
| E — f=28 freeze and 73-edge census | **CONFIRMED, mixed inherited cover** for `E/f28_cover.md`, with the same **UNCHECKED** fresh F10 verification (historical bulk enumeration unavailable). **CONFIRMED, hand + enum** for `E/window73.md`: checked 62 valid nonisomorphic 73-edge graphs (15/16/31 with 0/1/2 degree-seven vertices), 396 smaller controls and arithmetic. The four windows sum to `296−2D−P`; every 73-edge window needs `b_i≥14−D`. With parity and the available incidence surplus this forces D=0, P=0 for m≥9. For m=11 there cannot be a 73-edge window; the fixed sum then forces four at 74, and surplus 2 gives only `(10,10,10,12)` or `(10,10,11,11)`. This is a filter, not an 11-edge exclusion. |
| F — exact promoted and local pools | **CONFIRMED, enum, local.** `F/ROUND5.md`: audited all three exact promoted blocks (15,519 + 235,347 + 235,346), replayed the first with no sub-24 score, and replayed 2,801 + 3,458 new strict four-core keys to zero completions (`r5-F.log`). The canonical scope audit ties 936 previous keys and 6,259 new keys to all 7,195 clean four-deletion keys. To edit a smaller support, pad to four; an unclean unchanged core cannot yield zero. Non-clean two/three-pole runs are exact on their supplied scope, and the four-pole pilot covers only 768 of 75,578 keys. The interrupted score-24 run contributes only its completed prefix; disjoint ceiling-23 retries cover the suffix, not plateau enumeration. No new seed below 24 and no result for the involution family. |
| G — degree-five residue cover | **CONFIRMED, pub + enum.** `G/rows/no_degree_five_residue.md`: a d≤4 vertex in order 33 leaves a forbidden (3,8) order≥28; d5 leaves a (3,8;27) residue. Verified the 477,142-key source digest, nonisomorphism, exact inner/outer shard bindings, normalized 118 survivor keys and 984 class equality for the two extenders (`r5-G.log`). For each tuple of independent rows, the independence tests for ≥2 attached vertices are monotone under row extension to MIS; row repetitions are allowed, ordered tuple search loses no multiset, and trimmed subcolumns are exhausted in increasing edge order with sound monotone failure pruning. Replayed the complete independent C++ outer reject-all and one disjoint inner shard (`r5-G-extra.log`); retained independent full inner run and known smaller exact controls cover the balance. No total-e, MTF or gluing-floor assumption on the outer rejection. Cap 122 side result: **CONFIRMED, cert conditional on the 118-key enumerated cover**; rebuilt the inputs and spot-checked both LRAT checkers, with full retained proofs, plus five census graphs at 123. |
| G/B — distribution cuts and overlaps | **CONFIRMED, hand / enum / exact arithmetic.** `G/d5_global_cuts.jsonl`, `G/floor108_overlap.jsonl`, `r5-G.log`, `r5-bookkeeping.log`. Exterior d≥6 implies `c(u,w)≤d(w)−6` for a degree-six root; MTF then forces the degree-six vertices to form a clique, hence n6≤2. All 84 direct pins and e168 `(2,9,0,29)` are new relative to round 4: two adjacent d6 roots force odd Z at either, while floor120 and the private bound force Z=48. Floor108 takes five more (two unglued, three with inherited gluing), including the already described e162 key. Exact Farkas replay and an independent key merge give 39 surviving tightened threshold keys and four U88 removals and four additions relative to 283. The baseline 278 inherits the accepted inputs; it is not a global UNSAT result. |
| H — formal statements and literature | **CONFIRMED, Lean, named scope.** Read `lean/R310/{PrivateSignature,CompleteArms,ResidueDegreeFive}.lean` and rechecked the retained 12/270 axiom reports and the C13/K2,3 controls (`r5-H.log`, `H/LEAN_REPRO.md`). Signature uniqueness needs full private cells; the arm/wing results assume their specified support data and the degree-five reduction assumes the Ramsey bound. No finite census or combined order-40 conclusion is formalized. The negative publication/census searches in `H/LIT.md` are **UNCHECKED** as universal absence claims; nothing depends on such absence. H's 368+R is the pre-round baseline, not the post-audit count. |

**REJECTED as scope upgrades:** six missing e120/e121 classes do not imply
six e120 classes, a checked pinned proof does not cover its weaker CNF,
and LP-feasible, capped, sampled and retained-window inputs are not
completions or case closures. **REJECTED as bookkeeping:** adding the
direct e162 exclusion on top of all five floor-108 cuts; 368 was the
prior count, and 12 is the old U88 multiplier. No supported primary
exclusion was rejected at the stated scope.

## Rules and resources

- Flow snapshot: 17 busy, all B, within B's old share of 18 and total cap
  80; no flow over-cap kill. B's prefix uses 16 slots, e43 and tail are
  serialized; the later snapshot still shows e43 progressing and tail
  waiting. The other reported lane peaks fit their allocations where
  sampled or logged. The flow's RSS is rounded 0.0 GB; the sampled B
  process trees sum to 0.389 GiB RSS (`r5-rss.log`). Flow scratch was
  52.2 GB and later `du` shows 36 GiB, both below the 150 GB cap. Filesystem
  is still 95% used. Wrappers sampled carry time/RAM bounds and nice 5.
- `git status`, board diff and reflog show only allowed tracked lane
  edits, H's Lean/ledger edits and 20 board append lines before critic
  edits. Latest commit is flow round 4; push target is disabled. No
  observed lane commit, push or out-of-scope lane write. This does not
  prove absence of all transient external writes.
- **Confirmed critic-side write break:** C's `p3_antineighbour.py --verify`
  is not read-only. I pointed it at the lane's workdir and it rewrote
  `scratch/C/p3r5-antineighbour/{1,5,6}.cnf`. The three post-run SHA-256
  digests match C's retained production/replay bindings; only timestamps
  changed, not proof files or tracked files (`r5-C-scope.log`). Subsequent
  C regeneration used `scratch/critic/` copies/symlinks of read-only
  proof inputs. An A replay checker survived the outer timeout as a
  separate group. I registered and stopped the critic's own timeout
  process (`ralph/critic/STATE.md`); no live critic job remains. Use a
  single effective timeout or foreground nested wrappers on future
  partial replays. No long solver launch.
- **New A–H split: 2 / 22 / 8 / 2 / 17 / 2 / 25 / 2 = 80.** B and G
  gain slots for the checked floor/cuts. E's completed batch frees slots
  but the narrower measured m=11 pilot has room to scale. F is reduced
  after zero improvement in its completed search; two slots for a new
  source. No lane triggered literal three consecutive rounds without a
  measurable result. Details and caps in `ralph/ALLOC.md`.

**Best next direction:** target the **20 surviving e168 distributions
with a degree-six root**. The floor 120/private-signature equality and
n6≤2 narrow a direct obstruction. A complete e120 input recovery is
an alternative, but must account for unknown zero-addition residues;
do not launch another unchanged swap sweep. Do not subtract 20 until
an actual cover or obstruction is checked.
