# Round 12 — one-sided reciprocal 22-window census (November 22, 2026)

No candidate and no closure of R, R(5), or the full 22/20 case.
All runs limited to one core at a time (ceiling five). About **0.11
CPU-h** in measured runs and **38 MiB** new scratch at freeze. `S/`
below is `scratch/C/r12/`.

## Local mark census — enum

The 191 all-graph order-22 hosts have valid graph6, independent number
at most six and pairwise nonisomorphism checked in round 10. They are
complete by the published catalogue count (D-C7). The census was
calibrated by reproducing all 395 earlier planted width-four marks
from the ten 6-regular order-22 controls. A higher minimum union must
not keep those marks. On the full catalogue the 13-union `(row,Z)`
keys and their multiplicities match `r10/fixed22.tsv` byte-for-byte.

| Union of B masks | Markings | New status in this round |
|---:|---:|---|
| 12 | 278,160 | Previously excluded (22/22); do not count again. |
| 13 | 7,791,069 | Already excluded by confirmed C-033 (22/21). |
| 14 | 26,793,207 | Local only, including 1,307 tight 2/2/2 with triple intersection two. |
| 15 | 34,865,505 | Local only. |
| 16 | 21,884,678 | Local only. |
| 17 | 5,252,073 | Local only. |
| 18 | 391,873 | Local only. |

The floor alone retains **89,187,336** marks in **19,397,413 distinct
(row,Z) cards** across all 191 hosts. Profile-specific card totals
are not additive when distinct intersection types share one card.
`S/census.hist` gives all 15 nonempty exact profile counts, and
`S/census.hosts` gives the per-host census. The independently written
common-pair/petal generator `reciprocal_r12_tight_check.cpp` matched
all 1,307 literal tight keys (not just their totals), with 391 distinct
cards across 129 hosts. The census spent 62.55 CPU-s; the separate
tight enumerator spent 0.02 CPU-s (timings in `S/`).

## One-sided reroot test — hand + enum

One physical assignment of the common two sites' neighbourhoods is
shared across all reroots. The circulant C24(1,4,6,11) (8-regular,
α=8, maximum codegree six) is a five-common-site positive control in
two labellings. All 1,307 actual tight marks survived: 54,582 orbit
representatives, 54,384 live, 162 upper domination contradictions,
36 independent-set contradictions on the B-rooted window, none from
other triples. The pilot cost prediction was 251 CPU-s, the full
run 267.79 CPU-s, under 15 MiB RSS. See `S/reroot.full.log` and
`S/reroot.full.reroot`. No fitted data enter the classification.

## Necessary opposite-window projection — hand + enum + local cert

The identity `e(P) = e(F_A) − 45` for the 12 sites seeing A and
not B lets the full degree demand couple the two windows without an
order-20 catalogue. The projection is on the fixed overlap and
the twelve sites only. It uses full deficits on the overlap,
bounded deficits on the other sites, exact `e(P)`, and domination
by each of the five fixed six-sets after attaching the two extra
common sites. Its SAT result is merely a local projection.

Pinned positive C24 projections model-check in both labellings;
deleting a chosen projected edge while keeping all other pins has
dual LRAT in both. The 12-key dispersed pilot tested two keys per
edge count 15–20: eight hit the 500-iteration cap (bins 15–18),
and four received dual LRAT (two each in bins 19 and 20). That
cost 10.12 CPU-s. No conclusions about the other wings in bins
15–19. Then all **324 e20 keys** (9 exact marks, 36 wings each)
were discharged, 25.69 CPU-s for production plus the original
dual checks. Independent key binding, prefix reconstruction,
2,285 cap-axiom checks and 648 fresh dual-check runs cost 18.43
CPU-s. `S/projection-dense/projection.jsonl` binds every CNF and
LRAT by hash. All nine tight marks with `e(F_A)=65` are excluded;
the remaining 1,298 local tight marks have `e(F_A)≤64`. The same
391 `(row,Z)` cards and 129 hosts need not shrink just because
some marks do: this cut removes 3 cards and 3 hosts **in the tight
subfamily** (none of rows 8, 10, 28 has another tight mark outside the
dense slice). This is not a claim about cards aggregated over other
intersection types. Proof: `proofs/reciprocal_r12.md`.

## Replay

- `bash ralph/lanes/C/replay_reciprocal_r12.sh verify` binds hashes,
  independently rebuilds the tight keys, audits all covered
  assignments/clauses and rechecks both LRAT checkers. Allow 100
  seconds on a busy host. `census` instead reproduces the full
  local census and old card counts in lane scratch.
- Original one-sided upper journal is regenerateable from the tight
  keys using `reciprocal_r12_reroot.py`; the dense proof tranche from
  that journal with `reciprocal_r12_projection.py --dense-only`.
  See `ROUND12_PLAN.md` for commands/limits. Round 11's journals and
  receipts are untouched.
