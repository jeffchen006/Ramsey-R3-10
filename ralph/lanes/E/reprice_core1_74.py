#!/usr/bin/env python3
"""Post-stratify residual core-1 IDs using the current dual-checker pilot."""

from collections import Counter, defaultdict
import csv
import json
from math import ceil
from pathlib import Path
import re
from statistics import mean

from estimate_core1_74 import cost
from paired_core1_74 import FULL, FILE_CAP, ids


PARTS = ('prepare', 'solve', 'verify', 'bytes')
MODES = ('narrow', 'wide')
THIRDS = ('head', 'middle', 'tail')


def cpu(stats):
    return sum(stats[stage] for stage in PARTS[:-1])


def pricing():
    target = Path('target.log')
    observations = list(map(json.loads, Path('paired.jsonl').read_text().splitlines()))
    assert observations
    selected = [tuple(row['id']) for row in observations]
    residual = ids(Path('residual.jsonl'))
    assert sorted([*selected, *residual]) == ids(FULL/'pending.1.jsonl')
    assert selected == ids(FULL/'proposed_pilot.1.jsonl')[:len(selected)]
    with (FULL/'branch_rates.tsv').open(encoding='ascii') as source:
        branches = [(int(row['index']), int(row['row_begin']), int(row['rows']))
                    for row in csv.DictReader(source, delimiter='\t')]

    def stratum(projection):
        branch, begin, rows = next(row for row in branches if row[1] <= projection < row[1] + row[2])
        return branch, min(2, 3*(projection-begin)//rows)

    samples = defaultdict(list)
    for row in observations:
        assert (row['branch'], row['third']) == stratum(row['id'][0])
        samples[row['branch'], row['third']].append(row)
    counts = Counter(stratum(projection) for projection, _ in residual)
    fallbacks = Counter((row['branch'], row['third']) for row in observations if row['choice'] == 'wide-fallback')
    sums = {mode: {stage: sum(row[mode][stage] for row in observations) for stage in PARTS} for mode in MODES}
    baseline_samples = {mode: [row[mode] for row in observations if row[mode]['status'] == 'UNSAT']
                        for mode in MODES}
    assert all(baseline_samples.values())
    elapsed = cost(target)
    known_roster = float(re.search(r'frozen_roster_cpu=(\d+\.\d+)', target.read_text()).group(1))
    setup = elapsed - sum(row['cpu'] for row in observations)
    per_id = mean(row['cpu'] - sum(cpu(row[mode]) for mode in MODES) for row in observations)
    assert known_roster > 0 and setup >= 0 and per_id >= 0
    recheck_setup = cost(Path('preflight.log')) + cost(Path('audit.log'))
    framework = setup + recheck_setup + per_id * len(residual)
    print('Pilot IDs', len(observations), 'fallbacks', sum(fallbacks.values()), 'residual', len(residual))
    for mode in MODES:
        print(mode, {stage: round(value, 5) for stage, value in sums[mode].items()},
              'total route CPU-s', round(cpu(sums[mode]), 5))
    print('Pilot setup: roster read', round(known_roster, 5), '(part of driver setup', round(setup, 5), ')',
          'per-ID framework', round(per_id, 5), 'controls+audit', round(recheck_setup, 5))

    totals = {mode: Counter() for mode in MODES}
    coverage = Counter()
    with Path('reprice.strata.tsv').open('x', encoding='ascii') as out:
        print('branch', 'third', 'pending', 'pilot_exact', 'fallbacks_exact', 'pool', 'pool_n',
              *(f'{mode}_{stage}_id' for mode in MODES for stage in PARTS), sep='\t', file=out)
        for label in sorted(set(samples) | set(counts)):
            branch, third = label
            exact = [row for row in samples[label] if row['narrow']['status'] == 'UNSAT']
            same_branch = [row for (key, _), rows in samples.items() if key == branch
                           for row in rows if row['narrow']['status'] == 'UNSAT']
            pool, typ = (exact, 'third') if exact else (same_branch, 'branch') if same_branch else (
                [row for row in observations if row['narrow']['status'] == 'UNSAT'], 'global')
            assert pool
            rates = {mode: {stage: mean(row[mode][stage] for row in pool) for stage in PARTS} for mode in MODES}
            coverage[typ] += counts[label]
            for mode in MODES:
                totals[mode].update({stage: counts[label] * rate for stage, rate in rates[mode].items()})
            print(branch, THIRDS[third], counts[label], len(samples[label]), fallbacks[label], typ, len(pool),
                  *(f'{rates[mode][stage]:.5f}' for mode in MODES for stage in PARTS), sep='\t', file=out)

    print('Residual coverage by pool', dict(coverage), 'shared setup+framework CPU-s', round(framework, 3))
    mib = 1024**2
    for mode in MODES:
        print(mode, 'estimate CPU-s including whole framework charge', round(cpu(totals[mode]) + framework, 3),
              'route artifact retention MiB', round(totals[mode]['bytes']/mib, 3))
    peak_wide_cpu = max(map(cpu, baseline_samples['wide']))
    peak_wide_size = max(row['bytes'] for row in baseline_samples['wide'])
    for fraction in (0, 0.05, 0.20, 1.0):
        count = ceil(fraction * len(residual))
        print('fallback sensitivity', count, 'CPU-s', round(cpu(totals['narrow']) + framework +
                                                            count*(8+peak_wide_cpu), 3),
              'retained MiB', round((totals['narrow']['bytes'] + count*(FILE_CAP+peak_wide_size))/mib, 3))
    print('Each fallback adds 8 s narrow cap and max sampled checked wide route; each charged 8 MiB',
          'for potentially retained partial LRAT plus max observed wide size; these are scenarios, not bounds.')


if __name__ == '__main__':
    pricing()
