# Lane H — round 9 handoff, November 22, 2026

Share two cores. No H candidate, live jobs, or new distribution
subtraction. Critic checked through round 008: **278 near-regular
MTF distributions plus Case R**, **10 conditional U88 keys**, and
**20 open e168 degree-six keys** (11 single-root, 9 paired). These
are distinct scopes. Round-9 producer claims below are pending.

## Jobs

| PID | Command | Log | Cores | Start / finish CET |
|---|---|---|---:|---|
| — | No live, detached or stopped H job. | — | 0 | — |
| foreground, ended | pinned `build_private_signature.sh` targeted and integrated `build --old R310`, two `env lean -j1 -s8192` axiom runs and `check_axioms.py` | `scratch/H/round9-{kernel-lean-first,kernel-lean,integrated,targeted,project,axiom-audit}.log` | 1 | ~01:51–01:58 |
| foreground, ended | `python3 -SB ralph/lanes/H/check_round9_semantics.py` | `scratch/H/round9-semantics.log` | 1 | 02:00, 1.17 wall-s final run |

Pinned Lean/Mathlib v4.35.0 with the existing local cache. The two narrow
initial attempts failed on neighbour membership/substitution; final
integrated build and both axiom audits passed. No Mathlib source build,
SAT, bulk source regeneration, or LRAT replays in H this round.

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean, H-019 | If all oriented simple P6s in the current edge kernel have first/fifth codegree three, the two overlapping triple masks and high `a,d` imply high `c,d`. No L=6 coverage or LRAT formalization. 2 targeted / 286 project axiom reports pass. | `lean/R310/KernelReroot.lean`, `LEAN_REPRO.md`, `scratch/H/round9-axiom-audit.log` | ~0.052 including failed starts |
| hand + enum, H-019 audit | Reconstructed both orientations of four profiles 2298/2386/2424/2431 **as of the first 18 D refutations**. All eight oriented first/fifth codegrees are three. Smaller C22 has 22 positive and 456 premise-drop negative placements. | `ROUND9_REVIEW.md`, `check_round9_semantics.py`, `scratch/H/round9-semantics.log` | included below |
| hand + enum, A-015 audit | Mixed e168 `(2,7,4,27)`, `j=3,δ(T)=3`: weak order-26 source transports both mark orientations and gives all 7,166 ordered roles (5,438 matching, 1,728 middle). Independent exact roles and deficits 4/3, cut 3/3/4, cap 87. No production closure asserted by source. | `ROUND9_REVIEW.md`, `scratch/H/round9-semantics.log`, `scratch/A/strip9/mixed.j3.source.log` | <0.001 combined |
| hand + enum, G-032 audit | Same pin, mixed noncross d9 at `j=5` only: both retained holes checked, exact 5/1/3 X cut, full role-key and receipt-ID equality. Both orientation/shape loops evaluated; 162 matching and zero middle survive. H did not replay proofs. | `ROUND9_REVIEW.md`, `scratch/H/round9-semantics.log`, `scratch/G/round9/mixedfull.bound/certificates.tsv` | included above |
| open | No new usable literature premise imported; no repeat of round-8 catalogue refetch. | `LIT.md` | — |

## Ledger and next steps

- Round 008 imported: terminal G-029/A-013/E-023 with exact scopes,
  C's two layouts vs pattern cuts, B prefix only and separate 1,142 e108
  keys (124 missing), D global L=6 only, F unsigned cyclic quotient only.
  G c1 uses 32 non-eager originals and 17,162 eager CNFs; A uses all eager.
  A's 42 eager pilots include the alternatives for those 32. Do not mix hashes.
- Pending H-019, A-015/G-032 and E-024 recorded. E reports one more named
  core via 2,519→14→0 and the 14 independent proofs. D's new star-graft
  L=6 result was provisional when H stopped; import the final claim only
  with its replay and no change to L≥7. Keep G's j=3 proof production
  separate from the covered source until all receipts and gaps are bound.
- Best supported route remains marked windows with a cheap necessary
  filter and independent coverage. A reports the joint pure alternate-pivot
  caps are redundant at δ(T)≥4 under exact signatures; do not commission
  that high-min proof queue on this hope alone. Continue on G's exact mixed
  tranche, E's matched single-core pilots and D's audited conditional grafts.
- Next round: import critic verdicts, handle any new production claims at
  their actual scopes; formalize a short exact C/G lemma if assigned. No
  additional cores or source data needed by H.
