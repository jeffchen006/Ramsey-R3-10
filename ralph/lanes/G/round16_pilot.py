import argparse
import itertools as it
import json
from collections import Counter
from pathlib import Path
import resource
import sys
from time import process_time

from round16_grid import (GRID, ROOT, SCOUT, TAG, all_schemes, assignments, audit,
                          bind, bits, check_proof, expand, orbit_of_core, posting,
                          read_jsonl)


def cpu():
    return process_time() + sum(resource.getrusage(resource.RUSAGE_CHILDREN)[:2])


def receipt(directory, group):
    from project import oracle, unsigned
    from pysat.solvers import Solver

    sites = GRID + tuple(group)
    order = len(sites)
    variables = {pair: number for number, pair in
                 enumerate(it.combinations(range(order), 2), 1)}
    clauses = [[-number] for (left, right), number in variables.items()
               if sites[left] & sites[right]]
    clauses.extend([-variables[pair] for pair in it.combinations(triple, 2)]
                   for triple in it.combinations(range(order), 3))
    supports = (unsigned * order)(*sites)
    blocks = []
    with Solver(name='g4', bootstrap_with=clauses) as solver:
        while solver.solve():
            model = set(solver.get_model())
            adjacency = [0] * order
            for (left, right), number in variables.items():
                if number in model:
                    adjacency[left] |= 1 << right
                    adjacency[right] |= 1 << left
            bad = oracle(supports, (unsigned * order)(*adjacency), 1023,
                         (1 << order) - 1, 5, 1, 9, 10)
            if not bad:
                return adjacency
            active = list(bits(bad))
            remaining = 1023
            for vertex in active:
                remaining &= ~sites[vertex]
            if remaining & 33 == 33:
                remaining ^= 1
            pad = list(bits(remaining))[:10 - len(active)]
            assert len(active) + len(pad) == 10
            clause = [variables[pair] for pair in it.combinations(active, 2)]
            blocks.append([active, pad])
            clauses.append(clause)
            solver.add_clause(clause)
    directory.mkdir(parents=True, exist_ok=False)
    (directory / 'sub.cnf').write_text(f'p cnf {len(variables)} {len(clauses)}\n' +
                                     ''.join(' '.join(map(str, row)) + ' 0\n' for row in clauses))
    (directory / 'witnesses.json').write_text(json.dumps(dict(sites=sites, wing=1023, blocks=blocks)))
    check_proof(directory, 'cadical', 20, 's UNSATISFIABLE')
    return None


def check_model(group, model):
    sys.path.insert(0, str(ROOT / 'tools'))
    from check_graph import alpha, triangle_free, to_graph6

    adj = [0] * 10 + [neighbors << 10 for neighbors in model]
    adj[0] |= 32
    adj[5] |= 1
    for vertex, support in enumerate(GRID + tuple(group), 10):
        adj[vertex] |= support
        for anchor in bits(support):
            adj[anchor] |= 1 << vertex
    assert triangle_free(adj) and alpha(adj) <= 9
    return to_graph6(adj)


