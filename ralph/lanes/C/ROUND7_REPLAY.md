# Round 7: mapped simultaneous-incidence sieve

Scope: global `R(6), f*=9`, ordered wing union sizes `(12,14)` and
no shared core vertices. The H19 mark has private K12 and the H21
mark has private K14. These are not H20 windows or P3 residues.
The round-6 `(12,12)` certificate set has not changed; its manifest
still passes in the repository root.

`proofs/p2_simultaneous_incidence.md` proves the one-sided filter and
the exact compressed witnesses. A single list contains **whole**
cross-neighbour sets; an adjacent pair must choose disjoint sets,
and a nonadjacent pair must jointly hit all relevant independent-set
witnesses. Then propagate supports to a fixed point. The cap on the
fast bitsets is a deferral, not a rejection. A passing boundary is
also only a relaxation, not a graph.

## Calibration and measurements

- Planted control: test all ten known regular order-22 graphs, with
  all seven complete-wing codegree-four pairs. All seven still contain
  the actual cross choices in each orientation, using both the direct
  fixed-graph test and the compressed cache. For each planted mark,
  increasing a deficit to the full opposite side size rejects. A toy
  has feasible degree flow and both single lists nonempty but has no
  compatible pair; negative singleton, compatible pair, and deferral
  controls also pass.
- Direct fixed-graph search and compressed propagation agree on
  **3,912 + 12,168** mapped pack requests (2.80 + 11.95 CPU-s for
  audits, including both implementations and the old filter). All
  fail; the old degree/flow/full-wing/all-possible-alpha filter
  passes **73 + 381** of them. The C-free relaxation got no rejection
  under the 16,000 pair-check cap (all 47 + 132 group requests deferred).
- Wider cached-only shards: **166,128** and **1,309,452** mapped packs,
  zero survivors and zero deferrals. The broader shard takes about
  2.65 CPU-s end to end. These are reproducible, nonrandom strides of
  the retained 4,749 H19 pilot and 35,099 H21 marks, not a census.
- Replacing actual union counts of opposite wing attachments by the
  sum of their counts capped at width weakens the filter (more wing
  vertices may be deleted from a witness). On the same 166,128 maps,
  it leaves 150 passes and 1,427 deferrals and takes 3.32 CPU-s; use
  actual unions, not this grouping. The unpropagated cached pair test
  alone leaves 3,241 in that shard.
- The 4,749 H19 pilot has **977,058,888** exact *token-compatible* pack
  maps against all H21 inputs, before the common-column codegree test.
  This includes both sides' actual pack multiplicities, upgrading the
  round-6 sample's lower count, not its coverage. No such raw join was
  written or run. `p2_cover_index.py` checks right multiplicities against
  the frozen projection and independently checks the factorial products.

## Replay the bounded pilots

From `scratch/C`, use new names for output:

```sh
set -euo pipefail
ulimit -c 0
ulimit -v 16777216
lane=../../ralph/lanes/C
sed 's/^int main(/int window_join_main(/' "$lane/p2_window_join.cpp" >p2_window_join_r7.inc
nice -n 5 timeout 60 c++ -std=c++20 -O3 -Wall -Wextra -pedantic -I "$lane" -I . \
    "$lane/p2_incidence.cpp" -o p2-incidence-local
nice -n 5 timeout 30 ./p2-incidence-local control ../../duo/reg6_22.g6
nice -n 5 timeout 45 ./p2-incidence-local audit p2r6-h19-pilot-canon.g6 p2r5-strong21.tsv 911 31 16000
nice -n 5 timeout 60 ./p2-incidence-local audit p2r6-h19-pilot-canon.g6 p2r5-strong21.tsv 613 57 16000 30000
nice -n 5 timeout 30 ./p2-incidence-local arc p2r6-h19-pilot-canon.g6 p2r5-strong21.tsv 317 13 16000
nice -n 5 timeout 30 ./p2-incidence-local arc p2r6-h19-pilot-canon.g6 p2r5-strong21.tsv 239 3 16000 7500000
nice -n 5 timeout 30 ./p2-incidence-local loose p2r6-h19-pilot-canon.g6 p2r5-strong21.tsv 317 13 16000
nice -n 5 timeout 30 ./p2-incidence-local count p2r6-h19-pilot-canon.g6 p2r5-strong21.tsv round7-sample-local.tsv
cmp p2r7-incidence-sample-count.tsv round7-sample-local.tsv
```

`cover` accepts the exact profile `(e(K12), sorted C support sizes in
K12)` as a comma-delimited final argument. The argument immediately
before it is a guard on the exact raw map count. It aborts *before the
join* if the input exceeds that value. It emits only passes/deferrals;
it does not save the raw join. A completed transcript is indexed by
`p2_cover_index.py`; a partial transcript is never `ENUM-ZERO`.

## Full profiled H19 catalogue and four empty profiles

The complete profiled generator ran on all **116,792** K12 inputs.
Independent `geng -t` plus `pickg -h:5`, then `labelg` and an exact sorted
comparison, reproduced these inputs including multiplicities. Each of the
two 58,396-core jobs reached its terminal count (777.196 and 563.168
CPU-s). The 2,121,010 raw windows yield **1,988,646** canonical H19
marks with the root fixed; `pickg -n19 -T0 -h:6` accepts all of them.
The H21 source and profile list are frozen from rounds 5 and 6.

