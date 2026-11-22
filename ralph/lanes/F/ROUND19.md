# Round 19 — one doubled site: pilot only

**hand + enum, pending critic review.** On the 17 untouched sites of the one-exceptional-site construction, a physical parity checker rejects 102 of 128 sampled exactly-one-double exterior footprints. These are 203 labelled footprints, including one reversal fix. Of 32 sampled footprints also allowed as a marked endpoint, 13 are rejected (26 labels, zero fixes). They are a subset, not extra cuts. The other 26 pilot rows are **open**. No result is inferred for the 3,581 untested representatives. No signing, joint-header scan, order-40 graph, or unrestricted exclusion.

## Why the same receipt works in both roles

Keep the simple matchings on pairs of physical sites 1..17 at absolute differences 6..12. Let p be the exterior vertex, or *one* of the exceptional endpoints. Relabel each singly contacted site's endpoints so p sees bit 0. On the doubled site d, p sees **both** 0 and 1, in either naming. Thus the d-vertical is absent by triangle-freeness. If a contacted site were adjacent in the quotient to d, its contacted endpoint would meet one of d's two neighbors of p, giving a physical triangle. Between two singly contacted sites a matching cannot join their zero endpoints. These facts do not extend to another pole or the mate of p; we do not use either. In particular, there is no premise about a polar edge in the unexamined part of the graph.

Write `s_ij` for the XOR between bits of unmatched ends. Physical triangle-freeness on a quotient triangle imposes zero sum of the three `s`, and two singly contacted sites give `s_ij=0` when joined. A support of distinct singly selected sites has an independent transversal iff its endpoint bits satisfy `x_i XOR x_j = s_ij` on its induced matchings. Three ways to build the independent ten:

| Mode | Physical vertices adjoined | Legal singleton support and pins |
|---|---|---|
| 0 | none | 10 sites, no pins; d is allowed as one vertex |
| 1 | p | 9 sites excluding d entirely; only bit 1 survives at a contacted singleton |
| 2 | both ends of d | 8 other sites, excluding **every** quotient neighbor of d; no pins, **no p** |

Mode 2 uses a known *absent* vertical. It does not add verticals elsewhere. The unit inference is in original edge coordinates: if every consistency equation for a transversal already follows, the footprint fails; if all nontrivial equations are equal modulo prior rows, avoiding this ten forces their opposite. All other supports are left undecided. The producer uses component paths; the independent checker builds physical eligible endpoint sets, then eliminates the `x_i` directly in a separate GF(2) implementation. Quotient input diagonal ones are parser placeholders, never input constraints on actual verticals. Reversal (j to 18−j) transports the physical argument without assuming it is an automorphism of a signed graph.

## Denominators, controls and pilot

Input: round 18's `widemark.left` and `widepole.left`; 3,709 distinct one-double exterior reps, 1,050 of those eligible as marked endpoints. Stratification by original physical d, reversal fix, number of physical contacts (2..9) and marked membership produces **117 nonempty strata**. Pick minimum SHA-256 per stratum, then 11 more by global hash without replacement. Although the canonical representative never has d at physical label 12 or 13, their reflected orientations are accounted for. All 68,068 size-8/9/10 singleton masks and an eight-pass limit frozen before the pilot. `scratch/F/r19/{freeze.stdout,strata.tsv,pilot.rows,forecast.txt}`. No target no-double row was solved.

* Literal calibration used all eight simple three-site quotients and a four-site square, all matching parities, all site vertical choices (including forbidden ones), all labelled singleton contacts, exactly one double; tested both arbitrary exterior and mirrored marked roles. All 240/33,480 valid exterior and 72/66,960 valid marked physical configurations survived. The positive `C8(1,4)` with ordered labels `1,4,2,3,7,6,0,5` physically exhibits a double, both pole neighbor masks (19,35), and passes the small flow gate. Five corrupt small receipts and two target mutations failed verification. See `newcalib.stdout`, `positive.gate`, `newtamper.stdout`, `mutation.stdout`.
* Independent physical check: 2,050 steps (14/1,495/541 by modes 0/1/2); 102 contradictions, 26 unresolved. `pilot.trace`, `pilot.checked`, `pilotcheck.stdout`, `outcomes.tsv`. After this pilot the one-double exterior stratum has **3,607** reps (26 tested-open + 3,581 unseen), the marked subset **1,037**. All round-18 survivors in other strata remain untouched.

## Actual joint impact (price only)

Filter both role inventories by the same 102 physical cuts. Exterior reps 4,411 → 4,309 (8,576 labels, 42 fixed); marked reps 1,327 → 1,314 (2,596 labels, 32 fixed). Count compatibility by bitsets in either role order. For each incidence multiplicity the old minus new price is:

| Multiplicity | Labelled removed | Simultaneous reversal fixes removed | Orbits removed | Orbits remaining |
|---:|---:|---:|---:|---:|
| 0 | 755,242 | 32 | 377,637 | 11,132,320 |
| 1 | 310,921 | 7 | 155,464 | 3,903,704 |
| 2 | 71,437 | 5 | 35,721 | 577,637 |

Thus **16,182,483 → 15,613,661**, a reduction of **568,822** unsigned joint headers. Inclusion/exclusion gives 164,423 from the marked column plus 408,621 from the exterior column minus 4,222 in both. No graph realization is counted here. See `detailprice.stdout`, `joint.tsv`. Clean rebuild in `scratch/F/r19clean` reproduced 58 deterministic artifacts plus freeze and price logs. To reproduce from an empty folder under `scratch/F/`, run `bash ../../../ralph/lanes/F/round19_replay.sh`.

## Cost and decision

Pilot producer 0.39 CPU-s, verifier 0.12 s; mean producer time per populated stratum weighted by its actual population estimates **6.66 CPU-s** of row work for 3,709 (6.41 s for the 3,581 unseen). Allow indexing and 3.5 s for verifier (linear from the pilot), and ~0.5 s for arithmetic: **about 11 CPU-s per full run**, roughly 27 s with a clean rebuild, controls and independent repeat. One sample per small stratum is imprecise: substituting the largest measured row time everywhere gives 44.52 s producer-only, not a bound. Runtime extrapolation only; **no extrapolated cuts or success rate**. `pilotrun.stdout`, `cost.stdout`, `*.time`.

Request one worker, 512 MiB, ≤0.04 core-h next round for the **3,581 unseen** with the unchanged bank, checker, arithmetic and clean replay. Reuse the 128 pilot receipts. Do not pursue the 26 tested-open rows, remaining 264 no-double rows, or any joint signing without a separate decision. This round: 13.09 recorded CPU-s (0.00364 core-h), max RSS 168,660 KiB across timed commands, no surviving PID or candidate. Old empirical nearness unchanged at 24 independent tens on degree-valid 178/179-edge graphs.
