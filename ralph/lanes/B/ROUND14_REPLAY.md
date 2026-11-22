# Round 14 — supplied reducible 32/e108 extension tranche

## Prelaunch estimate

One foreground core, no discovery or full campaign. The preexisting round-6
4,096-key pilot has 3,923 eight-cliques and 173 complementary proofs. Its
compact path costs 9.61 CPU-s for production and 5.20 for replay; scaling by
eight gives 118.48 CPU-s. Two witness-verifier passes add about 16 CPU-s.
Budget 150–225 CPU-s total, allowing for the independent second encoder,
an extra replay checker, and binding/validating inputs. Expect about 1,384
proof files and 3.8 MB of LRAT payload by straight pilot scaling (not a
bound). A one-slot foreground run has a 520-s wall cutoff and per-child
timeouts (CaDiCaL also has a six-second soft CPU limit). This leaves margin
under the authorized 600 aggregate CPU-s including controls. The final
test is to cover 32,768 supplied keys; neither acquisition of missing
critical classes nor completion of the full reducible tranche is authorized.

## Coverage and replay

Use the SHA-bound, sorted `work/e108_r5/reducible.g6` with 2,102,271
distinct records. Select one key per equal-width rank stratum: one-based
ID `1 + floor((2*i+1)*2102271/65536)`, `0 <= i < 32768`.
Rebind this exact selection in replay. Independently check all eight-demand
cliques, require their exact ordered complement, and verify every seven-
demand pin before applying the row-permutation argument in `FLOOR7_108.md`.
Replay reconstructs the necessary CNF using a second implementation,
matches the producer digest, and checks the LRAT against these bytes
with both `lrat-check` and `cake_lpr`. No SAT solve is needed for replay.

From `scratch/B`, use one foreground core and fresh output directories:

```sh
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
script=../../ralph/lanes/B/src/e108_r14.py
nice -n 5 timeout --kill-after=3s 60s python3 "$script" control work/e108_r14_control_recheck
nice -n 5 timeout --kill-after=3s 250s python3 "$script" replay work/e108_r14 work/e108_r14_recheck
```

## Result: cert, named 32,768 keys only

All 32,768 supplied residues are nonextendible at a degree-seven root of
an MTF (3,10,40) graph: **31,407 checked eight-demand cliques and 1,361
dual-checked LRATs**. All complementary residues admit the seven-demand
pinning; 1,225 LRATs are single-line RUP, 136 from CaDiCaL. The two CNF
encoders agree at every proof index. The deterministic tranche overlaps
the archived 4,096-key pilot at exactly **64** keys (61 cliques, 3 proof
rows); common clique witnesses agree byte-for-byte at the mask level.
The full source digest, exact length and strict key ordering match the
earlier validated round-5 reducible partition. The tranche was freshly
checked for order, edge count, triangle-freeness, alpha at most eight,
and existence of an alpha-preserving one-edge deletion at every key.
Traces independently returned all 32,768 isomorphism types.

The positive smaller gluing control is `K7,9`: all nine degree-seven
roots satisfy the necessary CNF, a fresh SAT solve agrees, and the
eight-clique scan is empty. All 39 rooted completions of saturated
Exoo39 also satisfy the necessary clauses. The 39 known e104 controls
all replay as eight-demand cliques. Rejected mutations: zero demand,
dropped witness with unchanged complement, absent proof index, empty
LRAT and valid LRAT against a known SAT CNF. `cake_lpr` returns zero on the
two bad LRAT calls, but without its verification marker; exit status alone
would not distinguish them.

| Phase | CPU-s | Wall s |
|---|---:|---:|
| Bind full input twice and validate tranche once | 3.59 | 3.57 |
| Eight-demand scan plus seven-demand pin scan | 0.47 | 0.46 |
| Verify all 31,407 clique witnesses, overlap and exact complement (initial / replay) | 5.22 / 5.99 | 5.23 / 6.00 |
| Produce proofs with first checker | 68.35 | 68.72 |
| Independently rebuild CNFs and run both checkers | 75.95 | 76.58 |
| **Total tranche and replay** | **159.74** | **160.73** |

Controls and Traces add 1.14 CPU-s. Across the per-proof production
and replay loops, encoding cost 41.73 CPU-s, proof generation 7.90 CPU-s,
and checks including receipt hashing 94.54 CPU-s. The p99 and max CPU-s
per proof were 0.06175 / 0.06959 (producer, max source ID 708125) and
0.06506 / 0.07116 (replay, max source ID 149388). Max wall per proof was
0.12003 s / 0.08392 s. The 16 consecutive groups of 2,048 tranche keys
had **49–186** complementary proofs and **5.17–19.94 CPU-s** spent in the
combined proof loops, so use dispersed work assignment rather than
assuming uniform cost across contiguous key ranges.

**Storage:** 1,361 LRAT files, 3,346,242 proof bytes, largest 10,826
bytes (source ID 1049243). Production retains 1,369 files (8,929,331
apparent bytes); the replay adds two files (295,147 apparent bytes), no
duplicate proofs or retained CNFs. Combined allocated file bytes are about
15.48 MB as reported by `stat`, excluding directory metadata.

**Estimate only:** proportional scaling is about **2.85 core-hours** for
the whole named reducible list, including this tranche, or 2.8 more after
reusing this tranche but not deducting the prior pilot. This is 21 minutes
at eight continuously productive, perfectly balanced slots, not a wall
time commitment. Extrapolated storage is about 87,300 LRAT files and
215 MB of proof payload (about 1 GB total allocation if left unpacked).
This estimate is not a worst-case bound and says nothing about missing
critical keys. If approved, partition remaining source IDs exactly and
interleave by rank to reduce the observed tail skew. No full campaign has
been launched.

Neither five missing critical classes nor any untested supplied residue
is eliminated by this tranche. No floor 109, e88/U88 change, or profile
subtraction follows. Evidence: `scratch/B/logs/e108_r14{,_control,_traces,_metrics}.log`,
`scratch/B/work/e108_r14/`, `scratch/B/work/e108_r14_replay/`, and
`sha256sum -c ralph/lanes/B/ROUND14.sha256` from the repo root.
