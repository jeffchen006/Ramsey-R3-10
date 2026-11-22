# `h=5`: calibrated next-defect experiment (pending critic)

Only after both complementary `h=6` units checked and the whole cover reconciled, tested the next defect. The row proof is `rows/e170_folded_three_defect.md`. The total 286/184,488/156,112 (representatives/labelled boards/weak keys) agrees with the prior Burnside census. Independent catalogue and physical generation agree on zero strict order-17 placements; all 1,960 relaxed labelled placements, 218 classes, and 936 board/class incidences match the folded encoder on all 80 smaller boards. Both modes use the new peer-contact Hall rows with their own forbidden size.

| Board | Deficits | Solve CPU-s | Raw bytes | Checked compressed bytes | Result |
|---:|---|---:|---:|---:|---|
| 0 | triple deficits on both crossed anchors | 0.03 | 1,633 | 566 | dual checked |
| 110 | repeated/split | 9.07 | 42,642,010 | 12,473,588 | dual checked |
| 285 | separated on both shores | 99.88 | 322,240,512 | — | CPU resource cap under `prlimit`, no proof claim |

Pilot 110 generation+rebind used 11.26 CPU-s and dual check 5.06 CPU-s. The hard pilot is already close to the raw proof cap at the CPU cutoff. A rate reference for 283 boards at pilot 110 is ~2.0 core-h and ~3.53 GB compressed, **not a tail forecast**. The staged queue covers all 283 unattempted boards (excluding hard pilot 285, which stays open for a split). At most 70.75 solver core-h by limits (900 CPU-s each), 320 MiB live raw per worker, 5 GiB VM, 4 GiB archive guard in this stage, 100 GB filesystem floor. Combined with the finalized `h=6` archive, 20 live raw files, and logs/formulas, the worst planned logical staging is below 14 GB. Worker stops on archive/binding error; every capped, unstarted, or unverified attempt stays open. Invalid-at-cap raw proofs are discarded only after recording both check outcomes, size and hash. Outer timeouts bound the queue to 5 h. No whole adjacent-root or degree-distribution debit is implied.
