# Lane D: new SAT encodings and splits for case R

Start share: 12 cores.

Background: `paper/latex/sec7.tex`, `sec8.tex` (Knuth probes: plain SMS on cube R ~1e9+ CPU-s), the
edge-kernel reduction (sec8.tex "Kernels"; `duo/kernel_run2.py`, `duo/kfilt.c`; catalogues M = 3: 238,
4: 96,135 kernels). SMS (lane A builds it in opt/; until then build a private copy in scratch/D/build).

## Goals, in order
1. **Close R(3) completely (certified).** R(3): all non-adjacent codegrees are 1, 2 or 3 and
   n3 = n1 + 240 (Lemma Mc). The kernel catalogue for M = 3 has only 238 kernels; 11 of the first 15
   were UNSAT in 0.6-33 s, 4 timed out at 1 h. Get all 238 with the certificate chain. Use a stronger
   encoding first if the time-outs stay: e.g. the codegree counts (n3 = n1 + 240, per-vertex sums of
   L9), the matching lemma, cardinality of codegree-1 pairs <= 160.
2. **Then R(4)** (96,135 kernels; most samples > 1 h): find an encoding or split that makes the median
   kernel fast. Measure with Knuth-style random probes before any full run.
3. **New splits for R** that give exact partitions (each model in exactly one part): e.g. by the
   isomorphism type of the codegree profile of N(0), by q(0) (number of C4 through vertex 0), or by
   which (3,8;20+c)-class X belongs to. Test each split on a calibration where the answer is known:
   the 8-regular (3,9,35) case (only C35) and 7-regular (3,8,28) (none, SMS 1846 s in the old run).
Every UNSAT you call cert must pass the chain of sec7.tex. Coordinate with lane A (owner of the
certificate tools) and lane C (lemmas to encode).
