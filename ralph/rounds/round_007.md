# Round 7

Began 2026-11-21T23:27:45; ended 2026-11-22T00:38:01.

## Flow checks
```json
{
 "round": 7,
 "verified_340_graphs": [],
 "graph_files_checked": [],
 "solver_processes_now": 39,
 "per_lane_now": {
  "B": 16,
  "G": 23
 },
 "rss_gb_now": 5.5,
 "core_cap": 80,
 "killed_over_caps": [],
 "lane_turns": {
  "A": "ok",
  "B": "ok",
  "C": "ok",
  "D": "ok",
  "E": "ok",
  "F": "ok",
  "G": "ok",
  "H": "ok"
 },
 "lanes_failing_in_a_row": {},
 "critic_turn": "ok"
}
```

## Lane A: Toolchain and certified SAT (the 99 open R(7) cubes) (ok)
**Cert, pending critic:** Independently reproduced the complete 1,988-window cover and replayed every LRAT with both checkers. The full replay took 0.1604 core-hours. Missing, duplicate, and mismatched proof controls were rejected.

This excludes only the \(e=168\) subcase where both strips are path/leaf and their centres have codegree 3. Codegrees 1 and 2 and the mixed-role branch remain open. No whole degree distribution was closed, and no order-40 candidate was found.

Evidence: `ralph/lanes/A/PAIRED_WINDOWS.md:96`. No Lane A jobs remain. Next: independently bind Lane G’s lower-codegree sources at their exact scopes.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
**Round 7: no new case closed.** All ten U88 distributions remain open, and the e108 census is still missing 1,266 edge-critical classes.

- **Enum:** Adjacent-pair reconstruction passed the exact 42-class control but found no new e108 class across 5,249 sampled stems. The degree-six/e65 pilot recovered all 21 planted classes and no new ones; its filter rejected no rows. Neither pilot was scaled.
- **Running:** Prefix PID `1180084` is the only live Lane B job, at 16 slots. At 23:41 CET, 2,338 of 2,847 degree-six chunks were complete. Estimated finish: November 22, 00:50–02:00 CET.
- **Next:** Compare the final ≤87 union byte-for-byte with the checkpoint, then bind the prefix scan and separate its critical e88 keys. Even a terminal zero leaves the outside-prefix d6/e52 or d7/e44 critical slice open.

Replay instructions and evidence: `ralph/lanes/B/ROUND7_REPLAY.md:1`.

## Lane C: Theory for the 9-regular case R (ok)
- **Hand + enum, pending critic:** In global `R(6), f*=9`, for wing sizes `(12,14)` only, the 12-vertex private side must have **16–21 edges**. Four profiles had no marked window; the new filter rejected all **317,795,664** maps across 11 more profiles, with no deferrals.
- The simultaneous-neighborhood filter preserved the planted choices in all seven smaller full-wing controls. Direct and cached checks agreed on 16,080 pilot maps and a complete 10,944-map profile.
- **Open:** 24 of 39 profiles, both other wing splits, and \(R(3,10)\). No candidate graph and no running jobs.
- Both replay manifests verified. Evidence: `ralph/lanes/C/ROUND7_REPLAY.md:137`. Next: critic review, then test whether grouping common-column mappings can reduce the remaining join cost.

## Lane D: New SAT encodings and splits for case R (ok)
**Lane D, round 7:** No target pin excluded, no graph candidate, and no new certificate. No solver jobs remain.

- **Hand:** In max12 with `Smax=2`, either a score-two edge has endpoints whose score-two degrees sum to at least 7, or the score-two edges form a cubic graph with no score-zero edges and `w=0`. This partitions the stratum without deleting any of its six root keys. See `ralph/lanes/D/SCORE_CAP.md:68`.
- **Enum:** Both score encodings passed the C16/C20 controls. On key 24, `k=7`, the global cap raised the clause count from 1.11M to 3.57M; neither arm decided within 100 CPU-s.
- **Open:** The attachment-only dense arm found a feasible projection, not a graph. The balanced arm hit its 45 CPU-s cap. Don’t scale either pilot unchanged.

Handoff is in `ralph/lanes/D/STATE.md:1`. Requested H/C/critic review of the split and projection before pursuing a stronger balanced-case filter.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
- **Hand + enum + cert, pending critic review:** Excluded core `G?bBro` in the saturated involution subcase \(f=32,\ t=4,\ \delta(W)\ge2,\ e(W)=11\), profile `(10,10,11,11)`. No broader exclusion is claimed.
- The shared-window filter cut the matched proof queue from **785 to 57** in 16.28 CPU-seconds. The independent replay covered all 36,612 support orbits and checked all 57 regenerated CNF/LRAT pairs.
- Evidence and reproduction: `ralph/lanes/E/shared74.md:1` and `scratch/E/r7_shared/freeze.3.sha256:1`. Prior proof bundles rehash unchanged.
- No live lane E jobs or candidate graph. Next: critic review, then a graph-first pilot on another small core. **\(R(3,10)\) remains unresolved.**

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Lane F, round 7:** No candidate. The best degree-valid score remains 24 independent 10-sets.

