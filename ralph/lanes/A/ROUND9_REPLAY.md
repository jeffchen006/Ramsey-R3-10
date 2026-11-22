# Round 9: mixed strip covers and variant provenance

This round concerns only scoped cases of the e168 distribution
`(n6,n7,n8,n9)=(2,7,4,27)` and a separate pilot on the pure-strip cases.
It neither closes a distribution nor changes the status of Case R.
Replay outputs are under `scratch/A/strip9/`. All the local timings use
CPU user + system seconds; forecast times are not full measurements.

## Mixed noncross d8 pivot with j=3 and δ(T)=3

Use the accepted adjacent d6 strip hypotheses in G's `rows/path_leaf_windows.md`.
The path/leaf centre has 6 X-neighbours, and the other noncross d8
pivot has 7. With three common neighbours both roots and ten members of
X disappear along with the pivots. The remaining window T has 26
vertices, eight retained anchors, and α≤7. The eight anchors retain their
unique cross edge. Both sides' weak bounds are one or two attachments
per surviving exterior, at most four copies per singleton and at most
one per double. This is a shared upper envelope, **not** the original
pure path/leaf full signature multiset on both sides. Side A has 22
four-column occurrences before losing 4 to the cut; side B has 21
before losing 3. B's retained hole must not already occur as a double.
If the holes are disjoint then the cross anchor lies on one; if they
are incident then it is their common vertex. The other hole uses the
deleted B pivot. The cut classes are `3/3/4` (shared/A-only/B-only),
with missing-list labels sorted separately in the disjoint exclusive
classes. The marked degree sum is at most `(29-4)+(27-3)=49`, so
`2e(T) <= 49+7*18 = 175` and `e(T)<=87`.

For `δ(T)=3` remove a degree-three closed neighbourhood, obtaining
one of the 191 `(3,7;22)` classes in `gluing/val/r3_7_22.g6`. The
`glue3 -k 7 -d 3 -m 3 -M 7 -e 91` envelope includes every target
bound, and a gluer rerun agrees byte-for-byte on 2,712,471 labelled
extensions. A's scanner uses a different enumeration of independent
seven-sets and possible eighth labels. Its 2,111 marks match G's
exactly. `audit_mixed26.py` independently validates the core class
membership, triangles, α, mark support margins and the colour-orbit
quotient (1,767 representatives). Test **both** orientations before
classifying missing holes. The 7,166 role records match G's exact set:
5,438 matching, 1,728 middle. The role logic separately reproduces all
5,179 historical order-27 d8/j4 roles and all 256 local occupancy
snapshots. Four planted addbacks and four occupied-hole mutations
cover both orientations and both shapes. The addbacks are
triangle-free and reproduce the cut and both full signature lists;
they are controls, not MTF or α≤9 completions.

G's terminal 96 pilot + 7,070 production receipts all passed both
LRAT checkers; no caps or unwritten keys. A's audit rebuilds pins and
the eager independent-ten-set disjunctions, with base clauses from
G's encoder. `mixed.terminal.tsv` is read directly from scheduled
receipts and links every actual compressed trace. Sixteen spread
pilot traces were independently dual replayed. The terminal replays
use `run_mixed26_audit.sh --fast-hash --shard INDEX 3`; combine the
three replay logs with `finish_mixed26_audit.sh`. All 7,166 pin maps,
CNF hashes and compressed proof hashes agree with both indexes
(`mixed.union.log` and `mixed.G.join.log`, 840.13 CPU-s of full hash
replay). These proofs refute the relaxation; there are no external
SMS clauses.

## Mixed noncross d9 pivot with j=5

Use the same strip pin, not the pure cases. The d9 pivot uses all
four doubles involving it, so **both** holes now belong to the four
retained B anchors. The order-27 window has 19 exterior vertices,
with A/B pre-cut signature counts 22/20. Opposite-exclusive lists pin
3/1 labels, and the cut is `5/1/3`. Both shapes are valid role types;
there happen to be zero middle roles in the 1,988 weak source marks.
An independent enumeration of the three partitions into two pairs
and the three pairs of star-incident holes binds all 162 roles and
checks both strip orientations. As with the d8 branch, the original
five-column degree profiles imply six d7 and 22 d9 exterior, with
both signatures singletons for each d7. A independently matches all
162 CNF and trace digests, and independently reran both LRAT checkers
on all 162 (35.68 CPU-s). G's own full receipts are also dual-checked.
Evidence: `mixedfull.{source.log,terminal.tsv,hash.log,dual.log,dual.union.log}`.
The full-variant replay source is `scratch/A/strip9/audit_full_variants.py`
with `PYTHONPATH=../../../ralph/lanes/A` from that directory. The old
`audit_strip_extensions.py` is left byte-identical to Round 8.

