# Round 13 — named e98 remainder and e122 child pilot

Both results are **enum**, bounded to the named inputs. The best catalogue
remains **2,104,146 / 2,104,151** order-32/e108 graphs, five missing. No new
target graph, proof, floor 109, e88 result, or distribution subtraction.

## Authorized 545-parent remainder

Tested the exact disjoint set `work/e108_r12_provenance/not_deck_bound.g6`
at d7 and d8, in six shards. Every shard records the input and output
SHA-256, both labelled leaf counts and aggregate CPU. The calibrated
control recovered exactly the 42 known critical 16/e22 classes from their
48 deck parents. From the 545 e98 inputs, d7 emitted **1,001** labelled
leaves and d8 **393**. Canonicalization gives **477** critical 32/e108
classes; all were already in the round-11 1,875 critical keys. Traces
independently verifies the 477 count and the 1,875-key augmented union.
Validation includes graph order, edge count, triangle-freeness, alpha bound
and single-edge-deletion criticality of the input and output keys.

The 40 CPU-s authorized search-and-audit allowance had been priced at
21.2–24.4 CPU-s before validation; actual **22.225 CPU-s** including
validation. Calibration used 0.683 CPU-s. An initial control invocation
used bound 5 instead of 6 and was rejected immediately, before any lift
on a target parent (`logs/e108_r13_complement.log`). No job is left live.

The other **200** of the 745 set-aside keys were separately rebound in
0.057 CPU-s: independently select e98 from N's exact archived 843-row deck,
canonicalize, validate and compare with `deck.overlap`; recanonicalize
both N raw outputs and confirm their archived frontier keys and counts.
All e98 parents are eligible at both degrees because `108−98−d≥0` for
d=7 and 8 (N's d8 total is lower due to ineligible higher levels). This is
an **archival** binding, not fresh generation on the 200. The 545 and 200
are disjoint from each other, the earlier 471 and the round-12 7,954. Their
union completes the set-aside partition, not the full order-31/e98 level.

## Critic's e122 child pilot

Reproduced the critic's exact 77 canonical 33/e122 children by all **116**
triangle-safe edge additions to N's six e121 hosts. The 77 are valid and
Traces-distinct. Subtract the actual named previous direct-descent hosts
after filtering to e122: 243 scout `sample122`, 48 scout `stratified`,
128 round-8 e122 hosts, **419** in all. The seven e122 inputs from the
separate two-hole `strong33.in` also have no intersection. Do not subtract
unsearched rows just because they were in the larger G catalogue. Result:
**77/77 fresh hosts relative to these earlier runs**.

Before touching the fresh host set: reproduce the sole known 7/e6 residue
from all three order-8 controls; reject a valid order-8 input at the lower
target e5 (independently test 588 labelled five-edge subsets in its cards);
recover a withheld known e108 key from a previously used e122 host, bound
by a concrete labelled puncture and deletion witness (`held_out.witness.tsv`).
The projected descent cost was 0.264 CPU-s at the prior stratified rate.
Actual: **2,541** cards, 3,071 nodes, 85 labelled leaves, **five** checked
critical keys, **zero** novel; **0.085 CPU-s** descent plus canonicalization,
**0.886 CPU-s** total including build and controls. No larger run started.

## Replay

From the repository root, `sha256sum -c ralph/lanes/B/ROUND13.sha256` binds
the code, archived source, receipts, outputs and logs. To regenerate from
`scratch/B` with **one** foreground slot and a new directory for each run:

```sh
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
s=../../ralph/lanes/B/src
nice -n 5 timeout --kill-after=3s 180s python3 "$s/e108_r13.py" work/e108_r13_complement_replay
nice -n 5 timeout --kill-after=3s 150s python3 "$s/e108_r13_hosts.py" work/e108_r13_hosts_replay
```

Compare `done.tsv` except for its last column and the raw logs/keys for
both lift arms; compare the host `inventory.tsv`, `fresh.122.g6`,
`held_out.witness.tsv`, `target.raw`, `target.keys` and `novel.g6`. These are
regenerations with the same generators, not independent search algorithms.
The Traces counts and adverse-control brute force are independent checks.
