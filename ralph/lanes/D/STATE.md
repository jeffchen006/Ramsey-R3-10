# Lane D — round 6, 2026-11-21

**Open:** R(3) and R(4) remain open; 110 original minimum-root keys
unchanged. No graph candidate, no new Sec. 7 certification. In the
alternate maximum-square cover, a new hand argument reduces the
max12 root cover from 13 forest keys to **nine**. The 76 max13..16
keys are untouched. Higher strata must not use the forest premise.
Round 6 used at most two solver slots and started no detached jobs.

## Results and claims

| Label | Scope | Evidence | CPU-h |
|---|---|---|---:|
| hand + enum | New score `S(e)=q22(e)+p3(e)`, where `q22` counts isolated edges and `p3` counts 3-vertex path components in the edge kernel. In max12 `sum S=240+2*w`, hence max S≥2. Disjoint max-score classes: `Smax=2` keys 24,25,26,28,29,32; `Smax=3` keys 21,23,27. Root keys cover each class (not disjoint by key). Path-size census independent of graph generator; identity checked on C16 and mixed-codegree C20. | `TIGHT_FOREST.md`, `scratch/D/seed_r6/forest_score.log` | <0.001 |
| hand | In the subset `max_e q22(e)=0` of max12, at least 60 edges must have key 32. It alone covers this subset of the `Smax=2` class. Not an exclusion of rooted extensions at 33/34. | `TIGHT_FOREST.md`, `forest_score.py` | — |
| hand + enum | Exact root-to-anchor q22 caps via subset sums; all 360 C20 local cap checks agree, 300 negative controls. Independent seed windows and small residual floor table replay all 13 C16 witnesses. | `TIGHT_FOREST.md`, `scratch/D/seed_r6/{cal,q22-cal}.log` | <0.001 |
| enum | Exact SAT forest, signed count and compact variants exhaust 144 smaller solves each; two forest graphs (one nontrivial) of 13 labelled, all per-key sets and pin sets match. No-2/2 clause admits K3,3 and rejects tight Clebsch. | `scratch/D/seed_r6/{sat16/check,compact16/check,no22-cal}.log` | 0.012 |
| open | Ordinary/forest unpinned and plain/signed k=7 at key34 all cap at 48 CPU-s. Compact forest key32 control reaches 30,001 conflicts; global q22=0 variant hits 55 CPU-s. Neither model nor refutation. | `scratch/D/seed_r6/{sat40,compact40}/*.log` and `.time` | 0.083 |
| open | Independent seed-window transport: 34 feasible with/without forest; 21 inconclusive. q22 caps on t=0 keys 32/33 inconclusive; 34 and k=7 still feasible relaxations. No change in matched k=6,14 IPM endpoint pins on key32 (all internal limits). | `scratch/D/seed_r6/{*,q22/*,key32pins/*}.json` | 0.115 |

## Jobs

All bounded foreground jobs ended; no live or stopped Lane D PID.
Round 5 PIDs 30557, 136533, 479273 also absent. No detached table
entries, no requested extra cores or RAM. Sessions for the round's
matched probes (two cores each): 6616 windows, 40899 key34 SAT,
20852 q22 LP, 34913 key32 SAT, 24164 key32 pins. Scope, budgets,
exact commands as reflected by the invocations, and logs are under
`TIGHT_FOREST.md` / `scratch/D/seed_r6/`. New measurements total
about 0.21 CPU-h including controls, all outcomes are censored or
feasible relaxations on the target. No cost extrapolation to a full
run. Frozen replay: `scratch/D/round6_evidence.sha256`.

## Next

- H/C/critic: audit the score double-count and the nine-key cover
  in `TIGHT_FOREST.md`. Root at **max S**, not necessarily max q22;
  for `t=0` the same maximizing root is always key32. The four
  omitted root keys may still occur as non-maximizing edges.
- Try an eager local signature cut using `S(e)<=2` on all edges
  of the max-score-2 stratum, or a narrow pinned support design on
  key32 in `t=0`. The general window rows, extra q22 clauses and
  endpoint count pins have no demonstrated target win; don't
  repeat them at greater breadth without a new constraint.
- Keep older exact R5 exclusions 19/20/22 (`enum`, critic confirmed)
  and key34 k=6 exact Farkas separate. Nothing transfers to the 110
  minimum-root keys or to R(4). No single-group K3,4 or fixed-cycle
  reruns. Historic scope and evidence now in `LOG.md`.
