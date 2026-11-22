# Lane C — round 16, November 22, 2026

**No candidate. R and R(5) remain open.** Completed only the one-neutral
cap-five `K4,4` 16/17 *pilot*. Of A's **15,051,526,031** distinct labelled
headers, 544 were checked and have no joint package assignment; exact
untested frontier **15,051,525,487**. No production. The literal path
capped on 8 pilot IDs, all checked separately by both filtered and
independent indexed joins. No extrapolation is a proof or a tail bound.

## Results / claims for H and critic

| Label | Scope | Evidence | CPU-h |
|---|---|---|---:|
| hand, pending | In the explicit marked one-neutral premise, ordered 16/17 windows have 15/16 private sites, singleton shapes `2233/2333` and `2334/3333/3334`; the physical cover and first-witness cache key are necessary. All groups of sizes 2,3,4 are used. | `proofs/panel16_cover.md`, A's `ROUND16_ONE_NEUTRAL.md` | — |
| hand + enum, pilot only | 544 headers (16 in each of 34 shape/key strata, largest and weak shapes covered); 497 with a provably empty individual domain, 47 with all 8 nonempty but no join. Independent Python checks one full empty domain per empty ID and all domains plus exact join for 47. Eight 10M-probe literal caps are not used as rejections. Two native paths plus independent 153 smaller plants / 1,596 keyed joint assignments; 306 one-direction flips and 612 locally valid crossing conflicts rejected. Clean replay matches. | `ROUND16_REPLAY.md`, `ROUND16_FREEZE.sha256`, `scratch/C/r16/{summary.log,audit.log,controls.fills,pilot.stats}` | <0.087 incl. timing trials |
| estimate, no production | Whole direct C++ pilot 2.60 CPU-s with atlas, independent 166.99 CPU-s. Weighted warm estimates 11,400 core-h all-domain filtered; 4,348 core-h combining exact preflight with measured survivor work, not an integrated runtime. Independent Python replay ~1.84M core-h by same weights. Terminal target timing and unseen tails unpriced. | `scratch/C/r16/summary.log`, `ROUND16_REPLAY.md` | included |
| prior confirmed, round 15 | C-039/40: all 17/17 marked headers closed. 92,341,930 direct and 65,130,071 through exchange, including both neutral bits and all diagonals. Only the two-neutral case. | `ROUND15_REPLAY.md`, `ralph/critic/round_015.md` | prior |
| prior confirmed, rounds 11–12 | Cap-five K3,3 22/21 impossible; order-22 window with the three opposite codegrees five has ≤64 edges. 1,298 tight marks remain; full upper-only reroot retained all. | `ROUND{11,12}_REPLAY.md`, `ralph/critic/round_{011,012}.md` | prior |
| prior frozen, rounds 1–9 | R(7) excluded; R(6) no P4 and P3 diagonal bounds. R(6) f*=9 (12,12) impossible with 1,134 CakeLRAT; (12,14) smaller private K12 has 16≤e≤21, 24/39 profiles open. Diagonal-four P3 8/8: 34/105 zero patterns contradicted (90 rows excluded); 71 patterns and 330 rows open. | `ROUND{4,5,6,7,8,9}_REPLAY.md`, `ralph/critic/round_{001,003,004,005,006,007,009}.md` | prior |

## Jobs

**None active or detached.** Final independent audit ran in
`scratch/C/r16` at 12:04–12:07 Europe/Zurich, one core slot:
`nice -n 5 timeout 540 prlimit --cpu=420:430 /usr/bin/time -o audit.time -f '%U %S %e %M' python3 -B ../../../ralph/lanes/C/panel16_audit.py audit ../../../gluing/val/r3_6_16.g6 ../../../gluing/val/r3_6_17.g6 cases.tsv pilot.fills pilot.stats 9 5 9 4 --screen --timing`.
Logs `scratch/C/r16/audit.{log,err,time}`. The foreground exec completed
normally. Short compiler/replay work overlapped only within two core
slots; all jobs were foreground. Per-process VM cap 512 MiB; retained
545 KiB across the pilot and rebuild. Round-15 scheduler PIDs from the
previous state are gone. No SAT wave, no output to `ralph/found/`.

## Next

1. H/critic: ledger only the cover/cache lemmas and measured pilot scope.
   H may formalize the private sizes, the slot shapes, or invariance of
   package existence under permutations of row demands. None implies
   full one-neutral exclusion.
2. Do not run the 15B per-header scan. If authorized, price a separate
   weighted compatibility quotient by destination host/neutral and
   source multisets of group-demand vectors. Count both directions
   exactly before any join, and preserve exact physical singleton
   labels at the join. Scalability and independent audits remain open.
3. Do not rescan 17/17 or treat 15/17, 16/16, cap six, or R(5) as closed.
