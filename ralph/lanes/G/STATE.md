# Lane G state — round 19, November 22, 2026

**238 near-regular MTF distributions plus R remain open.** No candidate,
distribution cut, `t9`, U88, or residue-floor change. The accepted
marked `e170` adjacent d6 equality `h=8` roster was **79,072** in 12
schemes after confirmed `middle+middle.2` and scout leaf receipts.
One round-19 shared-grid **middle** LRAT excludes **57,947** of these in
six schemes locally; pending critic, **21,125** remain, all in the six
`matching+matching` schemes. `h=7`: 51/1,213 two-sided context orbits
checked from scout, 1,162 open; no new solve.

## Jobs

| PID | Command | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| — | No active or detached G jobs | `scratch/G/round19/` | 0 | — | — |

One sequential foreground slot, nice +5, ≤512 MiB virtual, the single
target solver ≤30 CPU-s. None capped, stopped or killed. Previous
checkpoint PID 3361393 remains gone.

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| hand + enum + cert (local, pending critic) | Marked `e170` adjacent d6 equality with `h=8`, fixed left middle, any right after permitted shore swap: 724-variable/23,733-clause formula rebound and LRAT accepted by both checkers, twice; aligned 24/0 and one-defect 129/11 calibrated on exact canonical class sets. 107,772 historical IDs in scope; exact 57,947 new after overlap, leaving 21,125. | `ROUND19_REPLAY.md`, `rows/e170_shared_middle.md`, `ROUND19_FREEZE.sha256`, `scratch/G/round19/{physical.tsv,crosswalk.json,middle.cnf,middle.lrat,review.log}` | 0.00854 all-in |
| enum (planning only) | `h=7` orbit accounting matches 51/1,213 checked. Eight dispersed untargeted fixed-left contexts frozen (six boards, preserving and flipping stabilizers, including asymmetric boards); they could add 184 distinct two-sided context orbits if all eight pass. No inference from unrun pilots. | `ROUND19_PREREG.md`, `scratch/G/round19/h7-prereg.json` | included |
| estimate + measured | Scout leaf used as initial price; observed 1.44 solver CPU-s, 30.73 CPU-s all-in including clean repeat, 10,058,455 bytes target CNF+LRAT, ~29.5 MiB apparent peak scratch, ~19.3 retained, peak 134,516 KiB RSS. | `scratch/G/round19/{baseline.time,solve.time,target.time,review.time}` | included |

## Handoff

- H/critic: please review and, if confirmed, debit exactly **57,947**
  from the accepted 79,072. Remaining exact labelled ranks are in
  `scratch/G/round19/outstanding-if-verified.json`. No overlap is new
  credit; no `h<8`, U88 or distribution consequence. Clean review
  command in `ROUND19_REPLAY.md` reuses the receipt without solving.
- Next subject to authorization: only the remaining fixed-left
  `matching` shape at `h=8`, before any fixed-ID sweep; independently
  bind the six scheme selectors to their exact residual ranks. For
  `h=7` use the eight preregistered pilots only under separately
  approved bounds. Never use 51/81 or extrapolate two scout timings to
  `h≤6`. No other target runs this round.
- At e170, sixteen degree-six keys remain (nine single, seven adjacent
  pair). `Z=48`, e(H)=122, 24 private and nine double sites; adjacent W
  has 28 sites, one wing crossing and 86 internal edges. No complete
  order-33/122 cover. Round-13 exact t9 thresholds and membership remain
  in `ROUND13_REPLAY.md` and its freeze. The 32/e108 project is lane B's.
