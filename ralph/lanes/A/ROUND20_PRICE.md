# Round 20 preregistered remainder price

At the end of the 12-input pilot (before running the other 106):

- Small control passed every literal/canonical comparison. The pilot used
  frozen one-based IDs `1,2,18,35,52,56,57,69,86,90,103,118`: every
  seventeenth source plus the last, the smallest and largest archive
  rooted buckets, and the first source at each extreme edge level.
- Pilot: 0.31 CPU-s expansion (peak 5,204 KiB), 3.73 CPU-s postcheck
  including complete archive rerooting. The 101 unrooted and 101 rooted
  keys match; the pilot includes all eight edge levels, including 5/5
  classes at 123 and 1/1 at 130. The slowest single expansion was 0.056 s.
- Project the tail at 2.74 CPU-s by the mean, 5.94 CPU-s at the observed
  maximum (estimates, not bounds); budget 12 CPU-s for final postcheck
  and about 35 CPU-s more including an end-to-end clean replay. No
  direct mass extrapolation beyond the 106 remaining sources. Budget
  4 MiB staging for live and clean artifacts; directive ceilings are
  one worker, 0.30 core-h, 1 GiB RAM, 128 MiB new scratch.
- Run the complementary IDs once, with no archived output keys as
  expansion inputs. Enforce time/RAM/file limits, validate every source
  receipt and both class sets, and halt with diagnosis on discrepancy.