## Both path/leaf c1/δ2: variant crosswalk

`crosswalk_c1_variants.py` joins A's and G's 17,194 selected keys to
the critic's `differences`, `primary.check` and `eager.check`; it
preserves the separate original indexes, and hashes both alternative
compressed traces for each pilot. All use `--cut-budget` with no
overlay option. On 17,152 keys both indexes select the same proof and
formula. On ten keys A's eager pilot and G's eager retry have the same
CNF but different trace paths. On **32** keys G's original pilot uses
`--eager 0` and A's alternative uses `--eager 10000`; use strictly the
paired CNF/trace. The critic already replayed both on all 32. No new
proof production/replay was needed for this crosswalk. Evidence:
`c1.variants.tsv` and `c1.variants.log`. Round-8 G source hashes that
predate its mixed-pivot extensions refer to tracked commit `eb5b11c`;
use those historical file versions to reproduce the input manifest.

## Pure cap controls and two-root pilot

For a noncross B anchor b, its pre-cut retained-column degree is
seven and its surviving degree is d_T(b); the difference `7-d_T(b)`
counts exactly the A-only deleted contacts. Its codegree with the
opposite A centre adds at most one common contact for a d9 full
anchor (unique double with B's centre), and zero for the d8 deficient
leaf (missing B-centre double). Thus both caps are redundant at
`δ(T)>=4`. At δ=3 they can bind only on d_T=3 anchors. The calculation
applies in both directions on the same assignment. `audit_joint_pivots.py`
checks 20 legal/wrong caps on C5, then a planted pure projection
(`179581`), independently evaluating all six codegrees and verifying
the simultaneous addition. The positive retains c=4 at a full
anchor. Changing which anchor is deficient makes c=4 at a d8 leaf;
moving the full-anchor centre double into the common cut makes c=5
instead. The correct direction and the joint encoder reject both
mutations. These structural controls do not assert MTF/α.

For pure order-26 `δ(T)=4`, a conditional source uses a degree-four
root a with second nonadjacent root b such that the joint residue has
order 16 or 17. The single-root antineighbourhood S has order 21 and
α≤6. Its minimum degree is at least three by R(3,6)=18; the second
root in S has degree four or three, respectively. Use the McKay
all-graphs `(3,6)` catalogs `r36_16.g6.gz` and `r36_17.g6` (2,576
and seven classes), glue with `-k 6 -d 4/3 -m 3 -M 6`, then shortg.
All 2,583 entries independently pass graph/alpha and distinctness checks.
Calibration: two successive glues from C5 recover the unique C13;
all 52 C13 nonadjacent-pair residues pass an independent check.
The S census: 1,002,378 + 9,959 raw glues give 604,645
distinct S classes in 10.12 CPU-s, versus 1,118,436 in the whole
order-21 source. For the 260 held-out high-minimum marks, 258 have
the required degree-four-root pair; all 37 distinct selected S
parents are present. The other two **do not** have any eligible
pair. No mark has a same-side marked pair leaving more than 14.

Matched 256-parent addback pilots with the same `e(T)<=88`:
subset 11.36 CPU-s / 969 marks, full-catalogue sample 9.19 CPU-s /
1,087 marks. Projected census ~7.45 vs ~11.15 CPU-h (about **1.5×**
faster only); the expensive proof stage was not tested and is not
claimed improved. Do not scale this method unchanged or treat the
conditional source as all δ=4. Data: `two_root.log`, `S21.full.log`,
`S21.heldout.log`, `S21.{matched,baseline}.graft.{log,time}`.

Freeze from `scratch/A/strip9`: `sha256sum -c round9.freeze.sha256`.
