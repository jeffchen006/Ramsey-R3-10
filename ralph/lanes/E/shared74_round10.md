# Mixed saturated f=32: round 10

**Hand + enum + cert, pending critic.** These are individual core
exclusions for `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, and profile
`(10,10,11,11)`, using universal `δ(G)≥5` and the inherited E-021
all-graph sole-missing e74-class premise. Core numbers are zero-based
indices in `scratch/E/r5_saturated/e11.g6`. No MTF assumption, no
assertion about the missing graph's identity, and no full f=32 closure.

## Core 12: `G?opuK`

All eight canonical first-support branches were sampled in forward
and reverse order within branch, up to 160 projections from each end.
Each sample had 1,191 projections, byte-bound into the full source.
Marking retains the four omitted-group roles and tries `K=6,7,8`;
neither test uses implications obtained from the other test.

| Sample | Lifts | Graph-only open | Marked-first CPU-s | Fused-first CPU-s | Identical residual IDs |
|---|---:|---:|---:|---:|---:|
| Front | 7,105 | 65 | 2.044 | 1.225 | 6 |
| Tail | 4,983 | 113 | 1.380 | 1.748 | 3 |

The benchmark disagreed by sample; fused-first was less costly in
sum. All nine pilot residual formulas produced and passed CakeLRAT
and fresh byte-regeneration checks (6.04 and 5.84 CPU-s). These are
sample IDs, not used for closure. Calibration passed 520 translated
positive and 520 altered `C13(1,5)` markings, and a six-vertex
exhaustive fusion completion control (67 positive, 12 negative).

## Additional tranche

`rank/summary.tsv` ranks the other 14 mixed cores by the larger of
the two residual counts and then by summed scanner CPU, keeping prior
capped cores 9 and 18 last. All 28 samples completed (198.37 CPU-s
including generation); up to 48 projections per first branch on
each end. Empty samples are not grounds for exclusion. In fact, the
three zero-residual pilots selected for exact work, 14, 10 and 11,
left respectively 1, 1 and 2 final IDs on the full sources. All
sample rows for this tranche byte-match their complete covers.

## Exact results

| Core | Projection orbits | Lift orbits | Projection-wide graph deaths | Other graph deaths | Fused deaths | Marked deaths after fusion | Four-window LRATs | Terminal CPU-s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 12 `G?opuK` | 9,850 | 52,202 | 43,012 | 8,663 | 472 | 39 | 16 | 53.78 |
| 14 `G?qrd_` | 14,502 | 54,742 | 41,373 | 12,375 | 974 | 19 | 1 | 52.92 |
| 10 `G?ovF_` | 27,093 | 110,296 | 84,331 | 24,671 | 1,215 | 78 | 1 | 100.23 |
| 11 `G?opv_` | 22,182 | 124,614 | 84,791 | 36,253 | 3,342 | 226 | 2 | 108.06 |
| **Total** | **73,627** | **341,854** | **253,507** | **81,962** | **6,003** | **362** | **20** | **314.99** |

The independent support binder matches every normalized projection
and lift. Contiguous scan shards merge and replay against the bytewise
cover; replay checks the graph cuts, fused contradiction, and marked
incompatibilities. For every exact final open ID, the binder regenerates
the **original** four-window CNF byte-for-byte (not strengthened by
fusion or marked isomorphism) and checks its CakeLRAT. Pilot proofs are
separate. Graph/marked/fused stages are hand + enum, not LRAT proofs.
Terminal CPU is census, independent binding, scans, receipt replay,
proof production and fresh binding/check; excludes pilots and small
split/merge operations. Tamper controls reject a wrong receipt ID
and wrong CNF bytes. Eleven mixed cores remain unclosed if these
four exclusions are accepted.

## Window memoization pilot (enum / estimate)

`memo_shared74.py` caches exact labelled `(lower, upper, alpha, edges)`
queries to the C prover, not the verifier or the semantics. Its small
window and six-vertex fusion controls pass, and a repeated fusion
control generates no query misses. On the four core-9/18 ranking
samples it produced byte-identical receipts; scanner CPU was
48.369 → 47.007 s (2.8% reduction, one run per sample), with memory
as high as about 71 MiB RSS. No worthwhile speedup demonstrated; keep
the existing scanner. No full run on 9 or 18.

## Replay

From `scratch/E/r10_shared`, using wall caps and `limited.sh` as in
`jobs.tsv` (set `n` and `key` to one of the four rows):

```sh
L=../../../ralph/lanes/E
sha256sum -c "freeze.$n.sha256"
python3 -B "$L/bind_shared74.py" "cover.$n.jsonl" --key "$key"
python3 -B "$L/order_shared74.py" replay "cover.$n.jsonl" "receipt.$n.jsonl"
python3 -B "$L/bind_shared74.py" "cover.$n.jsonl" --trace "todo.$n.jsonl" --proofs "proof.$n"
```
