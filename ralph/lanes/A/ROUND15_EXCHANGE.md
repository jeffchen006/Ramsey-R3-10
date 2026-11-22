# Round 15 — physical side exchange for the marked cap-five 17/17 block

## The transfer contract (`hand`)

Take two **copies** of the labelled frames `i,j`. On side L (respectively
R), use root vertices `rL(a)` (respectively `rR(a)`), one for each of the four
literal mark masks, and private vertices `pL(x)` (`pR(y)`) indexed by the
private labels in that copy's window. Write `n_i(0),n_i(1)` and
`n_j(0),n_j(1)` for the two neutral labels of each window in increasing
window-label order. Bit `b` identifies `n_i(k)` with `n_j(k xor b)`.
Denote this physical vertex by `z(k)` in the old left coordinates.

To read the same glued graph on header `(j,i,b)`, take the old right copy
as the new left copy, the old left copy as the new right copy, and map
the vertices by

| Old | New |
|---|---|
| `rL(a)` | `rR'(a)` |
| `rR(a)` | `rL'(a)` |
| `pL(x)` | `pR'(x)` |
| `pR(y)` | `pL'(y)` |
| `z(k)` | `z'(k xor b)` |

Indeed, in the new left coordinates the old neutral comes from the old
right label `n_j(k xor b)`, and the new identification returns it to
`n_i((k xor b) xor b) = n_i(k)`. Both permutations of two sites are
self-inverse, so the bit is unchanged. The marked `K4,4` and its literal
root marks are preserved. Each ordered frame retains its own induced
window and literal vertex/mask labels, and the common neutral edge is
preserved. Every private edge crossing `(x,y)` becomes `(y,x)`; its
entire Boolean matrix is transposed, with rows/columns indexed by the
corresponding literal private labels. There are no other edge types in
the marked construction. Applying the exchange twice returns every
physical vertex and crossing.

This applies to same-host pairs, including `i=j`: neither a shared host
nor an equal frame ID identifies any roots or private vertices across
the two copies. For `i=j`, the header is fixed separately for each bit;
the crossing matrix need **not** equal its transpose. If both bits are
admissible for a pair, both are retained. This is only an exchange of
shores, not a quotient by internal frame automorphisms or changes of
neutral labelling. It preserves regularity, triangle-freeness, codegrees,
independence numbers, and the unordered marking. A literal negative for
either orientation therefore transfers to the other. Scanner depths,
per-filling reason vectors and run times are **not** claimed symmetric.
Do not transfer any rejection that depends on a one-sided premise unless
its exchanged version is proved for the other orientation. Do not apply
the contract outside this marked, shore-symmetric 17/17 block.

## Coverage convention

Let `L = [0,24576)` and `H = [24576,55055)`. The 12 frozen **ordered**
receipts already cover every admissible `LL` and `LH` ID. An `HL` ID
uses its transposed `LH` receipt; it is not physically scanned by that
receipt. For `HH`, schedule the IDs `i <= j` in left-ID interval shards,
preserving both admissible bits even on the diagonal. Every fixture in
`HH` has exactly one such representative; an off-diagonal representative
has one other orientation, and a diagonal has none. This leaves the
original `LL` receipts intact where both orientations were scanned.
The census below binds a **coverage map**, not terminal exclusions for
unscanned representatives.

## Independent census and controls (`enum`)

The Round 14 independent header generator rebuilds all packed ordered
IDs from the seven host graphs and 55,055 literal frames. Each header
is `(left,right,bit,0)` as four little-endian unsigned 16-bit words. In
the exchange reader, every upper off-diagonal row with smaller ID `i`
places `2*j+bit` into `i`'s reference queue. The later lower row `(j,i,bit)`
must consume exactly that entry. Strict order and an exhausted queue for
every ID rule out duplicate, missing, or mistyped references in either
direction; diagonal records are additionally bound by their own hashes.
This is a literal membership audit, not a count-only Burnside check.

`scratch/A/r15/census.tsv` binds the full ordered digest, each of the 12
original 2,048-wide ordered shards, and 30 HH shards of width 1,024 (last
short). Each has ordered/subdomain SHA-256 and both per-map counts.
The full digest and all 12 original ordered shard hashes match Round 14.

| Domain | Bit 0 | Bit 1 | Total |
|---|---:|---:|---:|
| LL, direct | 7,023,914 | 20,174,899 | 27,198,813 |
| LH, direct | 11,260,347 | 28,958,051 | 40,218,398 |
| HL, references LH | 11,260,347 | 28,958,051 | 40,218,398 |
| HH, ordered | 10,756,714 | 39,079,678 | 49,836,392 |
| HH, representatives | 5,379,848 | 19,544,871 | 24,924,719 |
| HH, diagonal subset | 2,982 | 10,064 | 13,046 |
| HH, lower orientations | 5,376,866 | 19,534,807 | 24,911,673 |

