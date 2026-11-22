# Lane D — round 15, November 22, 2026

**K=2, t=16 excluded on all three shapes, submitted for critic review.** If an R(3) graph has exactly two deficient pairs, **both** deficient paths have at least **17 distinct induced C5 closures**. Not 17 disjoint pentagons. **R(3), R(4), R(3,10), and K=2 above equality remain open.** No candidate. Previous D-035–039 confirmed; round 14 summarized in `LOG.md`.

## Jobs

| PID | Command | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| none | All bounded producers, LPs and checkers finished. | `scratch/D/roles15/clean.log` | 0 | — | — |

Allocation 16; no detached or stopped jobs. No request for additional cores. `S=scratch/D/roles15`. All labels below scoped to stated local results, pending external review.

## Results / claims

| Label | Result | Evidence | Named core-h |
|---|---|---|---:|
| hand + enum + cert (local) | No K=2 deficient flag at t=16. D-028 ensures both unique paths are disjoint including their witnesses. The t≥16 base and three-shape reduction use the square bound D-039. 287 primary ordinary labelled LRATs; no original edge-kernel closure, no exclusion at t>16 or other K. | `EQUALITY16.md`; `S/clean/{catalog.log,completed.tsv}`; `round15_replay.sh` | 0.0672 original proof production + both checkers; 0.0472 independent clean replay incl alternate |
| hand + enum + cert (local) | C10+C6: the C6 alone fixes all 21 exterior masks: six singleton, six distance-two, three copies of each antipodal pair. Of 71 hub profiles 68 fail before seed cuts; three need 24 cuts total. Also one independent **unsplit** hub-labelled formula and proof. | `EQUALITY16.md` C10+C6; `S/{hex-seven.jsonl,edges?.jsonl,hex-edge-*.lrat,hexone-1-0-1-1.lrat}` | 0.00164 projected searches + 0.00280 primary proof/check sets |
| hand + enum + cert (local) | C8+C8: one component has no weak pair inside it or from it to Q. Independent catalog 1,547→123 component populations. 122 contradicted before any seed cut; ID 154 has a local SAT arrangement but 25 guarded seed cuts exclude it. All 123 proofs. | `S/{ind-8.log,octo?.jsonl,oct-last.jsonl,oct-*.lrat}` | 0.00355 searches + 0.00569 proof/check sets |
| hand + enum + cert (local) | C16 has an eight-site arc avoiding all weak endpoints on the cycle. Fix six central Q-contact columns; independent catalog 172→93 reversal classes. 78 span-eight proofs; 1 local model and 14 caps carried forward, all 15 refuted with the full wing (ID 346 needed 38,342 conflicts). | `S/{ind-6.log,arc8.*.jsonl,arc16.*.jsonl,arc-last.jsonl,arc-*.lrat}` | 0.05685 searches + 0.05874 proof/check sets |
| enum + exact arithmetic | Second pair **and unique witness**: all 23,310 labelled roles per shape after D-028; first-book stabilizers 32/120/256; direct local tests leave 7/11/6 orbits (15,750 labelled each). Shared marked LP alone cuts 1/24 placements and no whole shape; other 23 fractional. Both wrong-witness mutations rejected. | `S/{roster?.jsonl,role?.jsonl,role-final-cal.log,clean/catalog.log}` | 0.00283 full marked LPs |

## Next / reviewer requests

1. **Critic/H:** `bash ralph/lanes/D/round15_replay.sh scratch/critic/D15-audit 4`. Full successful lane-side replay `S/clean.log` rebuilt all 288 CNFs, compared original hashes and reran both proof checkers. `EQUALITY16.md` gives graph semantics, physical roles, budget and controls. `scratch/D/round15_evidence.sha256` binds primary evidence. The finite cover plus graph implications are hand+enum, not a single Section-7 global Ramsey certificate.
2. If accepted, the next equality layer **t=17 at K=2** has on each shore exactly one degree-three vertex and seven of degree two. Determine the possible marked graphs from this structure *before* running SAT. Search for a regular patch disjoint from degree-three vertices and the second pair, pricing its **integer column populations and actual Q edges**. At t=17 each degree-three site has five, not six, contacts to Q; `e(Q)=44`, not 43; a neighbor of a patch site may lie off patch. Do not reuse the C6 equality footprint without checking the residuals. No mass rich-roster run. Alternative: use the new bound as a necessary cut for original hard kernels without treating the two covers as a product.
3. No claim against K>2 or all of K=2. General lower bound remains ≥13 for every path and ≥16 for some path, not ≥17 in every graph. R(4) not reached.
