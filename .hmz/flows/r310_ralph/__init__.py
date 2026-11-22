"""A many-lane Ralph loop on R(3,10), checked by the flow's own gate.

    hmz exec -f @local/r310_ralph -a worker=codex@soru/gpt-6.2-sol:high,critic=codex@soru/gpt-6.2-sol:high \
        -p budget.duration=48h "operator note"

Each round, every lane (A..H) gets a FRESH session with the same lane task (a Ralph loop per lane):
what one round leaves the next is the workspace only (ralph/lanes/<L>/STATE.md is the lane's memory).
The lanes run at the same time. After them a fresh critic session re-checks their claims and writes
directives (ralph/critic/LATEST.md) and the core split (ralph/ALLOC.md) for the next round.
Solver jobs are detached and outlive the turns. After each round the flow itself checks every new
graph6 file in ralph/found/ (is it a (3,10,40)-graph? two independent algorithms), holds the
workspace to its core and RAM caps, measures scratch disk, and commits the round to git. The next
round's prompts start with these verdicts, so no agent can fake a result.

A verified (3,10,40)-graph proves R(3,10) = 41; the flow then stops. R(3,10) = 40 needs a proof that
no such graph exists; that cannot be gated, so the lanes collect certified partial results.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

from pydantic import Field

from hmz.flows import (
    Agent,
    AgentCollection,
    Budget,
    BudgetExceeded,
    DurationExceeded,
    EnvCollection,
    FilesEnvMixin,
    FlowContext,
    FlowParams,
    HarnessDropped,
    HarnessError,
    HarnessThrottled,
    LocalEnv,
    SessionError,
    ShellEnvMixin,
    flow,
)

HERE = Path(__file__).parent
GATE = HERE / 'gate.py'
R = 'ralph'
LANES = {
    'A': 'Toolchain and certified SAT (the 99 open R(7) cubes)',
    'B': 'Gluing (t9 <= 88, then a faster gluer)',
    'C': 'Theory for the 9-regular case R',
    'D': 'New SAT encodings and splits for case R',
    'E': 'Automorphisms (the open (p, f) cases)',
    'F': 'Constructions: search for a (3,10,40)-graph',
    'G': 'Near-regular degree distributions N(e)',
    'H': 'Literature scout, claim ledger, Lean',
}
LIMIT = 6000  # characters of each lane's report that go into the critic's prompt and the round file
AGY_MODELS = ('gemini-', 'claude-')  # models that run through Antigravity (agy) via agentlink: ralph/bin/turn_agy.sh
# Idea scouts: a fresh session beside the lanes every few rounds; it reads only, then writes one idea file.
SCOUT_FOCUS = {
    'R': 'Case R (9-regular): the max-codegree sub-cases that are still open (read the latest ralph/rounds file '
         'and ralph/CLAIMS.md for what is closed). Lanes C and D.',
    'N': 'The open near-regular MTF degree distributions N(e) and the residue / gluing floors they depend on. '
         'Lanes B and G.',
    'G': 'The 41 side (a construction that could find a (3,10,40)-graph if one exists), the open symmetry cases, '
         'and any global method that would cut many open cases at once. Lanes E and F.',
    'T': 'Theory: a new structural lemma or counting argument, proved by hand and calibrated on a smaller known case, '
         'that removes a whole open block at once (Case R at low max codegree, or many N(e) distributions). '
         'Lanes C, D and G.',
}

HEADER = """# r310_ralph: round {round}, {who} (fresh session)

Now: {now}. The run started {started} and may last {hours} h. Plan to end this turn within
{minutes} minutes; the flow cuts it off {grace} minutes later. The next round starts at least
{gap} minutes after this round ends; detached jobs keep running in between.

## Flow verdicts (only these count)
- (3,10,40)-graphs verified by the flow (each one would prove R(3,10) = 41): {found}
- Core cap: {cores} busy solver processes for the WHOLE workspace (8 lanes share it; your lane's share
  is in {r}/ALLOC.md). The flow kills the newest beyond {kill}, and the newest while the RSS sum is
  over {mem} GB.
- Now: {count} busy solver processes, per lane {per_lane}; RSS {rss} GB; scratch {scratch} GB
  (cap {disk} GB; filesystem free {free} GB).
- Last round's checks:
```json
{gates}
```

