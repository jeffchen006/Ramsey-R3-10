# Independent path-window cover replay

**Status: enum (coverage only).** The catalogue covers the 26-vertex residue
with designated endpoints on a four-vertex codegree-six path, subject to
Lane C's hand reduction and the published order-22 census size. This is
not a list of complete regular graphs, nor a refutation of this path case.

`check_path_cover.py` starts from every independent marked pair in the
191-graph order-22 census. It proves a marked pair is eligible only if its
existing codegree is at most five, because its common endpoint outside the
window contributes one. It deletes those marks, groups cores and enumerates
their attachments under every isomorphism with their representative. It
uses `labelg` to choose the same labelled core basis as C, but independently
checks distinct isomorphism classes and verifies all source-to-representative
maps. The fixed-point color partition is used only to restrict target domains;
the permutation search checks adjacency and nonadjacency explicitly. The
published counts, not the output of `labelg`, bind the input censuses.

For each unordered side-type pair, it builds the mandatory edges and enumerates
all subsets of the up-to-four cross edges whose endpoints have no common
core neighbour. It checks the edge count 73–81, degrees 3–7, codegree at most
six and independence number at most seven. No MTF or ambient completion is
asserted. The sorted list of labelled `X20,Y2,Z2,v0,v3` rows is compared
for equality, rejecting missing, extra, duplicate and reordered rows.

From the workspace root:

```sh
root=$PWD
cd scratch/A/path
ulimit -v 16777216
nice -n 5 timeout 900 prlimit --cpu=600:605 python3 -B \
    "$root/ralph/lanes/A/check_path_cover.py" \
    "$root/gluing/val/r3_7_22.g6" "$root/scratch/C/p4_full.g6" \
    --labelg "$root/opt/bin/labelg"
```

- `control.log`: order-21 C21(1,4,6) positive control, all 42 oriented paths
  represented; exact agreement with the 13-row smaller catalogue (0.09 CPU-s).
- `missing.log`, `forged-closed.log`, `forged-triangle.log`: deleted one row;
  claimed empty cover; appended a forged row that forms a triangle. All three
  fail the independent equality check.
- `sample.log`: 96 deterministically selected core classes, exact 18 rows,
  13.28 CPU-s including setup for all 191 source graphs.
- `full.log`: 31,994 marked placements, 13,613 core classes, 2,454 exact
  matching rows in 49.82 CPU-s and 247 MiB peak RSS.

All logs and mutated inputs are in `scratch/A/path`. The original order-22
census SHA-256 is `228d886ee01b3003d90c768af57804954f7adccbca901a3eeb3c69ccc020e8c5`;
the full exact C catalogue SHA-256 is
`a6385551754f3b545b03c06be4befc3c0e498969fec3d8362acc0bcd7b20d442`.
