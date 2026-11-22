# Lane A state

Round 11, November 22, 2026. Share 4; no live or stopped A jobs. No order-40 candidate,
whole-distribution exclusion, or Case R closure.
Current replay: `ROUND11_REPLAY.md` and `scratch/A/strip11/round11.sha256`.
Round 10 replay: `ROUND10_REPLAY.md`; earlier work in `LOG.md` and prior replay files.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start / expected end, CET |
|---|---|---|---:|---|
| — | No detached A jobs | — | 0 | — |

Finished: 790867/790884, 790868/790880, 790869/790883, slices 0/1/2
of `audit_middle25_binding.py` in `scratch/A/strip11`; all gone.
Started 04:41:13 CET and finished by 04:59:28 CET, one core each.
Pilot 96/96: 14.71 CPU-s, projected ~0.9 CPU-h total; actual 0.864 CPU-h.
No A LRAT production or replay; only bounded SAT for addback controls.

## Results and claims

| Label | Scope/result | Evidence | A CPU-h |
|---|---|---|---:|
| hand + enum + cert, pending critic | d8 j2 δ(T)=2 mixed **middle-only**: 21,236 source rows (13,413 raw graph rows) and exactly 21,236 G dual-LRAT receipts agree with independent roles, ordered 12-shard schedule, fixed pins, eager rows, DIMACS and compressed trace SHA256. Final manifest is byte-identical, zero failed/missing/nonterminal/orphan IDs. Matching 69,278 outside tranche. This is G's proof run; A independently binds but does not replay it. | `audit_middle25_binding.py`, `scratch/A/strip11/{middle.independent.tsv,middle.manifest.diff,middle.[012].log}`, `scratch/G/round10/r25.d8.middle.bound/certificates.tsv` | pilot 0.004, full 0.864 |
| enum | Independently re-enumerated exact 3+4 marks from directed cross edge; 42/42 smaller-control labels match. Full order21 catalogue 1,118,436 → 6,160 marks on 6,056 graphs, exact labels match G. Every deficit is the cross singleton; no double deficit. Parent catalogue completeness is inherited, not rerun. | `replay_short_anchor.cpp`, `scratch/A/strip11/short.crossfirst.full.{keys,log}` | 0.005 |
| hand + enum, pending review | Mixed e168, noncross B pivot `b` of d9: every retained noncross B anchor `s` has `d_T(s) ≥ |T|−21`. For d8 pivot the same holds for retained noncross B anchors of original degree nine. At equality to the weaker floor all three old B doubles occur; remaining hole(s) must touch `s`. At d9 two holes would have to touch noncross `s`, impossible for either shape. At d8 one hole would make `s` degree eight. Applies regardless of δ(T); neither crossed anchors, short A, nor distribution closure. | `ROUND11_REPLAY.md`, `scratch/A/strip11/short.crossfirst.full.log` | same census |
| hand + enum, coverage only | G's direct `|T|=24` CNF includes all lifts of a marked equality parent with both orientations and permitted holes. All 51,395 role IDs and fixed shells match independent oracle. Real size-24 addback SAT when planted with either extra ordering; physical double-deficit mutants accepted as geometry at relaxed cap, fail the Ramsey premise at strict cap, and test hole consumption and nonconsumption. Real size-25 graft 179581, parent orbit 290424, has `d_T(s)=3 > δ(T)=2`, so do not use global minimum in a generalization. | `audit_short_anchor.py`, `audit_pinned_anchor_cnf.py`, `scratch/A/strip11/{short.controls.json,short.cnf.final.log}` | ~0.026 incl. rerun |

## Next

- Critic/H: judge the narrow middle tranche with the completed manifest
  comparison, and review the new short-B floor dependent on order-21 census.
- G owns SAT production; A limited to independent proof/coverage binding.
  Do not reinterpret the direct-instance pilot as a closure or extrapolate
  order24 to larger windows or from equality to all marked anchors.
- No scale-up of all-pivot selector (removed zero marks); keep high-minimum
  pure caps and two-root census stopped absent a material new filter.
- R(7) remains untouched under the critic's mixed-strip directives.
