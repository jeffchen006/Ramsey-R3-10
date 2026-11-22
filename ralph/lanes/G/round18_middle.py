import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import itertools as it
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import zlib

from round16_grid import GRID, ROOT, SCOUT, assignments, read_jsonl
from round16_pilot import check_model, cpu, receipt
from round17_aligned import small_controls


TAG = 'middle+middle.2'
HOLES = (frozenset(((0, 3), (0, 4))), frozenset(((0, 1), (0, 2))))
WING = frozenset(range(10))
CROSS = frozenset((0, 5))
PARTS = ('sub.cnf', 'sub.lrat', 'witnesses.json')
MOVES = tuple(tuple(perm[anchor % 5] + 5 * ((int(anchor >= 5) + swap) % 2)
                    for anchor in range(10))
              for perm in ((0,) + tail for tail in it.permutations(range(1, 5)))
              for swap in (0, 1))
PREV = ROOT / 'scratch/G/round17'
BEFORE = ROOT / 'scratch/G/round16'
HERE = Path.cwd()


def write(path, data):
    path = Path(path)
    intermediate = path.with_suffix(path.suffix + '.tmp')
    intermediate.write_text(json.dumps(data, sort_keys=True, separators=(',', ':')) + '\n')
    intermediate.replace(path)


def load(path):
    return json.loads(Path(path).read_text())


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def mask(anchors):
    return sum(1 << anchor for anchor in anchors)


@lru_cache(maxsize=1024)
def literal(value):
    assert 0 <= value < 1024
    return frozenset(anchor for anchor in WING if value & (1 << anchor))


def moved(anchors, action):
    return frozenset(action[anchor] for anchor in anchors)


IMAGE = tuple(tuple(mask(moved(literal(value), action)) for value in range(1024))
              for action in MOVES)


def transport(group, move):
    return tuple(sorted(IMAGE[move][value] for value in group))


