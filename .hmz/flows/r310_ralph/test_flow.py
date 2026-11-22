"""Tests of r310_ralph on stand-in agents and a stand-in workspace.

    cd R310-hmz && uvx --with hmz==0.2.1 --with pytest-asyncio pytest -q -o asyncio_mode=auto \
        --import-mode=importlib -p no:cacheprovider .hmz/flows/r310_ralph/test_flow.py
"""

import json

from hmz.sdk import fakes

TURNS = []


def workspace(scans):
    """A fake workspace whose gate.py answers from a script: one scan result per round."""
    scans = list(scans)
    calls = TURNS

    def run(command, env):
        argv = list(command) if not isinstance(command, str) else command.split()
        if argv[0] == 'mkdir':
            return 0, '', ''
        if 'gate.py' in ' '.join(argv):
            what = argv[4]
            if what == 'scan':
                return 0, json.dumps({'checked': scans.pop(0) if scans else []}), ''
            if what == 'cores':
                return 0, json.dumps({'count': 5, 'per_lane': {'A': 5}, 'rss_gb': 1.0, 'killed': []}), ''
            if what == 'disk':
                return 0, json.dumps({'scratch_gb': 1.5, 'fs_free_gb': 300}), ''
            if what == 'commit':
                assert argv[6] == 'r310_ralph'
                return 0, json.dumps({'committed': True, 'head': 'abc123'}), ''
        if argv[:2] in (['bash', 'ralph/bin/turn.sh'], ['bash', 'ralph/bin/turn_agy.sh']):
            calls.append(argv)
            return (0, '', '') if 'critic' in argv[5] else (124, '', '')
        return None

    files = {'ralph/TASK_COMMON.md': 'COMMON RULES', 'ralph/CRITIC_TASK.md': 'CRITIC TASK', 'ralph/SCOUT_TASK.md': 'SCOUT TASK',
             'ralph/REFEREE_TASK.md': 'REFEREE TASK',
             'ralph/found/g.g6': 'graph\n'}
    files |= {f'ralph/lanes/{x}/TASK.md': f'LANE TASK {x}' for x in 'ABCD'}
    return fakes.FakeEnvDriver(files, workdir='/ws', run=run)


async def test_lanes_and_critic_fresh_each_round():
    worker = fakes.FakeAgentDriver(reply='lane report')
    critic = fakes.FakeAgentDriver(reply='critic report')
    ws = workspace([[{'path': 'ralph/found/x.g6', 'valid_graphs': [], 'graphs': [{'why': 'n = 39, not 40'}]}], []])
    said = await fakes.run_fake('r310_ralph', 'NOTE', local=ws, agents={'worker': worker, 'critic': critic},
                                params={'max_rounds': 2, 'gap_minutes': 0, 'stagger_seconds': 0, 'lanes': 'ABC', 'engine': 'hmz', 'referee_model': ''})
    assert said == 'r310_ralph ended after round 2; no (3,10,40)-graph verified.'
    assert len(worker.sessions) == 6 and len(critic.sessions) == 2   # fresh every turn
    assert sum('LANE TASK A' in p for p in worker.prompts) == 2
    assert all('COMMON RULES' in p and 'NOTE' in p for p in worker.prompts)
    assert all('CRITIC TASK' in p and 'lane report' in p for p in critic.prompts)
    assert 'n = 39, not 40' in [p for p in worker.prompts if 'round 2' in p][0]
    assert 'lane report' in ws.text('ralph/rounds/round_001.md')
    assert 'none' in ws.text('ralph/STATUS.md')


async def test_a_verified_graph_ends_the_run():
    worker = fakes.FakeAgentDriver(reply='lane report')
    critic = fakes.FakeAgentDriver(reply='critic report')
    ws = workspace([[{'path': 'ralph/found/g.g6', 'valid_graphs': [1], 'graphs': [{'why': 'ok'}]}]])
    said = await fakes.run_fake('r310_ralph', '', local=ws, agents={'worker': worker, 'critic': critic},
                                params={'max_rounds': 5, 'gap_minutes': 0, 'stagger_seconds': 0, 'lanes': 'AB', 'engine': 'hmz', 'referee_model': ''})
    assert 'R(3,10) = 41' in said
    assert ws.text('ralph/RECORD/g.g6') == 'graph\n'
    assert 'R(3,10) = 41' in ws.text('ralph/RESULT.md')
    assert len(worker.sessions) == 2                                 # one round only


async def test_dry_run_prompts():
    worker = fakes.FakeAgentDriver()
    critic = fakes.FakeAgentDriver()
    ws = workspace([])
    await fakes.run_fake('r310_ralph', '', local=ws, agents={'worker': worker, 'critic': critic},
                         params={'max_rounds': 1, 'dry_run': True, 'stagger_seconds': 0, 'lanes': 'AB', 'engine': 'hmz', 'referee_model': ''})
    assert all('DRY RUN' in p and 'LANE TASK' not in p for p in worker.prompts)
    assert 'hmz_write_test_A' in worker.prompts[0]
    assert 'DRY RUN' in critic.prompts[0]


