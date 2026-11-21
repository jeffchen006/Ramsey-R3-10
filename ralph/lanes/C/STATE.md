# Lane C — round 2, 2026-11-21

**Open:** R(3,10), Case R, and R(6). No candidate graphs. Critic accepted
round-1 R(7) as `cert`, a custom trace with published seeds and hand
reduction, not Lean; A has preserved its package. Round-1 detail is in
`LOG.md`, with reproduction in `RESULTS.md` and `TRACE.md`.

Round-2 directive addressed: use consecutive order-22 residue windows;
split P4/P5 from isolated codegree-six edges and the P3 diagonal subcases.
No C8 rescan. Allocation 6 cores; at most 1 used by C at a time.

Write J for the graph of codegree-six pairs. `P4` means four distinct
consecutive roots in J, not a graph induced by these roots in G. The
P4 cover joins two order-22 windows at X20, leaving a 26-vertex graph
A with marked endpoints. The P5 cover joins two A's along the middle
order-22 window, recovering H30 = G - N[v2], with 99 edges. The remaining
nine independent neighbours of v2 give three types of size-eight masks.

## Results and claims for H / critic

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| cert (round 1, accepted) | R(7) excluded. Preserve custom trace label. | `ralph/critic/round_001.md`, `ralph/lanes/A/R7_REPLAY.md` | — |
| enum (round 1, retained) | No J eight-cycle in R(6). | `proofs/cycle8_join.md`, `ralph/lanes/H/C6_REVIEW.md` | — |
| hand | P4 and P5 overlap reductions, no inducedness premise. G is MTF in Case R. For P4, an edge Y--Z is present exactly when the endpoint masks on X20 are disjoint. | `proofs/path_windows.md`, `ralph/lanes/H/PATH_WINDOW_REVIEW.md` | — |
| enum | P4 cover: 31,994 markings / 13,613 X20 families → 2,454 labelled A26 rows. A independently matched it exactly; this is not an extension test. | `path_windows.py`, `scratch/C/p4_full.{g6,log}`, `ralph/lanes/A/P4_REPLAY.md` | 0.020 C + 0.014 A |
| enum | P5 cover: 177 triple-window families / 47,031 port-pair trials before disjointness; 1,156 labelled H30/e99 rows. | `path_window_join.py`, `scratch/C/p5_full.{g6,log}` | 0.003 |
| enum, exact trace replayed | No distinct five-root J span in R(6), hence no path component of order at least five, conditional on the P5 cover. 940 unsupported MTF pairs, 216 exhaustive trees (289,649 nodes, max 10,760), no complete packing or limit. Separate verifier replayed all supplied residues; do not promote final exclusion without critic approval of coverage and replay. | `path_neighbourhood.py`, `verify_path_trace.py`, `scratch/C/p5_attachment_full.{log,tsv}`, `scratch/C/p5_trace.jsonl`, `scratch/C/p5_trace_verify.log`, `PATH_REPLAY.md` | 0.012 enumeration + 0.013 trace production + 0.020 trace checking |
| enum | P4 MTF forced cross-edge criterion leaves 1,356/2,454 rows. Fixing each exact D0--D3 cross pattern and propagating degree, codegree, TF, MTF tries 36,039 branches and leaves the same 1,356 rows (34,395 partial assignments). This is not an extension result. | `path_four_forced.py`, `scratch/C/p4_forced_full.{g6,log}` | 0.0082 |
| enum control / open pilot | Exact coverage/attachments find C21 (42 oriented planted spans); missing cover row and forged trace leaves rejected. P4 SAT control: 8 valid smaller witnesses independently checked, 5 UNSAT. Larger sample (3 spread rows per e(A) stratum 77..81): 15/15 hit iteration cap, no verdict. | `PATH_REPLAY.md`, `scratch/C/p4_sat_{control,independent_control,sample}.log` | 0.002 SAT pilot |

## Jobs

| Timeout PID | Command from `scratch/C` | Log | Cores | Start CET | Expected / actual end |
|---|---|---|---:|---|---|
| 2770701 (finished) | `setsid nohup nice -n 5 timeout 1800` + `python3 -B ../../ralph/lanes/C/path_windows.py ../../gluing/val/r3_7_22.g6 ../../opt/bin/labelg --output p4_full.g6` | `scratch/C/p4_full.log` | 1 | 17:56:02 | Hard end 18:26:02; completed in 89.02 s |

No detached jobs remain. Foreground tasks use `nice`, `timeout` and 16 GiB
virtual cap. P4 estimate 757 CPU-s (sample 96 families in 5.34 user-s of
13,613, setup was sunk); actual 72.47 CPU-s. P5 join 10.55 CPU-s. P5
attachment estimate 48 CPU-s from spread 96-row sample; actual 42.34 CPU-s.
P4 propagation estimate 29.4 CPU-s; actual 29.44 CPU-s. P5 trace checker
spread 24-row sample 1.18 CPU-s, estimates 57 CPU-s by rows / 111 by nodes;
actual 71.25 CPU-s.

## Next

- Request critic review of P5 (especially coverage of port isomorphisms and
  independent trace verifier); keep `enum` until accepted. A independently
  verified P4 coverage. H reviewed both hand reductions; Lean unclaimed here.
- If both C8 and P5 exclusions accepted, J in R(6) has only isolated vertices
  and P2/P3/P4 components. P4: split by edge count 77..81 and D0--D3 pattern;
  factor the two side packings using distinct loads and cover demands. Do not
  scale the measured lazy-cut pilot as-is.
- P3: use N(v0) intersect N(v2) contained in N(v1); keep codegree-3, -4,
  and -5 diagonals separate. Each consecutive pair residue with a third J
  neighbour has a marked degree-three vertex whose deletion with its closed
  neighbourhood gives the 22-census. At P3 the two marked end roots in H30
  are nonadjacent, so the P4/P5 edge-based join does not apply.
- P2 (isolated c6 pair) is not covered by any triple-window result. Case R(3)
  independently reduced to 110 rooted reps in D's work (round 1); not a partition.