- **Calibration (enum):** Degree-preserving vertical trades recovered all 8 planted 38-vertex controls; ordinary two-switches recovered none on the same inputs. The recovered graphs passed the gate.
- **Target (enum):** Exhausted 4,196 distinct labelled quotients from length-1–4 trades on the two score-24 seeds. None admits a score below 24. Both emitted ties are isomorphic to their respective seeds. No caps; no family excluded.
- **Handoff:** All jobs finished in 57.65 CPU-seconds. Evidence is in `ralph/lanes/F/ROUND7.md:1`. Keep these neighborhoods off cores; resume relifting only with a genuinely new source or selector.

## Lane G: Near-regular degree distributions N(e) (ok)
**Round 7: two subcases refuted; no degree distribution closed.** The baseline remains 278 near-regular distributions plus Case R. No order-40 candidate.

- **Cert + enum cover:** For both low-\(n_8\) e168 profiles with two path/leaf strips, centre codegree 3 is excluded. All 1,988 marked windows passed both LRAT checkers and Lane A’s independent replay.
- **Cert, cover audit pending:** Centre codegree 2 is excluded when the paired window has minimum degree 3. All 1,767 representative CNFs passed both LRAT checkers; an independent scan matched all 2,111 marks before deduplication.
- **Running:** Codegree 1 with minimum window degree 2 (PID `360479`, 16 cores) and mixed-strip codegree 4 (PID `710384`, 2 cores). Neither batch has complete coverage yet.

Next: bind both running proof sets, audit the codegree-2 gluing and deduplication, and seek an exact source for the higher-minimum-degree windows. Replay instructions: `ralph/lanes/G/ROUND7_REPLAY.md:1`.

## Lane H: Literature scout, claim ledger, Lean (ok)
**Lane H, round 7.** No case closed and no H jobs remain. The checked baseline is **278 near-regular MTF distributions plus Case R**, with ten conditional U88 keys and all 20 degree-six e168 keys still open.

- **Lean:** Five marked-window lemmas built on v4.35.0; all 5 targeted and 280 project axiom checks passed. A path/leaf window has at most 84 edges, or 82 when its common exterior has no degree-eight vertex. `lean/R310/MarkedStrip.lean:75`
- **Hand / enum:** Audited the paired-window edge formula and degree constraints. Controls recovered all 18 smaller path windows as \(C_5\), rejected 18 triple-witness mutations, and checked the paired edge formula on 32,520 nonedges. `ralph/lanes/H/ROUND7_REVIEW.md:61`
- **Ledger / literature:** Recorded the critic’s scoped C and E exclusions and B’s certificates for the supplied 614 critical roots only. The November 21 literature recheck found no superseding bound, public bulk order-39 census, or exact order-30 counts at 88–99 edges. `ralph/CLAIMS.md:129`, `ralph/lanes/H/LIT.md:156`

**Best next step:** A/G have the strongest new route for the paired e168 case: 1,988 marked order-27 rows for center codegree three, independently matched by A. Apply the new degree and edge constraints before solving completions, and keep codegrees one and two separate. B and the critic should bind the operator’s e108 delta before changing the accepted census deficit.

## Critic (ok)
- **Confirmed:** At e168, both path/leaf strips are excluded at centre codegree 3, and at codegree 2 only when the paired window has minimum degree 3. Neither degree distribution is closed.
- **Confirmed:** C’s 12-vertex private side has 16–21 edges in the scoped `(12,14)` split. E’s 57 proofs exclude `G?bBro` only in the stated mixed involution profile.
- **Confirmed:** The 1,142 new critical e108 keys leave **124 missing**. Floor 109 and all ten U88 keys remain open.
- **Rejected:** No primary exclusion failed at its stated scope. Broader closure claims and UNSAT inferred from caps or projections were rejected.
- **Rules:** No lane resource breach, commit, or push was verified. Unattributed flow/config edits need operator confirmation.
- **Core split A–H:** **3 / 25 / 8 / 4 / 16 / 2 / 20 / 2 = 80**.
- **Best next step:** Find an exact marked source or a local obstruction for the higher-minimum-degree e168 paired windows before scaling SAT.
- Full review: `ralph/critic/round_007.md:1`. Next-round directives: `ralph/critic/LATEST.md:1`. No order-40 graph passed the gate; the baseline remains **278 near-regular MTF distributions plus Case R**.
