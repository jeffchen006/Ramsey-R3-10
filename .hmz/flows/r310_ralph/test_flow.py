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
        if argv[:2] == ['bash', 'ralph/bin/turn.sh']:
            calls.append(argv)
            return (0, '', '') if 'critic' in argv[5] else (124, '', '')
        return None

    files = {'ralph/TASK_COMMON.md': 'COMMON RULES', 'ralph/CRITIC_TASK.md': 'CRITIC TASK',
             'ralph/found/g.g6': 'graph\n'}
    files |= {f'ralph/lanes/{x}/TASK.md': f'LANE TASK {x}' for x in 'ABC'}
    return fakes.FakeEnvDriver(files, workdir='/ws', run=run)


async def test_lanes_and_critic_fresh_each_round():
    worker = fakes.FakeAgentDriver(reply='lane report')
    critic = fakes.FakeAgentDriver(reply='critic report')
    ws = workspace([[{'path': 'ralph/found/x.g6', 'valid_graphs': [], 'graphs': [{'why': 'n = 39, not 40'}]}], []])
    said = await fakes.run_fake('r310_ralph', 'NOTE', local=ws, agents={'worker': worker, 'critic': critic},
                                params={'max_rounds': 2, 'gap_minutes': 0, 'stagger_seconds': 0, 'lanes': 'ABC', 'engine': 'hmz'})
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
                                params={'max_rounds': 5, 'gap_minutes': 0, 'stagger_seconds': 0, 'lanes': 'AB', 'engine': 'hmz'})
    assert 'R(3,10) = 41' in said
    assert ws.text('ralph/RECORD/g.g6') == 'graph\n'
    assert 'R(3,10) = 41' in ws.text('ralph/RESULT.md')
    assert len(worker.sessions) == 2                                 # one round only


async def test_dry_run_prompts():
    worker = fakes.FakeAgentDriver()
    critic = fakes.FakeAgentDriver()
    ws = workspace([])
    await fakes.run_fake('r310_ralph', '', local=ws, agents={'worker': worker, 'critic': critic},
                         params={'max_rounds': 1, 'dry_run': True, 'stagger_seconds': 0, 'lanes': 'AB', 'engine': 'hmz'})
    assert all('DRY RUN' in p and 'LANE TASK' not in p for p in worker.prompts)
    assert 'hmz_write_test_A' in worker.prompts[0]
    assert 'DRY RUN' in critic.prompts[0]


async def test_exec_engine_runs_turn_script_per_lane_and_critic():
    TURNS.clear()
    worker, critic = fakes.FakeAgentDriver(), fakes.FakeAgentDriver()
    ws = workspace([[]])
    await fakes.run_fake('r310_ralph', '', local=ws, agents={'worker': worker, 'critic': critic},
                         params={'max_rounds': 1, 'gap_minutes': 0, 'stagger_seconds': 0, 'lanes': 'AB',
                                 'effort': 'medium', 'critic_effort': 'xhigh'})
    assert not worker.sessions and not critic.sessions             # the hmz agents are not used
    assert [c[5].rsplit('_', 1)[1] for c in TURNS] == ['A.prompt', 'B.prompt', 'critic.prompt']
    assert TURNS[0][2:5] == ['gpt-6.2-sol', 'medium', '75'] and TURNS[2][3] == 'xhigh'
    assert 'COMMON RULES' in ws.text('scratch/flow/turns/r001_A.prompt')
    text = ws.text('ralph/rounds/round_001.md')
    assert '(cut)' in text and '## Critic (failed)' in text        # no last message = failed, not ok
