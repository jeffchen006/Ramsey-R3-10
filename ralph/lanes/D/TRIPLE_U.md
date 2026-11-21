# R(4) saturated K3,4: singleton-triple projection

The order-15 projection uses `balanced15.tsv` from `BICLIQUE_R4.md`.
The systematic 1-in-67 sample took 0.71 CPU-s (1,011 rows). Linear
estimate for the 67,730 rows: 48 CPU-s at one core, independent of the
Python witness checks. Sampled rows all had a witness. Bound the full
one-core run at 240 CPU-s with a 300-second wall limit and a per-row
limit of 200,000 tested compatible triples.

## Necessary rows (`hand`)

For a singleton-support group T of three vertices on the large part,
let each mask be its neighborhood in U. Each mask is independent;
its intersection with each U_i is at most three (one common core
neighbor with the anchor a_i). A mask adds no more than four common
neighbors with any u in U. Any two masks intersect in at most three
because the T vertices have their b-anchor in common. A U vertex has
cross slack 8−d_U; a U-pair has cross slack 4−c_U−[same group]. Check
these slacks for all three masks, allowing repeats. Two T vertices with
the other three b-anchors form an independent five, so their mask
union leaves alpha at most four in U. For three T vertices it leaves
alpha at most three, hence at most eight U vertices. Thus this tests
the seven-vertex hit condition with its stronger independence premise.
It fixes one T group only and leaves all other V attachments free.

## Measurements (`enum`)

- C12: 30 marked U rows from the 12-graph (3,5) control. Keep the same
  codegree slack rules but use U alpha bound four, so the pair/triple
  residual bounds become three/two. Exhaustive Python replay matched
  the complete mask counts, first witness validity, matching witness
  types and all outcomes: 28 pass, 2 fail; 1.95 CPU-s replay.
- Target: all 67,730 rows pass (0 rejected, 0 capped); 47.18 CPU-s.
  Independent Python verified all 67,730 emitted triples in 25.30
  CPU-s. Matching cover: 8,669 rows C15-only, 40,008 C6+C9-only,
  19,053 admit both, counting marked partitions rather than graph
  isomorphism classes. The witness types overlap. No K3,4 exclusion.

From `scratch/D` with `ulimit -v 16777216`:

```sh
g++ -Wall -Wextra -Wpedantic -Werror -O3 -std=c++17 ../../ralph/lanes/D/triple_u.cpp -o triple_u
nice -n 5 timeout 60 ./triple_u 4 20000000 1 < balanced12.tsv > triple12.tsv
nice -n 5 timeout 60 ../../opt/venv/bin/python -B ../../ralph/lanes/D/check_triple_u.py balanced12.tsv triple12.tsv --exhaustive-control
nice -n 5 timeout 300 prlimit --cpu=240:245 ./triple_u 5 200000 0 < balanced15.tsv > triple15.tsv
nice -n 5 timeout 120 ../../opt/venv/bin/python -B ../../ralph/lanes/D/check_triple_u.py balanced15.tsv triple15.tsv
```

The four input/output hashes are in `ROUND4_INPUTS.sha256`. Do not
repeat single-T filters unchanged; any useful next projection needs a
joint resource test across several T groups or explicit V incidences.