async def test_exec_engine_runs_turn_script_per_lane_and_critic():
    TURNS.clear()
    worker, critic = fakes.FakeAgentDriver(), fakes.FakeAgentDriver()
    ws = workspace([[]])
    await fakes.run_fake('r310_ralph', '', local=ws, agents={'worker': worker, 'critic': critic},
                         params={'max_rounds': 1, 'gap_minutes': 0, 'stagger_seconds': 0, 'lanes': 'AB',
                                 'effort': 'medium', 'critic_effort': 'xhigh', 'referee_model': ''})
    assert not worker.sessions and not critic.sessions             # the hmz agents are not used
    assert [c[5].rsplit('_', 1)[1] for c in TURNS] == ['A.prompt', 'B.prompt', 'critic.prompt']
    assert TURNS[0][2:5] == ['gpt-6.2-sol', 'medium', '75'] and TURNS[2][3] == 'xhigh'
    assert 'COMMON RULES' in ws.text('scratch/flow/turns/r001_A.prompt')
    text = ws.text('ralph/rounds/round_001.md')
    assert '(cut)' in text and '## Critic (failed)' in text        # no last message = failed, not ok
    assert TURNS[2][2] == 'gpt-6.2-astra'                           # the critic's model from lane_models


async def test_models_per_lane_and_scouts_beside_the_lanes():
    TURNS.clear()
    worker, critic = fakes.FakeAgentDriver(), fakes.FakeAgentDriver()
    ws = workspace([[], []])
    await fakes.run_fake('r310_ralph', '', local=ws, agents={'worker': worker, 'critic': critic},
                         params={'max_rounds': 2, 'gap_minutes': 0, 'stagger_seconds': 0, 'lanes': 'AD',
                                 'scout_every': 2, 'first_scout_round': 1, 'scouts': 'R,N,T',
                                 'referee_every': 1, 'first_referee_round': 1})
    names = [c[5].rsplit('/', 1)[1] for c in TURNS]
    assert sorted(names) == sorted(['r001_scout_R.prompt', 'r001_scout_N.prompt', 'r001_scout_T.prompt',
                                    'r001_referee.prompt', 'r001_A.prompt', 'r001_D.prompt', 'r001_critic.prompt',
                                    'r002_referee.prompt', 'r002_A.prompt', 'r002_D.prompt', 'r002_critic.prompt'])
    agy = {c[5].rsplit('/', 1)[1]: c for c in TURNS if c[1] == 'ralph/bin/turn_agy.sh'}
    assert sorted(agy) == ['r001_referee.prompt', 'r001_scout_T.prompt', 'r002_referee.prompt']
    assert agy['r001_referee.prompt'][2] == 'gemini-4-neon-high' and agy['r001_scout_T.prompt'][2] == 'gemini-4-neon-xhigh'
    assert agy['r001_scout_T.prompt'][8] == 'scout_T'
    assert 'REFEREE TASK' in ws.text('scratch/flow/turns/r001_referee.prompt')
    assert 'ralph/referee/round_001.md' in ws.text('scratch/flow/turns/r001_critic.prompt')
    assert names.index('r001_critic.prompt') > max(names.index(f'r001_{n}.prompt') for n in ('A', 'D', 'scout_R'))
    model = {c[5].rsplit('/', 1)[1]: c[2] for c in TURNS}
    assert model['r001_A.prompt'] == 'gpt-6.2-sol' and model['r001_D.prompt'] == 'gpt-6.2-astra'
    assert model['r001_scout_R.prompt'] == 'gpt-6.2-astra' and model['r001_critic.prompt'] == 'gpt-6.2-astra'
    assert 'SCOUT TASK' in ws.text('scratch/flow/turns/r001_scout_R.prompt')
    assert 'YOUR_NAME: r001_R' in ws.text('scratch/flow/turns/r001_scout_R.prompt')
    assert 'FOCUS: Case R' in ws.text('scratch/flow/turns/r001_scout_R.prompt')
    assert 'review/ideas/r001_N.md' in ws.text('scratch/flow/turns/r001_critic.prompt')
    assert 'review/ideas/r001_R.md' in ws.text('scratch/flow/turns/r002_A.prompt')   # next round points the lanes
    assert 'Idea scout R' in ws.text('ralph/rounds/round_001.md') and '## Referee' in ws.text('ralph/rounds/round_001.md')


async def test_referee_every_third_round():
    TURNS.clear()
    worker, critic = fakes.FakeAgentDriver(), fakes.FakeAgentDriver()
    ws = workspace([[], [], [], []])
    await fakes.run_fake('r310_ralph', '', local=ws, agents={'worker': worker, 'critic': critic},
                         params={'max_rounds': 4, 'gap_minutes': 0, 'stagger_seconds': 0, 'lanes': 'A',
                                 'scout_every': 0, 'referee_every': 3, 'first_referee_round': 2})
    referees = sorted(c[5].rsplit('/', 1)[1] for c in TURNS if 'referee' in c[5])
    assert referees == ['r002_referee.prompt']                       # rounds 2, 5, 8, ...
