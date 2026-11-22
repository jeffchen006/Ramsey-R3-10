# Round 20 — factored fifth-row gate; no right-key exclusions

## Hand proof and exact scope

`proofs/panel20_factored_card.md` proves that in the marked cap-five
one-neutral 16/17 cover with a degree-three triple `x` on the order-16
side, the three four-sets `N(a)−(V∪{x})` for its marked roots `a` are
disjoint and exhaust the physical 12-site core `H`. The neutral must
therefore be one of `x`'s three neighbors in the left window. In
frozen frame 42679 (host 97, `x=0`), the mark difference sets in physical
labels are `{1,4,9,11}`, `{2,3,6,13}`, `{5,8,10,14}`. The complement
outside `x` is exactly `N_W(x)={7,12,15}` and the neutral is `7`.

For each right mark `M_b`, let `Q_b` be its original singleton group.
There is one shared legal row `T` with `|T|=3`, `T∪{z}` independent
in the right window, and `|T∩M_b|≤2` for every `b`. The local card
condition holds exactly when `|Q_b−T|≤tau` for every `b`, where `tau=4`
if a degree-four card deletes to `H` and `tau=3` otherwise. This is
equivalence to the local fifth-row gate, not to completion. The tested
right triple roster necessarily has original sizes `(3,3,3,4)` up to
permutation; in particular the size-four group is **not** dropped at
tau=3. The program uses `max(0,|Q_b|−tau)` for every actual group.

## Enumeration and independent literal check

The only target roster was the pre-existing 116 right triple frames
at `(75,5)`, recovered from the frozen 59,521-line order-17 stream.
All 116 right payloads match the frozen handoff, and every frame is
rebound from the raw catalogue with its physical neutral and marks.
No left/right pair was generated, no margin rerun, no signed search.

| Right-only statistic | tau=3 (flag absent) | tau=4 (flag present) |
|---|---:|---:|
| Legal rows | 5,390 | 5,390 |
| Rows surviving the card condition | 3,714 | 5,390 |
| Minimum to maximum survivors per right key | 18–38 | 42–51 |
| Right keys with a surviving row | 116/116 | 116/116 |
| Right-key failures | 0 | 0 |

For the literal check enumerate triples of all 16 private sites,
check edges with ordinary sets, and assign each residual singleton
set to retained sites of a physical restored card. The two checks
agree on every legal mask and both flag settings. For the frozen
left `H`, scan all 21 raw degree-four roots and identify 14 matches
by residual graph isomorphism; the first is host 0/root 0. The tau=3
literal test deliberately withholds these degree-four witnesses,
while tau=4 includes the actual witness. Every one of the 578 legal
masks from the 12 previously signed-tested IDs is reproduced and
passes tau=4. Of those masks, 404 pass the counterfactual tau=3;
this is not a cut or new pair evaluation. The exact roster, counts
and least passing physical masks are in `scratch/C/r20/right_flags.tsv`.
Neither right-key failure list has a member; no margin intersection
is needed or priced.

Calibration: the known order-35 circulant gives 105 `K2,4` marks and
840 planted shared-row controls (both choices of neutral in the
distinguished pole's original card), each accepted by the enabled
physical card and rejected when that card size is withheld. Four
smaller labelled controls compare the two methods on 61 legal rows:
the original size-five group can need two hits, one hit or be
unhittable; an independent triple in one mark violates the pair cap.

## Accounting and replay

Before the full scan the 12-key priced sample took 0.83 CPU-s; the
initial full scan took 1.06 CPU-s. Final and clean full scans took 1.04
and 0.69 CPU-s. Including all controls, sample runs and all three full
runs, **7.30 CPU-s / 0.00203 core-h**, peak RSS 38,240 KiB, one worker,
512 MiB VM, roughly 104 KiB allocated scratch across both work dirs.
Five deterministic output files match byte-for-byte. No active jobs.

```sh
sha256sum -c ralph/lanes/C/ROUND20_FREEZE.sha256
bash ralph/lanes/C/replay_panel20.sh "$PWD/scratch/C/r20-review"
cmp scratch/C/r20/right_flags.tsv scratch/C/r20-review/right_flags.tsv
```

**Scope/status:** `hand` (exhaustion and factorization), `enum`
(negative right-only pilot), pending critic. No hypothesis branch or
marked ID was debited. Stop the fifth-row route in this roster, as
directed. The 12 exclusions from round 19 are already independently
confirmed and must not be credited again. No graph candidate; case R
and R(5) remain open.
