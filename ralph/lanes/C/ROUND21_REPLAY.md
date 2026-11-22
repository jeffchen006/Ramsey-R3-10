# Round 21 — shared physical core degree budget, toy only

**Hand, pending.** For disjoint singleton groups of physically labelled
deletion cards, sum the minimum *additional* degree of each card at the
same core site. The sum cannot exceed the site's target degree less all
already prescribed incidences. Keep every admissible physical
restoration; choosing one isomorphism is not sound. See
`proofs/panel21_shared_core_budget.md` for the argument and both fixtures.

**Enum, toy only, pending.** The two order-13 fixtures have the same
labelled scaffold, target degree four, triangle constraint and global
independence cap four. With two independent poles the card cap is three.
Exactly five core–singleton edges per card follow from total degrees in
both fixtures, independently of the test. The strict fixture forbids
`4–12`; the plant allows it, changing no other pin. The strict fixture
admits a triangle-free 4-regular degree-only completion (alpha five), and
both of its cards are separately restorable even with the exact
five-edge counts. However, every restoration of card `0` needs the
additional edge `6–8`, and every restoration of card `2` needs an
additional edge at `6`. Only one degree slot remains at this vertex after
counting `6–1`, `6–11`, and `6–5`. The one-pin positive is planted by
`C13(1,5)` with alpha four; its actual cards use zero and one added edges
at `6`. Counting the pinned `6–5` a second time would reject the plant.

| Fixture | Pole | Valid local restorations | Of these, exactly five edges | Min. *added* at site `6` |
|---|---|---:|---:|---:|
| Plant | `0` | 8 | 4 | 0 |
| Plant | `2` | 30 | 18 | 1 |
| Strict | `0` | 2 | 2 | 1 |
| Strict | `2` | 30 | 18 | 1 |

`panel21_budget_toy.py` checks all `2^12` masks of the local cross-edges
per fixture and card (16,384 masks), with fixed labels throughout.
For each mask reaching the independence/triangle check, literal
vertex-subset checks are compared with the hand row criterion. Degree
upper checks include fixed incidences outside the current card. Exact
minima agree whether or not the five-edge restriction is used, and
site `6` is the only overload. The checker first validates the complete
positive and both induced cards, then the strict scaffold's full
degree-only witness and separate local witnesses. No catalogue input.

Production and clean replay logs match byte-for-byte (0.35 CPU-s each,
peak RSS 10,316 KiB under 256 MiB VM). Including the 0.03 CPU-s initial
toy fixture check: **0.73 CPU-s / 0.00020 core-h** total, one worker.
Replay from the workspace root:

```bash
sha256sum -c ralph/lanes/C/ROUND21_FREEZE.sha256
(
  cd scratch/C/r21/clean
  ulimit -v 262144
  nice -n 5 timeout 5s prlimit --cpu=4:4 -- python3 -B \
    ../../../../ralph/lanes/C/panel21_budget_toy.py | cmp clean.log -
)
```

**Stop:** No target inputs, pairs, bins, signed joins, candidate, or
case/ID debit. The toy is a strictness result, not a target forecast.
No jobs running. Critic review requested; H may formalize the short
finite disjoint-edge counting step if it is useful and fits priorities.
