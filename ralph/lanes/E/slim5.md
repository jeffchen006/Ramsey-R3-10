# Order five, five fixed points: four pinned cases

**Result `cert`: no `(3,10,40)`-graph has order 5 with five fixed points.**
The hand reduction applies to all graphs, not just MTF, and uses the
original project's universal `δ≥5` certificate (`notes/critic.md`, Review 4;
fresh replay below), L6 (the universal pair bound), and F6.

Let `F` be the fixed set, of size five. Every fixed vertex must have a
moved neighbor (`δ≥5`), and degree at most nine means it touches
exactly one moved orbit. If a moved orbit `O` sees two or more fixed
vertices `u,v`, they are nonadjacent and share at least five neighbors.
Their degrees are `5+d_F(u)` and `5+d_F(v)`. L6 now says
`d_F(u)+d_F(v) >= 6`. If `a=|N(O)∩F|`, each fixed neighbor has
`d_F <= 5-a`, so `a<=2`. If `a=2`, both fixed vertices must touch
all three others, and triangle-freeness forces `G[F]=K_{2,3}`.
Put `A=N(O)∩F`, `B=F\A`, so `B` is independent.

In that `a=2` case `O` is independent by F6 and must touch every
other moved orbit `J`. If `J` is independent and not joined to `O`,
their union is an independent 10-set. If `J` contains an edge, it
has no fixed neighbor (F6); a nonadjacent pair in `J` could then
join `O∪B` if `J` does not touch `O`. So `N(O)\F` consists of all 30
other moved vertices. Since they are anticomplete to the independent
pair `A`, they would have `α<=7`, impossible by `R(3,8)=28`.

Thus the fixed-to-moving neighborhoods are injective: after relabeling,
five moved orbits are assigned to the five fixed vertices, one per
vertex, leaving two unassigned orbits. The assigned orbits are
independent. Each unassigned orbit is either independent (`I`) or a
5-cycle using cyclic differences `±1` (`C`) or `±2` (`D`): an internal
edge forces its full shift orbit, and both shift orbits would make a
clique. Permuting the two unassigned orbits and simultaneously
multiplying phases by 2 cover all possibilities with `II`, `IC`,
`CC`, `CD`.

Calibration uses `(3,7,22)` with order 5 and 2 fixed vertices. The
same injective attachment assumption is valid there: `δ≥4` via
`R(3,6)=18`, and `Δ<=6`, so each fixed vertex touches exactly one
orbit. If they share an orbit, the two fixed vertices are
nonadjacent, have degree 5, and their common neighborhood is the
orbit. Deleting both closed neighborhoods would leave 15 vertices
with `α<=4`, contradicting `R(3,5)=14`. Again 2 unassigned orbits
remain, with the same four types. See `slim5.py` and `scratch/E/` logs.

## Proof checks

The checker rebuilds the allowed base clauses (orbit triangles and the
pins and lex constraints of this exact subcase) and reconstructs the
edge-orbit map independently from the search map. The normalizers are
rotations of individual orbits, transpositions of two assigned orbits
simultaneously swapping their matched fixed vertices, and the swap of
the two unassigned orbits if their type is equal. All of these preserve
the exact pins, so the lex-least representative of an orbit of their
group satisfies the breakers. Each lazy clause in the final CNF is
matched to a logged independent-set witness: the clause contains the
variables for all pairs of that set. DRAT-trim checks the complete CNF
and proof. Strengthening a calibration lazy clause by dropping one
literal was rejected before DRAT (`cal22_bad_slim5_II.log`).

| Template | Solve wall s | CPU s, including checks | DRAT |
|---|---:|---:|---|
| II | 23.87 | 68.77 | VERIFIED |
| IC | 64.26 | 264.33 | VERIFIED |
| CC | 22.35 | 54.99 | VERIFIED |
| CD | 47.87 | 146.49 | VERIFIED |

Total 534.58 CPU seconds (0.1485 core-hours), excluding positive
controls, the earlier unpinned run, and dependency replay. Files are
`scratch/E/n40_slim5_{II,IC,CC,CD}.{full.cnf,drat,ext.sets,map,base.cnf,log}`.
Verify e.g. from `scratch/E` with
`python3 ../../ralph/lanes/E/slim5.py II n40_slim5_II --check` (use the
lane resource limits for a replay). `scratch/E/cert_sha256.txt` records
hashes. The degree-four proof was regenerated using the original
`critic/src/deg4_cnf.py`: exact original CNF hash, DRAT `s VERIFIED`,
LRAT `s VERIFIED UNSAT` by `cake_lpr`, 55.64 CPU s. The published
uniqueness of `C35(1,7,11,16)` is the hypothesis for `δ≥5`; see
`scratch/E/deg4_replay.log` and `scratch/E/deg4_k10.{cnf,drat,lrat}`.
