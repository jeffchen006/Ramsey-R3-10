# Round 10: residual e168 pivot windows

Scope for every row: `(n6,n7,n8,n9)=(2,7,4,27)`, adjacent degree-six
strip hypotheses, path/leaf A and matching/incident or path/middle B,
and a **noncross** B pivot paired with the A centre. Definitions and
proofs: `rows/residual_mixed_windows.md`. No whole distribution closed.

Use cwd `scratch/G/round10`, `root=../../..`, `src=$root/ralph/lanes/G`,
`py=$root/opt/venv/bin/python`, and `ulimit -v 16777216`. Times are
user+system CPU, not sums of parallel wall time.

## Exact source and proof bundles

Just as in rounds 7–9, the 191 complete order-22 cores produce the
rooted degree-three order-26 list (2,712,471 raw; 2,111 weak marks;
1,767 marked orbits) and the rooted degree-two order-25 list
(18,333,381 raw; 20,181 weak marks; 17,194 marked orbits).
The same envelope covers both types of mixed holes. Generate roles:

```sh
nice -n 5 timeout 90s "$py" -B "$src/residual_mixed_cover.py" \
  ../round7/lowdegree26.canon.keys r26.d9.replay.keys 9 --minimum 3
cmp r26.d9.keys r26.d9.replay.keys
for degree in 8 9; do
  nice -n 5 timeout 120s "$py" -B "$src/residual_mixed_cover.py" \
    ../round7/lowdegree25.canon.keys "r25.d$degree.replay.keys" "$degree" --minimum 2
  cmp "r25.d$degree.keys" "r25.d$degree.replay.keys"
done
```

The ordered role IDs for all three lists match Lane A after sorting
(`scratch/A/strip10/roles.{26.9,25.8,25.9}.keys`). Expected:

| B d, j, δ(T) | Matching | Middle | Status |
|---|---:|---:|---|
| 9,4,3 | 50 | 165 | 215/215 terminal dual LRAT and bound, A independently replayed all |
| 9,3,2 | 2,134 | 3,997 | 6,131/6,131 terminal dual LRAT and bound, independent role IDs |
| 8,2,2 | 69,278 | 21,236 | Middle-only detached batch; matching pilot only |

All selected CNFs use `--mixed --residual --eager 10000`, **no**
`--joint` or `--cut-budget`. The exact bound is per role, not per
ordinary graph. For the two terminal bundles (change output suffix
if replaying), run:

```sh
nice -n 5 timeout 155s "$py" -B "$src/bind_strip_batch.py" \
  r26.d9.keys ../round7/lowdegree26.raw.g6 r26.d9.rebind \
  --batch r26.d9.pilot.keys r26.d9.pilot 2 r26.d9.pilot \
  --batch r26.d9.production.keys r26.d9.production 4 r26.d9.production --io-workers 3
nice -n 5 timeout 155s "$py" -B "$src/bind_strip_batch.py" \
  r25.d9.keys ../round7/lowdegree25.raw.g6 r25.d9.rebind \
  --batch r25.d9.pilot.keys r25.d9.pilot 3 r25.d9.pilot \
  --batch r25.d9.production.keys r25.d9.production 8 r25.d9.production --io-workers 4
cmp r26.d9.rebind/certificates.tsv r26.d9.bound/certificates.tsv
cmp r25.d9.rebind/certificates.tsv r25.d9.bound/certificates.tsv
```

For proof replay, use `prove_strip_windows.py KEY_SUBSET PROOF_DIR
--mixed --residual --eager 10000 --replay`. Do not use a pilot trace
against a budget/joint formula. Middle-only uses `r25.d8.middle.keys`
and a single 12-shard batch in the binder if it terminates (see
`STATE.md` for progress, PID and caps). A certificate index binds
receipts and hashes; `--replay` independently runs both checkers.

## Hand exclusion and census controls

The saturated 3+4 cut proves that a noncross retained anchor has
degree at least `|T|−22`. At the mixed pin this excludes `d9,j1,δ=0`
and `d8,j1,δ=1` / `d9,j2,δ=1` (cross endpoints have degree ≥2 in the
last two cases). `leaf_window_core.py` gives an independent bracketing
check on the 191 order-22 classes; the 410-graph control agrees with
brute force on all 42 ordered marks. There are zero projection
matches after 6,411 preliminary 3+4 pairs. Separate gluing gave zero
marks on 513,438 rooted order-24 leaf glues and 191 order-23 isolated
graphs. The degree-one gluer recovers all three known order-seven
minimum-degree-one classes before the target run.

```sh
nice -n 5 timeout 65s "$py" -B "$src/leaf_window_core.py" \
  ../round7/control8.g6 "$root/gluing/val/r3_7_22.g6"
```

At equality `d_T(s)=|T|−22`, deleting the noncross anchor `s` and its
neighbours leaves an order-21 core whose small side misses exactly
one slot, incident to its cross endpoint. `short_anchor_core.cc`
finds 6,160 roles on 6,056 of the 1,118,436 published-count classes
(3.20 CPU-s); unpruned replay reproduces exactly the same keys in
3.38 CPU-s. All 42 ordered small-control keys match the Python
literal enumeration. Compile with `g++ -std=c++20 -O3 -march=native`;
run `gzip -dc ../round8/r37_21.g6.gz | ./short_anchor_core 3 4 4 one-deficit`
under bounded time, RAM and `pipefail`. This is a tiny **conditional**
parent queue, not a full higher-minimum window source. Raw grafting
from a 256-parent pilot for order 24 δ=2 capped at 100 s despite
1,194,099 already emitted weak marks. Of 1,004 sampled capped-prefix
marks, 999 were rooted at the noncross minimum; they admit 6,532 d8
roles and 339 d9 roles, uncanonicalized. Do not scale raw grafting.
Next try direct partial-window clauses with the core and its 3+4 marks
pinned, rather than producing every legal order-24 graph first.

## Matched-variant tests (no scope change)

`residual_mixed_joint.py` compares the same roles, with 215/215 retained
for order 26 and 639/640 retained for the order-25 samples. The only
extra rejection is on the held-out d8 matching arm; verified by the
independent 210-placement oracle in `test_residual_mixed.py`, which
also fixes an explicit positive triangle-free support shell into the
joint CNF and tests 1,076 nonadjacent pairs in C13/C35/Exoo39. The
sample is **not** a complete catalogue of higher-minimum windows.
Lane A separately reports 130/1,096 role attrition (zero lost marks)
on a higher-minimum d8 sample and zero attrition on 125 d9 roles.

Matched d8 sample, 48 roles including 11 middle: eager base 48/48
at 32.12 CPU-s; structural only 41/48, seven conflict caps and 56.11
CPU-s; joint eager 48/48 at 32.73 CPU-s; budget eager 48/48 at 32.56
CPU-s. No demonstrated proof-cost improvement. No d8 matching sweep,
higher-minimum sweep, class-LP closure, floor upgrade or graph claim.
