# Round 24: mate-independent physical I10 clauses

**Status: hand + enum, controls and six saved relaxations only.** No target
search, UNSAT, proof certificate, 40-vertex candidate, board debit, or Ramsey
bound. The round-23 transport and `physical.v2` are unchanged.

## Graph-to-clause argument

Choose a shore, a list of boundary vertices, and distinct exterior
coordinates on that shore. Each exterior coordinate is either a labelled
grid copy or a physical slot, never an equivalence class of contact masks.
Together they must name exactly ten vertices. Reject any list with a fixed
boundary edge, a grid-to-boundary contact, or a contact between a chosen
slot and a chosen anchor of its own shore. A fixed root on the opposite
shore causes no exterior contact and does not require a guard.

Add these literals to a single clause:

- The negative occupancy bit of each chosen optional slot.
- For each such slot, **all** positive selectors to mates whose contact
  meets a chosen boundary anchor on the opposite shore.
- The physical edge bit on the chosen shore, when one exists, for every
  pair of chosen exterior coordinates. Include the bit even if it would
  be forced false for the mates of the saved model.

If the clause is false, all chosen slots exist. The occupancy/mate and
injectivity rows provide one actual mate each, with no opposite slot
reused. The absent positive selectors imply that these mates do not meet
the chosen opposite anchors. Every possible exterior edge is false by the
chosen shore's edge channel or by a fixed common anchor where there is no
bit. Thus the ten physical vertices form an independent set. The argument
is symmetric in the shores, applies with any forbidden independence size
if the number of names is changed accordingly, and needs no new variable.
If the boundary has no opposite anchors, the clause has no mate selectors.
It is a graph-necessary row, not asserted to follow from the relaxed CNF.

## Independent calibration and saved leaves

The width-three control decodes all 1,960 literal order-17 placements with
alpha exactly six. It enumerates 38,464 independent six-subsets and checks
all 48,956 distinct seven-subsets with just one edge (summed over
placements). Per shore, 17,804 are rejected by a fixed edge and the other
31,152 have exactly one true literal, including 5,040 with exactly one true
positive mate filter. For both shores, omitting such a filter loses a
verified order-17 plant. For both shores an induced order-16 plant of alpha
six, obtained by deleting one site of the sole edge, is lost on deleting the
corresponding negative occupancy guard. The latter is a **physical**
guard control, not a claim the order-16 graph satisfies the order-17 slot
population equations. All four fixtures are in `scratch/A/r24/controls.json`.

A's independent decoder checks all 367,934 rows of the six frozen model
assignments, their exact prefixes and mate relations, 40 physical vertices,
170 edges and triangle-freeness. It finds a total of 12,974 I10s. The
selected ten-set on each leaf has an exact compact clause absent from the
saved formula, leaf witness file **and** then-current `seeds-follow`. Each
new seven-literal projected clause has three occupancy guards and four
edge bits and is falsified by the saved assignment. The unused exact
clause has five literals. The projected row is wider but does not specify
any mates. Recompute the row using `(side,boundary,coords)` from
`scratch/A/r24/targets.json`; do not rely on unverified DIMACS numbers.
Coordinates `0..16` are grid indices; `17+slot` names the shore slot.

| Residual leaf | Shore | Projected row | Old guard matchings → projected matchings | CNF channel rows bound |
|---|---|---|---:|---:|
| `d175_1` | L | `-8 -6 -5 265 280 295 311` | 7,680 → 1,468,800 | 370 |
| `d185_1` | R | `-22 -17 -15 455 481 507 540` | 3,168 → 1,468,800 | 219 |
| `d246_1` | L | `-8 -6 -5 283 298 313 328` | 7,680 → 2,916,000 | 367 |
| `d252_1` | L | `-10 -9 -8 287 301 317 332` | 3,552 → 2,916,000 | 370 |
| `d275_1` | L | `-10 -7 -6 331 343 355 368` | 11,520 → 7,715,520 | 367 |
| `d281_1` | L | `-10 -9 -8 333 345 357 370` | 11,520 → 9,486,720 | 370 |

The matching counts are restricted to **the same occupied left and right
slots as the model**, using only allowed selector pairs, the boundary
filter, and injectivity. Subset DP and independent inclusion-exclusion
agree. The receipt exhibits a second possible matching at each leaf for
which the same projected witness is applicable but the old exact guard
is disabled. These are not counts of SAT models, of realizable full
graphs, or of excluded keys. The local alternate fixture is not a model
of the full CNF. The oracle explicitly checks the corresponding mate
clauses and both directions of every needed channel (or its conditional
zero) against the actual frozen CNF.

## Replay and use

From the root: `bash ralph/lanes/A/replay_shore24.sh r24-review`.
This checks the two unchanged A23 manifests plus `SHORE24.sha256` and
recreates both outputs byte for byte without a SAT solver. The six source
models/CNFs and used-seed inventories are copied under
`scratch/A/r24/inputs` (under 10 MB). An initial unoptimized matching
ranking hit its CPU limit (40.03 CPU-s); the revised implementation uses
the clause width as a cheap first filter and caches matching counts.
G owns any production integration, split decisions and LRAT; no
throughput improvement from these cuts is claimed without a paired run.
