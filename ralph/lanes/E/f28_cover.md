# Frozen involution cover for 28 fixed vertices

For a triangle-free graph on 40 vertices with independence number at most
9 and an involution with 28 fixed vertices, let `a` be its maximum fixed
attachment to a moved pair. F7 gives `1 <= a <= 7`: any adjacent moved
pair has no attachment by F6, an independent one has at most seven, and
at least one attachment is nonempty by connectedness (F3). No MTF
reduction is used within this symmetry case.

| `a` | Status | Evidence |
|---|---|---|
| 1–3 | hand, E-005 | `involution.md`, six-pair crown and residue bounds |
| 4 | cert, E-012 | `crown28_exact.md`, 42 checked proofs and exhaustive core cover; `replay_crown28.sh` |
| 5 | hand, E-005 | `involution.md`, six-pair crown and two-edge residue budget |
| 6 | enum | `overlap28.md`, four-cycle reduction and an exhaustive marked order-17 window check; `replay_overlap28.sh` |
| 7 | inherited F10 | `notes/symsat.md`, complete `(3,8,27)` involution census excludes 21 fixed points |

The aggregate is a mixed hand/cert/enum exclusion, not a new blanket
SAT certificate. In particular `a=6` uses the universal degree cap
and the seven complete order-17 classes, not `δ>=5`, MTF, or any f=32
hypotheses. The f=32 crown analysis starts with the separately checked
universal minimum degree five, and does not enter this cover. The round-5
freeze does not repeat any f=28 computations.
