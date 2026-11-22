# Round 20 — one-double footprints, complete marginal census

**Hand + enum (pending critic review).** In the construction with one exceptional site, the unchanged parity test excludes **3,172 of 3,581** previously unseen exterior footprints with exactly one doubled contact. The new cuts include **646 of 1,018** tested footprints that can also occur as a marked endpoint; these are not additional cuts. Counting the prior pilot once, **3,274 of 3,709** one-double representatives are excluded; **435 remain open**, including 391 marked. No target signing or graph was sought, and no unrestricted degree or symmetry case is closed.

## What was verified

The scope is the 17 ordinary pairs of `ROUND19.md`: single perfect matchings at absolute differences 6..12, no other inter-pair edges, arbitrary verticals. One physical vertex contacts both ends at exactly one site. Exclusion follows from an independent ten forced on those 34 ordinary vertices, optionally using that one vertex. This local statement applies in either role. Row reversal transports it, without assuming a target graph has that symmetry.

The producer and physical verifier, quotient, support bank and eight-pass limit are unchanged. All round-19 pins were verified before production. Rebuilt small controls retained all 240 valid exterior configurations of 33,480 and all 72 valid marked configurations of 66,960, including the marked `C8(1,4)` positive (gate OK). All nine control traces and cut lists matched byte-for-byte. Five small corruptions and both frozen pilot mutations, including the wrong physical pin, were rejected. `scratch/F/r20/{calibrate,tamper,corrupt_pin,hashes}.stdout`.

`preflight.stdout` establishes that 128 prior pilot representatives plus 3,581 unseen are disjoint and exhaust the frozen domain, with canonical masks, unique physical keys and correct reversal weights. Only the unseen rows went to the producer. `pilot.rows` in the **r20** directory is the verifier's input name; its content is **r19/unexamined.rows**. The 26 open pilot rows were not rerun. The independent physical GF(2) verifier replayed 50,877 deductions (244 without padding; 33,550 using the exterior or marked vertex; 17,083 using both ends of the doubled site). Every one of the 3,581 rows has a checked outcome: 3,172 contradictions, 409 open. See `scratch/F/r20/{pilot.trace,pilot.checked,verify.stdout}`. `strata.tsv` records original size, pilot size/cuts, unseen size/cuts, and total left for each of the 117 original strata.

| Role | New cuts: reps / labels / fixed | Full cuts: reps / labels / fixed | Full open: reps / labels / fixed |
|---|---:|---:|---:|
| Exterior | 3,172 / 6,339 / 5 | 3,274 / 6,542 / 6 | 435 / 859 / 11 |
| Marked subset | 646 / 1,291 / 1 | 659 / 1,317 / 1 | 391 / 771 / 11 |

## Joint price (not graph realizations)

Repricing from the **post-pilot** baseline gives **15,613,661 → 1,979,210** unsigned joint headers, a **net reduction of 13,634,451**. A pair consists of one marked footprint and one exterior footprint, quotiented by a *simultaneous* reversal. The marked cut accounts for 7,874,417 headers and the exterior cut for 11,697,486; subtract their intersection of 5,937,452 once. Both role orders give the same orbits; fixed-only inventories, per-multiplicity Burnside and inclusion/exclusion agree. See `scratch/F/r20/{price.stdout,joint.tsv}`.

| Incidence multiplicity | Post-pilot orbits | Remaining labelled headers | Simultaneous fixes | Remaining orbits |
|---:|---:|---:|---:|---:|
| 0 | 11,132,320 | 2,919,285 | 1,147 | 1,460,216 |
| 1 | 3,903,704 | 889,124 | 478 | 444,801 |
| 2 | 577,637 | 148,340 | 46 | 74,193 |

The full remaining inventories `pole.left` and `mark.left` contain 1,137 and 668 representatives respectively. By number of doubled sites (0, 1, 2, 3) these split as (264, 435, 412, 26) and (263, 391, 14, 0). `one-double.open` lists all 435 exact unresolved masks. No other stratum was re-tested.

## Resources and next decision

`scratch/F/r20/forecast.txt`: 6.41 CPU-s forecast for unseen producer row work; actual whole producer 2.43 CPU-s, physical verification 0.96 s, price 0.39 s. All 19 metered invocations returned zero; total 7.16 CPU-s (0.00199 core-h), peak RSS 168,676 KiB (compiler), about 2.1 MB new scratch. One sequential worker; no active or stopped jobs. Replay entry point for a fresh empty lane scratch directory: `bash ../../../ralph/lanes/F/round20_replay.sh`; it checks the prior freeze. `ROUND20_FREEZE.sha256` binds this run. Historical nearness only: 24 independent tens on degree-valid examples with 178 and 179 edges; no new score.

**Request, not run:** restrict the next pilot to the **14** two-double rows in the remaining marked roster (also exterior). There are two known absent verticals; the four doubled endpoints are neighbors of the same vertex and hence independent. A new witness may pad a six-site transversal by all four endpoints, excluding both doubled sites and all their quotient neighbors. Keep the old singleton, pole and individual-pair modes with exact physical pins. First calibrate on a positive with two doubled sites (e.g. `K2,4` at target five), a negative with forced padding, exhaustive small configurations and corrupted physical-double controls. One worker, ≤0.02 core-h and 512 MiB; book only checked cuts. No 412-row sweep, three-double run, signing, or revisit to open rows requested.
