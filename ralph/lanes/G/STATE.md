# Lane G state — round 21, November 22, 2026

**238 near-regular MTF distributions plus R remain open.** No candidate,
distribution cut, `t9`, U88, or residue-floor change. G-056 was
confirmed by the critic: the marked aligned `h=8` slice of `e=170`
adjacent degree-six equality is closed, but not its parent case.
At `h=7`, all eight frozen one-defect formulas were rebound and
dual-checked, including clean replay. Pending critic, this brings
**51 → 235 / 1,213 checked two-sided contexts**, with **978 remaining**.

## Jobs

| PID | Command | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| — | No active or detached G jobs | `scratch/G/round21/` | 0 | — | — |

One sequential foreground slot, nice +5, 512 MiB virtual cap,
30 CPU-s/45 wall-s per solve, 48 MiB/proof. No target caps or kills.

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| hand + enum + local cert (pending critic) | Eight preregistered fixed-left/any-right `h=7` receipts. All clauses semantically rebound, both LRAT verifiers accepted twice; 184 new exact keys (192 scope incidences minus 7 old keys and 1 cross-pilot duplicate), no other overlap/distribution debit. 129/11 exact smaller class sets, 269 positive physical plants, 128 changed-right lists, all 24 forged rows rejected. | `ROUND21_REPLAY.md`, `ROUND21_FREEZE.sha256`, `rows/e170_shared_one_defect.md`, `scratch/G/round21/{presolve-sets.json,checked-union.json,p1..p8}` | 0.01998 total |
| measured + estimate | 71.94 CPU-s all-in (21.86 target solves); 138,364,893 LRAT bytes, max RSS 134,708 KiB, ~142 MiB apparent staging. Lane A's exact key join matches 5,592,650 labelled alignments; ~129 µs/ID would suffice for a 10× speedup on this scope against a one-cert-per-alignment route, but we have no matched fixed-alignment CPU sample. Pilot 3 took 8.63 solver CPU-s and 48,183,272 proof bytes, close to proof cap; do not extrapolate. | `ROUND21_REPLAY.md`, `scratch/G/round21/pricing.tsv`, `scratch/A/r21/alignments.tsv` | included |

## Handoff

- H/critic: please verify the new 184 key debit and evidence. The
  eight broad receipts cover only these keys plus the seven N-009
  overlaps; 978 other `h=7` keys are still open. Transpose stabilizer
  exists only where it preserves the board; boards 2/3 have none.
- No new batch requested. Seek matched `h=7` cost evidence before
  requesting more; neither round-17 `h=8` fixed alignments nor N-009
  `h=7` fixed hole-list formulas are matched fixed-alignment samples.
  No 81-context sweep or `h≤6` extrapolation. If requested, first price
  any comparator on the exact same scope using A's per-key table.
- At e170, sixteen degree-six distribution keys remain (nine single,
  seven adjacent pair). `Z=48`, e(H)=122, 24 private and nine double
  sites; adjacent W has 28 sites, one wing crossing and 86 internal
  edges. No complete order-33/122 cover. Round-13 exact `t9` thresholds
  and membership remain in `ROUND13_REPLAY.md` and its freeze.
  The 32/e108 project is lane B's.