def footprint(masks):
    return tuple(frozenset(tuple(sorted(anchor % 5 for anchor in literal(value)
                                       if anchor // 5 == shore)) for value in masks)
                 for shore in (0, 1))


def census():
    sides = tuple(tuple(sorted(set(it.combinations(range(5), 2)) - holes)) for holes in HOLES)
    group_set = set()
    for perm in it.permutations(sides[1]):
        double = [frozenset(left + tuple(anchor + 5 for anchor in right))
                  for left, right in zip(sides[0], perm)]
        if any(CROSS <= site for site in double):
            continue
        if all(any({anchor, anchor + 5} <= site for site in double) for anchor in range(1, 5)):
            group_set.add(tuple(sorted(map(mask, double))))
    groups = sorted(group_set)
    catalog = load(SCOUT / 'schemes.json')[TAG][1]
    assert [sorted(map(mask, side)) for side in sides] == catalog
    assert tuple(groups) == assignments(catalog) and len(groups) == 16350
    rank_of = {group: rank for rank, group in enumerate(groups)}
    holes_as_masks = tuple(mask(pair) for pair in HOLES[0]) + tuple(
        mask(anchor + 5 for anchor in pair) for pair in HOLES[1])
    stabilizers = [number for number, action in enumerate(MOVES)
                   if {mask(moved(literal(value), action)) for value in holes_as_masks}
                   == set(holes_as_masks)]
    assert len(stabilizers) == 8 and stabilizers[0] == 0
    cross_orbit = {transport(holes_as_masks, move) for move in range(48)}
    assert len(cross_orbit) * len(stabilizers) == 48
    assert {MOVES[outer][MOVES[inner][anchor]] for outer in stabilizers for inner in stabilizers
            for anchor in (0, 5)} == {0, 5}
    assert all(tuple(MOVES[outer][MOVES[inner][anchor]] for anchor in range(10))
               in {MOVES[number] for number in stabilizers}
               for outer, inner in it.product(stabilizers, repeat=2))
    for number, action in enumerate(MOVES):
        assert set(action) == WING and moved(CROSS, action) == CROSS
        assert set(transport(GRID, number)) == set(GRID)
        assert (number in stabilizers) == (footprint(transport(groups[0], number)) ==
                                            footprint(groups[0]))
    assert transport((1 | (1 << 6), 3 | (24 << 5)), 1) == (34, 120)
    orbit_by_rank = {}
    orbits = {}
    fixed = Counter()
    for rank, group in enumerate(groups):
        row = [rank_of[transport(group, move)] for move in stabilizers]
        members = sorted(set(row))
        multiplicity = Counter(row)
        assert set(multiplicity.values()) == {len(stabilizers) // len(members)}
        fixed.update({str(move): 1 for move, image in zip(stabilizers, row) if rank == image})
        orbit_by_rank[rank] = members[0]
        if rank == members[0]:
            orbits[rank] = {str(member): stabilizers[row.index(member)] for member in members}
    assert sum(fixed.values()) == len(stabilizers) * len(orbits)
    for rep, orbit in orbits.items():
        assert set(map(int, orbit)) == {rank_of[transport(groups[rep], move)] for move in stabilizers}
        assert all(orbit_by_rank[int(member)] == rep for member in orbit)
    return groups, rank_of, stabilizers, orbits, orbit_by_rank, fixed


@lru_cache(maxsize=8)
def variables(order):
    pairs = tuple(it.combinations(range(order), 2))
    by_pair = {pair: index for index, pair in enumerate(pairs, 1)}
    triangles = tuple((-by_pair[first, second], -by_pair[first, third], -by_pair[second, third])
                      for first, second, third in it.combinations(range(order), 3))
    return pairs, by_pair, triangles


def semantic(directory, source):
    witness = load(directory / 'witnesses.json')
    sites = witness['sites']
    assert witness['wing'] == 1023 and tuple(sites[:20]) == GRID
    assert tuple(sorted(sites[20:])) == source and len(set(sites)) == len(sites)
    pairs, by_pair, triangles = variables(len(sites))
    expected = Counter(triangles)
    expected.update((-number,) for number, (first, second) in enumerate(pairs, 1)
                    if literal(sites[first]) & literal(sites[second]))
    for active, wing in witness['blocks']:
        indices, anchors = set(active), frozenset(wing)
        assert len(indices) == len(active) and all(0 <= idx < len(sites) for idx in indices)
        assert len(anchors) == len(wing) and anchors <= WING and not CROSS <= anchors
        assert len(anchors) + len(indices) == 10
        assert not anchors & frozenset().union(*(literal(sites[idx]) for idx in indices))
        expected[tuple(by_pair[pair] for pair in it.combinations(sorted(active), 2))] += 1
    header, *lines = (directory / 'sub.cnf').read_bytes().splitlines()
    assert header.split() == [b'p', b'cnf', str(len(pairs)).encode(), str(len(lines)).encode()]
    actual = Counter()
    for row in lines:
        *clause, final = map(int, row.split())
        assert final == 0 and all(clause)
        actual[tuple(clause)] += 1
    assert actual == expected, directory
    return witness


def check(directory, source):
    witness = semantic(directory, source)
    for binary, opts, marker in (
            ('lrat-check', [], b'c VERIFIED'),
            ('cake_lpr', ['--CML_HEAP_SIZE=128', '--CML_STACK_SIZE=32'], b's VERIFIED UNSAT')):
        result = subprocess.run(['timeout', '10s', ROOT / 'opt/bin' / binary, *opts, *PARTS[:2]],
                                cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        assert result.returncode == 0 and marker in result.stdout.splitlines(), (
            directory, binary, result.returncode, result.stdout[-500:])
    return witness


def physical(source, target, move, witness=None):
    action = MOVES[move]
    sites = GRID + tuple(source) if witness is None else tuple(witness['sites'])
    target_sites = GRID + tuple(target)
    assert moved(CROSS, action) == CROSS
    target_index = {value: idx for idx, value in enumerate(target_sites)}
    mapped = [target_index[IMAGE[move][site]] for site in sites]
    assert len(set(mapped)) == len(sites)
    assert all(index < 20 for index in mapped[:20]) and all(index >= 20 for index in mapped[20:])
    assert all(moved(literal(site), action) == literal(target_sites[index])
               for site, index in zip(sites, mapped))
    if witness is not None:
        for active, wing in witness['blocks']:
            mapped_anchors = moved(wing, action)
            mapped_sites = {mapped[index] for index in active}
            assert len(mapped_anchors) + len(mapped_sites) == 10 and not CROSS <= mapped_anchors
            assert not mapped_anchors & frozenset().union(
                *(literal(target_sites[index]) for index in mapped_sites))


def source_dirs():
    for batch in ('m8.sample', 'price.leaf+leaf.1'):
        for number, rec in enumerate(read_jsonl(SCOUT / (batch + '.jsonl'))):
            assert not rec['possible']
            yield 'scout', SCOUT / 'proof' / f'{batch}.{number}', tuple(sorted(rec['extra']))
    for rec in read_jsonl(BEFORE / 'transfer/price.jsonl'):
        assert 'sat' not in rec
        yield 'r16', BEFORE / 'transfer' / str(rec['rank']), tuple(sorted(rec['core']))


def audit():
    begin = cpu()
    small_controls()
    groups, rank_of, stabilizers, orbits, orbit_by_rank, fixed = census()
    by_support = defaultdict(set)
    for rank, group in enumerate(groups):
        for site in group:
            by_support[site].add(rank)
    owners = {}
    sources = Counter()
    covered_by = defaultdict(set)
    for stage, directory, core in source_dirs():
        checked_witness = None
        for move in range(48):
            image = transport(core, move)
            matches = set.intersection(*(by_support.get(site, set()) for site in image))
            if not matches:
                continue
            if checked_witness is None:
                checked_witness = check(directory, core)
                sources[stage] += 1
            physical(core, groups[min(matches)], move, checked_witness)
            covered_by[stage].update(matches)
            for rank in matches:
                physical(core, groups[rank], move)
                owners.setdefault(rank, [str(directory.relative_to(ROOT)), move, list(core)])
    frozen = load(PREV / 'coverage.json')[TAG]
    remaining = set(frozen['uncovered'])
    assert len(owners) == 660 and covered_by['scout'] == set(owners) and not covered_by['r16']
    assert set(range(len(groups))) - set(owners) == remaining
    old_reps = {orbit_by_rank[rank] for rank in owners}
    assert set(owners) == {int(rank) for rep in old_reps for rank in orbits[rep]}
    pilot_description = load(PREV / 'sample.json')
    assert sha((PREV / 'coverage.json').read_bytes()) == pilot_description['coverage_sha256']
    pilot = next(row['ids'] for row in pilot_description['sample'] if row['tag'] == TAG)
    records = {rec['rank']: rec for rec in read_jsonl(PREV / 'pilot/price.jsonl') if rec['tag'] == TAG}
    assert set(pilot) == set(records) and len(pilot) == 6 and set(pilot) <= remaining
    for rank in pilot:
        directory = PREV / 'pilot' / TAG / str(rank)
        group = groups[rank]
        payload = {name: (directory / name).read_bytes() for name in PARTS}
        assert {name: sha(value) for name, value in payload.items()} == records[rank]['hashes']
        assert {name: len(value) for name, value in payload.items()} == records[rank]['sizes']
        witness = check(directory, group)
        for move in stabilizers:
            image = transport(group, move)
            physical(group, image, move, witness)
            target = rank_of[image]
            assert target in remaining
            owners.setdefault(target, [str(directory.relative_to(ROOT)), move, list(group)])
    assert len(owners) == 708
    uncovered = {rep: orbit for rep, orbit in orbits.items() if rep not in owners}
    assert set(range(len(groups))) - set(owners) == {
        int(member) for orbit in uncovered.values() for member in orbit}
    assert len(uncovered) == 2024
    report = dict(stabilizers=stabilizers, fixed=dict(fixed), all_orbits=len(orbits),
                  all_weights=dict(Counter(map(len, orbits.values()))), sources=dict(sources),
                  old_scout=660, pilot=pilot, pilot_images=42, prior=owners, new=uncovered)
    write('orbits.json', report)
    print('physical cover', dict(zip(('all', 'old', 'pilot-extra', 'new-orbits', 'new-weight'),
                                    (len(groups), 660, 42, len(uncovered), len(groups)-len(owners)))),
          'old sources', dict(sources), 'all-orbit weights', report['all_weights'],
          'new weights', dict(Counter(map(len, uncovered.values()))), 'fixed', dict(fixed),
          f'{cpu()-begin:.4f} CPU-s', flush=True)


def make_plan():
    roster = load('orbits.json')
    groups, *_ = census()
    by_size = defaultdict(list)
    for rep, orbit in sorted(roster['new'].items(), key=lambda item: int(item[0])):
        by_size[len(orbit)].append(int(rep))
    assert set(by_size) <= {1, 2, 4, 8}
    measured = {}
    for size, ranks in by_size.items():
        count = min(len(ranks), {1: 12, 2: 14, 4: 22, 8: 48}[size])
        if count == len(ranks):
            for rank in ranks:
                measured[rank] = [size, 'all-small']
            continue
        assert count >= 8
        for rank in (ranks[0], ranks[-1]):
            measured[rank] = [size, 'rank-tail']
        def shape(rank):
            sites = GRID + groups[rank]
            degree = Counter(anchor for site in groups[rank] for anchor in literal(site))
            disjoint = sum(not (first & second) for first, second in it.combinations(sites, 2))
            return (disjoint, sum(val * val for val in degree.values()), rank)
        ranked_shapes = sorted(ranks, key=shape)
        for sequence in (ranked_shapes, ranked_shapes[::-1]):
            rank = next(rank for rank in sequence if rank not in measured)
            measured[rank] = [size, 'site-pair-tail']
        middle = [rank for rank in ranks if rank not in measured]
        count -= 4
        for position in range(count):
            rank = middle[(2 * position + 1) * len(middle) // (2 * count)]
            assert rank not in measured
            measured[rank] = [size, 'quantile']
    assert 1 <= len(measured) <= 96
    write('sample.json', dict(roster_sha=sha(Path('orbits.json').read_bytes()),
                              selected={rank: detail for rank, detail in sorted(measured.items())}))
    print('sample registration', len(measured), dict(Counter(size for size, _ in measured.values())),
          dict(Counter(reason for _, reason in measured.values())), flush=True)


def pack(directory, output):
    parts = [(directory / name).read_bytes() for name in PARTS]
    encoded = zlib.compress(struct.pack('>III', *map(len, parts)) + b''.join(parts), level=3)
    temporary = output.with_suffix('.tmp')
    temporary.write_bytes(encoded)
    temporary.replace(output)
    return dict(digest=sha(encoded), hashes=list(map(sha, parts)), sizes=list(map(len, parts)),
                packed=len(encoded))


def charged_bytes(size):
    return ((size + 4095) // 4096 + 1) * 4096


def unpack(archive, directory, record):
    encoded = archive.read_bytes()
    assert sha(encoded) == record['digest'] and len(encoded) == record['packed']
    stream = zlib.decompressobj()
    decoded = stream.decompress(encoded, 32 * 2**20)
    assert stream.eof and not stream.unconsumed_tail and not stream.unused_data
    sizes = struct.unpack_from('>III', decoded)
    assert list(sizes) == record['sizes'] and len(decoded) == 12 + sum(sizes)
    offset = 12
    for name, size, expected in zip(PARTS, sizes, record['hashes'], strict=True):
        part = decoded[offset:offset + size]
        assert sha(part) == expected
        (directory / name).write_bytes(part)
        offset += size


def inputs():
    roster = load('orbits.json')
    sample = load('sample.json')
    assert sha(Path('orbits.json').read_bytes()) == sample['roster_sha']
    catalog = load(SCOUT / 'schemes.json')[TAG][1]
    return roster, sample, assignments(catalog)


def job_queue(phase, start, end, roster, sample):
    if phase == 'sample':
        selected = sorted(map(int, sample['selected']))
        assert start is None and end is None and len(selected) <= 96
        return Path('sample'), selected
    todo = sorted(map(int, set(roster['new']) - set(sample['selected'])))
    assert 0 <= start < end <= len(todo) and end - start <= 192
    return Path('production') / f'{start:04d}-{end:04d}', todo[start:end]


def paths(directory, rank):
    return directory / f'{rank}.z'


def stage(direction, phase, start, end):
    stage_start = cpu()
    roster, sample, groups = inputs()
    directory, selected = job_queue(phase, start, end, roster, sample)
    stage_root = HERE / 'stage'
    stage_root.mkdir(exist_ok=True)
    if direction == 'make':
        directory.mkdir(parents=True, exist_ok=False)
        records = None
        journal = directory / 'make.jsonl'
    else:
        records = read_jsonl(directory / 'make.jsonl')
        assert [row['rank'] for row in records] == selected and all('model' not in row for row in records)
        assert {path.name for path in directory.glob('*.z')} == {paths(directory, rank).name for rank in selected}
        journal = directory / 'replay.jsonl'
    print(direction, str(directory), len(selected), flush=True)
    allocated = 0
    with journal.open('x', buffering=1) as output:
        for slot, rank in enumerate(selected):
            before = cpu()
            stats = dict(rank=rank, weight=len(roster['new'][str(rank)]))
            with tempfile.TemporaryDirectory(dir=stage_root) as staging:
                raw = Path(staging) / 'literal'
                archive = paths(directory, rank)
                if direction == 'make':
                    model = receipt(raw, groups[rank])
                    if model is not None:
                        stats.update(model=check_model(groups[rank], model), cpu=cpu()-before)
                        print(json.dumps(stats), file=output)
                        raise RuntimeError('stop: local projection model')
                    stats.update(pack(raw, archive))
                    allocated += charged_bytes(stats['packed'])
                    if allocated > 104 * 2**20:
                        raise RuntimeError('stop: checkpoint allocation guard')
                else:
                    rec = records[slot]
                    raw.mkdir()
                    unpack(archive, raw, rec)
                    witness = check(raw, groups[rank])
                    for member, move in roster['new'][str(rank)].items():
                        physical(groups[rank], groups[int(member)], move,
                                 witness if phase == 'sample' else None)
                    stats['digest'] = rec['digest']
                    stats['checkers'] = ['lrat-check', 'cake_lpr']
            stats['cpu'] = cpu() - before
            print(json.dumps(stats, sort_keys=True), file=output)
    print(direction, 'PASS', str(directory), len(selected), f'{cpu()-stage_start:.6f} CPU-s', flush=True)


def paired(directory):
    produced = read_jsonl(directory / 'make.jsonl')
    replayed = read_jsonl(directory / 'replay.jsonl')
    for make, playback in zip(produced, replayed, strict=True):
        assert make['rank'] == playback['rank'] and make['digest'] == playback['digest']
        assert make['weight'] == playback['weight'] and playback['checkers'] == ['lrat-check', 'cake_lpr']
        yield dict(rank=make['rank'], weight=make['weight'], cpu=make['cpu']+playback['cpu'],
                   size=charged_bytes(make['packed']), raw=sum(make['sizes']),
                   staged=sum(map(charged_bytes, make['sizes'])),
                   digest=make['digest'])


def estimate():
    roster, sample, _ = inputs()
    sample_stats = list(paired(Path('sample')))
    assert {rec['rank'] for rec in sample_stats} == set(map(int, sample['selected']))
    all_stats = list(sample_stats)
    for directory in sorted(Path('production').glob('*')):
        all_stats.extend(paired(directory))
    counted = {row['rank'] for row in all_stats}
    assert len(counted) == len(all_stats)
    remaining = Counter(len(orbit) for rank, orbit in roster['new'].items() if int(rank) not in counted)
    used_cpu = used_cpu_times()
    used_bytes = disk_used()
    forecast = dict(cpu_used=used_cpu, allocated=used_bytes, priced=len(all_stats),
                    remaining=dict(remaining), left=sum(remaining.values()))
    for metric, used, unit in [('cpu', used_cpu, 1), ('size', used_bytes, 2**20)]:
        margin = 38 * unit
        high, mean = 0., 0.
        for weight, count in remaining.items():
            observations = [row[metric] for row in all_stats if row['weight'] == weight]
            assert observations
            high += max(observations) * count
            mean += sum(observations) / len(observations) * count
        forecast[f'{metric}_mean_end'] = used + mean + margin
        forecast[f'{metric}_high_end'] = used + 1.20 * high + margin
        forecast[f'{metric}_max_observed'] = max(row[metric] for row in all_stats)
    forecast['go'] = forecast['cpu_high_end'] < 2160 and forecast['size_high_end'] < 512 * 2**20
    forecast['peak_raw_staging_observed'] = max(row['staged'] + row['size'] for row in all_stats)
    print(json.dumps(forecast, sort_keys=True), flush=True)
    assert forecast['go'], 'stop: end-to-end CPU or scratch forecast over budget'


def used_cpu_times():
    total = 0.
    for path in Path('.').glob('*.time'):
        lines = path.read_text().splitlines()
        if lines:
            user, system, *_ = lines[-1].split()
            total += float(user) + float(system)
    return total


def disk_used():
    directories = [Path('.')] + [path for path in Path('.').rglob('*') if not path.is_symlink()]
    stats = [(path, path.stat()) for path in directories]
    return sum(max(result.st_blocks * 512, charged_bytes(result.st_size) if path.is_file() else 4096)
               for path, result in stats)


def reconcile(full):
    roster, sample, groups = inputs()
    fresh_groups, _, stabilizers, orbits, _, _ = census()
    assert tuple(fresh_groups) == groups and stabilizers == roster['stabilizers']
    assert all({int(rank): move for rank, move in orbit.items()}
               == {int(rank): move for rank, move in orbits[int(rep)].items()}
               for rep, orbit in roster['new'].items())
    covered = {}
    for target, (source, move, core) in roster['prior'].items():
        assert (ROOT / source / 'sub.lrat').is_file()
        physical(core, groups[int(target)], move)
        covered[int(target)] = ['inherited', source, move]
    assert len(covered) == 708
    checked, staged = set(), set()
    for directory in [Path('sample'), *sorted(Path('production').glob('*'))]:
        if not (directory / 'make.jsonl').exists():
            continue
        produced = {row['rank']: row for row in read_jsonl(directory / 'make.jsonl') if 'digest' in row}
        assert not staged & set(produced)
        staged.update(produced)
        if not (directory / 'replay.jsonl').exists():
            continue
        for entry in read_jsonl(directory / 'replay.jsonl'):
            rep = entry['rank']
            assert rep not in checked and entry['digest'] == produced[rep]['digest']
            assert entry['checkers'] == ['lrat-check', 'cake_lpr']
            assert sha(paths(directory, rep).read_bytes()) == entry['digest']
            checked.add(rep)
            for target, move in roster['new'][str(rep)].items():
                rank = int(target)
                assert rank not in covered and move in stabilizers
                physical(groups[rep], groups[rank], move)
                covered[rank] = [rep, str(paths(directory, rep)), move]
    open_ids = sorted(set(range(len(groups))) - set(covered))
    open_reps = sorted(set(map(int, roster['new'])) - checked)
    assert set(open_ids) == {int(rank) for rep in open_reps for rank in roster['new'][str(rep)]}
    write('reconciliation.json', dict(checked=covered, staged_only=sorted(staged-checked),
                                      open_ids=open_ids, open_reps=open_reps))
    if full:
        assert not open_ids and len(checked) == 2024 and len(covered) == 16350
    print('orbit-to-proof ledger', dict(checked=len(checked), labelled=len(covered),
          open_orbits=len(open_reps), open_ids=len(open_ids)), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('audit', 'register', 'make', 'replay', 'estimate', 'reconcile', 'complete'))
    parser.add_argument('part', nargs='?', choices=('sample', 'production'))
    parser.add_argument('lo', nargs='?', type=int)
    parser.add_argument('hi', nargs='?', type=int)
    args = parser.parse_args()
    if args.phase in {'make', 'replay'}:
        stage(args.phase, args.part, args.lo, args.hi)
    elif args.phase in ('reconcile', 'complete'):
        reconcile(args.phase == 'complete')
    else:
        dict(audit=audit, register=make_plan, estimate=estimate)[args.phase]()