The direct arithmetic underlying the profile join is as follows. For
the H19 side `A`, let `S_A=sum_{c∈C}d_H19(c)`, and similarly for `B`.
`S_A+S_B=54`, and each side's sum of cross degrees is
`9|A|−15−2e(A)−(S_A−6)` (replace `A` by `B` on the other side).
Equality gives `e(A)=e(B)+S_B−36`, so `e(H19)=e(B)+18`. A column of
degree `d` in H21 must have `8−d` neighbours in K12. The six resulting
sizes are sorted to form the profile with `e(A)`. On a fixed pair of
compatible marks, the number of column maps prior to the column
codegree test is the product of the factorials of size multiplicities.
Multiplying by both sides' pack counts gives an exact raw denominator.

Of 39 complementary profiles, 35 occur and four are empty. Those four
are precisely the profiles with `e(A)≥23`. Rebuild all 7,420 possible
cores at edges 23/24 from `geng` and rerun just these four profiles:
**no** windows, in 1.30 CPU-s. This is a separately replayed **hand +
enum candidate** for `e(A)≤22` in global `R(6), f*=9, (12,14)`, pending
critic. It is not an edge bound for `X`, `B`, or any P3 residue.

The exact entire token-compatible denominator is **369,169,500,080**;
it is a map count, not an extension count. At the 1.31M pilot's
2.03 μs/map this would be ~208 CPU-h, before checking heterogeneity
across profiles. Round 7 limits streaming evaluation to the 11
profiles below 210M maps each: **317,795,664** pre-column maps, 645
estimated CPU-s plus scans, balanced over three cores. The largest
profile is 82,960,844,400 maps and was not launched. Files are under
`scratch/C/p2r7-census/`; raw *window* records are saved, not raw map joins.

```sh
cd p2r7-census # from scratch/C
bin=../../../opt/bin
lane=../../../ralph/lanes/C
export LC_ALL=C
nice -n 5 timeout 40 "$bin/geng" -tq 12 23:24 | nice -n 5 timeout 40 "$bin/pickg" -q -h:5 >high-local.g6
nice -n 5 timeout 40 ./glue glue high-local.g6 12 1 high-profiles.tsv >high-windows-local.g6 2>high-local.log
test ! -s high-windows-local.g6
nice -n 5 timeout 80 ../p2r7-incidence count h19-full-canon.g6 ../p2r5-strong21.tsv profiles-local.tsv
cmp profiles.tsv profiles-local.tsv
nice -n 5 timeout 20 python3 -B "$lane/p2_cover_index.py" ../p2r6-h19-profiles.tsv profiles-local.tsv --budget 210000000
```

In each exact batch, `cover` counts before constructing any maps and
refuses if the requested cap would be exceeded. The three initial
staging launches accidentally used the factorial multiplier instead of
the raw-map column as the cap; all three guards refused, and their
partial logs are not results. `run-list-{0,1,2}.tsv` and `run-jobs.tsv`
are the actual bounded runs. A `cover` checker result uses `enum`,
not `cert`, unless separately proof-logged and checked.

## Terminal selected profiles

All 11 selected profiles terminated, with **317,795,664** exact and
tested column/pack maps, **zero** passes and **zero** deferrals in
**557.244 CPU-s**. The retained outcomes match the original batch list
and their pass/deferral files are all empty. The least expensive
profile `(15; 2,2,3,3,4,4)` also replayed all 10,944 maps by the direct
fixed-graph method: 1,152 bad degrees and 9,792 empty singleton lists;
no cap or survivor (12.76 CPU-s including the cached comparison).

All profiles at K12 edge counts **15** and **22** are among these 11.
Together with the four absent profiles at 23/24 and the necessary H21
projection (there is no profile below 15), this gives **16 ≤ e(K12) ≤ 21**
for the `(12,14)` split in global `R(6), f*=9` (`hand + enum`, pending
critic). **24** of the original 39 profiles remain open, with
368,851,704,416 untested token-compatible maps; no result for other
wing splits or global distributions. The bound uses the K12 private
side only. The raw-set fraction is only about 0.086%, despite removing
15 of the 39 profile types.

On three of the largest untested profiles, a fixed right sample
(`NR % 101 == 1`) gives 2,894,400 / 693,360 / 397,800 exact mapped
requests, respectively 4.36 / 1.18 / 1.43 CPU-s, zero survivors.
Their rate varies substantially (roughly 1.5–3.6 μs/map), so the full
budget remains an estimate. Nothing from those sample runs is excluded.

Recheck terminal index, run a small audited replay, and check last
round's frozen bundle (from the appropriate directories):

```sh
cd p2r7-census # from scratch/C
lane=../../../ralph/lanes/C
nice -n 5 timeout 15 python3 -B "$lane/p2_cover_index.py" ../p2r6-h19-profiles.tsv \
    profiles.tsv --runs results --budget 210000000
nice -n 5 timeout 100 ../p2r7-incidence-audit1 cover-audit h19-full-canon.g6 \
    ../p2r5-strong21.tsv smallest-audit-local.tsv 10944 15,2,2,3,3,4,4
test ! -s smallest-audit-local.tsv
cd ../../..
nice -n 5 timeout 90 sha256sum -c --quiet ralph/lanes/C/ROUND7_REPLAY.sha256
nice -n 5 timeout 90 sha256sum -c --quiet ralph/lanes/C/ROUND6_REPLAY.sha256
```
