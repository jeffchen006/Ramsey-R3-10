# Round 19 — physical closed-neighborhood deletion cards

**Hand + enum (pending review); no new case or distribution exclusion.**
This is the lossless order-12 lookup and one physical bin delivered to C.
It does not evaluate any target fifth-pole row, perform a signed join, or
regenerate the 56 order-13 structural removals.

## Why the index is lossless (hand)

For one pole `b` of the re-rooted `K3,5`, delete the closed neighborhoods
of the other four poles. The remaining induced graph is `H + b + S_b`,
where `S_b` has exactly the singleton sites on `b`. It is triangle-free
and has independence number at most five, since an independent six
there could join the four deleted poles. In the order-12 core, the card
has order `13 + |S_b|`, with `deg(b) = |S_b|`. Thus `|S_b| > 4` is
impossible by `R(3,6) = 18`; degrees three and four are precisely the
order-16 and order-17 catalogue lookups here. A card of size at most two
is **not** queried against this index. Keeping it without a catalogue
test is a necessary relaxation, not a rejection or an existence claim.

Every relevant physical root of **all** source graphs is retained. The
stored map `v` sends canonical coordinates to original card labels. For
a physical core let `q` send canonical coordinates to the physical core
positions. If the keys agree, every residual binding is exactly
`v ∘ a ∘ q⁻¹`, where `a` runs over the complete automorphism group of the
canonical graph: composing any binding with the inverse reference maps
gives such an automorphism, and each such automorphism gives a binding.
For each binding, permute all actual card singleton labels onto the
physical singleton positions, and keep exactly the maps consistent with
all supplied edges **and nonedges**. Unspecified pairs remain free.
There is no quotient of singleton labels or pinning to one arbitrary
canonical map. A physical neutral in the induced window is mapped by
the same binding; it is not required to be a prescribed *catalogue* label.

## Lookup and controls (enum)

`scratch/A/r19/cards-v1.json` is format `r310.deletion-cards/1`, generated
with the workspace's pynauty 2.8.8.1. Group keys are canonical graph6;
`groups[key].aut` is the full list of canonical-coordinate permutations.
Each `groups[key].cards` entry is `[order, host, root, core_labels,
singleton_labels, contact_masks]`. Host and labels are zero-based
original catalogue rows and graph6 labels. `core_labels[j]` is the
original label at canonical coordinate `j`; `contact_masks[i]` has bit
`j` iff original `singleton_labels[i]` is adjacent to `core_labels[j]`.
The Python API `restorations(index, dense_core, k, known, neutral)` takes
physical core positions followed by physical singleton positions, a
list of `(position, position, edge_bool)` constraints and the optional
physical neutral position. Each result has `(order, host, root, image,
neutral_image)`. This also supports deliberately incomplete contacts.

| All-graph catalogue | Input graphs | Relevant roots | Exact residual maps checked |
|---|---:|---:|---:|
| `(3,6,16)` (degree 3) | 2,576 | 1,458 | 5,022 |
| `(3,6,17)` (degree 4) | 7 | 21 | 72 |
| Total | 2,583 | 1,479 | 5,094 |

These give ten distinct core keys, with group sizes 2 to 16. The clean
replay independently checks residual maps by adjacency-preserving
backtracking, compares all fixed-contact same-root lifts on physically
relabeled cores and for neutral positions in both parts, and rejects
1,479 corrupt root-neighbor/core swaps. It also checks all 438 physical
roots in the two small control catalogues: `(3,4,4..8)` and `(3,5,6)`.
For 105 relevant small roots, all rooted lifts against every catalogue
host agree with literal bijective reconstruction for both fully and
partially known contacts (100 degree-three and five degree-four roots).
All 105 adverse singleton-edge mutations are rejected. The clean rebuilt
old-margin evaluator matches all 34,504 archived small-control flag rows.

## Held-out physical bin (enum, old margins only)

The preregistered rule is C's 16:00 BOARD line: in key `(66,4)`, select
the first `(physical frame16 ID, x)` in order with `x` a degree-three
triple and at least one both-old-margin positive against all 116 marked
right frames in `(75,5)`, skipping any left frame whose bin intersects
the 544 frozen raw pilot IDs. No lookup or fifth-row filter is consulted
in this selection. `selection.tsv` shows `(42072,1)` skipped for one old
pair and the next `(42679,0)` selected. The latter has host16=97,
neutral16=7, `x` adjacent to the neutral, and exactly three still
required neighbors on the order-17 private axis. The shared physical
neutral is not counted a second time as a right private site.

| Raw | Neither | 16→17 only | 17→16 only | Both | Old pilot overlap |
|---:|---:|---:|---:|---:|---:|---:|
| 116 | 18 | 86 | 0 | 12 | 0 |

`heldout.cases.tsv` has the standard 14 integers, in increasing original
right ID, and `heldout.flags.tsv` has both four-bit old group rows in
original mask order. `heldout.positive.cases.tsv` is the same rows for
the 12 both-pass IDs. `heldout.marked.jsonl` adds the physical `x16`,
both crossing axes, the sorted order-16 core labels and canonical map,
the singleton labels and neutral contacts. The first 116 rows of the
archived critic order-13 raw block independently agree on every **right**
ID/host/neutral/four masks; no rerun of the 56-ID crosswalk.

## Cost and replay

The initial 31-root price was 0.56 CPU-s (26.72 CPU-s at naive linear
scaling, not a tail bound); checking all roots took 2.44 CPU-s. The
three-bin old-margin sample took 1.71 CPU-s; production bin binding took
1.43 CPU-s. Total including both passes, builds and early controls:
19.31 CPU-s = 0.00536 core-h, maximum 319,144 KiB RSS (compiler),
40,116 KiB for the binders, and 636 KiB allocated scratch at receipt.
At most one CPU worker at a time; no detached jobs. The 99,557-byte
lookup and the held-out data replay byte-for-byte. Evidence:

```sh
sha256sum -c ralph/lanes/A/ROUND19_FREEZE.sha256
bash ralph/lanes/A/replay_deletion_cards19.sh r19-review
cmp scratch/A/r19/cards-v1.json scratch/A/r19-review/cards-v1.json
cmp scratch/A/r19/heldout.marked.jsonl scratch/A/r19-review/heldout.marked.jsonl
```

C owns testing a single fifth row simultaneously against the five
poles and reporting any result on this bin. No further bins, candidate,
Case R debit, or claim about how many signed joins the lookup saves.
