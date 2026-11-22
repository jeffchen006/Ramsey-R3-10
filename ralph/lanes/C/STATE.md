# Lane C — round 15, November 22, 2026

**No candidate. R and R(5) remain open. Completed the entire marked
cap-five `K4,4` 17/17 block (`hand + enum`, pending critic).** In a
hypothetical target under cap five, every `K4,4` now has at most one
exterior vertex with no neighbour in the biclique, conditional on the
review of this exhaustive result. This is not a statement that a
biclique exists or that all marked cases are excluded.

## Results / claims for H and critic

| Label | Scope and result | Evidence | CPU-h |
|---|---|---|---:|
| hand + enum, pending | Entire marked 17/17 census: 92,341,930 ordered IDs physically tested and 65,130,071 covered by exact shore exchange, zero unresolved of 157,472,001. Both neutral bits and all 13,046 HH diagonal IDs retained. Every joint filling fails a necessary rule; direct terminals agree for all 18,621 panel IDs (222,863 fillings over 5,081 IDs). Do not infer scan depths or terminal reasons for exchanged IDs. | `ROUND15_REPLAY.md`, `proofs/{panel17_census,reciprocal_panel17,panel17_cache}.md`, `ROUND15_{INPUTS,RESULTS}.sha256`, `scratch/C/r15/audit.log`, `scratch/A/r15/{receipts.final.log,coverage.final.tsv}` | 0.075 HH production / 0.108 charged incl. setup; prefix prior |
| enum, calibration only | New Python terminal keeps literal package join and exact cached independent-set witnesses; unchanged C++ terminal is independent. All six tail and 785 easy vectors match. Six tails: 20,797 cache hits, 13 searches, no common upper witness. The current easy stratum has 268 common upper witnesses. 2,118 smaller positives, 3,278 exact graph instances and 2,118 fixed-crossing mutations replay. Clean build reproduces first HH shard. | `scratch/C/r15/price/{controls.log,tail.tsv,tail.stats,easy.tsv}`, `scratch/C/r15/first-replay.log` | included |
| prior confirmed, round 12 | Cap-five order-22 K3,3 window `F_A` with all three opposite B codegrees five satisfies `e(F_A)≤64`. Only the named tight triple: 324 local repairs, 648 checker invocations; 1,298 local tight marks remain. Full upper-only reroot retained all marks. | `ROUND12_REPLAY.md`, `proofs/reciprocal_r12.md`, `ralph/critic/round_012.md` | prior |
| prior confirmed, round 11 | C-033: cap-five K3,3 22/21 impossible; 11,657,178 maps and 32 local dual LRAT repairs. Inherited 22/22 exclusion forces union ≥14 for order-22 marks. C-034: thin/selector pricing only. | `ROUND11_REPLAY.md`, `ralph/critic/round_011.md` | prior |
| prior frozen, rounds 1–9 | R(7) excluded; R(6) no P4 and P3 diagonal bounds. R(6) f*=9 (12,12) impossible with 1,134 CakeLRAT; (12,14) smaller private K12 has 16≤e≤21, 24/39 profiles open. Diagonal-four P3 8/8: 34/105 zero patterns contradicted (90 rows excluded); 71 patterns and 330 rows open. | `ROUND{4,5,6,7,8,9}_REPLAY.md`, `ralph/critic/round_{001,003,004,005,006,007,009}.md` | prior |

## Jobs

**None active or detached.** The round-15 scheduler finished normally;
its old timeout/time/Python PIDs were 779393/779397/779398. Command was
`nice -n 5 timeout 2500 /usr/bin/time -o rest.time -f '%U %S %e' python3 -B ../../../ralph/lanes/C/panel17_round15.py . A.census.tsv rest`
in `scratch/C/r15`, 10:29:17–10:33:02 Europe/Zurich, at most two scanner
or terminal workers (small parent merger), 16 GiB VM hard limits.
Logs `scratch/C/r15/{rest.log,rest.err,rest.time}`. All gates passed:
first shard cost 29.516 CPU-s; conservative first projection 1,034.821
CPU-s; final 270.204 CPU-s on HH production, ≤3 MiB retained including
the extra first replay. Max IDs 79.963 ms C / 2,123.519 ms Python vs
180/7,000 ms predeclared gates. No SAT wave.

## Next

1. H/critic: audit and ledger the exact marked-case conclusion only. H
   may formalize `|Z|=2 iff 17/17` and the involution on physical shores;
   neither Lean step would formalize the enumeration itself.
2. Do not rerun the 17/17 census or label 16/17, 15/17, or 16/16 excluded.
   If directed, attempt a cheap smaller-calibrated pricing experiment
   for the one-neutral 16/17 roster and restored singleton packages;
   don't presume an affordable join or order-16 atlas. Do not broaden
   to cap six or revive the previous upper-only 22/20 reroot.
