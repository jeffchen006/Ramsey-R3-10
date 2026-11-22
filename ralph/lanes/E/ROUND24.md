# Round 24 — two e8 extremes and a factorized successor

## Scope and premises

As in `ROUND23.md`: type `(2,32)` with four independent size-six
attachments, `δ(W)≥2`, universal `δ(G)≥5`, `e(W)=8`, and `P=0`.
No maximality. The four fixed-deletion cards `H_i=F−A_i` have 26
vertices, 74 edges and `α≤7`; every fixed core vertex meets each
attachment. The known-card arms are inherited from rounds 22 and 23.
Thus, conditional on the E-021 all-graph catalogue premise, all four
cards for this branch are copies of one class. This is not a new
catalogue claim. `b_i=e(W,A_i)`, `Σb_i=48`, and `b_i≥10`.

## Exact bmax=16 cover and formula binding

The two profiles are `(10,10,12,16)` and `(10,11,11,16)`; the remaining
three attachments after deleting the size-16 role form the projection.
The four omitted triple-contact vertices determine the residue word.
Round 23's first `2C4` independent-cover command hit its CPU limit,
before that shard's solver ran; no credit for its empty output. An
explicit anti-join of the six pilots and the 15 successful producers
gave 14,391 previous IDs and 959 missing, all `0 mod 16`. Four repair
shards covered precisely these 959 IDs and all reported `CHECKED`.
`2c4.old.json` and `2c4.repair.ids` retain this pre-replay split.

`cover_deck24.py` independently starts from all 70 labelled residue
markings (seven shards) and enumerates direct columns: reserve one
distinct column for each singleton row, then enumerate the remaining
unordered columns over non-singleton rows. Each column avoids a W
edge, and direct Hall on independent W subsets enforces the one-wing
alpha cap. Triple candidates are joined by exact row sum. The scan
constructs automorphisms from all `8!` permutations of the W edges,
instead of calling the producer's automorphism routine, and compares
the exact canonical row files, not merely counts. Sharing the old
small `canon` routine for high-shape equality does not identify
physically different marks. `control2.log` has the 45 matching-toy
row checks, ten exact smaller completion counts and cardinality
truth tables.

The exact joins matched **15,350** `2C4` and **243,162** `C8` rows
(`stage15.log`). Each eight-site core is 2-regular and triangle free,
so the only component partitions are one 8-cycle or two 4-cycles.
The much larger sums over independent shards reflect canonicalized
duplicates across labelled residue markings, not further leaves.

`rebind_projection23.py` now uses `K−#singleton_W_rows` per physical
omission; the old `K−6` shortcut sufficed only for e10. Six selected
e10 hashes are unchanged. Every new C8 proof binds a byte-for-byte
physical re-encoding before solving and receives both CakeLRAT and
`lrat-check` acceptance. Packed archives retain a gzip LRAT member
per checked ID, exact offsets/lengths, physical lazy masks and the
raw LRAT and DIMACS SHA-256. The independent C8 replay mode uses
those members and the physical re-encoder, not the producer CNF.

**`2C4` terminal closure, pending critic.** Seven fresh-replay
shards expired at their outer wall bound with 14,409 checked IDs.
A reserved-lease anti-join replayed the 941 distinct missing IDs,
without discovery or duplicate credit. At 22:55:08 CET, the exact
join held **15,350/15,350**, zero open, no lazy I8 additions. Each
row's regenerated formula bytes and retained raw proof hashes agree
with the producer, and each LRAT replayed in both checkers. Replay
CPU 1,839.459 seconds, plus ~103.8 seconds for the r24 missing solver
shard (0.540 core-h without census). `2c4.final.log` is the exact
join; `freeze.2c4.sha256` (30 files) verifies. The join references
the original proof bundles through `2c4.old.json` and `2c4.repair`.
This excludes **only** the two bmax=16 profiles over the `2C4` core
under the scope and E-021 premise above. The separate `C8` arm is
open: 29,578 distinct checked (224 pilots + 29,354 production), zero
nonchecked terminals in the 22:55:17 CET snapshot; remaining 213,584.

## Next two profiles: a necessary d7-shape screen

For `bmax=15` with `bmin=10`, the only profiles are `(10,10,13,15)`
and `(10,11,12,15)`. A W row has one to three contacts per wing
because its four incidence counts add to six. As already used in
round 23, the exterior d7 vertices of any card form a clique of
size at most two. With `s_i` W singletons the common d7 count K
satisfies `s_i≤K≤s_i+2`. The size-ten omission gives `K≥6`; the
seven W-surplus contacts of the size-15 role occupy at least four
rows, so `K≤6`. Exactly four W rows are nonsingleton there: three
have three contacts and one has two. Its card has two adjacent
exterior d7 vertices. Other retained W row words with fewer than
four singletons are impossible.

