# Lane C — round 12, November 22, 2026

No graph candidate. R(3,10), R and R(5) remain open. Completely tested
the current directive's one-sided cap-five order-22 marks, with a
narrow exclusion of the densest tight 22/20 slice pending critic review.
No order-20 catalogue or two-window join was used this round.

## Results and claims for H / critic

| Label | Scope and result | Evidence | CPU-h |
|---|---|---|---:|
| enum | The 191 order-22 hosts have 89,187,336 viable local B marks with union ≥14 (19,397,413 `(row,Z)` cards, all 191 hosts). The old 12 and 13 families have 278,160 and 7,791,069 marks and were excluded earlier; union-13 card/multiplicity manifest byte-matches round 10. 395 planted two-mask positives. Tight `14/222/2`: 1,307 keys, 391 cards, 129 hosts; separate common-pair/petal generator matches all literal keys. | `ROUND12_REPLAY.md`, `scratch/C/r12/{census.hist,census.hosts,census.tight,independent.tight}` | 0.0174 |
| hand + enum (negative result) | Shared two-root attachment and upper checks across all reroot triples leave all 1,307 tight marks live. 54,582 wing representatives: 162 fail domination, 36 fail opposite-window independent-set check, 54,384 live. C24 five-common-site positive in both labellings. | `proofs/reciprocal_r12.md`, `scratch/C/r12/reroot.full.log` | 0.0744 |
| **hand + enum + cert, pending** | Cap-five 22-window A, all three opposite B codegrees five: `e(F_A) ≤ 64`. The fixed 12 A-mask sites P have `e(P)=e(F_A)−45` by degree balance. All 9 tight marks at `e(F_A)=65` (3 cards/hosts) exhaust 324 one-sided e(P)=20 keys; all dual LRAT. Fresh replay, independent orbit binding and all 2,285 added cap axioms audited. Only the dense tight slice; 1,298 local tight marks remain. | `proofs/reciprocal_r12.md`, `ROUND12_REPLAY.sha256`, `scratch/C/r12/{dense-ledger.log,projection-dense/projection.jsonl}` | 0.0123 (+ census and reroot above) |
| cert (sample only) / open | Projection pilot two keys per bin e(P)=15..20: two sample dual LRAT at each of e19/e20, eight iteration caps at e15..18; pinned C24 projections + two dual LRAT controls. No e15–19 general claim. | `scratch/C/r12/{projection.pilot.log,projection-pilot/projection.jsonl}` | 0.0028 |
| C-033 prior confirmed | Cap-five K3,3 reciprocal 22/21 impossible; 11,657,178 maps, 32 local dual LRAT repairs. With 22/22 impossible, union ≥14 for order-22 marks; three opposite pairs of codegree five force a 20-window and five common sites. | `ROUND11_REPLAY.md`, `ralph/critic/round_011.md` | prior |
| C-034 prior confirmed | Proof price pilot only, thin/selector proof-only forecast 10.37/6.57 CPU-h for the 153,699 domain keys; no new production queue. | `ROUND11_REPLAY.md`, `ralph/critic/round_011.md` | prior |
| prior frozen C-024–027 | R(6) f*=9 private `(12,12)` impossible with 1,134 CakeLRAT; `(12,14)` smaller private K12 has 16≤e≤21, 24/39 profiles open. Diagonal-four P3 8/8 105 zero patterns, 34 contradictions; 90 excluded rows, 71 patterns and 330 rows open. No new private-wing work. | `ROUND{6,7,8,9}_REPLAY.md`, `ralph/critic/round_{006,007,009}.md` | prior |
| prior confirmed | R(7) excluded; R(6) no P4; P3 diagonal-five residue e≤61, diagonals three/four e≤63. Global f*≥8 P3 both arms 8/diag 3 or 4; f*=9 implies J is a nonempty matching. Isolated f8/e80 ≤1 degree-three vertex; anchored X′ e≤64. | `ralph/critic/round_{001,003,004,005}.md`, `ROUND{4,5}_REPLAY.md` | prior |

## Jobs

**None active.** All round-11 wrappers absent when checked.

| PIDs | Working directory / command | Log | Cores | Started / end |
|---|---|---|---:|---|
| 2877924 wrapper, 2877926 time, 2877927 Python | `scratch/C/r12`: `timeout 700 bash -c 'ulimit -v 16777216; ulimit -c 0; exec prlimit --cpu=420:425 /usr/bin/time -f "%U %S %e %M" -o reroot.full.time python3 -B ../../../ralph/lanes/C/reciprocal_r12_reroot.py --input census.tight --prefix reroot.full'` | `reroot.full.log` | 1 | 06:09:07 / completed ~06:13:35 (wall bound 06:20:47) |

Remaining tests were bounded foreground jobs. Nothing detached remains.

## Next

1. Critic/H: run `bash ralph/lanes/C/replay_reciprocal_r12.sh verify` for
   the 324 keyed certificates and independent tight census. H: the short
   hand lemma `e(P)=e(F_A)−45` in `proofs/reciprocal_r12.md`, step 4,
   is a Lean candidate and does not require any tight B-mark assumption.
2. The two sampled e19 wings had 156 and 455 added cap/IS clauses, LRATs
   ~1.5 MiB per key. There are 9,366 live e19 wings in the census. Do not
   scale this proof branch without a much stronger shared obstruction or
   critic approval. The upper reroot test alone removed zero full marks.
3. No 22/20 or 21/21 join, cap-six run, R(7) restart, large proof queue,
   or revisit of diagonal-four private wings without new direction.
