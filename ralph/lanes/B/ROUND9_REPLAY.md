# Round 9: two bounded e108 sources

Neither source added a class. The frozen starting catalogue is still
2,104,027 of 2,104,151, with 124 deletion-critical keys absent. No floor
109, t9 floor 89, U88 exclusion or candidate follows. No e88 gluer was
restarted and no d6/e52 or d7/e44 batch was launched.

`scratch/B/logs/round9_freeze.log` checks both separate round-8 manifests
from the workspace root, including the terminal e88 binding, the
153,612 prefix-critical keys and the 1,142 e108 scout keys and receipts.
`ROUND9.sha256` binds this round's code, sampled inputs, outputs and logs.

## Pair-neighborhood repartition (enum / estimate)

For nonadjacent roots, keep their common stem and their neighborhood
union U, optionally adding one exterior vertex to U. Keep the two roots
nonadjacent. A vertex attached to both must be isolated in H[U], and each
nontrivial component of H[U] must be bipartite, with just two choices of
orientation. Isolates may attach to one root or both. The edge budget
fixes exactly how many isolates attach to both. An I9 using neither root
is absent in the input; one using both roots is still absent because U
never shrinks. I9s using exactly one root are ruled out if each row hits
each stem I8. The leaf separately tests every edge for deletion criticality.
Thus the search is exact for the specified move, not an assertion of
reachability from e107 or of critical-family connectivity.

From `scratch/B`, run `timeout 90s bash ../../ralph/lanes/B/src/e108_pair_r9.sh
work/fresh_pair_control control`. Independent labelled enumeration on
the three exact order-8 (3,4) controls agrees in all 12 tests, 72
emissions. From the complete 15 order-16/e21 parents, the image recovers
33 of the 42 withheld critical e22 classes, with no unexpected key.

Replay the held-out probe with `timeout 120s bash
../../ralph/lanes/B/src/e108_pair_r9.sh work/fresh_pair_probe probe`.
Each of three deterministically spaced sources supplies 32 parents.

| Source | Unique target keys | Scout keys recovered | New keys | Kernel CPU s |
|---|---:|---:|---:|---:|
| e107 | 0 | 0 | 0 | 3.03 |
| Reducible e108 | 0 | 0 | 0 | 1.84 |
| Old critical e108 | 40 | 0 | 0 | 2.16 |

Probe total 10.29 CPU-s including compilation, sampling and comparison.
No scale-up. Source and output digests: `logs/e108_r9_pair_probe.log`.

## Unrestricted nonadjacent-stem lifts (enum / estimate)

Delete a nonadjacent pair. For each supplied stem, enumerate independent
rows of the permitted sizes hitting every stem I8. Join two rows by
edge budget, minimum/maximum degrees and the exact requirement that
their union hits every I7 (both roots can be present in an I9). No fixed
neighborhood union; shared vertices are allowed, subject to the degree
cap and triangle-freeness of the two rows separately. At each valid
leaf check that removing each edge creates an I9. At every row branch,
the first selected vertex of the chosen unmet I8 partitions the search;
if none is unmet, enumerate independent supersets. The join takes one
ordering of the two rows. Scope is only the specified stems and degree
range; it does not imply coverage of all critical e108.

Control: `timeout 120s bash ../../ralph/lanes/B/src/e108_nonadjacent_r9.sh
work/fresh_nonadj_control control` matches all labelled deletions from
the three order-8 graphs and all 324 brute-force lift comparisons modulo
root exchange (106 outputs). The 15 e21 parents yield 285 distinct
stems and recover **38/42** withheld e22 keys, 667 raw lifts, with no
unexpected key. Control total 3.35 CPU-s. A cheap capacity measurement
used 17 stems from the first 4,096 e107 hosts (0.01 wall s for lifting);
no such hosts enter the e107 held-out probe.

Target: `timeout 300s bash ../../ralph/lanes/B/src/e108_nonadjacent_r9.sh
work/fresh_nonadj_heldout heldout 256`. Project 256 spaced e107 and 128
spaced old-critical e108 hosts, and lift 256 spaced distinct stems per
source and per level. The pilot explicitly tests output degrees 4..8;
it makes no claim about coverage outside that range.

| Source/stem edges | Distinct stem pool | Sample | Unique targets | New vs full known union |
|---|---:|---:|---:|---:|
| e107/e92 | 7,009 | 256 | 0 | 0 |
| e107/e93 | 33,653 | 256 | 0 | 0 |
| Old e108/e92 | 416 | 256 | 112 | 0 |
| Old e108/e93 | 5,371 | 256 | 118 | 0 |

Held-out total 3.59 CPU-s including sampling, projection, canonicalization
and comparisons (0.34 CPU-s of lifts). No scout key recovered. The 173
distinct critical e108 outputs across both pilots are all in the old
614 catalogue; separate graph checks and Python per-edge witness replay
agree (`logs/e108_r9_output_audit.log`). Novel yield is 0 keys/CPU-h on
both probes, not a bound on unsampled stems. Stop both sources.

## Degree-eight card diagnostic (enum, supplied keys only)

`src/critical_root_cards.py` profiles marked degrees/edge levels or
emits explicitly induced cards. Order-16/e22 degree-four/e8 control:
16 marks in five input graph classes and 12 distinct labelled
cards; all 12 pass order/size/independence checks. On the 1,756 supplied
critical e108 keys: no d8/e49 or d8/e50, 27 marked d8/e51 cards in 23
classes (7 in the withheld scout tranche), and 3,206 marked d8/e52
cards in 1,246 classes. The explicit e51/e52 cards have 27/3,145 distinct
labelled records and both pass independent validity checks. This
describes the supplied census only and does not restrict unknown keys.
We did not launch a d8/e51 lift over the 356,041 GR Table 13 seeds given
the few known controls and no prior cost or novelty justification.
Evidence: `logs/e108_r9_d8_{profile,bind}.log`.