In any retained small omission with six W singletons, those six
physical W vertices are the entire induced d7 subgraph of its card.
Their components, paths and cycles, give its complete isomorphism
type (`W=2C4` or `C8`). Compare all such anchors. In the largest
omission the candidate exterior pair is in distinct wings, their
W supports are disjoint, and the pair edge is fixed by the clique
necessity. Thus the six-vertex induced graph on that pair and the
four known W singletons can be tested **exactly**, without assuming
that any isomorphism respects W or wing marks. The E-031 all-graph
minimum degree four in each 26/e74 card bounds the degree from an
exterior site to *each other retained wing* by three. Using the
available disjoint-support contacts, clipped at three per wing,
can further certify some candidates cannot be d7. An empty set of
candidate pairs refutes the pinned projected card; a nonempty set
does not produce a card or an extension.

`profile15_deck24.py` first quotients the residual row words and
retained row words, then stores each product in factorized form.
No materialization of the full product. Raw product size may
overcount under stabilizers and equal-row wing swaps. Measured
pair-screen samples are only a price/prototype, not formal
coverage or a closure of either smaller-b profile. The third
`bmax=15` profile `(11,11,11,15)` is not in that preflight.

C independently developed the more powerful all-anchor trace gate
at the same time. For 64 dispersed physically named records in
each of the four staged products, its primary and literal inverse
implementations agree on every stage count and exact retained
pair/support assignment. C-058/C-059 are the relevant hand/enum
results; this is a disjoint b15 pilot, not a repetition of C's
224-row b16 pilot. The shape-only column uses 512 samples, including
the 64 trace-gate samples. The candidate pairs in the shape-only
column use the E-031 contact cap, whereas the C implementation uses
the C-056 physical rectangle necessity and the trace subtraction.

| Core | Profile | Factorized row packs | Ordered raw product upper bound | Shape-only vetoes / 512 | C trace plus literal vetoes / 64 | Both trace CPU-s |
|---|---|---:|---:|---:|---:|---:|
| `2C4` | `(10,10,13,15)` | 82 | 80,896 | 377 | 56 | 2.19 |
| `2C4` | `(10,11,12,15)` | 373 | 1,980,000 | 394 | 60 | 1.90 |
| `C8` | `(10,10,13,15)` | 234 | 480,730 | 181 | 63 | 1.41 |
| `C8` | `(10,11,12,15)` | 1,598 | 19,455,311 | 208 | 55 | 3.32 |

First successor to price end to end: `2C4 (10,10,13,15)`. A crude
upper-product extrapolation is 0.76 core-h for the two analyzers
and another ~0.43 core-h at 1/8 pass rate and the b16 proof price.
That second figure is uncalibrated for b15 CNFs; do not launch a
large solver wave until actual survivor proofs and an independent
exact b15 cover have been priced. No b15 SAT or claim of closure.

## Resources and artifact paths

All current data: `scratch/E/r24_deck/`, plus the retained r23
plan and original receipts under `scratch/E/r23_deck/`. The C8
pilot contains 32 dispersed IDs from each of seven ordered
profile/budget strata, total 224 exact `CHECKED` with no caps.
Weighted estimate: 36,852 CPU-s (10.24 core-h) and 1.883 GB packed
proofs. Production 242,938 IDs, modulo 22 excluding exactly those
pilots; 120 MiB retained and 32 MiB temporary proof cap per slot.
At dispatch logical workspace scratch was 130.262 GB, free space
228.232 GB; E's worst simultaneous reservation <3.65 GB.
Every replay/census/solver obtains one file-lock lease; the staged
waiting supervisors execute no solver, release only after children
exit, and do not add to the 22 active work slots. `jobs.tsv`,
`exits.tsv`, `snapshots.tsv` and `price.log` hold accounting.
At handoff all 22 leases hold C8 producer wrappers; final lease
20 started immediately after the complete tail replay, PID 774191.
Between 22:45:12 and 22:55:17, production gained 2,674.823 completed
CPU-s in 605 s (~4.42 actual core equivalents despite up to 21/22
active workers), with zero caps so far. Nominal lease occupancy is
not a claim of full CPU delivery. Local staging 407,883,428 bytes.

No graph sent to the flow and no Ramsey verdict.
