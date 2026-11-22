# Round 20: independent G-019 expansion audit

**Hand + enum (pending critic):** a new enumerator matches all 118 frozen
order-27 inputs against all 984 order-33 unrooted classes, and all 985
degree-five-rooted keys at their precise source IDs. This is only the
middle arrow in G-019. No replay of the 477,142-source prefilter or the
984 outer exclusions, no new theorem or case debit, and no SAT claim.

## Completeness of the new search

Fix a core `Q`, an added root, and its `d` neighbors (the slots). A slot
has an independent attachment column in `Q`. The `d` slots have no edges
to one another. For each independent set `J` of `Q` let `h(J)` be the
number of slots whose columns meet `J`. The largest independent set
avoiding the root with intersection `J` in `Q` has size `|J|+d-h(J)`:
take every slot missing `J`. Thus `h(J) >= |J|+d-a` is necessary and
sufficient for independence at most `a`, since a set using the root has
size at most `1+alpha(Q) <= a`. The expander verifies the core premises
while enumerating core independent sets. For the target, the only
nontrivial sizes are 4 through 7, with required contacts 1 through 4.

Any actual column can be extended to a maximal independent **column**;
this can only increase `h(J)`. Such an envelope may violate degree and
edge limits and is not itself assumed to be a solution. Every valid
graph is a subassignment of some envelope. The size-7 tests require
every pair of envelope slots to meet each size-7 witness; a sorted
compatibility clique enumerates these multisets, keeping a diagonal
precisely when the repeated pair passes. Other witness sizes are tested
on each complete envelope. Sorting the slots loses only renamings;
identical columns, at the envelope and actual stages, are not deduped
into one physical slot.

Within an envelope, `expand_d5_20.cc` builds a fresh Boolean system.
If the demand at `J` is `r`, each `(d+1-r)`-subset of slots must select
at least one actual cross edge to `J`. These are positive clauses on
individual incidences. Separate integral cardinality bounds impose
each residual vertex's degree, each slot's degree, and the total edge
interval; the fixed root is checked apart. Split a free incidence into
the 0 and 1 branches, with sound unit and bound propagation; collect the
actual sorted column multiset from every solution. This is not a walk
deleting edges from a maximal graph or a reuse of the old sorted
actual-column extender. I share the monotone envelope argument with
the old replay, not its generator, trimming logic, or archived answers.
No maximal triangle-free graph assumption is used anywhere. For the
target, degree five at the root and degree at most eight elsewhere give
`2e <= 5+32*8`, so 130 covers all edge levels. No positive edge floor
is imposed. The archive is never an expansion input; it is used for
the pilot schedule and for the post-run comparison only.

## Controls and target

- Small: all nine triangle-free order-5 residues with alpha at most 3,
  with three slots and alpha cap 4. Literal multisets draw columns from
  all 32 subsets (even nonindependent ones); build each complete graph
  and check triangles, independence, degrees and edges directly. The
  three windows give 46/135/0 literal rows and 9/28/0 unrooted classes,
  also matched to a complete independent order-9 triangle-free `geng`
  census. Positive-source counts are 7/8/0. The controls contain 18
  repeated-column assignments and 165 proper-subcolumn assignments;
  a deleted positive row was detected in both positive profiles.
- Preregistered pilot and budget: `ROUND20_PRICE.md`. The 12 dispersed
  sources match 101 rooted keys, including the 5 minimum-edge and 1
  maximum-edge class. The complementary 106 exact sources took 4.14
  CPU-s; worst target source was ID 61 at 0.080002 CPU-s. The all-source
  final comparison took 6.04 CPU-s. Full expansion tallies are 301
  pair-compatible tuples, 225 witness-feasible envelopes, 1,446
  envelope assignments, and 989 different per-source labeled multisets.
  All 989 are non-MTF, 764 have a non-maximal column, and none have a
  repeated column (which the small positive controls exercise).
- The independent archive binder roots each of 984 graphs at **each**
  degree-five vertex, canonicalizes the 27-vertex antineighbourhood to
  find its source, and canonicalizes with a singleton root color to find
  its marked class. It gives 985 roots and 985 rooted orbits. The new
  output preserves the source's literal labels and the five physical
  slots; validate that deletion yields exactly that source, then apply
  the same marked and unmarked canonicalizers. Exact per-source class
  sets agree (empty `all.diff.tsv`); `all.coverage.tsv` pins rooted and
  literal sets and records every source's completion counts. Dropping a
  global class was detected, and dropping only the marked role at ID
  117 was detected while all 984 unrooted classes remained.

| Edges | 123 | 124 | 125 | 126 | 127 | 128 | 129 | 130 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Unrooted classes | 5 | 44 | 149 | 266 | 294 | 184 | 41 | 1 |

## Replay and limits

From the workspace root:

```bash
sha256sum -c ralph/lanes/A/ROUND20_FREEZE.sha256
bash ralph/lanes/A/replay_d5_20.sh r20-review
cmp scratch/A/r20/all.coverage.tsv scratch/A/r20-review/all.coverage.tsv
```

One foreground worker at a time, 1 GiB VM, 60 s wall / 45 s CPU per
bounded command. Live and clean replay consumed 37.35 measured CPU-s;
including three calibration-development attempts, 39.14 CPU-s
(0.01087 core-h). Largest RSS 162,136 KiB (compiler); the expander used
at most 5,292 KiB. Live and clean staging together were under 1 MiB.
The clean rebuild matched 23 reports/outputs byte-for-byte and six
receipt files after dropping only timing. The 984-class graph6 stream
is byte-identical to the frozen archive. No jobs left running.
