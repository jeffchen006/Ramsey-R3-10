# Lane D — round 11, November 22, 2026

**R(3), R(4), R(3,10) open; no candidate.** Submitted: every R(3) graph has two disjoint codegree-one nonedges whose unique witnesses are **different**. Result is hand + enum, *not* Sec. 7 certification. The four-star cover can therefore use 111 rather than 117 generally live representatives. Shared witnesses may still occur at other markings of the same graph. D-019, D-020 and D-021 were confirmed last round. R10 details archived in `LOG.md`.

## Jobs

|PID|Command|Log|Cores|Start|Expected end|
|---|---|---|---:|---|---|
|none|All bounded foreground producers and checkers finished.|`scratch/D/wit11/`|0|—|—|

Share 9; no detached or stopped D jobs, no extra cores requested.

## Results and claims

`S=scratch/D/wit11`. CPU hours below refer to measured engine time, not complete pipeline cost.

|Label|Result / claim|Evidence|CPU-h|
|---|---|---|---:|
|hand|Defect count K is even: `2 C4=1080+K`. Thus the former exactly-one and intersecting-triangle alternatives need no enumeration. Nonnegative square excess at min q≥12 lives only on positive-defect endpoints. At K=2 with that minimum, exactly two disjoint cross edges have q=14 and all others q=12. Five marked roots after checking remaining codegrees.|`DEFECT_EXCESS.md`; `S/excess-source.log`|—|
|hand + enum; cert local only|117 generally live roots → 13,078 raw completed witness-star leaves. Exactly 1,351 have direct I10 witnesses and **1,351 dual LRATs**, leaving 11,727. No further original root terminates in the four matched 500-node arms; simultaneous domination of four independent nines does not further reduce the frontier. Full C22 control: 54 occupied roots, all 349 coloured classes.|`WITNESS_STARS.md`; `S/{frontier.tsv,front.log,cal-check.log,branch-audit.log,branch-cert/witnesses.tsv,branch-cert/certs-0-2-0.tsv,branch-cert/certs-1-2-0.tsv}`|0.0111 four target arms; 0.0197 proof processes; 0.0154 three C22 arms|
|hand + enum|All deficient pairs cannot have the same witness. Under that assumption they are a matching of at most four inside N(z). Dense-root search: P7 168,540→14,494→9,803. Conditional P8 join 560,069→20,149→9,241→3,458. Separate global path cap 8: 9,241→59→0, so an induced kernel P9 exists *in this branch*. P9 join 62,307→382→0. All 382 separately graph-only without a library (808,279 nodes, max 7,417/root). This is not an unconditional P9 or C6/C8 assertion.|`MONO_WITNESS.md`; `S/{join-check.log,mono9/coverage.log,limit8b/bind.log,mono9plain/bind.log,mono9a/bind.log,mono9b/bind.log}`; every stage's `receipt.tsv`|1.72 including both redundant terminal replays|
|hand bridge + enum|Together with D-020 the preceding theorem gives some two disjoint deficient pairs with distinct witnesses; if a differently witnessed edge hit both original pairs with shared witness z, it too would have witness z. **111** generally sufficient roots (102/6/3 by number of external witnesses 2/1/0), **55** remaining old K=2 tails, not global exclusions of the six shared configurations.|`MONO_WITNESS.md`; `S/distinct111.in`; `S/exact-sources.log`|included|
|estimate/open|Row-multiplicity moment LP: no separated target among 10 original +20 witness-frozen samples; every planted occupied C22 input verified. K=2/min-q≥12 all five still have integral projected counts (witnesses), and all five full signed searches cap at 12,000. Not a reason to scale. If no two marked P3s are vertex-disjoint, one can root at nine internal cases; all nine cap at 4,000 nodes.|`WITNESS_STARS.md`, `DEFECT_EXCESS.md`; `S/{moment-children.jsonl,excess-int.jsonl,excess.out,nextflags/pilot.out}`|0.0097 signed, 0.0008 flag pilot|

## Next steps / cautions

1. H/critic: review `MONO_WITNESS.md`, especially the cap-eight vs unrestricted-library distinction, both deleted endpoints and the elementary different-colour bridge. Inspect `S/{mono7,mono7b,mono8,mono8b,mono8c,limit8,limit8b,mono9,mono9plain}/receipt.tsv`. Source and bindings in `scratch/D/round11_evidence.sha256`. The remaining 111 are a cover, not disjoint unrooted parts.
2. New target: prove there are two **vertex-disjoint marked P3s** (including witnesses). If not, all such triples intersect, not necessarily at one common site. By this round's theorem choose a distinct-witness marking among only 9 internal roots. For fixed intersecting triples T1,T2, all others meet both. Test bounds/mark projections relative to these two before materializing another join; the 4,000-node pilot rejects naive restarts. Mode 32768 enforces pairwise intersection among forced triples; do not reuse the mono-only deck. C5 is a positive intersecting-flags example and a negative monochrome example.
3. Reusable path-deck tactic: supplement existence of a library match with common forced/forbidden arcs across matched slots, then test paths with one hypothetical edge. In 72 conditional P8 tails this changed 13→31→35 exhausted at 300 nodes; repriced before full use. Strong results obtained only with substantially restricted parents; unrestricted 20M P8 and the unchanged K=2 signed pilot remain frozen.
4. If revisiting full certification, distinguish the 1,351 atomic formulas from the graph-search/cover theorem. No end-to-end LRAT chain for the latter. No full R(3) closure.
