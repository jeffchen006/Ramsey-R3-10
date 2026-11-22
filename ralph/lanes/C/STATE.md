# Lane C — round 13, November 22, 2026

No candidate. R(3,10), R and R(5) remain open. Critic's cap-five 17/17
directive completed: independent check of reciprocal panel semantics,
replay of old triple slice, and disjoint deterministic ~1% pilot. Three
price gates pass; no production scan or new proof queue launched.

## Results and claims for H / critic

| Label | Scope and result | Evidence | CPU-h |
|---|---|---|---:|
| hand | Under cap five, for a marked K4,4 with two neutral sites, each window has order 17; restoring a single root of a three-singleton group gives the same labelled 17-window after deleting its closed neighbourhood. Every actual package ensemble survives transpose support; only the joint step requires one physical filling. | `proofs/reciprocal_panel17.md` | — |
| enum (binding/control) | A's independent frames and two scout atlases agree on 55,055 physical frames and 9,959 literal row multisets. A checks 8,472 small physical root restorations, 366 small atlas entries, and both scanners accept 3,448 planted 3×3 panels and reject 31,032 mutations; 2,118 small planted partial graphs survive terminal propagation. The 498,668 header-passing left-triple alignments replay to 17,604 local→0 panel, complete at the stated marking only. | `ROUND13_REPLAY.md`, `scratch/C/r13/{A.controls.log,C.triple.stages,A.triple.stages,controls.log}` | 0.003 screen |
| **enum, finite pilot only** | 1,554,349 distinct ordered alignments in 366 deterministic strata, exactly disjoint from both triple orientations and the scout's regenerated old draws and their reversals. Two independent scanners match every ID's stage: 197,502 local→327 panel→97 joint→0 open. 1,869 joint fillings, all rejected; both terminal implementations agree on every ID's reason vector. No general 17/17 closure. | `ROUND13_REPLAY.md`, `ROUND13_{INPUTS,RESULTS}.sha256`, `scratch/C/r13/{pilot.audit.log,A.pilot.stages,replay.log,terminal.keyed}` | 0.007 screen + terminal; 0.009 roster+audit |
| estimate only | 604× fewer terminal calls than local fit count, not a time ratio. Buffered runs price full twin screening + C terminal ~0.38 CPU-h, ~0.75 CPU-h with Python terminal replay too; reserve 1–2 CPU-h, estimate excluding proof work. C per-ID terminal p50/p95/p99/max 0.753/1.887/2.441/9.239 ms on the sample. | `ROUND13_REPLAY.md`, `scratch/C/r13/{C.pilot.buffered.time,A.pilot.time,C.terminal.tsv,scout.perid.tsv}` | above |
| prior confirmed, round 12 | Cap-five order-22 K3,3 window `F_A` with all three opposite B codegrees five satisfies `e(F_A)≤64`. Only the named tight triple: 324 local repairs, 648 checker invocations; 1,298 local tight marks remain. Earlier full upper-only reroot retained all marks, do not rerun. | `ROUND12_REPLAY.md`, `proofs/reciprocal_r12.md`, `ralph/critic/round_012.md`, `scratch/C/r12/dense-ledger.log` | prior |
| prior confirmed, round 11 | C-033: cap-five 22/21 impossible; 11,657,178 maps and 32 local dual LRAT repairs. Inherited 22/22 exclusion forces union ≥14 for order-22 marks. C-034: thin/selector pricing only (10.37/6.57 CPU-h on 153,699 keys). | `ROUND11_REPLAY.md`, `ralph/critic/round_011.md` | prior |
| prior frozen, rounds 1–9 | R(7) excluded; R(6) no P4 and P3 diagonal bounds. R(6) f*=9 (12,12) impossible with 1,134 CakeLRAT; (12,14) smaller private K12 has 16≤e≤21, 24/39 profiles open. Diagonal-four P3 8/8: 34/105 zero patterns contradicted (90 rows excluded); 71 patterns and 330 rows open. | `ROUND{4,5,6,7,8,9}_REPLAY.md`, `ralph/critic/round_{001,003,004,005,006,007,009}.md` | prior |

## Jobs

**None active or detached**. Round-12 PIDs 2877924, 2877926, 2877927
were absent. All round-13 tests were foreground, 1 core/run, timed and
16-GiB VM capped. No solver launched; cap was 6 cores.

## Next

1. Critic/H may run `bash ralph/lanes/C/replay_panel17.sh OWNED_EMPTY_WORKDIR`
   for the atlas, control, roster and twin/terminal receipts. H: step 3 of
   `proofs/reciprocal_panel17.md` is a small Lean candidate (fixed labelled
   root restoration, no Ramsey catalogue needed).
2. If approved, run **bounded left-frame ID shards** of the cap-five 17/17
   roster with both Z maps and checked exact header totals. Screen inline
   or in chunks; reprice on the first complete shard before scaling. Print
   every terminal-open alignment; any remaining requires proof or stays
   open. Expect <3 CPU-h before proof work, not a guaranteed tail bound.
   Avoid counting the pilot/prior draw receipts as independent graph
   classes or assuming any `K4,4` occurs universally.
3. No 16/17 or cap-six claim; no full 22/20 census or upper-only reroot.
   R(5) 17/17 complement, 16/17, 15/17 and 16/16 and unmarked graphs
   remain out of this pilot. Revisit only with repricing or a fresh idea.
