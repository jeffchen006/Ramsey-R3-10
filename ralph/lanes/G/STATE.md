# Lane G state — round 13, November 22, 2026

**238 near-regular MTF distributions plus R remain open.** No candidate.
The critic's confirmed MTF d6 residue floor 122 removes exactly
20 e168 + 19 e169 + one e170 `(2,7,0,31)` from the 278-key ledger.
This round reproduced those removals, and found 12 new conditional
t9 improvements; no further whole-key exclusions. All ten old U88
keys are unchanged. Floor 123 is not proved, even with the e170 pin.

## Jobs

| PID | Command | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| — | No active or detached G jobs | `scratch/G/round13/` | 0 | — | — |

Prior PIDs 3268364 (B-middle) and 3475785 (static replacements) were
absent on entry; archived round-12 scopes are superseded by floor 122.
Foreground one-core runs only this round, with per-command timeouts,
16 GB virtual-memory cap and nice +5. At e170 there were still only
96 one-/two-root signature rows; no census or proof-production queue.

## Results and claims

| Label | Result | Evidence | User CPU-h |
|---|---|---|---:|
| hand + cert | Reconstruct 238 keys (same identities as critic); 39 direct floor cuts and one exact parity LP cut, all already confirmed. 12 **new** rational t9 thresholds, one edge each, with floors 108/97/88 and d6=122. No U88 increment or new closure; all 12 matched floor-120 relaxations numerically feasible at the new pins. | `scratch/G/round13/{thresholds.csv,multipliers.jsonl,t9.log,t9.binding.log}`, `round13_thresholds.py`, `ROUND13_REPLAY.md` | 0.014 |
| hand + enum | e170 equality: 66 single-root signature rows and 30 paired rows all have exact integer points; one paired 4-s cap resolved on retry. The paired model joins both masks and degree on the same W sites, not W-edge identities. C13: 26 literal pairs survive; 260 broken swaps rejected. No graph and no distribution closure. | `rows/e170_equality_signatures.md`, `scratch/G/round13/{single,pair}.witnesses.jsonl`, `*.replay.log` | 0.052 |
| hand + enum | Same-source held-out attachment comparison: N's support deletion rules reject all 512 distinct sampled e122 residues (128+384) in 16.62 CPU-s. Old clique+5k pinned core leaves 20 caps; 235 old-core UNSAT are unchecked. Bundling lowers waves but gives no new rejection and costs 17.90 s. Independent replay of 24 samples ×3 modes; actual 13 C13 equality attachments retained. No census or new floor. | `rows/e170_bundled_demands.md`, `scratch/G/round13/{attach,held}.*`, `ROUND13_REPLAY.md` | 0.044 incl. audit |

## Next round

- H/critic: independently bind the 12 *conditional* t9 receipts and
  retain gluing premises. Do not subtract these from 238. Across the
  sixteen e170 d6 keys, nine have one root and seven an adjacent pair.
- For e170, `Z=48`, `e(H)=122`, 24 private/9 double sites. Adjacent
  roots have a shared order-28 core W, exactly one wing crossing,
  and `e(W)=86`; the old e168 e84 strips or holes do not apply.
  Any next pair experiment needs a stronger joint condition on
  **edges** of W or independently complete coverage, not increasing
  MIP caps on the 96 already explicitly feasible relaxations.
- The old scout support rule on fixed supplied rows is stronger than
  the priced old clique/core route; do not repeat the more costly
  bundled variant absent a case where the scout rule leaves rows.
  The named e122 inputs used here are partial. Do not launch a broad
  e122 proof queue without an independently complete cover.
- Stop all mixed e168 A/B/matching work and do not rediscover e121
  classes. B owns descent to 32/e108. `review/ideas/r012_T.md` was absent
  (referee/T failed). R's reciprocal panel concerns C, not this lane.
- Historical round-12 claim, matching identities, and proofs remain
  in `ROUND12_REPLAY.md` and `ROUND12_FREEZE.sha256`; not additive.
