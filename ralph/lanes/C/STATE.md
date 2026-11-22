# Lane C — round 18, November 22, 2026

**No candidate. R, R(5), and the full one-neutral 16/17 branch remain
open.** In the marked cap-five `K4,4` 16/17 window cover, just the two
shape slices `(D16,d16;shape16,shape17)=(67,5;2333,3334)` and
`(68,4;2333,3334)` have no completion (`hand + enum`, pending critic).
The denominators are **32,340 and 28,301** labelled headers. Exactly
46 and 24 pass both margins; all have incompatible package joins.
One already failed in round 16: **69 newly tested**. If accepted,
**2,542,514,376** both-pass headers elsewhere are still joint-untested.

## Results / claims for H and critic

| Label | Scope | Evidence | CPU-h |
|---|---|---|---:|
| hand, pending | Exact row-union independent-set witness bitmap; signed crossing matrices use original order-16 rows and order-17 columns (transpose in reverse). Arc deletion preserves any joint tuple. Independent signed-mask join is exhaustive. | `proofs/panel18_signed_join.md` | — |
| hand + enum, pending scoped exclusions | C independently rebound all 70 headers to A's ordered hosts, neutrals, masks, singleton labels, and crossing axes. All 12,762 exact marginal query bits and all 11,250 weighted host products match A; each ID matches all eight literal domain sizes and both join checks. 70/70 arc-empty; no C++ literal cap or independent indexed cap. Zero compatible tuples, no target terminals. 32 old marginal overlaps, one old joint overlap `(2501780,31298)`. | `ROUND18_REPLAY.md`, `scratch/C/r18/{summary.log,keyed.tsv,marginal-target.log,audit-target.log}`, A's `ROUND18_PHYSICAL_IDS.md` | 0.05673 native + independent target stages (first successful pass) |
| enum, calibration | 153 marked 6/7 plants, 1,596 jointly compatible assignments (20 triangle/1,576 live at terminal), both one-direction flips rejected on each plant. 2,067 small marginal predicates and 29,220 host products. Extra 1,485 literal four-row demand controls (23 positive), since physical 6/7 groups have size at most 3. | `scratch/C/r18/{audit-controls.log,bound-control.log,marginal-bit-control-final.log}` | <0.001 |
| enum, replay | All 16 replay comparisons pass (12 byte-identical, four after removing timing). All A round-18 pins verify. Total measured CPU includes both passes and the failed marginal attempt. Peak checker RSS 99,248 KiB. | `ROUND18_FREEZE.sha256`, `scratch/C/r18/{clean.compare.log,budget.log,A.freeze.log}` | 0.13740 cumulative |
| confirmed, round 17 | C-042 `(71,5)` zero forward, 35,458,804 labelled headers excluded. C-043 independently arithmetic-bound 2,542,514,492 / 15,051,526,031 both pass, prior 47 joint failures. Do not count marginal rejects again as new joint failures. | `ROUND17_REPLAY.md`, `ralph/critic/round_017.md` | prior |
| prior confirmed | C-039/40 exclude two-neutral 17/17 (92,341,930 direct + 65,130,071 by exchange). Cap-five K3,3 22/21 impossible, 1,298 tight e≤64 local marks open. Prior R(7), R(6) no-P4, and marked `f*=9`/diagonal-four results are in successive frozen replay notes. | `ROUND{4,5,6,7,8,9,11,12,15}_REPLAY.md` | prior |

## Jobs

**No active or detached jobs.** First exact joint and marginal stages
completed normally; the earlier straight Python marginal attempt
stopped at its 45 CPU-second cap and is not evidence. Clean foreground
replay wrapper PID 3431924, one worker at a time, ran from ~14:42:56 to
~14:46:56. Exit 0, PIDs checked gone.
`bash ralph/lanes/C/replay_panel18.sh <root>/scratch/C/r18-clean <root>/scratch/A/r18`.
Stage logs in `scratch/C/r18-clean/`; 512 MiB VM, `nice` and `timeout`
plus per-stage CPU caps. No detached jobs.

## Next

1. Critic: check the two separate labelled shape exclusions. They do
   not exclude either whole degree key, all one-neutral windows, or R(5).
   H may formalize the finite signed-overlap/arc-deletion implication if useful.
2. Do not scan 2.54B survivors. If authorized, the next smallest nonzero
   shape `(69,5;2333,2334)` has 159 both-pass of 593,219 raw (before
   old-pilot subtraction). Maintain original IDs and price the new slice
   with its own sample; do not use this round as a rate across strata.
