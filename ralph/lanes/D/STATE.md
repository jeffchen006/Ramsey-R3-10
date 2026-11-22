# Lane D — round 8, 2026-11-22

**Open: R(3), R(4); no graph candidate.** New all-R(3) induced P6
root. Let L be the maximum *number of vertices* on a simple path in
any edge kernel. If L=6 there are **three surviving eight-star profiles**,
not three for all of R(3). If L>=7 one can root at an induced P7.
Submitted for independent critic/H audit; no new unrooted Sec. 7 cert.

## Results / claims

| Label | Scope | Primary evidence | Measured CPU-h |
|---|---|---|---:|
| enum | Independent tip-root extraction from all 191 C22 classes: ten regular, three cap-three, 136 physical punctures. Both SMS formulations reproduce all 34 coloured marks and exactly all three unrooted classes. | `PUNCTURED.md`, `scratch/D/punct8/cal-{base,panel}.log` | ~0.002 |
| open | Matched 022/223 six-anchor target pilots both with and without canonical panel+tip windows: 0/4 decisions at 60-CPU-s limits. Stop this route unchanged. | `PUNCTURED.md`, `scratch/D/punct8/{022,223}-{base,panel}.log` | 0.066 |
| hand | Some edge kernel in every R(3) contains an induced P6. Without a simple P6 the high-diagonal graph must consist entirely of K1,3's, forcing each kernel to consist of two P3s and two P5s (matching six < seven). A closing C6 has one unit of boundary pair slack and forces an induced P7 on another edge. Works without max12, forest, or global minimum-root assumptions. | `PATH_ROOT.md`, Steps 1–2 | — |
| hand + enum | P6 eight-star cover: 4,756 labelled / 2,434 unoriented boundary profiles. Recovered all 239 planted C22 P6 occurrences. Independent unary SAT exactly matches labelled target cover. Fixed-star path checks (component and independent walk implementations) yield 22 max6, 1,184 max7, 1,228 max8. Only the 22 can occur when global L=6. | `PATH_ROOT.md`, `scratch/D/punct8/{path,audit-boundary,audit-paths}.log` | 0.002 |
| hand | L=6 only: local triple masks meet in edge-sharing pairs or are isolated triples, hence at most 14 triples in any neighborhood, at most two codegree-one partners per vertex, and at most 40 such unordered pairs globally. | `PATH_ROOT.md` “Local packing bound”; `scratch/D/punct8/packing-cal.log` (34 short C22 stars) | <0.001 |
| hand + enum | L=6 only: 22 reduced to **2298,2424,2431** (zero-based `path.tsv`). 16 basic, 2 exact and 1 packing projected CNF refutations. The packing proof for 2386 depends on the *four*-profile intermediate library from the first 18. All 19 byte-identically regenerated and dual LRAT-replayed; crossed proof rejected. Four already-empty inputs use explicit `.empty.lrat` copies of the input empty clause. Projection semantics and graph-first cover remain hand/enum, not link-(a) certified. | `PATH_ROOT.md`, `scratch/D/punct8/{receipts.tsv,audit-proofs.log,packing-sat-cal.log}` | 0.046 target solver + 0.0076 final replay |
| hand + enum / open | L=6 implies q*=12 or 13. Root at q* containing P6. Remaining 5+5 panel has five oriented types at 12, two at 13; profile 2298 is impossible at 12. At most **16 decorated roots** remain (10+6), not yet closed. Single-row overlaps and projected mask tables calibrated but no new surviving profile exclusion: first matched mask pilot six SAT, two trivially contradictory at max12. | `PATH_ROOT.md`, `scratch/D/punct8/{panel-cal,mask-overlap-cal}.log`, `{panels,masks,overmask}/` | 0.028 target solver |

No change to the 110 old minimum-root orbits or the round-7 dense/balanced
split. The latter is frozen with its existing scope (`SCORE_CAP.md`);
Farkas/enum max12 keys 19/20/22 and the key34/k6 pin remain separate.
This round used about 0.140 timed target solver CPU-h plus control,
construction, graph-first checks and proof replay (not exact total).

## Jobs

| PID | Command | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| none | All bounded foreground pilots, calibrations and proof checks completed; no detached or stopped lane jobs. | `scratch/D/punct8/` | 0 | — | — |

Share was 4 cores, never exceeded. Capped or SAT nonproof LRAT streams
discarded; all 19 witnesses used by the three-profile result retained.
`scratch/D/round8_evidence.sha256` freezes the code, cover, CNFs, witnesses
and experiment outputs. The checker reads actual verification strings.

## Next

- H/critic: review the short direct P6 and C6→P7 arguments first, then
  eight-star cover, contracted-link semantics, and the conditional
  high-hole step behind the nineteenth proof. `path_audit.py . proofs`
  replays the chain in order; independent audit requested, not assumed.
- For L=6 try a **joint** attachment constraint: in a 16-root decorated
  kernel all 17 kernels on the two full stars are determined by the
  22 exterior attachments. Enforce the three-profile marginals on every
  P6 in those stars simultaneously, not one exterior row at a time.
  First calibrate on all 48 corresponding C22 component placements.
- For L>=7 investigate a nine-anchor P7 boundary bound. Never carry the
  three residual keys, packing bound, or forest assumption into this
  branch. No higher core allocation requested.
