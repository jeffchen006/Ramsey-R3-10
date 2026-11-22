# Lane G state — round 14, November 22, 2026

**238 near-regular MTF distributions plus R remain open.** No candidate.
The 40 degree-six floor cuts are inherited from the critic; none added
this round. The ten conditional U88 keys and the round-13 t9 bounds
are unchanged. No floor 123 or complete order-33/122 cover.

## Jobs

| PID | Command | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| — | No active or detached G jobs | `scratch/G/round14/` | 0 | — | — |

Initial internal-uncapped simplex PID 3097512 exhausted its 140-s
outer CPU cap; window+MIP CPU-capped at 165 s. Neither an UNSAT.
No detached launches. All commands used one thread, 16 GB virtual
memory cap, nice +5 and wall limits. Largest RSS ~1.13 GiB.

## Results and claims

| Label | Result | Evidence | User CPU-h |
|---|---|---|---:|
| hand + enum | Built same-W-edge join: combined masks and degree on both endpoints, one matrix projected into both old residue edge tables, integer product capacities, target domination/codegree/private matching, optional mixed-wing induced edge windows. C13 all 26 literal positive pairs; 97 quota checks; literal C35/Exoo39 controls. | `rows/e170_shared_edges.md`, `round14_shared_edges.py`, `scratch/G/round14/{control,controls.final}.log` | ~0.014 controls incl. development |
| hand + cert + enum | On four predeclared old population tuples: three exact Farkas/weighted-box contradictions even with both edge tables free, independently explained by absence of a compatible occupied common-neighbor type. One exact shared-edge integer point for matching+middle, but its W has 22 triangles and fails 38 window rows. Mutating that point's projected edge table retains all old rows but needs four shared edges where only three exist. No whole-template implication. | `scratch/G/round14/{recomplete-0.jsonl,cert-details.log}`, `round14_edge_control.py`, `ROUND14_REPLAY.md` | 0.017 incl. double replay |
| open / estimate | Four free-population plain IPM/MIP prices: three numerically LP feasible, one LP cap, four MIP caps (one exact point via separate population pin above). Four free-population window LP caps. No cert/major full-template cost cut; do not scale. | `round14_pilot.json`, `scratch/G/round14/{plain-bounded,windows,windows-with-mip}.log`, `ROUND14_FREEZE.sha256` | 0.122 price incl. outer caps |

## Next round

- H/critic: independently bind the three rational certificates **only
  to their named round-13 population tuples**, not the whole templates.
  `ROUND14_REPLAY.md` has the commands; `cert-details.log` explains the
  three contradictions by no possible common-neighbor type. No cut to
  the 238 ledger, no extra U88 debit. One remaining pinned population
  is only an integer relaxation point, not a graph.
- Do not expand the free same-edge matrix to the other 26 templates
  or increase solver caps. The cheap support check is appropriate if
  a later algorithm actually supplies population tuples; this pilot
  does not cover those tuples. A substantially smaller complete
  projection would need a proof, not arbitrary population fixing.
- For e170, sixteen d6 keys remain (nine single, seven adjacent pair).
  `Z=48`, `e(H)=122`, 24 private/9 double sites; adjacent cores W have
  order 28, one wing crossing, 86 W edges. Old e168 geometry is not
  valid here. The 66+30 coarse integer witnesses are not embeddings.
- Keep scout N mode 0 as fixed-source comparator if needed; do not
  repeat the 512-sample experiment, bundle or launch an e122 census.
  B owns descent to 32/e108. No e168 work. Round-13 exact threshold
  gains and membership remain in `ROUND13_REPLAY.md` and its freeze.
