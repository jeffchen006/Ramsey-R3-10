# Lane C — round 10, 2026-11-22

R(3,10), Case R, R(5), R(6) and global `f*=9` remain **open**. No
candidate. The cap-five reciprocal 22/21 join below is only a pilot,
not all catalogue rows. No cap-six or 21/21 extrapolation.

## Results and claims for H / critic

| Label | Scope and result | Evidence (lane-relative unless stated) | CPU-h |
|---|---|---|---:|
| hand + enum, independent confirmation | A complete K3,3 in a 9-regular target at max codegree ≤5 cannot have both anti-triple windows of order 22. 191 valid nonisomorphic source graphs (class count [D-C7]); 278,160 marked halves, 202,980 cards, 13,875 requested keys, no mates. Therefore the three B masks have union ≥13 when F_A has order 22. This reproduces scout R; do not count twice or as R(5) closure. | `proofs/reciprocal_windows.md`, `ROUND10_REPLAY.md`, `scratch/C/r10/{equal22,source-check,source22-shortg}.log` | 0.00024 equality stream |
| enum, pilot only | 8,192 new disjoint order-21 hosts at cap five: 34,172 candidate card pairs, 57,121 marked pairs, 41,907 aligned card maps, **70,229 exact role maps, 0 undecided**. Separate index and exact replay match every role key, all 69,450 elementary witnesses and all 779 domain obstructions. 395 planted maps pass; bounded direct join matches 4,882 full keys. | `ROUND10_REPLAY.md`, `scratch/C/r10/{cal-check,pilot,audit,scout-index}.log`, `scratch/C/r10/{pilot,pilot-ids}.tsv` | 0.00457 stream + 0.0168 alternate source and audit |
| cert, bounded proof sample only | Four asymmetric SAT controls; 48 sampled non-cap role maps have dual checked LRATs in both dense and thin CNFs. The thin clause sets are subsets of the corresponding dense sets, with identical keys. 29.63→7.54 end-to-end CPU-s (3.93×), not a closure of the other sample maps or of the source. | `reciprocal_proof_pilot.py`, `scratch/C/r10/proof-{pilot,pilot-thin}/receipts.tsv`, `scratch/C/r10/proof-compare.log` | 0.0103 matched tests |
| estimate | ~0.26 CPU-h fast census stream, ~2.3 independent audit, ~4.7 thin proof queue for the measured domain fraction. Plan 7–16 CPU-h total excluding full catalogue provenance, not a guarantee; third quartile has >13× the alignment density of the fourth. Explicitly audit the heavy `forced-domain` tail before scaling. | `ROUND10_REPLAY.md` | forecast only |
| confirmed, frozen | R(6) diagonal-four 8/8 P3: 105 zero patterns, 34 contradictions; 47 no triples, 24 at most one triple, none allows quadruple. No new rounds on private wings; round-9 hashes pass. C-026/C-027 remain 90 excluded layout/residue rows, 71 patterns and 330 rows open. | `proofs/p3_rounded_incidence.md`, `ROUND9_REPLAY.{md,sha256}`, `scratch/C/r10/p3-freeze.log`, `ralph/critic/round_009.md` | prior |
| confirmed C-025 / C-024 | Global R(6) f*=9 `(12,14)`: smaller private K12 has 16≤e≤21; 24 of 39 profiles open. `(12,12)` impossible with 1,134 CakeLRAT replays; at most one shared vertex. | `ROUND{6,7,8}_REPLAY.md`, `ralph/critic/round_{006,007}.md` | prior |
| previously confirmed | R(7) excluded; R(6) no P4. P3 diagonal-five residue e≤61, diagonals three/four e≤63. If f*≥8 P3 arms both 8 and diagonal 3 or 4. Global f*=9 makes J a nonempty matching. Isolated f8/e80 has ≤1 degree-three vertex; anchored X' e≤64. | `ralph/critic/round_{001,003,004,005}.md`, `ROUND{4,5}_REPLAY.md` | prior |

## Jobs

None detached. All target batches and SAT subprocesses were foreground,
niced and wall/CPU/memory bounded. An exploratory all-by-all run on the
395 repeated control windows reached its 60-s wall TIMEOUT; the
same-parent planted recovery plus the exact bounded no-index control
replaced it (no target result, temporary output deleted). Two earlier
proof-cost attempts had an input-empty-clause reporting mismatch in
`lrat-check`; use the final dual receipts, not the earlier exits. No
solver cap or undecided result in the final target/proof pilots.

## Next

1. Critic: review the hand+enum 22/22 reproduction and authorize (or
   decline) a **cap-five 22/21-only** sharded census. Do not count the
   8,192 sample hosts as full coverage. Before launching, check the
   1,118,436-host source provenance, bind all shard IDs, and monitor the
   third-quartile/heavy proof tail; use witness replay for the three
   elementary categories, thin CNF for the actual proof queue. H: useful
   small Lean target is the degree identity and 22/21 opposite-profile
   dichotomy in `proofs/reciprocal_windows.md`.
2. D: for a codegree-five triangle with exactly three common
   neighbours, reciprocal 22/22 forbids opposite mask union 12. A
   future 22/21 exclusion would forbid union 13 (opposite [4,5,5] with
   three common neighbours or [5,5,5] with four); not a general
   codegree-five triangle ban. The sample gives no new necessary cut.
3. Freeze the diagonal-four 47/24 split. Revisit only a genuine
   both-wings, same-common-assignment test with a measured loss of
   placements. No cap-six, 21/21, higher P3 SAT cap or R(7) production.
   P2 `(12,13)` still needs U1 calibration; `(13,13)` needs separate
   H20/K13 catalogues. There J denotes the codegree-six graph and f*
   the minimum wing-cross count; P2 denotes an isolated J-edge.
