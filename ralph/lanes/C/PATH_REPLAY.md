# Lane C round 2: codegree-six path windows

The criterion is a span of distinct vertices joined consecutively in the
codegree-six graph J. There is no inducedness assumption in the ambient G.
`proofs/path_windows.md` proves the reductions, including the cover and the
attachment rows. Inputs use the complete three-class (3,4;8) and 191-class
(3,7;22) censuses in `gluing/val`, dependencies D-G3b and D-G3. The main
join also uses e(3,8,26)=73 (D-E8), and the usual Ramsey bounds (D-R1).

## Regenerate and replay

From `scratch/C`, with distinct output names if comparing to a previous run:

```sh
ulimit -v 16777216
C=../../ralph/lanes/C
LABEL=../../opt/bin/labelg
SMALL=../../gluing/val/r3_4_8.g6
FULL=../../gluing/val/r3_7_22.g6
nice -n 5 timeout 45 python3 -B "$C/path_windows.py" "$SMALL" "$LABEL" --control --output replay-p4-ctl.g6
nice -n 5 timeout 45 python3 -B "$C/path_window_join.py" replay-p4-ctl.g6 "$LABEL" --control --output replay-p5-ctl.g6
nice -n 5 timeout 45 python3 -B "$C/path_neighbourhood.py" replay-p5-ctl.g6 "$LABEL" --control
nice -n 5 timeout 1800 python3 -B "$C/path_windows.py" "$FULL" "$LABEL" --verify p4_full.g6
nice -n 5 timeout 180 python3 -B "$C/path_window_join.py" p4_full.g6 "$LABEL" --verify p5_full.g6
nice -n 5 timeout 240 python3 -B "$C/verify_path_trace.py" p5_full.g6 p5_trace.jsonl
```

To regenerate the trace rather than consume it, use:

```sh
nice -n 5 timeout 180 python3 -B "$C/path_neighbourhood.py" p5_full.g6 "$LABEL" --node-limit 0 --trace replay-p5.jsonl --verify p5_attachment_full.tsv
```

A P4 row is graph6 on X[20], Y[2], Z[2], v0, v3. P5 rows on 30 vertices
are W[18], P5[2], P(-1)[2], P4[2], P0[2], v0, v1, v3, v4. These are labelled
covers, not necessarily distinct as unmarked graph classes. The trace is
JSONL with one row `[sha256(graph6_without_newline), category, witness, nodes]`
per supplied P5 row. A root obstruction `mtf` gives its unsupported pair;
`load` would give a vertex with insufficient capacity. In a `tree`, each
preorder node names a branch row q (q >= 0) or a shortage row -q-1. Rows are
the three type quotas, the thirty vertex demands, and lexicographically
ordered unsatisfied-pair rows. Masks are ordered by type and lexicographic
list of their vertices. The independent replay implementation does not
trust the search's chosen pivots or classify a complete packing as a leaf.
It binds the supplied residue rows, not the completeness of their cover;
check the two join stages separately. Lane A's independent P4 replay is in
`ralph/lanes/A/P4_REPLAY.md`. H's hand review of both reductions is in
`ralph/lanes/H/PATH_WINDOW_REVIEW.md`.

## Controls and P4 pilot

- C21 gives 42 oriented spans and a full regular graph recovery; all three
  stages pass (`p4_control.log`, `p5_control.log`, `p5_attachment_control.log`).
- Missing P4/P5 catalogue rows were rejected (`*_control_missing.log`). A
  forged P5 trace shortage was rejected (`p5_trace_forged.log`).
- `path_four_forced.py p4_full.g6 --cross` tests local degree, triangle,
  codegree, and maximality rows, splitting over all cross-edge placements
  on D0 x D3 with the required edge total. It leaves 1,356 rows, exactly the
  number satisfying the simpler forced Y--Z-edge criterion. The control
  keeps all 42 spans and rejects a corrupted missing endpoint edge.
- `path_four_sat.py p4_control.g6 --control --budget 0 --iters 60` gives 8
  valid positive rows and 5 UNSAT rows; all 8 witnesses independently pass
  `tools/check_graph.py --n 21 --k 7`. In the large pilot, three spread rows
  per e(A) stratum (77 to 81) all reached the 24-iteration limit, about
  0.31–0.59 process CPU-s each (6.79 user-s total). No UNSAT proof, no
  closure, and no reason to scale the same lazy-cut encoding. Logs
  `p4_sat_{control,independent_control,sample}.log`.
