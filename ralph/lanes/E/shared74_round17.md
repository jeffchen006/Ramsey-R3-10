# Mixed saturated f=32: round 17, core 15 only

Scope: zero-based `GCQf?{` (core 15 in `scratch/E/r5_saturated/e11.g6`),
`(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, mixed `(10,10,11,11)`,
universal `δ(G)≥5`, and E-021's all-graph sole-missing `e=74` premise.
All four omission roles, `K=6,7,8`; no MTF assumption. Only the round-16
frozen ordered cover and its receipts are used. No repeat cover search.

## Controls and gate before production

The round-16 manifest verifies. Both six-site routes return SAT on
the positive control (narrow-first tries wide), and both proofs check
on the negative control. The original branch binder rejects a genuine
narrow CNF for the wrong degree branch; the independently checked route
roster rejects a wrong fresh replay ID. The new queue/branch helper passed
small valid and invalid spacing, duplicate-ID and wrong-branch controls.
There was one immediate helper syntax error before those tests, fixed and
retried. Extracting open rows from the frozen merged receipt gives the
same 142 ordered IDs; the 16 spaced IDs include `(22646,18)` and
`(93731,12)`. The branch table's cumulative bounds bind each ID to the
actual ordered cover row, first group and omission, not just its filename.

| Same 16 IDs, including separate fresh bind/check | Checked | CPU-s | Peak RSS (KiB) | Route bytes before fresh logs |
|---|---:|---:|---:|---:|
| Width eight, regenerated original | 16 | 18.65 + 9.34 = 27.99 | 177,156 | 17,065,012 |
| Width three first, with original reference and inclusion | 16 | 12.10 + 5.34 = 17.44 | 40,624 | 18,074,104 |

No sample fallback. Choose narrow first: 37.7% less CPU than wide with
the same extra fresh rebind, 4.36× lower peak RSS, ~5.9% more bytes. Save
the sample narrow proofs and count each sample ID once. For the remaining
126 use this conservative pricing rule: triple the sum of both complete
sample routes extrapolated per ID, as if every narrow attempt needs a
full wide fallback and right-tail IDs cost 3× the paired averages. That
is ~1,074 CPU-s, or ~1,471 CPU-s (0.409 core-h) including round 16 and
the comparison, plus small audit overhead. This is a price, not a proof
of future costs. Including the whole prior and comparison retention, two
times both routes' sampled worst per-ID size for all 126 is <0.68 GiB.
Comparison/control caps total 466 CPU-s; actual 47.44 CPU-s. Four strided
production workers, at most one solver/checker per worker; each has 260
route and 110 separate rebind CPU-s. The combined budget, even with the
full comparison and production caps, full round-16 measured cost and a
20 CPU-s final audit, is 2,316 CPU-s (<1 core-h). Each shard has a 200
MiB route gate, a 210 MiB fresh rebind gate, and a 4 MiB per-file limit;
including controls, comparison, and per-shard overshoot reserve keeps
round-16 plus round-17 staging below 1.25 GiB. A bad or missing route
stops its shard and blocks the final debit.

## Conditional exclusion — pending critic

**Hand + enum + cert, core 15 only.** Round 16 independently regenerated
the exact ordered cover (34 nonempty first branches, 94,738 projections,
716,045 lifts) and replayed all eight receipt shards. Round 17 resolves
the resulting open queue without recalculating the earlier dispositions:

| Disposition | Lifts |
|---|---:|
| Projection-wide graph witness | 559,940 |
| Later single-window graph witness | 142,652 |
| Fused contradiction | 11,733 |
| Marked incompatibility | 1,578 |
| Bound width-three CNF with checked CakeLRAT | 142 |

The checked union is 16 sample IDs plus 32/32/31/31 disjoint production
IDs. All 142 narrow CNFs were independently reconstructed from their
actual `(projection,lift)` cover rows and checked for literal inclusion
in their own regenerated width-eight references. Each proof passed both
initial checks and the separate fresh rebind/check. No fallback was
needed. The 16 matched wide proofs are comparison evidence only and are
not counted again. The sorted `checked.15.tsv` identifies the first
branch, first group, cover-row digest, omitted group and proof folder
for every routed ID (110 projections and 12 branches). The checked union
matches the frozen exact queue including both extremes.

New routes 93.96 CPU-s, new fresh rebinds 40.96 CPU-s, and final audit
0.13 CPU-s. Round 17 total including controls and both sample routes:
182.49 CPU-s (0.05069 core-h). Rounds 16+17: 531.58 CPU-s (0.14766
core-h), ~254 MB logical retained. Four peak slots. All 18 bounded
wrappers collected, 17 successful and one recovered helper setup
error before calibration. No active, stopped or detached jobs. If
accepted, mixed cores 1, 6, 9 and 18 remain. This does not close the
full `(2,32)` case or decide `R(3,10)`.

## Independent audit without production solvers

From `scratch/E/r17_shared`, verify `sha256sum -c --quiet freeze.15.sha256`
and `(cd ../r16_shared && sha256sum -c --quiet freeze.15.sha256)`.
`shared74_round16.md` documents the optional independent earlier
cover/receipt replay. For the new part, use an absolute fresh directory
`A` in your scratch area; the new proof rebind checks need no SAT solve.
The selected shard lists come from `remaining.15.jsonl`. The comparison
wide folder can be verified the same way as its narrow counterpart.

```bash
set -eu
L=$(realpath ../../../ralph/lanes/E)
W=$PWD
C=$(realpath ../r16_shared/cover.15.jsonl)
Q=$(realpath ../r16_shared/spaced.15.jsonl)
run() { nice -n 5 timeout -k 8s "$1" bash "$L/limited.sh" "$2" "${@:3}"; }
(cd "$A"; run 30s 16 python3 -B "$L/core15_queue74.py" prepare --original "$W/../r16_shared")
cmp "$A/remaining.15.jsonl" remaining.15.jsonl
for folder in compare.narrow proof.{0..3}; do
    mkdir "$A/$folder"
    find "$W/$folder" -maxdepth 1 -type f \( -name '*.cnf' -o -name '*.lrat' -o -name '*.replay.log' \) \
        -exec cp -l -t "$A/$folder" -- {} +
    if [[ $folder == compare.narrow ]]; then
        run 140s 65 python3 -B "$L/price_width74.py" rebind "$C" "$Q" "$A/$folder"
    else
        run 175s 110 python3 -B "$L/price_width74.py" rebind "$C" "$A/remaining.15.jsonl" \
            "$A/$folder" --stride 4 --offset "${folder##*.}"
    fi
done
```
