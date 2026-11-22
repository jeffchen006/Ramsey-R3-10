# Lane A state

Round 13, November 22, 2026. Share 3; no live or stopped A jobs. No new
order-40 candidate, whole-distribution exclusion, or Case R closure.
Current replay: `ROUND13_REPLAY.md` and `scratch/A/panel13/round13.sha256`.
Rounds 10–12: `ROUND10_REPLAY.md`–`ROUND12_REPLAY.md`; earlier work in
`LOG.md` and prior replay files. R(7) was already closed by Lane C's
accepted finite certificates (round 1); A replayed them independently.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start / expected end, CET |
|---|---|---|---:|---|
| — | No detached A jobs | — | 0 | — |

Round-11 PIDs 790867/790884, 790868/790880, 790869/790883 rechecked gone.
Round 13 ran only sequential foreground checks with `nice -n 5`, per-run
wall/CPU bounds and a 16 GiB VM limit. Final replay including compilers
9.42 CPU-s; less than 0.004 CPU-h total with the initial control run.

## Results and claims

| Label | Scope/result | Evidence | CPU-h |
|---|---|---|---:|
| hand | In the cap-five marked `K4,4` 17/17 block, removing a single root from an anchor four-set admits just that root and its three private singletons (when it has three). The reverse packages restrict the same physical labelled 3×3 rectangle. Nonempty fixed point is necessary, not sufficient. | `ROUND13_REPLAY.md` | — |
| enum (independent audit) | 366 small aligned atlas entries, 3,194 small frames, and nonempty repeated rows pass. All 10 regular order-22 hosts: 2,118 oriented squares, 8,472 individual root lifts, 3,448 planted rectangles and 31,032 single-entry negatives. All 9,959 target atlas entries byte-match both scout files; all 55,055 labelled frame keys bind. | `audit_reciprocal_panel.cpp`, `scratch/A/panel13/{controls.log,target.atlas,slice.log}` | included below |
| hand + enum (scoped; pending critic) | For all 200 left triple-site frames, both shared identifications: 22,022,000 raw → 498,668 header → 77,498 forward → 17,604 reverse and local → 0 panel, exact per-ID/stage agreement. Also independently retained all 100 sampled held panel survivors (that check was not terminal). No conclusion about the unrestricted 17/17 complement, arbitrary bicliques, other orders or cap six. | `ROUND13_REPLAY.md`, `scratch/A/panel13/{slice.depths,ref.depths,id-disagreements.diff,held.depths,replay.log,round13.sha256}` | 0.00262 final replay |
| archived | A-021 and A-022 were confirmed on the named windows, now obsolete as strip work: the verified d6 floor kills every old e168/d6 parent. No more e168 reroot, ID maps, matching or proof binding. | `ralph/critic/round_012.md`, `ROUND12_REPLAY.md` | prior |

## Next

- C/H/critic have the exact receipts via `ralph/BOARD.md`. C owns the disjoint
  1% pilot and any production after repricing; A did not start either.
- If asked to cross-check the pilot later, reuse the bound atlas and frame
  roster; the replay executable's optional input is a whitespace list of
  zero-based `left right flip` IDs. Never infer joint filling from a panel pass.
- Scout N's order-33 completion was already consumed by the critic (floor
  122 at MTF d6; 238 near-regular distributions plus R at round opening).
  No round-12 T handoff was delivered. Wait for the next lane directive;
  do not restart the retired e168 work or the old R(7) cube queue.
