# Round 13 — independent, disjoint cap-five 17/17 pilot

**Status: hand + enum on the bound pilot, plus a runtime estimate.** The
pilot does not close the general 17/17 stream, R(5), or R. No new SAT proofs
were generated. The round-12 cap-five 22/20 dense cut is confirmed separately
in `ralph/critic/round_012.md`; it was not an input to this pilot.

## Bindings and controls

- `proofs/reciprocal_panel17.md` proves the labelled restoration and the
  necessary transpose/terminal tests. An actual assignment gives a fixed
  package across *all* its rectangles. The panel test only requires a
  match in each opposite domain; the later joint test really chooses one
  compatible package from every domain.
- A's independently built audit (source snapshot `scratch/C/r13/audit_A.cpp`)
  confirms the 55,055 physical frame entries one by one; no unseen frame
  in its inventory, no duplicate reference entry. Its 9,959 multisets
  byte-match both the directly enumerated and catalogue-lift scouts'
  atlases. Per-host counts: 1,499 / 1,574 / 2,214 / 1,290 / 2,887 / 223 / 272.
  The smaller order-11 atlas also matches all 366 entries. Of A's 2,118
  squares in the ten smaller regular graphs, all 8,472 root restorations
  preserve their physical window. A and C accept 3,448 physical 3×3
  rectangles and reject their 31,032 single-bit mutants. C's terminal
  propagation preserves the 2,118 planted partial graphs.
- ID is `(left frame line, right frame line, Z-bijection bit)`, with
  zero-based IDs and no exchange quotient. Header grouping uses both
  host IDs, each oriented signature `(private degree total, Z edge,
  first Z degree, second Z degree, Z codegree)`, and the bijection bit.
  Out of 157,472,001 passing headers, remove 498,668 left-triple and
  496,536 right-triple-only IDs. The latter are within the old left
  slice after side exchange, whose inverse bijection has the same bit.
  The 2,132 IDs with both triple sites are included in the left count.
- Regenerate all header-pass IDs of the scout's three original draws:
  519,387 / 5,210 / 301 in seeds 147031 / 6035 / 441703. The 301 IDs
  match the saved roster byte-for-byte; all archived scout panel survivors
  occur in the regenerated 523,968 distinct IDs. Remove all these and
  their reversals (1,039,243 IDs after triple removal). Neither the old
  triple slice nor any of these proposals can overlap the pilot.
- This leaves 155,437,554 fresh ordered IDs in 366 strata. Within each
  stratum visit IDs lexicographically by `(left,right)`; for every block
  of 100 consecutive fresh ranks take one deterministic mixed offset
  (include the final truncated block only if its offset falls inside).
  Selected: 1,554,349 IDs, 0.99998% of the fresh pool and 0.9871% of the
  preliminary count. A second Python census checks the stratum products,
  exclusions, sample size per stratum and all IDs for uniqueness and no
  overlap. The ordered pilot itself contains 7,955 side-reversal pairs
  and 265 self-inverse IDs, reported rather than treated as invariant
  classes. See `pilot.strata` and `pilot.audit.log` in `scratch/C/r13`.

## Matched results

| Stage | Prior left-triple replay | Fresh 1% pilot |
|---|---:|---:|
| Preliminary headers / submitted IDs | 498,668 | 1,554,349 |
| Forward signatures | 77,498 | 519,077 |
| Both signatures | 17,604 | 197,579 |
| Both local row domains | 17,604 | 197,502 |
| Iterated transpose support | 0 | 327 |
| At least one simultaneous filling | 0 | 97 |
| Not rejected by cheap terminal checks | 0 | 0 |

Two separate scanners agree on the **stage of each ID**, not only totals.
The 230 panel survivors without a joint choice have zero simultaneous row
fillings. The other 97 have 1,869 joint fillings: 213 degree contradictions,
322 codegree contradictions, 1,334 independent ten-sets even in the upper
graph, no triangle-only result and zero open. C's C++ terminal and the
scout's Python terminal agree on the complete per-ID count vector, even
though C starts from domains reduced by panel propagation and the scout
reconstructs whole pre-panel domains. Max fillings per ID: 384. No claim
that unprocessed IDs have this same outcome, and no graph was produced.

## Cost and stop gates

`scratch/C/r13/*.time` records user, system, wall, peak KiB. C buffered
screen: 5.85 CPU-s for the fresh pilot (5.89 wall); A independent screen:
6.79 CPU-s. C terminal: 0.35 CPU-s, including setup; per-ID CPU-ms median,
p95, p99, maximum 0.753 / 1.887 / 2.441 / 9.239 on the first C run.
Scout terminal independent repeat: 13.18 CPU-s; per-ID values 27.152 /
67.979 / 202.147 / 553.587 ms. Roster construction traversed all header
pairs without screening them, in 21.45 CPU-s. The unnecessary unbuffered
stage dump cost 28.95 CPU-s; the final buffered implementation produces
the same full stage manifest.

The reduction in terminal calls is 197,502 / 327 = **604×**; this is not
a measured end-to-end speedup. With ~101.3× the pilot's inputs, the observed
mean rates price a streamed full C pass at ~0.18 CPU-h, both scanners and
C terminal at ~0.38 CPU-h, or ~0.75 CPU-h also repeating projected terminal
survivors in Python. This assumes equivalent densities, no heavy unseen
tails and an inline or chunked roster (do not dump a full ID stream into
`ralph/`). It is reasonable to reserve 1–2 CPU-h for an independently
replayed finite scan before any proof work. Use bounded shards keyed by
left frame range, print all nonterminal IDs, and reprice after the first
complete shard before increasing the queue. In the pilot all three gates
pass: >100× fewer calls, price <3 CPU-h, and 0/327 open after cheap checks.
No full run was launched. Only the cap-five 17/17 biclique marking is
priced; no implication for 16/17, cap six, or absence of a biclique.

## Replay

From the repo root: `bash ralph/lanes/C/replay_panel17.sh CALLER_OWNED_EMPTY_WORKDIR`.
The command checks frozen inputs, builds both scanners, reruns all listed
controls and the old draw reconstruction, generates the stratum table,
replays both scopes and reconciles the terminal receipts. Stable hashes
are in `ROUND13_INPUTS.sha256` and `ROUND13_RESULTS.sha256`. Timing is not
part of the digest. The scout Python replay uses the checked graph-class
inputs, not SAT or an independence heuristic. Runtime is an estimate;
the finite pilot results are `enum`, not `cert`.
