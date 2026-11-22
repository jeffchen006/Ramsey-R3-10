# Lane C — round 14, November 22, 2026

**No candidate. R, R(5), and the full marked 17/17 block stay open.**
Completed 12 disjoint cap-five K4,4 17/17 shards `[0,24576)`; stopped as
directed when a completed shard reached a new expensive terminal tail.
No unresolved fillings within the prefix. Remaining left IDs:
`[24576,55055)` = 90,054,790 header IDs; never launched.

## Results and claims for H / critic

| Label | Scope and result | Evidence | CPU-h |
|---|---|---|---:|
| hand | For cap-five K4,4, exactly two neutral sites is equivalent to 17/17. Every such actual marked graph maps into the ordered header ID census with one of the two neutral bijections, and its true joint filling survives all necessary screens. The full-census implication is conditional, not established this round. | `proofs/panel17_census.md`, `proofs/reciprocal_panel17.md` | — |
| hand + enum, finite prefix only | 67,417,211 distinct header-passing alignments across 12 shards `[0,24576)`, independent per-ID stage and A roster match. 8,076,698 local→12,594 panel→3,464 joint→0 unresolved. Both terminals agree per ID on 148,231 joint fillings: 7,584 degree, 0 triangle, 36,245 codegree, 104,402 I10. | `ROUND14_REPLAY.md`, `ROUND14_{INPUTS,RESULTS}.sha256`, `scratch/C/r14/{coverage.tsv,audit.log,unresolved.tsv}` | 0.142 shards / ~0.159 all |
| estimate / measured stop | First `[0,2048)` (4,322,749 headers) cost 20.741 CPU-s; independent full-run estimates 756 s from first, 2,651 s from earlier pilot. Later shard `[22528,24576)` cost 114.886 s, six Python IDs >1 s (max 3.860 s) and max 7,059 fillings per ID; all resolved. Scheduler stopped without launching further. | `scratch/C/r14/{first.log,rest.log,rest.err,22528-24576/result.json}` | included |
| prior, round 13 | 366-stratum disjoint pilot 1,554,349 exact IDs, 197,502 local→327 panel→97 joint→0 open; smaller controls 366 atlas entries, 3,448 panels/31,032 mutations, 2,118 planted terminal inputs. | `ROUND13_REPLAY.md` | prior |
| prior confirmed, round 12 | Cap-five order-22 K3,3 window `F_A` with all three opposite B codegrees five satisfies `e(F_A)≤64`. Only the named tight triple: 324 local repairs, 648 checker invocations; 1,298 local tight marks remain. Earlier full upper-only reroot retained all marks; do not rerun. | `ROUND12_REPLAY.md`, `proofs/reciprocal_r12.md`, `ralph/critic/round_012.md` | prior |
| prior confirmed, round 11 | C-033: cap-five 22/21 impossible; 11,657,178 maps and 32 local dual LRAT repairs. Inherited 22/22 exclusion forces union ≥14 for order-22 marks. C-034: thin/selector pricing only (10.37/6.57 CPU-h on 153,699 keys). | `ROUND11_REPLAY.md`, `ralph/critic/round_011.md` | prior |
| prior frozen, rounds 1–9 | R(7) excluded; R(6) no P4 and P3 diagonal bounds. R(6) f*=9 (12,12) impossible with 1,134 CakeLRAT; (12,14) smaller private K12 has 16≤e≤21, 24/39 profiles open. Diagonal-four P3 8/8: 34/105 zero patterns contradicted (90 rows excluded); 71 patterns and 330 rows open. | `ROUND{4,5,6,7,8,9}_REPLAY.md`, `ralph/critic/round_{001,003,004,005,006,007,009}.md` | prior |

## Jobs

**None active or detached.** PID 3002933 exited with status 1 due to the
intentional expensive-tail guard, not TIMEOUT; no other C work continues.
First and remainder ran foreground with at most two cores, per-process
16 GiB VM, hard CPU limits and wall timeouts. A bounded additional first
replay overlapped remainder briefly, staying within four cores.

## Next

1. H and critic: audit exact prefix receipts and the small counting
   lemma. See `ROUND14_REPLAY.md` for one-command first-shard replay,
   completed coverage and reason-vector digests. The first complete
   shard and lane A's old-pilot/old-triple overlap controls match.
2. **No continuation without review.** Reprice the six slow IDs
   and lighter controls before restarting at `[24576,26624)` with
   independent terminal comparison, remaining A checks and actual cap.
   The two worst 7,059-fillings IDs reject every fill by `I10` and may
   be suitable for a cheap upper-possibility-graph shared witness.
3. No 16/17, 15/17 or 16/16 result. Do not broaden to cap six,
   unmarked graphs or rerun the upper-only 22/20 reroot at old prices.
