# Frozen order-33 residue audit, round 5

The scope is the degree-six root of a maximal triangle-free (3,10,40)-graph.
This audit binds the supplied rows to G's frozen round-4 proofs and checks
their one-edge decomposition. It is **not** a census of the six omitted
types, a new case exclusion, or a degree-six floor of 121 or 122.

## Census and exact edge moves

The exact e118/e119 counts of 5/69 and the combined count of 14,395 through
e121 are published dependencies (Goedgebeur–Radziszowski Tables 4/14;
Angeltveit, arXiv:2401.00392v2, §§3.3 and 6). The supplied rows are 74,
1,223 and 13,092, leaving six absent classes across e120/e121. The checker
validates graph6, order, triangle-freeness, no independent 9-set and
canonical distinctness. It uses dense nauty labels independently of G's
sparse-label checking. Raw labels are retained for proof binding.

| Adjacent levels | Exact canonical incidences | Higher derived | Higher deletion-critical | Lower with zero additions |
|---|---:|---:|---:|---:|
| 119 to 120 | 1,523 | 993 | 230 | 0 |
| 120 to 121 | 24,794 | 12,289 | 803 | 0 |

An addition is valid exactly when the nonadjacent endpoints have no common
neighbor. Adding cannot increase alpha. Any independent 9-set newly
created by deleting an edge `uv` contains both endpoints and seven more
vertices outside `N(u) ∪ N(v)`, and conversely. The standalone C++ loop
enumerates these moves with labelled edge witnesses. The Python checker
compares the **whole canonical incidence relation** upward and downward,
not just the cardinalities. It also matches the 803 critical classes to
G's frozen critical set.

Because every e119 type is supplied, any missing e120 type is
deletion-critical. Because every valid deletion of a supplied e121 has
its child in the supplied e120 list, every valid addition to a missing e120
is itself a missing e121. In fact, if `m` e120 classes are missing, each of
them has at most `6-m` nonisomorphic e121 additions, including zero. No
known e120 has zero additions: one known class has five upper neighbors,
the other 1,222 have at least ten. The five-child outlier is supplied
row 789, deletion-critical with 20 labelled additions (see
`scratch/A/residue5/five-children.log`). The empirical histogram is not a
universal bound and does not rule out the no-addition case.

Calibration: all 191 known (3,7,22) classes, all labelled moves compared to
literal toggling and an independent complement-clique check, with full
up/down incidence at each edge level. A permuted duplicate, an omitted
incident class, an omitted frozen class and a short exact count all fail.
An isolated class omission can escape an incidence check, so a count or
another complete cover must be supplied separately.

## Proof binding

The frozen manifest and the actual graph6/proof partitions are checked for
all 14,315 e120/e121 rows. The catalogue and exact trace/shard indices are
matched, and every cited CNF is rebuilt from its labelled residue. For a
clique trace, every listed singleton or nonedge without a common exterior
neighbor must be covered by one column; cross-adjacency makes any two
demands incompatible. Seven pairwise incompatible demands cannot fit the
six columns. For the unpinned core, columns are independent dominating
sets in the residue, cover every residue vertex, obey the global degree
cap, and cover each nonedge with no internal common neighbor. All are
necessary for MTF gluing; a SAT core is not a gluing witness.

| Residue | Unpinned clique | Unpinned LRAT | Exact total e=169 LRAT |
|---|---:|---:|---:|
| e120 | 1,157 | 66 | 0 |
| e121 | 10,268 | 2,813 | 11 |

For e121 pinned rows, let `P` be the total number of private vertices
(with exactly one attachment). Each of the six private cells has at most
four elements: it and the other five neighbors are independent. Every
exterior vertex must attach by maximality. Therefore the cross-edge count
is at least `2·33 - P >= 42`. At e=169 there are exactly `169-121-6=42`
cross edges, so each cell has four private vertices, and all other nine
vertices attach twice. These are the equality rows used alongside the
ordinary MTF and degree rows to rebuild the pinned DIMACS, independently of
G's generator (both use PySAT for cardinality primitives). The positive
calibration substitutes the actual attachments at all 13 C13(1,5) equality
roots. The argument precludes total e<169 with e121, but the pinned proofs
are **not** unpinned or claimed at total e>169.

All 2,890 LRATs passed `lrat-check` and `cake_lpr` on the independent
regeneration. All 11 fallback unpinned model files satisfy every
regenerated unpinned-core clause. The first pinned LRAT failed both
checkers on its unpinned CNF. Omitted and duplicated partition keys and a
corrupted demand mask also fail the checker. The full replay used 294.63
CPU-s, 440.45 wall s, and 104 MiB peak RSS.

## Replay and deltas

Run `bash ralph/lanes/A/replay_high_residues.sh NEW_SCRATCH_OUTPUT_DIR`
from the workspace root. It uses one slot, replays existing proofs with
both checkers, and does not rerun the producer SAT solving. Outputs are in
`scratch/A/residue5/`; `index-full.tsv` records raw graph6 and DIMACS/LRAT
hashes, exact source positions and proof scopes. Proof files remain in
G's frozen tree rather than copied into a second 700 MiB bundle.

To bind later augmented inputs, use `audit_residue_moves.py BINARY bind-delta
OLD120 OLD121 NEW120 NEW121 OUTPUT`. It validates canonical set inclusion,
levels and total count; it rejects a gap unless `--allow-gap` is explicit.
It emits only new labelled rows at each edge level for a separate proof
check. This mode verifies membership/count, not extension impossibility.
