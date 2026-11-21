# r310_ralph: how to run and watch it

- Start (48 h): `./launch.sh` (detached: `setsid nohup ./launch.sh > scratch/flow/hmz.log 2>&1 &`).
- Test: `./launch.sh --dry-run`. Resume: `./launch.sh --resume`.
- Add Claude later: `ENGINE=hmz WORKER=claude/claude-opus-5-5:high CRITIC=claude/claude-opus-5-5:high ./launch.sh --resume`.
- Watch: `ralph/STATUS.md` (each round), `ralph/rounds/round_NNN.md` (lane and critic reports),
  `ralph/critic/LATEST.md`, `ralph/CLAIMS.md`, `ralph/BOARD.md`, `git log`; or `hmz web`.
- A verified (3,10,40)-graph: `ralph/RESULT.md` and `ralph/RECORD/`; the flow stops then.
- Stop: kill the `hmz exec` process; then `ralph/stop_jobs.sh` (list) and `ralph/stop_jobs.sh --kill`
  (the lanes' detached solver jobs outlive the flow).
- Caps: 80 busy solver processes (kill above 100), RSS 300 GB, scratch 150 GB (shown to agents).
- Agents: GPT-6.2-sol through SoruxGPT. Each turn is `codex exec` (ralph/bin/turn.sh; key read from the hmz
  account ~/.hmz/providers/codex/soru) under a Landlock write fence (ralph/bin/fence.py): the agents and
  their detached jobs can write only in this folder, /tmp, /var/tmp, ~/.cache and ~/.elan.
- Turn prompts and logs: scratch/flow/turns/rNNN_<lane>.{prompt,log,last}. Flow log: scratch/flow/hmz.log.