The first HH shard `[24576,25600)` binds 2,647,995 representatives:
372,890/2,275,105 by bit, including 75/466 diagonals. Its packed SHA-256
is `2e8d59183e3051e6aeffef0dd1c3496fb9749285d8a9d9df6fbae586bdc0e8ca`.
An interval-only replay matches its upper and diagonal hashes byte for byte.
Starting from the ordered prefix, exchange reduces the outstanding direct
header checks from 90,054,790 to 24,924,719 (about 3.61× fewer); this is a
roster saving, not a runtime forecast.

The smaller physical controls come from the 10 six-regular graphs in the
191-entry (3,7,22) catalogue. For 334 planted 10/10 bicliques with nonempty
private crossings, rebuild the whole source graph in both orientations
and for all four choices of neutral order (2,672 comparisons); the wrong
bit changes each reconstructed edge set. Root/private/neutral preserving
isomorphisms of the two windows give 18 bit-zero and 102 bit-one physically
planted fixed-header relabelings, including 8 and 42 asymmetric crossing
matrices. These are control placements, not counts of distinct smaller
graphs. A separate packed fixture keeps both diagonal bits, both bits
on one off-diagonal pair, and two prefix references. A missing diagonal
passes off-diagonal matching but fails the bound fixture hash; replacing
one map bit at constant row count and omitting the source of a transposed
prefix reference both fail exact membership.

## Final receipt audit (`hand + enum`, pending critic)

All **30 of 30** HH representative receipts passed the independent
`--require-full` audit. The 24,924,719 directly scanned HH representatives
gave 3,620,522 local, 6,027 panel, and 1,617 joint IDs. Both terminals
agree on all **74,632** rejected fillings (2,876 degree, 0 triangle,
11,940 codegree, 59,816 independent ten-set); the keyed terminal digest is
`bf5587676c1e8f9d473f2411eca08afe105183cd49e4c7d10e4edf41b43c8ecd`.
The historical direct scan contributes 148,231 more rejected fillings;
no counts of fillings or screen stages are inferred for transferred IDs.
The complete ordered partition is **92,341,930 direct, 65,130,071 by
exchange, 0 unresolved**. C's 30 new production receipts report 270.204
aggregate CPU-s. The final A receipt-only audit used about 0.3 CPU-s.
The first receipt also passed unaltered in a separate copy; a dropped
diagonal counted as exchanged, a count-preserving map overwrite, and a
live/disagreeing terminal all fail without publishing coverage.

Combined with `ralph/lanes/C/proofs/panel17_census.md`, this is a
hand + enum exclusion of the marked cap-five two-neutral-site case,
subject to critic acceptance of the catalogue/finite screen and terminal
arguments. It does not exclude a biclique with zero or one neutral site,
the cap-six cases, or any whole distribution. It is not an LRAT/DRAT
certificate and does not settle R(3,10).

## Replay and consumption

From the repository root:

```sh
bash ralph/lanes/A/replay_panel_exchange.sh
```

This checks the immutable Round 14 evidence, rebuilds the two tools,
replays smaller controls before reading the target, and rechecks all 12
old terminal receipts. Before ingesting HH receipts, the partition is
67,417,211 direct, 40,218,398 by exchange, and 49,836,392 unresolved
ordered headers. The auditor rejects an incomplete `--require-full`
partition and does not publish a partial output for that request.

For completed HH receipts, run the same script with the extra arguments
`--reports ../../C/r15 --require-full` (omit `--require-full` for a
snapshot). It reads but never edits C's receipts. A shard contributes its
representative roster as direct only after checking independently bound
header hashes and map counts, triangular bounds, both terminal streams,
and absence of live fillings. Only its off-diagonal representatives
transfer one more negative each. `coverage.published.tsv` puts unresolved
counts in **ordered** units and charges inferred rows to their source
interval; it does not infer any stage depth or per-filling reason at the
transposed ID. Unmatched or stopped shards supply no receipt. The audit
does not rerun C's production search or certify the screen predicates as
formal proofs.

Frozen final outputs: `scratch/A/r15/{coverage.final.tsv,receipts.final.log,totals.final.log}`.
`sha256sum -c ralph/lanes/A/ROUND15_FREEZE.sha256` checks these files,
the tools and inputs, and all receipt files read for the 30 HH shards.
