# Round 9: mixed strip completions and pure-window filtering

Use `scratch/G/round9` as working directory for these producer commands,
set `root=../../..`, `src=$root/ralph/lanes/G`, `py=$root/opt/venv/bin/python`,
and use the usual CPU/wall/RAM bounds. For independent replay use a
separate writable copy of the proof directory. Both cert bundles use
`prove_strip_windows.py KEYS PROOF_DIR --mixed --eager 10000 --replay`.
The DIMACS SHA and stored trace size must match the selected receipt.
The compressed trace SHA is independently recorded by the binder.

## Mixed d8, codegree 3, δ(T)=3

Scope: `(n6,n7,n8,n9)=(2,7,4,27)` only, opposite path/leaf and
matching/incident or path/middle, an uncrossed d8 anchor of the latter
with codegree 3 to the path centre, and the induced order-26 common
antineighbourhood having minimum degree 3. Higher minimum degree
and lower pivot codegrees are outside this bundle.

Regenerate the complete 191-core rooted source, 2,712,471 glues,
2,111 labelled marks, and 1,767 marked isomorphism representatives as
in `ROUND7_REPLAY.md`. This is the same weaker envelope as the pure
round-7 source, but **not** that proof encoding. From those weak marks:

```sh
nice -n 5 timeout 60s "$py" -B "$src/mixed_strip_cover.py" \
  ../round7/lowdegree26.canon.keys mixed26.replay.keys
cmp mixed26.keys mixed26.replay.keys
LC_ALL=C sort mixed26.replay.keys > mixed26.replay.sorted
LC_ALL=C sort ../../A/strip9/mixed.j3.keys > mixed26.replay.A.sorted
cmp mixed26.replay.sorted mixed26.replay.A.sorted
```

5,438 matching +1,728 middle roles. A independently regenerated the full source and verified 16
pilot fresh DIMACS hashes/proofs; see `scratch/A/strip9/`.

```sh
nice -n 5 timeout 150s "$py" -Bu "$src/bind_strip_batch.py" \
  mixed26.keys ../round7/lowdegree26.raw.g6 mixed26.replay --io-workers 4 \
  --batch mixed26.pilot.keys mixed26.pilot 3 mixed26.pilot \
  --batch mixed26.production.keys mixed26.production 8 mixed26.production
cmp mixed26.bound/certificates.tsv mixed26.replay/certificates.tsv
```

The 96 dispersed pilot roles all gave dual LRATs, in 40.57 CPU-s
(0.423 CPU-s/key), versus 6.89 CPU-s for the 24 d8/j4 pilot roles
(0.287 CPU-s/key; measured old production 0.279 CPU-s/key). The order-26
encoding preserves all 24 historical order-27 pilot DIMACS hashes.
Production gave 7,070/7,070 dual LRATs in 2,970.90 CPU-s, 0.420 CPU-s/key.
The full 7,166-key index is terminal with no CAP or missing receipts;
the compressed traces total 197.82 MiB.

## Mixed d9, codegree 5

Same two mixed strip types and same profile, but select a noncrossed
degree-nine pivot, at codegree 5. The complete 1,988 weak source marks
from `pair27.keys` cover the order-27 window. Both B holes remain on
active anchors rather than use the pivot. See `rows/mixed_pivot_windows.md`.

```sh
nice -n 5 timeout 90s "$py" -B "$src/mixed_full_cover.py" \
  ../round7/pair27.keys mixedfull.replay.keys
cmp mixedfull.keys mixedfull.replay.keys
nice -n 5 timeout 90s "$py" -B "$src/test_mixed_full.py" mixedfull.keys
nice -n 5 timeout 100s "$py" -Bu "$src/bind_strip_batch.py" \
  mixedfull.keys ../round5/r38_27.canon.g6 mixedfull.replay --io-workers 2 \
  --batch mixedfull.pilot.keys mixedfull.pilot 1 mixedfull.pilot \
  --batch mixedfull.production.keys mixedfull.production 1 mixedfull.production
cmp mixedfull.bound/certificates.tsv mixedfull.replay/certificates.tsv
```

The complete role scan produces 162 matching and zero path/middle
roles. All 162 structural triangle-free addbacks pass. 23 pilot and
139 production traces all dual-check in 6.57 and 37.79 CPU-s.

## Pure higher-minimum samples: not a closure

`joint.dispersed.keys` selects 26 order-25 (j=1, δ=3) and 26 order-26
(j=2, δ=4) marks; see round 8 for the sampled catalogues. Trial without
alpha cuts, using exactly the old triangle/MTF/degree/budget rows:

```sh
nice -n 5 timeout 240s "$py" -B "$src/joint_pivot_caps.py" \
  --controls ../round7/completion.control.g6 joint.dispersed.keys --conflicts 2500
nice -n 5 timeout 150s "$py" -B "$src/projected_degree_caps.py" \
  --controls ../round7/completion.control.g6 joint.dispersed.keys
```

At that cap, the old rows returned 14 unchecked UNSAT and 38 CAP;
the joint caps gave one further unchecked UNSAT and 37 CAP among the
same 38. This is a bounded comparison, not 15 checked closures or a
measured proof reduction. The joint caps are logically redundant when
δ≥4 (Lane A, `scratch/A/strip9/joint.audit.log`); at δ=3 they can bind
only through degree-three anchors. The new projected degree ceiling
and support DP reject zero marks and zero of their two profiles.
Neither pure branch scales; no order-21 census or proof batch launched.

## c1 variant provenance

The corrected round-8 recipe has 32 non-eager original pilot proofs and
17,162 eager production/retry proofs in G's selection. A's alternative
selection is all eager. The conclusions and key sets are identical;
the original 32 and A's replacements have different DIMACS hashes.
Do not cross-use these traces. See `ROUND8_REPLAY.md` and the critic's
32+32 independent passed replays at `scratch/critic/r8/G/`.