"""
DRY_LANE = ('DRY RUN (a test of the flow; do no research; start NO solver). Do exactly this, then end the turn: '
            '1) Read {root}/AGENTS.md. 2) Append the line "dry run ok {lane}" to {root}/{r}/lanes/{lane}/STATE.md. '
            '3) Run `curl -sI https://github.com | head -1` and report the line. '
            '4) Run `touch <team-folder>/hmz_write_test_{lane}` and report whether it was refused, '
            'and remove the file if it was made. 5) Only lane A: copy {root}/{r}/.dry/not340.g6 to '
            '{root}/{r}/found/dry_A.g6. Report in 5 short lines.')
DRY_CRITIC = ('DRY RUN (a test of the flow; start NO solver). Read {root}/AGENTS.md, then write the file '
              '{root}/{r}/critic/LATEST.md with the single line "dry run ok critic", and report the lane '
              'statuses you were given in one line.')


class Workspace(LocalEnv, ShellEnvMixin, FilesEnvMixin):
    """The workspace the run was started in."""


class Agents(AgentCollection):
    """A worker takes each lane each round, and a critic checks the round; both fresh each time."""

    worker: Agent
    critic: Agent


class Envs(EnvCollection):
    """Everything happens in the workspace."""

    workspace: Workspace


class Params(FlowParams):
    lanes: str = Field(default='ABCDEFGH', description='The lanes that run, as letters A..H.')
    round_minutes: int = Field(default=60, ge=2, le=720, description='Minutes a lane turn should take; cut 15 min later.')
    critic_minutes: int = Field(default=30, ge=2, le=240, description='Minutes the critic turn should take; cut 10 min later.')
    gap_minutes: int = Field(default=10, ge=0, le=720, description='Minutes between the end of a round and the next.')
    stagger_seconds: int = Field(default=20, ge=0, le=600, description='Delay between the starts of the lane turns.')
    cores: int = Field(default=80, ge=1, le=192, description='Busy solver processes the workspace may run.')
    kill_factor: float = Field(default=1.25, ge=0, le=10, description='Kill the newest beyond this times the cap (0 = never).')
    mem_gb: float = Field(default=300, ge=0, description='RSS sum of workspace processes the flow allows (0 = no cap).')
    disk_gb: float = Field(default=150, ge=1, description='Scratch disk cap shown to the agents.')
    max_rounds: int = Field(default=0, ge=0, description='0 = until the budget is spent.')
    hours: float = Field(default=48, ge=0, description='Run length shown to the agents (set budget.duration too).')
    throttle_wait_minutes: int = Field(default=20, ge=1, le=600, description='Extra wait after a round in which every lane was throttled.')
    dry_run: bool = Field(default=False, description='A short test of the flow: no research, no solvers.')
    engine: str = Field(default='exec', description="'exec': each turn is a fresh `codex exec` through SoruxGPT "
                                                    "(ralph/bin/turn.sh); 'hmz': the worker/critic agents.")
    model: str = Field(default='gpt-6.2-sol', description="Model of the 'exec' engine.")
    effort: str = Field(default='high', description="Reasoning effort of lane turns ('exec' engine).")
    critic_effort: str = Field(default='high', description="Reasoning effort of the critic ('exec' engine).")
    lane_models: str = Field(default='D:gpt-6.2-astra,F:gpt-6.2-astra,critic:gpt-6.2-astra',
                             description="'exec' engine: model per lane or 'critic', as NAME:MODEL,...; others use model.")
    scout_every: int = Field(default=3, ge=0, description='Run idea scouts beside the lanes every N rounds (0 = never).')
    first_scout_round: int = Field(default=9, ge=1, description='The first round with idea scouts.')
    scouts: str = Field(default='R,N,T', description=f'Scout focuses, letters of {sorted(SCOUT_FOCUS)}.')
    scout_model: str = Field(default='gpt-6.2-astra', description="Model of the scouts ('exec' engine).")
    scout_models: str = Field(default='T:gemini-4-neon-xhigh',
                              description="Model per scout focus, as F:MODEL,...; 'gemini-*'/'claude-*' run through agy/agentlink.")
    referee_model: str = Field(default='claude-opus-5-5-high',
                               description="Model of the referee beside the lanes every round ('' = no referee).")
    referee_minutes: int = Field(default=45, ge=2, le=240, description='Minutes a referee turn should take; cut 10 min later.')
    scout_effort: str = Field(default='xhigh', description="Reasoning effort of the scouts ('exec' engine).")
    scout_minutes: int = Field(default=50, ge=2, le=240, description='Minutes a scout turn should take; cut 10 min later.')


async def gate(ws, *args, timeout=900):
    """Run one gate.py command in the workspace and return its JSON answer."""
    code, out, err = await ws.exec(['python3', '-I', str(GATE), str(ws.workdir), *map(str, args)], timeout=timeout)
    try:
        return json.loads(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {'error': f'gate {args[0]} exit {code}: {err.strip()[-400:]}'}


def now():
    return datetime.now().isoformat(timespec='seconds')


def clip(text, limit=LIMIT):
    text = str(text or '')
    return text if len(text) <= limit else text[:limit] + f'\n... ({len(text) - limit} more characters)'


@flow(agents=Agents, envs=Envs, params=Params, resumable=True)
async def r310_ralph(task: str, *, agents: Agents, envs: Envs, params: Params, ctx: FlowContext) -> str:
    """A many-lane Ralph loop on R(3,10), checked by the flow's own gate."""
    state = ctx.state
    assert state is not None  # noqa: S101 -- a resumable flow is always handed its state
    ws = envs['workspace']
    root = ws.workdir
    worker, critic = agents['worker'], agents['critic']
    lanes = [x for x in params.lanes.upper() if x in LANES]
    dry = params.dry_run
    minutes = 3 if dry else params.round_minutes
    cminutes = 3 if dry else params.critic_minutes
    grace, cgrace = (2, 2) if dry else (15, 10)
    gap = 0 if dry else params.gap_minutes
    kill = int(params.kill_factor * params.cores) or 'no'
    if 'started' not in state:
        state['started'] = now()
    found = state.get('found', [])
    last_gates = state.get('gates', {'note': 'first round of this run'})
    lane_fails = state.get('lane_fails', {})
    dead_rounds = 0
    models = {k.strip(): v.strip() for k, _, v in
              (part.partition(':') for part in params.lane_models.split(',')) if k.strip() and v.strip()}
    scout_names = [x for x in (s.strip().upper() for s in params.scouts.split(',')) if x in SCOUT_FOCUS]
    scout_models = {k.strip().upper(): v.strip() for k, _, v in
                    (part.partition(':') for part in params.scout_models.split(',')) if k.strip() and v.strip()}

    async def read(path, default=''):
        try:
            return (await ws.read(path)).decode(errors='replace')
        except Exception:  # noqa: BLE001 -- a missing task file is the operator's to fix; say so in the prompt
            return default

    async def exec_turn(prompt, limit, name, effort, model):
        """One turn as a fresh `codex exec` session (ralph/bin/turn.sh); its log stays in scratch/flow/turns."""
        base = f'scratch/flow/turns/r{state.get("round", 0) + 1:03d}_{name}'
        await ws.write(f'{base}.prompt', prompt.encode())
        minutes_ = max(1, int(limit.total_seconds() // 60))
        via_agy = model.startswith(AGY_MODELS)
        script = ['turn_agy.sh'] if via_agy else ['turn.sh']
        extra = [name] if via_agy else []
        code, _, err = await ws.exec(['bash', f'{R}/bin/{script[0]}', model, effort, str(minutes_),
                                      f'{base}.prompt', f'{base}.last', f'{base}.log', *extra],
                                     timeout=limit.total_seconds() + 300)
        said = await read(f'{base}.last')
        log_tail = (await read(f'{base}.log'))[-1500:]
        if code == 0 and said.strip():
            return 'ok', said
        if code in (124, 137):
            return 'cut', said or f'(the turn was cut off after {limit}; read its STATE.md)'
        if any(k in log_tail.lower() for k in ('429', 'rate limit', 'too many requests', 'quota')):
            return 'throttled', f'(no turn: throttled; exit {code}; log {base}.log)\n{log_tail[-600:]}'
        return 'failed', f'(the turn failed: exit {code}; log {base}.log; {err.strip()[-200:]})\n{log_tail[-800:]}'

    async def turn(agent, prompt, limit, delay=0, name='turn', effort='high', model=None):
        """One turn in a fresh session; returns its status and what it said."""
        if delay:
            await asyncio.sleep(delay)
        if params.engine == 'exec':
            return await exec_turn(prompt, limit, name, effort, model or models.get(name, params.model))
        started = time.monotonic()
        try:
            said = await agent.run(prompt, session=await agent.spawn(), env=ws,
                                   budget=Budget(duration=limit, graceful=False))
            return 'ok', said
        except DurationExceeded:
            if time.monotonic() - started < limit.total_seconds() * 0.95:
                raise  # the run's own deadline, not this turn's
            return 'cut', f'(the turn was cut off after {limit}; read its STATE.md)'
        except BudgetExceeded:
            raise
        except (HarnessThrottled, HarnessDropped) as error:
            return 'throttled', f'(no turn: {type(error).__name__}: {error})'
        except (HarnessError, SessionError) as error:
            return 'failed', f'(the turn failed: {type(error).__name__}: {error})'

    async def watch(stop, killed_log):
        """Every 5 minutes, during the turns and the gap, hold the workspace to its caps."""
        while not stop.is_set():
            try:
                await asyncio.wait_for(stop.wait(), timeout=300)
            except TimeoutError:
                seen = await gate(ws, 'cores', params.cores, params.kill_factor, params.mem_gb, timeout=120)
                if seen.get('killed'):
                    print(f'r310_ralph: killed {len(seen["killed"])} processes over the caps')
                    killed_log.extend(f"{p['why']}: {p['args']}" for p in seen['killed'])

    await ws.exec(['mkdir', '-p', f'{R}/found', f'{R}/rounds', f'{R}/critic', f'{R}/RECORD', f'{R}/referee',
                   'scratch/referee',
                   *[f'{R}/lanes/{x}' for x in lanes], *[f'scratch/{x}' for x in lanes]])
    while params.max_rounds == 0 or state.get('round', 0) < params.max_rounds:
        round_no = state.get('round', 0) + 1
        began = now()
        print(f'r310_ralph: round {round_no} begins ({began}), lanes {"".join(lanes)}')
        seen = await gate(ws, 'cores', params.cores, params.kill_factor, params.mem_gb, timeout=120)
        space = await gate(ws, 'disk', timeout=400)
        common = dict(round=round_no, now=began, started=state['started'], hours=params.hours, gap=gap,
                      found=found or 'none', cores=params.cores, kill=kill, mem=params.mem_gb, r=R,
                      count=seen.get('count'), per_lane=seen.get('per_lane'), rss=seen.get('rss_gb'),
                      scratch=space.get('scratch_gb'), disk=params.disk_gb, free=space.get('fs_free_gb'),
                      gates=json.dumps(last_gates, indent=1))
        task_common = await read(f'{R}/TASK_COMMON.md', f'(missing: {R}/TASK_COMMON.md)')
        note = f'\n\n## Operator note\n{task.strip()}\n' if task.strip() else ''
        last_scouts = state.get('scouts', {})
        if not dry and last_scouts.get('round') == round_no - 1 and last_scouts.get('files'):
            note += ('\n\n## Idea scouts of the last round (claims, not facts)\n'
                     f'Read the parts for your lane in {", ".join(last_scouts["files"])}. The critic put the best of '
                     'them into its directives; re-check any scout result before you build on it.\n')
        scouting = bool(params.scout_every and not dry and scout_names and round_no >= params.first_scout_round
                        and (round_no - params.first_scout_round) % params.scout_every == 0)
        scout_prompts = {}
        if scouting:
            brief = await read(f'{R}/SCOUT_TASK.md', f'(missing: {R}/SCOUT_TASK.md)')
            for s in scout_names:
                name = f'r{round_no:03d}_{s}'
                head = HEADER.format(who=f'idea scout {name}', minutes=params.scout_minutes, grace=10, **common)
                scout_prompts[s] = f'{head}{brief}\n\nYOUR_NAME: {name}\nFOCUS: {SCOUT_FOCUS[s]}\n'
        referee_prompt = ''
        if params.referee_model and not dry:
            rname = f'round_{round_no:03d}'
            rhead = HEADER.format(who=f'referee ({params.referee_model})', minutes=params.referee_minutes, grace=10,
                                  **common)
            referee_prompt = (f'{rhead}{await read(f"{R}/REFEREE_TASK.md", f"(missing: {R}/REFEREE_TASK.md)")}'
                              f'\n\nYOUR_NAME: {rname}\n')

        prompts = {}
        for x in lanes:
            head = HEADER.format(who=f'lane {x}: {LANES[x]}', minutes=minutes, grace=grace, **common)
            if dry:
                body = DRY_LANE.format(root=root, r=R, lane=x)
            else:
                lane_task = await read(f'{R}/lanes/{x}/TASK.md', f'(missing: {R}/lanes/{x}/TASK.md)')
                body = f'{task_common}\n\n{lane_task}{note}'
            prompts[x] = head + body

        killed_log = []
        stop = asyncio.Event()
        watcher = asyncio.create_task(watch(stop, killed_log))
        try:
            limit = timedelta(minutes=minutes + grace)
            scout_job = asyncio.gather(*(turn(worker, scout_prompts[s], timedelta(minutes=params.scout_minutes + 10),
                                              (len(lanes) + i) * params.stagger_seconds, name=f'scout_{s}',
                                              effort=params.scout_effort,
                                              model=scout_models.get(s, params.scout_model))
                                         for i, s in enumerate(scout_prompts)))
            referee_job = asyncio.gather(*([turn(worker, referee_prompt,
                                                 timedelta(minutes=params.referee_minutes + 10),
                                                 (len(lanes) + len(scout_prompts)) * params.stagger_seconds,
                                                 name='referee', effort=params.effort, model=params.referee_model)]
                                           if referee_prompt else []))
            results = await asyncio.gather(*(turn(worker, prompts[x], limit, i * params.stagger_seconds,
                                                  name=x, effort=params.effort)
                                             for i, x in enumerate(lanes)))
            status = {x: r[0] for x, r in zip(lanes, results)}
            said = {x: r[1] for x, r in zip(lanes, results)}
            for x in lanes:
                lane_fails[x] = 0 if status[x] == 'ok' else lane_fails.get(x, 0) + 1
            scout_results = await scout_job
            sstatus = {s: r[0] for s, r in zip(scout_prompts, scout_results)}
            ssaid = {s: r[1] for s, r in zip(scout_prompts, scout_results)}
            scout_files = [f'review/ideas/r{round_no:03d}_{s}.md' for s in scout_prompts]
            referee_results = await referee_job
            rstatus, rsaid = referee_results[0] if referee_results else (None, '')

            reports = '\n\n'.join(f'### Lane {x} ({status[x]})\n{clip(said[x])}' for x in lanes)
            if referee_prompt:
                reports += (f'\n\n## Referee ({params.referee_model}, {rstatus}), file '
                            f'{R}/referee/round_{round_no:03d}.md\nAn independent check of earlier claims by another '
                            'model family. Weigh each GAP against the files; reject or keep the claim and say why.\n\n'
                            + clip(rsaid, 4000))
            if scout_prompts:
                reports += ('\n\n## Idea scouts this round (claims, not facts)\nRead their files. Put the ideas that '
                            'deserve a test, with the calibration each needs, into the lane sections of LATEST.md; '
                            'append each dead end they measured as one line to review/ideas/TESTED.md.\n\n'
                            + '\n\n'.join(f'### Scout {s} ({sstatus[s]}), file {f}\n{clip(ssaid[s], 3000)}'
                                          for s, f in zip(scout_prompts, scout_files)))
            chead = HEADER.format(who='critic', minutes=cminutes, grace=cgrace, **common)
            if dry:
                cbody = DRY_CRITIC.format(root=root, r=R) + f'\nLane statuses: {status}'
            else:
                cbody = (await read(f'{R}/CRITIC_TASK.md', f'(missing: {R}/CRITIC_TASK.md)')) + note
            cstatus, csaid = await turn(critic, f'{chead}{cbody}\n\n## The lanes\' own reports this round '
                                                f'(claims, not facts: check them against the files)\n{reports}',
                                        timedelta(minutes=cminutes + cgrace), name='critic',
                                        effort=params.critic_effort)

            if all(s in ('throttled', 'failed') for s in status.values()):
                dead_rounds += 1
                if dead_rounds >= 3:
                    raise RuntimeError(f'r310_ralph: every lane failed in 3 rounds in a row; last: {said}')
            else:
                dead_rounds = 0
            rest = gap * 60
            if all(s == 'throttled' for s in status.values()):
                rest = max(rest, params.throttle_wait_minutes * 60)
            if rest > 0:
                await asyncio.sleep(rest)
        finally:
            stop.set()
            await watcher

        # The flow's own checks: nothing an agent writes can change these verdicts.
        scanned = await gate(ws, 'scan', timeout=3600)
        new = [c for c in scanned.get('checked', []) if c.get('valid_graphs')]
        for c in new:
            data = await ws.read(c['path'])
            name = Path(c['path']).name
            await ws.write(f'{R}/RECORD/{name}', data)
            found.append(f"{R}/RECORD/{name} (lines {c['valid_graphs']})")
            print(f'r310_ralph: VERIFIED (3,10,40)-GRAPH in {c["path"]}, lines {c["valid_graphs"]}')
        seen = await gate(ws, 'cores', params.cores, params.kill_factor, params.mem_gb, timeout=120)
        killed_log.extend(f"{p['why']}: {p['args']}" for p in seen.get('killed', []))
        gates = {
            'round': round_no,
            'verified_340_graphs': found,
            'graph_files_checked': [{'path': c['path'], 'valid_lines': c.get('valid_graphs'),
                                     'why': sorted({g.get('why', '')[:60] for g in c.get('graphs', [])})[:5]}
                                    for c in scanned.get('checked', [])],
            'solver_processes_now': seen.get('count'),
            'per_lane_now': seen.get('per_lane'),
            'rss_gb_now': seen.get('rss_gb'),
            'core_cap': params.cores,
            'killed_over_caps': killed_log[-30:],
            'lane_turns': status,
            'lanes_failing_in_a_row': {x: n for x, n in lane_fails.items() if n},
            'critic_turn': cstatus,
        }
        if scout_prompts:
            gates['scout_turns'] = sstatus
        if referee_prompt:
            gates['referee_turn'] = rstatus
        if 'error' in scanned or 'error' in seen:
            gates['gate_errors'] = [x['error'] for x in (scanned, seen) if 'error' in x]

        lane_text = '\n\n'.join(f'## Lane {x}: {LANES[x]} ({status[x]})\n{clip(said[x], 20000)}' for x in lanes)
        lane_text += ''.join(f'\n\n## Idea scout {s} ({sstatus[s]}): {f}\n{clip(ssaid[s], 6000)}'
                             for s, f in zip(scout_prompts, scout_files))
        if referee_prompt:
            lane_text += f'\n\n## Referee ({params.referee_model}, {rstatus})\n{clip(rsaid, 6000)}'
        await ws.write(f'{R}/rounds/round_{round_no:03d}.md',
                       (f'# Round {round_no}\n\nBegan {began}; ended {now()}.\n\n'
                        f'## Flow checks\n```json\n{json.dumps(gates, indent=1)}\n```\n\n{lane_text}\n\n'
                        f'## Critic ({cstatus})\n{clip(csaid, 20000)}\n').encode())
        await ws.write(f'{R}/STATUS.md',
                       (f'# r310_ralph status\n\nRound {round_no} done at {now()} (run started {state["started"]}).\n\n'
                        f'- (3,10,40)-graphs verified by the flow: {found or "none"}\n'
                        f'- Solver processes now: {seen.get("count")} (cap {params.cores}), per lane {seen.get("per_lane")}\n'
                        f'- Lane turns: {status}; critic: {cstatus}\n').encode())
        if found:
            await ws.write(f'{R}/RESULT.md',
                           ('# A (3,10,40)-graph, verified by the flow\n\n'
                            'Two independent checks (bitset search with a matching bound, and Bron-Kerbosch) agree: '
                            'the graph has 40 vertices, no triangle and no independent set of 10 vertices. '
                            'So R(3,10) >= 41, and with Angeltveit\'s R(3,10) <= 41, R(3,10) = 41.\n\n'
                            f'Files: {found}\n').encode())
        committed = await gate(ws, 'commit', round_no, 'r310_ralph', timeout=600)
        print(f'r310_ralph: round {round_no} done, lanes {status}, critic {cstatus}, '
              f'commit {committed.get("head")}, {seen.get("count")} solver processes')

        state['round'] = round_no
        state['found'] = found
        state['lane_fails'] = lane_fails
        state['gates'] = last_gates = gates
        if scout_prompts:
            state['scouts'] = {'round': round_no, 'files': scout_files}
        if found:
            return f'r310_ralph: a (3,10,40)-graph was verified in round {round_no}: {found}. R(3,10) = 41.'
    return f'r310_ralph ended after round {state.get("round", 0)}; no (3,10,40)-graph verified.'
