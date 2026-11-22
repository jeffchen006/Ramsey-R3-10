import argparse
import itertools as it
import json
from collections import Counter
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[3]
SCOUT = ROOT / 'scratch/ideas/r015_N'
TAG = 'leaf+leaf.1'
GRID = tuple((1 << left) | (32 << right)
             for left in range(5) for right in range(5) if left != right)
EDGES = frozenset((1 << left) | (1 << right)
                  for left, right in it.combinations(range(5), 2))
DIAG = tuple(1 << vertex | 32 << vertex for vertex in range(5))
PERMS = tuple((0,) + tail for tail in it.permutations(range(1, 5)))
MOVES = tuple(tuple(1 << (perm[vertex % 5] + 5 * ((vertex // 5) ^ swap))
                    for vertex in range(10))
              for perm in PERMS for swap in range(2))


def image(mask, move):
    return sum(bit for pos, bit in enumerate(move) if mask >> pos & 1)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def all_schemes():
    catalog = json.loads((SCOUT / 'schemes.json').read_text())
    holes = {tuple(sorted(pair)) for pair in it.combinations(EDGES, 2)
             if (pair[0] | pair[1]) & 1}
    assert len(holes) == 30
    raw = set(it.product(holes, repeat=2))
    covered = set()
    for tag, (_, (left, right)) in catalog.items():
        assert len(left) == len(right) == 8 and set(left) <= EDGES and set(right) <= EDGES
        missing = (EDGES - set(left), EDGES - set(right))
        types = []
        for side in missing:
            first, second = side
            types.append('matching' if not first & second else
                         'middle' if first & second & 1 else 'leaf')
        assert types == tag.split('.')[0].split('+')
        orbit = set()
        for move in MOVES:
            rotated = tuple(tuple(sorted(image(mask, move[:5]) for mask in side))
                            for side in missing)
            if move[0] == 32:
                rotated = tuple(tuple(mask >> 5 for mask in side) for side in rotated[::-1])
            orbit.add(rotated)
        assert not covered & orbit
        covered.update(orbit)
    assert covered == raw and len(catalog) == 30
    return catalog


def assignments(sides):
    left, right = sides
    valid = []
    for inverse in it.permutations(left):
        group = tuple(sorted(first | (second << 5) for first, second in zip(inverse, right)))
        if any(mask & DIAG[0] == DIAG[0] for mask in group):
            continue
        if all(any(mask & needed == needed for mask in group) for needed in DIAG[1:]):
            valid.append(group)
    assert len(set(valid)) == len(valid)
    return tuple(sorted(valid))


def orbit_of_core(core):
    return {tuple(sorted(image(mask, move) for mask in core)) for move in MOVES}


def posting(groups):
    index = Counter()
    for rank, group in enumerate(groups):
        for mask in group:
            index[mask] |= 1 << rank
    return index


def expand(cores, index, count):
    covered = 0
    for core in cores:
        matches = (1 << count) - 1
        for mask in core:
            matches &= index[mask]
            if not matches:
                break
        covered |= matches
    return covered


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def bind(directory, group, expected=None, dual=True):
    witness = json.loads((directory / 'witnesses.json').read_text())
    sites = witness['sites']
    assert witness['wing'] == 1023 and tuple(sites[:20]) == GRID, directory
    core = tuple(sorted(sites[20:]))
    assert core and len(set(core)) == len(core) and set(core) <= set(group), directory
    if expected is not None:
        assert core == tuple(sorted(expected)), directory
    variables = {pair: number for number, pair in
                 enumerate(it.combinations(range(len(sites)), 2), 1)}
    clauses = Counter((-literal,) for (left, right), literal in variables.items()
                      if sites[left] & sites[right])
    clauses.update(tuple(-variables[pair] for pair in it.combinations(triple, 2))
                   for triple in it.combinations(range(len(sites)), 3))
    for active, wing in witness['blocks']:
        assert len(set(active)) == len(active) and all(0 <= idx < len(sites) for idx in active)
        assert len(set(wing)) == len(wing) and all(0 <= anchor < 10 for anchor in wing)
        assert len(active) + len(wing) == 10 and not {0, 5} <= set(wing)
        assert all(not sites[idx] >> anchor & 1 for idx in active for anchor in wing)
        clauses[tuple(variables[pair] for pair in it.combinations(sorted(active), 2))] += 1
    head, *rows = (directory / 'sub.cnf').read_text().splitlines()
    assert head.split() == ['p', 'cnf', str(len(variables)), str(len(rows))]
    actual = Counter()
    for row in rows:
        *clause, sentinel = map(int, row.split())
        assert sentinel == 0 and all(clause)
        actual[tuple(clause)] += 1
    assert clauses == actual, directory
    if dual:
        check_proof(directory, 'lrat-check', 0, 'c VERIFIED')
        check_proof(directory, 'cake_lpr', 0, 's VERIFIED UNSAT')
    return core


def check_proof(directory, binary, rc, phrase):
    options = ['--lrat', '--no-binary'] if binary == 'cadical' else []
    result = subprocess.run(['timeout', '10s', ROOT / 'opt/bin' / binary,
                             *options, 'sub.cnf', 'sub.lrat'], cwd=directory,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert result.returncode == rc and phrase.encode() in result.stdout, (
        directory, binary, result.returncode, result.stdout[-500:])


def audit(destination):
    catalog = all_schemes()
    groups = {tag: assignments(sides) for tag, (_, sides) in catalog.items()}
    cores = []
    for batch, proof_count in [('m8.sample', 30), ('price.leaf+leaf.1', 32)]:
        current = set()
        records = read_jsonl(SCOUT / (batch + '.jsonl'))
        assert len(records) == proof_count
        for number, rec in enumerate(records):
            group = tuple(sorted(rec['group']))
            assert not rec['possible'] and group in groups[rec['tag']]
            assert batch == 'm8.sample' or rec['tag'] == TAG
            core = bind(SCOUT / 'proof' / f'{batch}.{number}', group, rec['extra'])
            current.update(orbit_of_core(core))
        cores.append(current)

    indexed = read_jsonl(SCOUT / 'cover.index.jsonl')
    expected = {(tag, tuple(group)) for tag, group in indexed}
    assert len(expected) == len(indexed)
    actual = set()
    total = Counter()
    for tag, alignments in groups.items():
        count = len(alignments)
        index = posting(alignments)
        seed, front = (expand(part, index, count) for part in cores)
        union = seed | front
        actual.update((tag, alignments[rank]) for rank in bits(union))
        bucket = dict(total=count, seed=seed.bit_count(), front=front.bit_count(),
                      overlap=(seed & front).bit_count(), union=union.bit_count())
        total.update(bucket)
        print(tag, bucket, flush=True)
        if tag == TAG:
            assert (count, union.bit_count()) == (1828, 356)
            destination.write_text(json.dumps(dict(groups=alignments, prior=list(bits(union)))) + '\n')
    assert actual == expected
    assert total == dict(total=169635, seed=2803, front=7652, overlap=69, union=10386)
    print('audit PASS', dict(total), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    audit(parser.parse_args().output)
