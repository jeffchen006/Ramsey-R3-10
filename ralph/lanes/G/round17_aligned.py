import argparse
from collections import Counter, defaultdict
import hashlib
import itertools as it
import json
import math
from pathlib import Path
import re
import subprocess
import sys

from round16_grid import (GRID, MOVES, ROOT, SCOUT, TAG, all_schemes, assignments,
                          bind, bits, expand, image, orbit_of_core, posting, read_jsonl)
from round16_pilot import check_model, cpu, rank_sample, receipt


PREV = ROOT / 'scratch/G/round16'
MASK = 31
PARTS = ('sub.cnf', 'sub.lrat', 'witnesses.json')


def write_json(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bound(directory, group, core):
    pattern = bind(directory, group, core, dual=False)
    for binary, options, marker in (
            ('lrat-check', [], b'c VERIFIED'),
            ('cake_lpr', ['--CML_HEAP_SIZE=128', '--CML_STACK_SIZE=32'], b's VERIFIED UNSAT')):
        result = subprocess.run(['timeout', '10s', ROOT / 'opt/bin' / binary, *options, 'sub.cnf', 'sub.lrat'],
                                cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        assert result.returncode == 0 and marker in result.stdout.splitlines(), (
            directory, binary, result.returncode, result.stdout[-500:])
    return pattern


def independent_forward(left, right):
    groups = set()
    for permutation in it.permutations(right):
        diagonal = 0
        for first, second in zip(left, permutation):
            diagonal |= first & second
        if diagonal == 30:
            groups.add(tuple(sorted(first | (second << 5)
                                    for first, second in zip(left, permutation))))
    return groups


def move_tables(width):
    full = (1 << width) - 1
    for tail in it.permutations(range(1, width)):
        perm = (0,) + tail
        table = [sum(1 << perm[anchor] for anchor in bits(mask)) for mask in range(full + 1)]
        yield [(table[mask & full] | (table[mask >> width] << width))
               for mask in range(1 << (2 * width))]
        yield [(entry >> width) | ((entry & full) << width)
               for entry in (table[mask & full] | (table[mask >> width] << width)
                             for mask in range(1 << (2 * width)))]


def check_actions():
    for table, move in zip(move_tables(5), MOVES, strict=True):
        assert tuple(table[mask] for mask in range(1024)) == tuple(
            image(mask, move) for mask in range(1024))
        assert set(table[mask] for mask in GRID) == set(GRID)
    print('S4 x shore exchange: exact agreement on all 48 x 1024 masks', flush=True)


def small_controls():
    sys.path.insert(0, str(ROOT / 'tools'))
    from check_graph import alpha, parse_graph6, triangle_free

    def aligned_marks(adj):
        for first, second in it.combinations(range(len(adj)), 2):
            if not adj[first] >> second & 1 or (adj[first].bit_count(), adj[second].bit_count()) != (4, 4):
                continue
            left = list(bits(adj[first] ^ (1 << second)))
            right = list(bits(adj[second] ^ (1 << first)))
            crossing = [(aa, bb) for aa, bb in it.product(left, right) if adj[aa] >> bb & 1]
            if len(crossing) != 1:
                continue
            left0, right0 = crossing[0]
            left = [left0] + [anchor for anchor in left if anchor != left0]
            right = [right0] + [anchor for anchor in right if anchor != right0]
            exterior = set(range(len(adj))) - set(left + right + [first, second])
            halves = [(tuple(aa for aa in left if adj[site] >> aa & 1),
                       tuple(bb for bb in right if adj[site] >> bb & 1)) for site in exterior]
            if any(len(aa) != len(bb) or len(aa) not in (1, 2) for aa, bb in halves):
                continue
            private = [(aa[0], bb[0]) for aa, bb in halves if len(aa) == 1]
            if any(Counter(site[side] for site in private) != dict.fromkeys(wing, 2)
                   for side, wing in enumerate((left, right))):
                continue
            doubles = [(aa, bb) for aa, bb in halves if len(aa) == 2]
            if any(len({pair[side] for pair in doubles}) != len(doubles) for side in range(2)):
                continue
            assert len(private) == len(set(private)) == 6
            right = [next(bb for bb in right if (aa, bb) not in private) for aa in left]
            assert right[0] == right0 and len(set(right)) == 3
            observed = tuple(sorted(sum(1 << anchor for anchor, vertex in enumerate(left + right)
                                        if vertex in aa + bb) for aa, bb in halves))
            yield observed

    expected_grid = {1 << row | 8 << column
                     for row, column in it.product(range(3), repeat=2) if row != column}
    tables = tuple(move_tables(3))
    assert len(tables) == 4
    assert len({table[1 | 16] for table in tables}) == 4
    assert all(table[1 | 8] == 1 | 8 and table[1 | 2 | 32].bit_count() == 3 for table in tables)
    assert {table[1 | 2 | 32] for table in tables} == {35, 21, 28, 42}
    control_dir = Path('controls')
    counts = Counter()
    for order in (15, 16):
        extract = (control_dir / f'{order}.scan.set').read_text().splitlines()
        generated = (control_dir / f'{order}.gen.set').read_text().splitlines()
        scout = (SCOUT / f'small.{order}.extract.set').read_text().splitlines()
        assert extract == generated == scout
        assert len(extract) == {15: 24, 16: 0}[order]
        allowed = set()
        pairs = [3, 5, 6]
        for left in it.combinations(pairs, order - 14):
            for right in it.permutations(pairs, order - 14):
                if all(not aa & bb & 1 for aa, bb in zip(left, right)):
                    allowed.add(tuple(sorted(expected_grid | {aa | (bb << 3)
                                                             for aa, bb in zip(left, right)})))
        for row in extract:
            adj = parse_graph6(row)
            assert len(adj) == order and triangle_free(adj) and alpha(adj) <= 5
            marked = list(aligned_marks(adj))
            assert marked
            for supports in marked:
                assert supports in allowed
                for table in tables:
                    transformed = tuple(sorted(table[mask] for mask in supports))
                    assert transformed in allowed
                    assert {mask for mask in transformed if mask.bit_count() == 2} == expected_grid
                    counts['moved'] += 1
                counts['marks'] += 1
    assert counts == dict(moved=104, marks=26), counts
    print('24/0 canonical classes; 26 physical marks x 4 controls; asymmetric transpose check PASS', flush=True)


def coverage():
    start = cpu()
    check_actions()
    small_controls()
    catalog = all_schemes()
    groups = {tag: assignments(sides) for tag, (_, sides) in catalog.items()}
    assert all(set(groups[tag]) == independent_forward(*sides)
               for tag, (_, sides) in catalog.items())
    assert sum(map(len, groups.values())) == 169635
    print('30 forward/inverse exact roster equalities', flush=True)

    prior = set()
    for batch, size in [('m8.sample', 30), ('price.leaf+leaf.1', 32)]:
        records = read_jsonl(SCOUT / (batch + '.jsonl'))
        assert len(records) == size
        for number, rec in enumerate(records):
            group = tuple(sorted(rec['group']))
            assert not rec['possible'] and group in groups[rec['tag']]
            directory = SCOUT / 'proof' / f'{batch}.{number}'
            core = bound(directory, group, rec['extra'])
            prior.update(orbit_of_core(core))
    indexed = {(tag, tuple(group)) for tag, group in read_jsonl(SCOUT / 'cover.index.jsonl')}
    initial = {}
    for tag, alignments in groups.items():
        initial[tag] = expand(prior, posting(alignments), len(alignments))
    assert {(tag, groups[tag][rank]) for tag, bitmap in initial.items()
            for rank in bits(bitmap)} == indexed and len(indexed) == 10386

    source = groups[TAG]
    source_index = posting(source)
    old_uncovered = sorted(set(range(len(source))) - set(bits(initial[TAG])))
    pilot = rank_sample(old_uncovered)
    new_full, new_short = set(), set()
    source_masks = initial[TAG]
    for mode in ('direct', 'transfer', 'finish'):
        transfer_orbits = set()
        records = read_jsonl(PREV / mode / 'price.jsonl')
        expected = (sorted(set(range(len(source))) - set(bits(source_masks)))
                    if mode == 'finish' else pilot)
        assert [rec['rank'] for rec in records] == expected and all('sat' not in rec for rec in records)
        for rec in records:
            rank = rec['rank']
            core = bound(PREV / mode / str(rank), source[rank], rec['core'])
            if mode != 'transfer':
                assert core == source[rank]
            orbit = orbit_of_core(core)
            if mode == 'direct':
                source_masks |= 1 << rank
            if mode == 'transfer':
                transfer_orbits.update(orbit)
            if len(core) == 8:
                new_full.update(orbit)
            else:
                new_short.update(orbit)
        if mode == 'transfer':
            source_masks |= expand(transfer_orbits, source_index, len(source))
    assert len(new_full) and len(new_short)
    print('dual rebound: 62 scout + 1,357 round-16 receipts', flush=True)

    report = {}
    for tag, alignments in groups.items():
        count = len(alignments)
        index = posting(alignments)
        full = expand(new_full, index, count)
        short = expand(new_short, index, count)
        before = initial[tag]
        after = before | short | full
        if tag == TAG:
            assert after.bit_count() == count == 1828
        else:
            assert not full, tag
        report[tag] = dict(total=count, before=before.bit_count(), short=(short & ~before).bit_count(),
                           full=(full & ~(before | short)).bit_count(), covered=after.bit_count(),
                           uncovered=list(bits(((1 << count) - 1) ^ after)))
    write_json('coverage.json', report)
    print('coverage complete', f'{cpu() - start:.6f} CPU-s', flush=True)


def sample_plan():
    report = json.loads(Path('coverage.json').read_text())
    sorted_tags = sorted((tag for tag in report if tag != TAG),
                         key=lambda tag: (len(report[tag]['uncovered']), tag))
    assert len(sorted_tags) == 29
    sample = []
    for number, tag in enumerate(sorted_tags):
        uncovered = report[tag]['uncovered']
        maximum = len(uncovered) - 1
        assert maximum > 32
        offsets = {maximum // 32, maximum * (12 + (number * 5 % 9)) // 32,
                   maximum - maximum // 32}
        if number in (0, 14, 28):
            offsets.update((0, maximum // 4, maximum))
        sample.append(dict(tag=tag, uncovered=len(uncovered),
                           ids=[uncovered[offset] for offset in sorted(offsets)], offsets=sorted(offsets)))
    assert sum(len(item['ids']) for item in sample) == 96
    return dict(coverage_sha256=digest('coverage.json'), sample=sample)


def queue():
    registered = json.loads(Path('sample.json').read_text())
    assert registered == sample_plan()
    catalog = all_schemes()
    for row in registered['sample']:
        tag = row['tag']
        alignments = assignments(catalog[tag][1])
        for rank in row['ids']:
            yield tag, rank, alignments[rank]


def receipt_directory(tag, rank):
    assert re.fullmatch(r'[a-z+.0-9]+', tag) and rank >= 0
    return Path('pilot') / tag / str(rank)


def run_sample():
    start = cpu()
    byte_blocks = 0
    Path('pilot').mkdir(exist_ok=False)
    with Path('pilot/price.jsonl').open('x', buffering=1) as out:
        for tag, rank, group in queue():
            if cpu() - start >= 80 or byte_blocks >= 72 * 2**20:
                raise RuntimeError('sample guard, do not extend the queue')
            directory = receipt_directory(tag, rank)
            before = cpu()
            model = receipt(directory, group)
            after_proof = cpu()
            if model is not None:
                print(json.dumps(dict(tag=tag, rank=rank, model=check_model(group, model),
                                      cpu=after_proof - before)), file=out)
                raise RuntimeError('stop on local projection model')
            assert bound(directory, group, group) == group
            sizes = {name: (directory / name).stat().st_size for name in PARTS}
            hashes = {name: digest(directory / name) for name in PARTS}
            byte_blocks += sum((directory / name).stat().st_blocks * 512 for name in PARTS) + 4096
            print(json.dumps(dict(tag=tag, rank=rank, proof=after_proof - before,
                                  bind_archive=cpu() - after_proof, sizes=sizes, hashes=hashes)), file=out)
    print('production complete', f'{cpu() - start:.6f} CPU-s', byte_blocks, flush=True)


def replay_sample(output):
    start = cpu()
    records = read_jsonl(Path('pilot/price.jsonl'))
    receipts = []
    for (tag, rank, group), rec in zip(queue(), records, strict=True):
        assert (tag, rank) == (rec['tag'], rec['rank']) and 'model' not in rec
        directory = receipt_directory(tag, rank)
        before = cpu()
        assert {name: digest(directory / name) for name in PARTS} == rec['hashes']
        assert {name: (directory / name).stat().st_size for name in PARTS} == rec['sizes']
        assert bound(directory, group, group) == group
        receipts.append(dict(tag=tag, rank=rank, replay=cpu() - before))
    assert len(receipts) == 96
    write_json(output, receipts)
    print('archive replay PASS: 96/96 exact IDs', f'{cpu() - start:.6f} CPU-s', flush=True)


def summarize():
    coverage = json.loads(Path('coverage.json').read_text())
    produced = read_jsonl(Path('pilot/price.jsonl'))
    replayed = json.loads(Path('pilot/replay.json').read_text())
    timings = defaultdict(list)
    for made, bound in zip(produced, replayed, strict=True):
        assert (tag := made['tag']) == bound['tag'] and made['rank'] == bound['rank']
        timings[tag].append((made['proof'] + made['bind_archive'] + bound['replay'],
                             made['sizes']['sub.lrat'], sum(made['sizes'].values())))
    print('scheme\ttotal\told_bound\tnew_short\tnew_full\tuncovered\tfresh\tleft\tcpu_sum\tcpu_min\t'
          'cpu_mean\tcpu_max\tlrat_min\tlrat_max\treceipt_max\test_mean_h\test_max_h')
    totals = Counter()
    for tag, row in sorted(coverage.items(), key=lambda pair: (len(pair[1]['uncovered']), pair[0])):
        sample = timings[tag]
        raw, fresh = len(row['uncovered']), len(sample)
        remaining = raw - fresh
        values = [point[0] for point in sample] or [0]
        mean, high = sum(values) / len(values), max(values)
        lrat = [point[1] for point in sample] or [0]
        payload = [point[2] for point in sample] or [0]
        lower, upper = remaining * mean / 3600, remaining * high / 3600
        print(tag, row['total'], row['before'], row['short'], row['full'], raw, fresh, remaining,
              f'{sum(values):.6f}', f'{min(values):.6f}', f'{mean:.6f}', f'{high:.6f}',
              min(lrat), max(lrat), max(payload), f'{lower:.6f}', f'{upper:.6f}', sep='\t')
        totals.update(dict(raw=raw, fresh=fresh, left=remaining, cpu=sum(values),
                           est_mean_h=lower, est_max_h=upper,
                           mean_bytes=remaining * sum(payload) / len(payload),
                           max_bytes=remaining * max(payload)))
    assert totals['fresh'] == 96
    print('TOTAL', json.dumps(totals, sort_keys=True), sep='\t')
    sample_size = len(produced)
    for key in ('sub.lrat', 'full_receipt'):
        sizes = sorted(made['sizes'][key] if key != 'full_receipt' else sum(made['sizes'].values())
                       for made in produced)
        print('BYTES', key, *[sizes[math.ceil(sample_size * quantile) - 1] for quantile in (.5, .9, .95, .99, 1)],
              sep='\t')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('coverage', 'register', 'sample', 'replay', 'summary'))
    parser.add_argument('--audit', action='store_true')
    args = parser.parse_args()
    phase = args.phase
    assert not args.audit or phase == 'replay'
    if phase == 'register':
        assert not Path('sample.json').exists()
        write_json('sample.json', sample_plan())
    elif phase == 'replay':
        replay_sample('pilot/replay.audit.json' if args.audit else 'pilot/replay.json')
    else:
        dict(coverage=coverage, sample=run_sample, summary=summarize)[phase]()
