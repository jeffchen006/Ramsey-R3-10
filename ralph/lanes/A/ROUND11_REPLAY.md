# Round 11: middle-tranche binding and order-21 parent audit

Scope throughout: the e168 pin `(n6,n7,n8,n9)=(2,7,4,27)` with
adjacent degree-six roots, path/leaf strip A, and matching/incident
or path/middle strip B, as in G's `rows/residual_mixed_windows.md`.
Both selected pivots are noncross. Nothing below removes a whole
degree distribution or a Case R cube.

## Middle-only binding, d8/j2/δ(T)=2

Restricted the independent Round-10 exact order-25 role source to
`middle`, preserving both orientations. Full labelled role strings,
including graph6, match G's 21,236 selected strings. Each of the 13,413
distinct referenced graph6 rows also matches the fixed-stride raw
source. All 12 receipt sequences match the exact round-robin schedule
(8×1,770 and 4×1,769); no missing, duplicate, nonterminal, or orphan
trace IDs. The 69,278 matching roles are **outside** this audit.

`audit_middle25_binding.py` restores the base through the shared
encoding, independently matches the full fixed-edge map (including
forbidden edges implied by fixed triangles), independently enumerates
eager 10-set clauses, and reserializes the identical DIMACS. The
generated DIMACS SHA256, stored compressed LRAT SHA256, filename, and
size are bound by key. This is an independent binding audit, not a
second run of the LRAT checkers; the proof checks are G's original
`cake_lpr` and `lrat-check` checks before a worker emits `CERT`. No SMS,
symmetry clauses, or unlogged dynamic IS clauses enter this tranche.

**Complete:** the independently generated manifest is byte-identical
to G's 21,236-line final manifest, SHA256
`857a7f5ea9a14e30d6f04d67755e3847413dfa92b2411396b6f22d7dc16356f2`.
There are zero failed IDs; totals are 12,349,556 fixed pairs and
275,427,449 eager clauses across all formulas. Full binding used
3,109.58 CPU-s and finished by 04:59:28 CET. The 215-role d9/j4
previous bundle also reproduced byte-for-byte with the generalized
pin helper (`regression26.log`).

From `scratch/A/strip11` (`root=../../..`, `ulimit -v 16777216`),
the 96-role `--limit 96` calibration regenerated 55,860 pins and
1,119,365 eager rows in 14.71 CPU-s. To replay the complete binding,
run the following once for each `slice=0,1,2` (distinct working CNFs).

```sh
nice -n 5 timeout -k 3s 2100s prlimit --cpu=1800:1802 -- \
  "$root/opt/venv/bin/python" -B "$root/ralph/lanes/A/audit_middle25_binding.py" \
  --slice "$slice" 3 >"middle.$slice.tsv" 2>"middle.$slice.log"
LC_ALL=C sort -m middle.[012].tsv > middle.independent.tsv
diff -u ../../G/round10/r25.d8.middle.bound/certificates.tsv middle.independent.tsv
```

## Order-21 parent coverage

Let `T` be a weak paired window with independent, disjoint marked
4-sets and one cross edge. Each exterior has a 1- or 2-anchor support
on each side, cap four for singleton and one for double. Let `s` be
a retained noncross anchor with `d_T(s)=|T|−22` (not necessarily
minimum degree). `H=T−N_T[s]` has order 21 and independence number
at most 6, and still has the 3+4 marks: all neighbours of `s` in `T`
are exterior. Every exterior in `H` preserves its nonempty supports.
On the 3-side, 14 exterior vertices fill 14 of 15 available places.
Full capacity would give the crossed short anchor degree seven, so
the unique unfilled place is one of its singleton places or one of
its two double places. Thus its degree is six and the remaining
short anchors have degrees at least five.

`replay_short_anchor.cpp` enumerates from the directed cross edge
instead of from an independent side. For every choice of the two
uncrossed short anchors, vertices untouched by the short set, other
than the short set itself, are **exactly** the three uncrossed long
anchors. Adjacent masks then check all widths and multiplicities.
The degree filter follows the preceding slot argument. The 410
smaller order-eight graphs reproduce exactly G's 42 ordered marks
without the degree filter and agree with a separate literal Python
enumerator. On the complete order-21 source from B (as reused by G),
the reconstructed labelled keys agree exactly with G's full keys,
including 6,160 marks from 6,056 parent classes in 18.05 CPU-s. **All
6,160 have the singleton deficit; zero have either double deficit.**
The underlying order-21 graph catalogue completeness is an inherited
enumeration dependency, not a new independently regenerated census.

### Scoped consequence (hand + enum)

