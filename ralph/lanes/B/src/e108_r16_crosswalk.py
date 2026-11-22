"""Bind the archived critical certificates to the accepted reducible inventory."""

import argparse
import ast
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import zip_longest
import json
from pathlib import Path
import re
import subprocess


ROOT = Path('../..')
LANE = ROOT / 'ralph/lanes/B'
WORK = Path('work')
REDUCIBLE = WORK / 'e108_r5/reducible.g6'
DISPOSITIONS = WORK / 'e108_r15/rank-dispositions.tsv'
CRITICAL = WORK / 'e108_r11/critical.g6'
UNION = WORK / 'e108_r11/union.g6'
REDUCIBLE_SHA = 'c816d7f02fd929d4503a39cf3b7c0fed5f9d79e5fe542389661932f967f43f91'
HEX = re.compile(rb'[0-9a-f]{64}')
EXPECTED_RED = {'C6': 3862, 'P6': 170, 'C14': 31407, 'P14': 1361,
                'C15': 1980937, 'P15': 84534}


@dataclass(frozen=True)
class Cohort:
    name: str
    input: str
    directory: str
    freeze: str
    counts: tuple
    cliques: str = 'cliques.tsv'
    complement: str = 'complement.tsv'


COHORTS = (
    Cohort('r6', 'e108_r6_rewire/startcritical.g6', 'e108_r6_critical_proof',
           'ROUND6_REPLAY.sha256', (569, 45), 'clique.cliq.tsv', 'clique.missing.tsv'),
    Cohort('r8', 'e108_r8_import/scout1142.g6', 'e108_r8_scout_proofs',
           'ROUND8_E108.sha256', (761, 381)),
    Cohort('r10_scout', 'e108_r10_import/scout61.g6', 'e108_r10_import',
           'ROUND10.sha256', (57, 4)),
    Cohort('r10_stitch', 'e108_r10_new/stitch5.g6', 'e108_r10_new',
           'ROUND10.sha256', (2, 3)),
    Cohort('r10_repuncture', 'e108_r10_micro/repuncture6.g6', 'e108_r10_micro',
           'ROUND10.sha256', (5, 1)),
    Cohort('r11', 'e108_r11/novel.g6', 'e108_r11', 'ROUND11.sha256', (37, 10)),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def frozen_digest(freeze, path):
    relpath = (str(path) if freeze == 'ROUND6_REPLAY.sha256' else f'scratch/B/{path}')
    matches = [row.split()[0] for row in (LANE / freeze).read_text().splitlines()
               if row.split()[1] == relpath]
    require(len(matches) == 1, f'{path}: missing or ambiguous hash in {freeze}')
    return matches[0]


def frozen_bytes(freeze, path):
    data = path.read_bytes()
    require(sha256(data).hexdigest() == frozen_digest(freeze, path), f'{path}: frozen bytes changed')
    return data


def record(key):
    require(len(key) == 84 and key[0] == 95 and all(63 <= byte <= 126 for byte in key),
            f'invalid order-32 graph6 record: {key!r}')
    return key


def canonical(data):
    run = subprocess.run(['timeout', '30s', '../../opt/bin/labelg', '-q'],
                         input=data, capture_output=True, check=True)
    keys = list(map(record, run.stdout.splitlines()))
    require(len(keys) == len(data.splitlines()), 'labelg changed the number of records')
    return keys


def read_rows(data, width, count):
    rows = {}
    previous = 0
    for line_no, line in enumerate(data.splitlines(), 1):
        raw_index, fields = line.split(b'\t', 1)
        index = int(raw_index)
        require(previous < index <= count, f'bad receipt rank {index}')
        if width:
            masks = [int(mask, 16) for mask in fields.split()]
            require(len(masks) == width and len(set(masks)) == width and
                    all(0 < mask < (1 << 32) and mask.bit_count() in (1, 2) for mask in masks),
                    f'invalid demand layout at rank {index}')
        rows[index] = line_no, fields
        previous = index
    return rows


def bind_partition(raw_keys, cliques, complement):
    require(set(cliques).isdisjoint(complement), 'conflicting clique/LRAT receipt ranks')
    for index, (_, key) in complement.items():
        require(raw_keys[index - 1] == key, f'wrong labelled graph at complement rank {index}')
    return set(range(1, len(raw_keys) + 1)) - cliques.keys() - complement.keys()


def proof_log(data, phase, complement):
    lines = data.splitlines()
    label, count, summary = lines.pop().decode().split(maxsplit=2)
    require(label == 'counts' and int(count) == len(complement), f'{phase}: wrong footer count')
    entries = {}
    methods = dict.fromkeys(('rup', 'cadical', 'replay'), 0)
    for line_no, (index, line) in enumerate(zip(complement, lines, strict=True), 1):
        actual, cnf_hash, proof_hash, method = line.split()
        allowed = (b'rup', b'cadical') if phase == 'production' else (b'replay',)
        require(int(actual) == index and HEX.fullmatch(cnf_hash) and HEX.fullmatch(proof_hash)
                and method in allowed, f'{phase}: wrong transcript row {line_no}')
        methods[method.decode()] += 1
        entries[index] = line_no, cnf_hash, proof_hash
    require(ast.literal_eval(summary) == methods, f'{phase}: wrong footer methods')
    return entries


def equal_proof_logs(production, replay):
    require(production == replay, 'production and replay transcripts conflict')


def add_key(table, key, receipt):
    require(key not in table, f'duplicate canonical receipt key {key!r}')
    table[key] = receipt


def bind_cohort(cohort, table):
    directory = WORK / cohort.directory
    data = frozen_bytes(cohort.freeze, WORK / cohort.input)
    raw_keys = list(map(record, data.splitlines()))
    keys = canonical(data)
    get = lambda name: frozen_bytes(cohort.freeze, directory / name)
    cliques = read_rows(get(cohort.cliques), 8, len(keys))
    complement = read_rows(get(cohort.complement), 0, len(keys))
    pins = read_rows(get('pins.tsv'), 7, len(complement))
    unbound = bind_partition(raw_keys, cliques, complement)
    require((len(cliques), len(complement)) == cohort.counts, f'{cohort.name}: wrong tranche totals')
    produced = proof_log(get('production.log'), 'production', complement)
    replayed = proof_log(get('replay.log'), 'replay', complement)
    equal_proof_logs(produced, replayed)
    expected_payloads = {f'{index:07d}.lrat' for index in complement}
    require({path.name for path in (directory / 'proofs').glob('*.lrat')} == expected_payloads,
            f'{cohort.name}: wrong exact LRAT filename set')
    for index, key in enumerate(keys, 1):
        if index in cliques:
            line_no, _ = cliques[index]
            fields = (b'clique', str(line_no).encode(), b'-', b'-', b'-', b'-')
        elif index in replayed:
            line_no, cnf_hash, proof_hash = replayed[index]
            filename = f'{index:07d}.lrat'
            payload = (directory / 'proofs' / filename).read_bytes()
            require(sha256(payload).hexdigest().encode() == proof_hash, f'{cohort.name}: wrong payload {index}')
            pin_line = pins.get(line_no, (0,))[0]
            fields = (b'LRAT', str(line_no).encode(), str(pin_line).encode(), filename.encode(),
                      cnf_hash, proof_hash)
        else:
            require(index in unbound, f'{cohort.name}: unexpected unbound rank {index}')
            fields = (b'UNBOUND', b'-', b'-', b'-', b'-', b'-')
        label = cohort.name.encode(), str(index).encode()
        add_key(table, key, label + fields + (raw_keys[index - 1],))
    print(f'{cohort.name}: {len(cliques)} cliques, {len(complement)} LRATs, '
          f'{len(pins)} pinned LRATs, {len(unbound)} unbound', flush=True)


def bind_union(table, output):
    require(len(table) == 1875, 'wrong size of critical index')
    critical = frozen_bytes('ROUND11.sha256', CRITICAL).splitlines()
    require(sorted(table) == critical, 'receipt key set differs from the supplied critical roster')
    red_counts = Counter()
    crit_counts = Counter()
    source_hash, disp_hash, union_hash = sha256(), sha256(), sha256()
    previous = b''
    with REDUCIBLE.open('rb') as src, DISPOSITIONS.open('rb') as disp, UNION.open('rb') as union:
        critical_iter = iter(critical)
        next_critical = next(critical_iter, None)
        union_rank = 0
        header = b'key\tunion_rank\tcohort\tinput_rank\tkind\treceipt_line\tpins_line\tpayload\tcnf_sha256\tlrat_sha256\toriginal_g6\n'
        result = [header]

        def take(key):
            nonlocal union_rank
            line = union.readline()
            require(line == key + b'\n', f'merge mismatch at union rank {union_rank + 1}')
            union_hash.update(line)
            union_rank += 1

        def take_critical(key):
            take(key)
            receipt = table[key]
            crit_counts[receipt[2].decode()] += 1
            result.append(b'\t'.join((key, str(union_rank).encode(), *receipt)) + b'\n')

        for rank, (line, disposition) in enumerate(zip_longest(src, disp), 1):
            require(line is not None and disposition is not None, 'source/disposition length mismatch')
            key = line[:-1]
            require(len(line) == 85 and line[-1:] == b'\n' and key > previous,
                    f'wrong source order or shape at rank {rank}')
            code = disposition.rstrip(b'\n').rsplit(b'\t', 1)[-1].decode()
            require(disposition == f'{rank}\t{code}\n'.encode() and code in EXPECTED_RED,
                    f'wrong disposition at rank {rank}')
            while next_critical is not None and next_critical < key:
                take_critical(next_critical)
                next_critical = next(critical_iter, None)
            require(next_critical != key, f'critical/reducible overlap at rank {rank}')
            take(key)
            source_hash.update(line)
            disp_hash.update(disposition)
            previous = key
            red_counts[code] += 1
        while next_critical is not None:
            take_critical(next_critical)
            next_critical = next(critical_iter, None)
        require(not union.read(1), 'trailing unmatched union keys')

    require(red_counts == EXPECTED_RED and source_hash.hexdigest() == REDUCIBLE_SHA,
            'wrong reducible inventory')
    require(disp_hash.hexdigest() == frozen_digest('ROUND15.sha256', DISPOSITIONS), 'wrong accepted R15 transcript')
    require(union_hash.hexdigest() == frozen_digest('ROUND11.sha256', UNION), 'wrong supplied union digest')
    output.write_bytes(b''.join(result))
    print(json.dumps({'reducible': red_counts, 'critical': crit_counts,
                      'unbound_supplied': crit_counts['UNBOUND'], 'union': union_rank,
                      'crosswalk_sha256': sha256(output.read_bytes()).hexdigest(),
                      'union_sha256': union_hash.hexdigest()}, sort_keys=True))


def controls():
    keys = [b'small labelled key A', b'small labelled key B']
    cliques, complement = {1: (1, b'clique')}, {2: (1, keys[1])}
    require(not bind_partition(keys, cliques, complement), 'positive receipt control failed')
    require(bind_partition(keys, cliques, {}) == {2}, 'missing receipt not reported')
    print('control missing complement: reported unbound rank 2')
    cases = (
        ('swapped labelled input', lambda: bind_partition(keys[::-1], cliques, complement)),
        ('overlapping dispositions', lambda: bind_partition(keys, {**cliques, 2: (2, b'clique')}, complement)),
        ('duplicate normalized key', lambda: add_key({keys[0]: 'old'}, keys[0], 'new')),
        ('changed replay hash', lambda: equal_proof_logs({2: (1, b'a', b'b')}, {2: (1, b'a', b'c')})),
    )
    for label, test in cases:
        try:
            test()
        except ValueError:
            print(f'control {label}: rejected')
        else:
            raise ValueError(f'control {label}: not rejected')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    controls()
    table = {}
    for cohort in COHORTS:
        bind_cohort(cohort, table)
    bind_union(table, args.output)