def rank_sample(uncovered):
    return [uncovered[(2 * position + 1) * len(uncovered) // 96]
            for position in range(48)]


def measure(mode):
    start = cpu()
    data = json.loads(Path('prior.json').read_text())
    groups = [tuple(group) for group in data['groups']]
    prior = set(data['prior'])
    assert len(groups) == 1828 and len(prior) == 356
    ranks = rank_sample(sorted(set(range(len(groups))) - prior))
    covered = sum(1 << rank for rank in prior)
    covered_directly = set(ranks)
    folder = Path(mode)
    folder.mkdir(exist_ok=False)
    if mode == 'finish':
        direct = read_jsonl(Path('direct/price.jsonl'))
        assert {rec['rank'] for rec in direct} == covered_directly and all('sat' not in rec for rec in direct)
        if Path('transfer/price.jsonl').exists():
            for rec in read_jsonl(Path('transfer/price.jsonl')):
                assert 'sat' not in rec
                covered_directly.update(rec['new_ids'])
        ranks = sorted(set(range(len(groups))) - prior - covered_directly)
    index = posting(groups) if mode == 'transfer' else None
    if mode == 'transfer':
        from m8sample import test as shrink
    used_disk = 0
    print('setup', mode, len(ranks), f'{cpu()-start:.6f} CPU-s', flush=True)
    with (folder / 'price.jsonl').open('w', buffering=1) as out:
        for rank in ranks:
            group = groups[rank]
            directory = folder / str(rank)
            before = cpu()
            if mode == 'transfer':
                discovery = shrink(group)
                core = group if discovery['possible'] else tuple(discovery['extra'])
            else:
                core = group
            after_shrink = cpu()
            model = receipt(directory, core)
            after_proof = cpu()
            if model is not None:
                assert core == group
                model_g6 = check_model(group, model)
                stats = dict(rank=rank, sat=model_g6, cpu=cpu()-before)
                print(json.dumps(stats), file=out)
                print('stop on local projection model', rank, flush=True)
                return
            proved = bind(directory, group, core)
            after_bind = cpu()
            batch = 1 << rank
            if mode == 'transfer':
                batch = expand(orbit_of_core(proved), index, len(groups))
                assert batch >> rank & 1
            fresh = batch & ~covered
            covered |= batch
            cost = dict(shrink=after_shrink-before, proof=after_proof-after_shrink,
                        bind=after_bind-after_proof, index=cpu()-after_bind)
            stats = dict(rank=rank, core=proved, new_ids=list(bits(fresh)), sizes={
                item.name: item.stat().st_size for item in directory.iterdir()}, **cost)
            print(json.dumps(stats), file=out)
            used_disk += sum(item.stat().st_blocks * 512 for item in directory.iterdir()) + 4096
            if mode == 'finish' and (used_disk >= 450 * 2**20 or cpu() - start >= 540):
                print('stop on bounded production budget', rank, used_disk, flush=True)
                return
    print('complete', mode, len(ranks), f'{cpu()-start:.6f} CPU-s', flush=True)


def final():
    audit(Path('replay.prior.json'))
    assert Path('replay.prior.json').read_bytes() == Path('prior.json').read_bytes()
    sides = all_schemes()[TAG][1]
    groups = assignments(sides)
    left, right = sides
    forward = set()
    for permutation in it.permutations(right):
        common = [first & second for first, second in zip(left, permutation)]
        if any(mask & 1 for mask in common):
            continue
        diagonal = 0
        for mask in common:
            diagonal |= mask
        if diagonal == 30:
            forward.add(tuple(sorted(first | (second << 5)
                                     for first, second in zip(left, permutation))))
    assert forward == set(groups) and len(forward) == 1828
    print('forward/inverse exact alignment rosters agree', len(forward), flush=True)
    prior = set(json.loads(Path('prior.json').read_text())['prior'])
    expected_pilot = rank_sample(sorted(set(range(len(groups))) - prior))
    index = posting(groups)
    proved = set(prior)
    total = Counter()
    for mode in ('direct', 'transfer', 'finish'):
        seen = []
        fresh_proved = set(prior) if mode != 'finish' else proved.copy()
        for rec in read_jsonl(Path(mode) / 'price.jsonl'):
            rank = rec['rank']
            assert mode != 'finish' or rank not in proved
            seen.append(rank)
            if mode != 'transfer':
                assert tuple(rec['core']) == groups[rank]
            core = bind(Path(mode) / str(rank), groups[rank], rec['core'])
            covers = {rank} if mode != 'transfer' else set(bits(expand(orbit_of_core(core), index, len(groups))))
            assert rank in covers and covers - fresh_proved == set(rec['new_ids'])
            proved.update(covers)
            fresh_proved.update(covers)
        assert len(seen) == len(set(seen))
        if mode != 'finish':
            assert seen == expected_pilot
        total[mode] = len(seen)
        print('proved', mode, len(seen), len(proved), flush=True)
    assert proved == set(range(len(groups)))
    print('local scheme PASS', dict(total), len(proved), flush=True)


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('mode', choices=['direct', 'transfer', 'finish', 'final'])
    mode = args.parse_args().mode
    sys.path.insert(0, str(Path.cwd()))
    final() if mode == 'final' else measure(mode)