At the mixed pin with B pivot `b` noncross and degree 9, every other
retained noncross B anchor `s` obeys **`d_T(s) ≥ |T|−21`**. The general
hand floor is `|T|−22`; it suffices to exclude equality. If the short
side of `H` is B, the singleton-deficit census says all three pairs
of old B anchors occur as doubles. Neither B hole may use `b`, because
its degree is nine. Hence **both** holes would have to use the restored
`s`. Matching holes are disjoint and middle holes share the crossed
B endpoint, not `s`. Both are impossible. This argument applies
independently of the order of `T` and of `δ(T)` wherever the stated
strip and pivot hypotheses apply. For a degree-eight B pivot there
is one retained B hole, which must likewise involve `s`. In either
hole shape `s` then belongs to exactly one hole and has original
degree eight. So the stronger floor also applies to retained
noncross B anchors of original degree nine when the B pivot has
degree eight. In the middle shape the retained hole is exactly
`{s, crossed B endpoint}`. None of this addresses crossed anchors
or a short A side.

## Audit of G's direct order-24 instance

G's `pinned_anchor_window.py` covers `|T|=24` with the named equality
anchor only. Here `s=21`, its two exterior neighbours of `T` are
22,23 (unfixed order), roots 24,25, and pivots 26,27. Both short-side
orientations are considered, the A leaf among the three noncross
partners of the A pivot is never preselected, and the B holes are
exactly the two missing support pairs in either permitted shape with
the named B-pivot degree. A truly occupied support cannot be a hole.

The sole unfilled old-only short-side slot is either a B double hole
or must live in the opposite-exclusive group: vertices 22,23 touch
`s`; common and own-exclusive vertices touch the own pivot. Members
of the opposite-exclusive group are interchangeable for choosing
the canonical slot label. Every other member must touch `s`, as all
old-only slots are then either filled or holes. No analogous fixed
assumption is made for the long-side addback supports. The pinned
triangle pruning, MTF, exact support multiplicity and exterior-degree
rows are all necessary. In particular the A path has eight doubles
(28 exterior minus 5·4 singletons); six are between retained anchors,
none is at the cross/pivot pair, and any two of the three remaining
pivot doubles are allowed. No separate leaf-choice restriction is
needed. The direct window I8 cuts use six independent core vertices
and both extras; an optional eager I10 cut uses six core vertices,
three mutually nonadjacent members of one exclusive group, and the
opposite pivot. Each is valid; no minimum-degree condition on `s`
is used. A full valid lift therefore maps to an instance after only
relabeling the two extras and the mutually interchangeable cut-group
labels. A SAT model of the relaxation is not necessarily a full lift.

`audit_pinned_anchor_cnf.py` checks every role by choosing any two
holes among the ten B pairs and using degree/shared-endpoint tests,
and independently constructs all fixed pairs for each role, before
the producer's fixed-triangle pruning. It matches all 51,395 role
records and their fixed shells (44.14 CPU-s, final run). In the table “short A”
and “short B” name the side of `s`.

| B degree / hole shape | Short A | Short B |
|---|---:|---:|
| d8 matching | 13,597 | 24,640 |
| d8 middle | 5,200 | 6,160 |
| d9 matching | 902 | 0 |
| d9 middle | 896 | 0 |

Independently verified 6,000 exact labelled order-24 addbacks in the
first 6,000 raw graft rows. One actual order-24 lift is SAT when
every induced edge is planted in G's weak-window formula, in either
ordering of the two extras. A second actual order-25 addback, orbit
290424, graft 179581, has `d_T(s)=3 > δ(T)=2` and explains why extending
the method to order 25 must not assume that `s` is a minimum-degree
vertex. This second control is not an input to the current order-24
encoder. Each physical mutation deletes exactly one edge to change
the missing singleton into one of the two allowable missing doubles.
The mutated geometry has a planted weak SAT addback at relaxed alpha
cap 8, but fails the Ramsey-parent premise for cap 7 by explicit I7
witnesses (the corresponding lifts have I8 witnesses). The role/pin
oracles exercise both consumption as a B hole and placement in the
opposite-exclusive slot on these geometrically valid test fixtures.

```sh
nice -n 5 timeout 30s g++ -std=c++20 -O3 -Wall -Wextra \
  "$root/ralph/lanes/A/replay_short_anchor.cpp" -o short.crossfirst
./short.crossfirst control8 < ../../G/round7/control8.g6 > short.crossfirst.control.keys
nice -n 5 timeout 150s bash -o pipefail -c \
  'gzip -dc ../../G/round8/r37_21.g6.gz | ./short.crossfirst core21' > short.crossfirst.full.keys
diff <(LC_ALL=C sort short.crossfirst.full.keys) \
  <(LC_ALL=C sort ../../G/round10/short-anchor.full.keys)
nice -n 5 timeout 120s "$root/opt/venv/bin/python" -uB \
  "$root/ralph/lanes/A/audit_short_anchor.py" --output short.controls.json
nice -n 5 timeout 220s "$root/opt/venv/bin/python" -uB \
  "$root/ralph/lanes/A/audit_pinned_anchor_cnf.py" short.controls.json \
  ../../G/round10/short-anchor.full.keys
```

The direct-instance work here binds coverage and exercises small
controls. It is not a proof-production run, an order-24 closure, or a
recommendation to scale the all-pivot selector or raw addback.
