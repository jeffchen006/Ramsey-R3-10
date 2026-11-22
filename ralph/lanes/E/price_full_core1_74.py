#!/usr/bin/env python3
"""Post-stratify the exact pending roster by round-18 paired measurements."""

from collections import Counter, defaultdict
import json
from math import ceil
from pathlib import Path
import re
from statistics import mean

from estimate_core1_74 import cost
from full_core1_74 import PREV, tsv


MODES = ('narrow', 'wide')
SCALES = ('head', 'middle', 'tail')
ROUTE = re.compile(r'(\d+)_(\d+) \S+ \S+ encode_bind_cpu=(\d+\.\d+)')


def route_observations(mode, ids):
    prefix = PREV/f'matched.{mode}'
    elapsed = cost(f'{prefix}.log') + cost(f'{prefix}.rebind.log')
    measured = {}
    with Path(f'{prefix}.log').open(encoding='ascii') as log:
        for line in log:
            if result := ROUTE.fullmatch(line.strip()):
                index, lift, parent = result.groups()
                measured[int(index), int(lift)] = float(parent)
    assert set(measured) == set(ids) and len(ids) == 16
    sizes = defaultdict(int)
    rss = 0
    for artifact in prefix.iterdir():
        stem, suffix = artifact.name.split('.', 1)
        index, lift, *_ = stem.split('_')
        key = int(index), int(lift)
        assert key in measured
        sizes[key] += artifact.stat().st_size
        if suffix in ('solve.log', 'lrat.log', 'replay.log', 'fresh.log'):
            measured[key] += cost(artifact)
            rss = max(rss, int(re.findall(r'RSS=(\d+)', artifact.read_text(encoding='ascii'))[-1]))
    overhead = (elapsed - sum(measured.values())) / len(measured)
    assert overhead >= 0
    print(mode, 'pilot CPU-s', round(elapsed, 3), 'shared parent/startup s/ID', round(overhead, 3),
          'bytes min/max', min(sizes.values()), max(sizes.values()), 'peak child RSS KiB', rss)
    return {key: (seconds + overhead, sizes[key]) for key, seconds in measured.items()}


def roster(path):
    ids = []
    with path.open(encoding='ascii') as stream:
        for line in stream:
            index, lift, status = json.loads(line)
            assert status == 'open' and (not ids or ids[-1] < (index, lift))
            ids.append((index, lift))
    return ids


def pricing():
    branches = list(tsv(Path('branch_rates.tsv')))
    terminals = roster(Path('terminal.1.jsonl'))
    pending = roster(Path('pending.1.jsonl'))
    matched = roster(PREV/'matched.1.jsonl')
    assert sorted([*pending, *matched]) == terminals

    def pair(key):
        index, _ = key
        row, = (row for row in branches if int(row['row_begin']) <= index < int(row['row_begin']) + int(row['rows']))
        return int(row['index']), min(2, 3 * (index - int(row['row_begin'])) // int(row['rows']))

    measured = {mode: route_observations(mode, matched) for mode in MODES}
    counts = Counter(map(pair, pending))
    samples = defaultdict(list)
    for key in matched:
        samples[pair(key)].append(key)
    totals = Counter()
    pools = Counter()
    with Path('price.strata.tsv').open('x', encoding='ascii') as out:
        print('branch\tthird\tpending\texact_paired_sample\tpool\tpool_n\tnarrow_cpu_s_id\twide_cpu_s_id\t'
              'narrow_bytes_id\twide_bytes_id', file=out)
        for (branch, third), count in sorted(counts.items()):
            exact = samples[branch, third]
            same_branch = [key for (adjacent, _), keys in samples.items() if adjacent == branch for key in keys]
            pool, label = (exact, 'branch-third') if exact else ((same_branch, 'branch') if same_branch
                                                                 else (matched, 'global'))
            pools[label] += count
            rates = {}
            for mode in MODES:
                for metric, column in (('cpu-s', 0), ('bytes', 1)):
                    value = mean(measured[mode][key][column] for key in pool)
                    totals[mode, metric] += count * value
                    rates[mode, metric] = value
            print(branch, SCALES[third], count, len(exact), label, len(pool),
                  *(f'{rates[mode, metric]:.4f}' for metric in ('cpu-s', 'bytes') for mode in MODES),
                  sep='\t', file=out)
    print('pending', len(pending), 'sample used by stratum', dict(pools), flush=True)
    for mode in MODES:
        print(mode, 'baseline CPU-s', round(totals[mode, 'cpu-s'], 2), 'retention MiB',
              round(totals[mode, 'bytes'] / 1024**2, 2), flush=True)

    combined_peak = max(sum(measured[mode][key][1] for mode in MODES) for key in matched)
    narrow = totals['narrow', 'cpu-s']
    wide = totals['wide', 'cpu-s']
    for rate in (0, 0.05, 0.2, 1):
        count = min(len(pending), ceil(rate * len(pending)))
        budget = narrow + count * (7 + 3*10 + max(value[0] for value in measured['wide'].values()))
        disk = totals['narrow', 'bytes'] + count * max(value[1] for value in measured['wide'].values())
        print('fallback attempts charged', count, 'CPU-s scenario', round(budget, 2),
              'retention MiB scenario', round(disk / 1024**2, 2))
    print('conservative planning (not a bound): 3x both route baselines CPU-s', round(3*(narrow + wide), 2),
          '2x paired pilot maximum retained bytes/ID', 2*combined_peak,
          'times roster in MiB', round(2*combined_peak*len(pending)/1024**2, 2), flush=True)
    if pending:
        queues = defaultdict(list)
        for key in pending:
            queues[pair(key)].append(key)
        ordered_strata = sorted(queues, key=lambda label: (bool(samples[label]), -len(queues[label]), label))
        iterators = []
        for label in ordered_strata:
            group = queues[label]
            offsets = dict.fromkeys((len(group)//2, len(group)//4, 3*len(group)//4, 0, len(group)-1))
            iterators.append(iter([group[offset] for offset in offsets]))
        proposal = []
        while iterators and len(proposal) < 16:
            keep = []
            for queue in iterators:
                if (key := next(queue, None)) is not None:
                    proposal.append(key)
                    keep.append(queue)
                if len(proposal) == 16:
                    break
            iterators = keep
        assert len(proposal) == len(set(proposal)) and set(proposal) <= set(pending)
        with Path('proposed_pilot.1.jsonl').open('x', encoding='ascii') as out:
            for key in sorted(proposal):
                print(json.dumps((*key, 'open'), separators=(',', ':')), file=out)
        print('proposed next matched pilot IDs', len(proposal), '(not run)', flush=True)


if __name__ == '__main__':
    pricing()
