#!/usr/bin/env python3
"""Join the two c1/δ2 terminal indexes to the critic's variant checks."""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import sys
import re


ROOT = Path(__file__).resolve().parents[3]
G8 = ROOT / 'scratch/G/round8'
A8 = ROOT / 'scratch/A/strip8'
CRITIC = ROOT / 'scratch/critic/r8/G'


def table(*sources):
    result = {}
    for source in sources:
        for line in source.read_text().splitlines():
            key, *fields = line.split()
            if line.startswith('continuation attempted ') or re.match(r'^17194 keys;', line):
                continue
            assert re.fullmatch(r'\d+_\d+_\d+', key) and key not in result, (source, key)
            result[key] = tuple(fields)
    return result


def main():
    lane_a = table(A8 / 'lower.terminal.tsv')
    a_replays = table(*(A8 / name for name in ('lower.hash.0.log', 'lower.hash.1.log', 'lower.delta.hash.log')))
    lane_g = table(G8 / 'c1.final/certificates.tsv')
    differences = table(CRITIC / 'differences')
    critic_a = table(CRITIC / 'eager.check')
    critic_g = table(CRITIC / 'primary.check')
    assert len(lane_a) == 17194 and lane_a.keys() == lane_g.keys() == a_replays.keys()
    assert len(differences) == 32 and differences.keys() == critic_a.keys() == critic_g.keys()
    counts = Counter()
    print('key\tG_eager\tG_cnf_sha256\tG_trace_sha256\tG_trace\tA_eager\tA_cnf_sha256\tA_trace_sha256\tA_trace')
    for key in sorted(lane_a):
        a_cnf, a_size, a_path = lane_a[key]
        _, _, a_replay_cnf, a_digest = a_replays[key]
        assert a_cnf == a_replay_cnf
        g_cnf, g_digest, g_path, g_size = lane_g[key]
        a_file = (A8 / a_path).resolve()
        g_file = (G8.parent / 'round7' / g_path).resolve()
        eager_g = '0' if g_file.parent.name == 'proof-low25-pilot' else '10000'
        assert g_file.stat().st_size == int(g_size) and a_file.stat().st_size == int(a_size)
        a_pilot = a_file.parent.name == 'proof-low25-eager'
        distinct = a_cnf != g_cnf
        assert distinct == (eager_g == '0') == (key in differences)
        if distinct:
            assert a_pilot and differences[key] == (a_cnf, g_cnf)
            assert critic_a[key] == (a_cnf,) and critic_g[key] == (g_cnf,)
            assert sha256(a_file.read_bytes()).hexdigest() == a_digest
            assert sha256(g_file.read_bytes()).hexdigest() == g_digest
            counts['different pilot CNFs'] += 1
        elif a_pilot:
            assert g_file.parent.name == 'proof-c1retry' and a_file != g_file
            assert sha256(a_file.read_bytes()).hexdigest() == a_digest
            assert sha256(g_file.read_bytes()).hexdigest() == g_digest
            counts['same-CNF pilot/retry'] += 1
        else:
            assert a_file == g_file and a_digest == g_digest
            counts['identical trace path and CNF'] += 1
        print(key, eager_g, g_cnf, g_digest, g_file.relative_to(ROOT),
              '10000', a_cnf, a_digest, a_file.relative_to(ROOT), sep='\t')
    assert counts == {'different pilot CNFs': 32, 'same-CNF pilot/retry': 10,
                      'identical trace path and CNF': 17152}
    print('Both independently selected indexes cover 17194 keys:', dict(counts), file=sys.stderr)


if __name__ == '__main__':
    main()
