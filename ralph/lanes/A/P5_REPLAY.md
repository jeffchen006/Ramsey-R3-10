# Independent five-root window-cover check

**Scope: enum (coverage only).** This check starts from the exact labelled
P4 cover independently checked in `P4_REPLAY.md`. It checks the P5 join in
`ralph/lanes/C/proofs/path_windows.md`; it does not decide extension. The
separate attachment trace and checker are documented in
`ralph/lanes/C/PATH_REPLAY.md`. The combined exclusion remains subject to the
critic's verdict on C-009.

`check_p5_cover.py` takes both orientations of each whole P4 graph. It
canonically labels the induced middle window and enumerates every witness
isomorphism with Lane A's independent adjacency-checking backtracker. It
relocates the **whole** input graph, including its two exterior roots, onto
the common labelled window. For a pair of compatible placements it overlays
both adjacency matrices, adds the forced cross-root edges and enumerates
the cross-wing edges with the right total. It checks triangle-freeness,
degrees, codegrees and independence directly on the overlay. Equal
placements need not be paired because the window marks are nonempty and
must be disjoint.

The comparison is exact graph6 equality after taking the lexicographic
minimum of each row and its root reversal. Within each of `W`, `P5`,
`P(-1)`, `P4`, and `P0`, the labelled order is retained when reversing.
It is **not** a comparison of unmarked graph isomorphism classes. The two
outer wings are ordered by their transported masks on the common canonical
window so the exact comparison uses Lane C's label convention. The
checker also rejects duplicates modulo reversal.

## Reproduce

From the repository root (commands write nothing outside scratch):

```sh
root=$PWD
sha256sum --strict -c ralph/lanes/C/PATH_INPUTS.sha256
sha256sum --strict -c ralph/lanes/A/P5_REPLAY.sha256
cd scratch/A/p5
ulimit -v 16777216
ulimit -t 240
check() {
  nice -n 5 timeout 300s python3 -B "$root/ralph/lanes/A/check_p5_cover.py" \
    "$@" --labelg "$root/opt/bin/labelg"
}
check ../../C/p4_control.g6 ../../C/p5_control.g6 --control
check reversed-p4.g6 ../../C/p5_control.g6 --control
check ../../C/p4_control.g6 reversed.g6 --control
# These two intentionally exit nonzero:
check ../../C/p4_control.g6 missing.g6 --control
check ../../C/p4_control.g6 wrong-mark.g6 --control
check ../../C/p4_full.g6 ../../C/p5_full.g6
```

The control has 13 P4 rows, 3 window classes, 430 placement pairs, and 16
P5 rows. Every one of 42 oriented C21 spans is found under every alignment
of its middle window (672 exact marked alignments). Reversing the entire
input P4 catalogue or the output P5 catalogue independently leaves the
comparison unchanged. Deleting a P5 row yields `(missing=1, extra=0)`;
swapping its first marked vertex with vertex 0 (in W) gives `(1,1)`.

The full run checks 2,454 P4 rows, 177 middle windows, 47,031 placement
pairs and matches all 1,156 P5 rows modulo reversal in 10.87 CPU-s (10.88
wall, 33 MiB peak RSS), with no duplicate classes. Logs, canonical
reversal keys, controls and the pre-run estimate are in `scratch/A/p5`.
