#!/usr/bin/env python3
"""Bind a fresh degree-five expansion to all frozen source and rooted class keys."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations_with_replacement
from pathlib import Path
from subprocess import run


ROOT = Path(__file__).resolve().parents[3]
BIN = ROOT / 'opt/bin'
ARCHIVE = ROOT / 'scratch/G/round5/d5'
CORE_SHA = 'a2173308cd8dcd8fd4698b2bd28a003866d235c0d17895c45e50d7708019bce4'
CLASS_SHA = '053c5236bbcbb114a63b5540979ed19d29e7a25b2a2c7c91041e9a3d4b664026'
LEVELS = {123: 5, 124: 44, 125: 149, 126: 266, 127: 294, 128: 184, 129: 41, 130: 1}
RECEIPT_HEADER = b'id\tmaximal\tpair_edges\tfull_tuples\tenvelopes\tnodes\tcompletions\tunique\tcpu_s'


def graph6(adjacency):
    bits = [bool(adjacency[high] & (1 << low))
            for high in range(len(adjacency)) for low in range(high)]
    bits += [False] * (-len(bits) % 6)
    return bytes([63 + len(adjacency)] + [63 + sum(int(bits[start + index]) << (5 - index) for index in range(6))
                                          for start in range(0, len(bits), 6)])


def decode(row):
    assert all(63 <= digit <= 126 for digit in row)
    order = row[0] - 63
    assert 1 <= order <= 33 and len(row) == 1 + (order * (order - 1) // 2 + 5) // 6
    bits = [(digit - 63) & (1 << shift) for digit in row[1:] for shift in reversed(range(6))]
    result = [0] * order
    position = 0
    for high in range(order):
        for low in range(high):
            if bits[position]:
                result[high] |= 1 << low
                result[low] |= 1 << high
            position += 1
    assert not any(bits[position:])
    return result


def has_independent(graph, size):
    def search(mask, left):
        if left <= 1:
            return bool(mask) or left == 0
        while mask.bit_count() >= left:
            vertex = (mask & -mask).bit_length() - 1
            mask ^= 1 << vertex
            if search(mask & ~graph[vertex], left - 1):
                return True
        return False

    return search((1 << len(graph)) - 1, size)


def no_triangle(graph):
    return not any(graph[first] & graph[second]
                   for first in range(len(graph)) for second in range(first) if graph[first] & (1 << second))


def relabel(graph, vertices):
    return [sum(bool(graph[vertex] & (1 << other)) << index for index, other in enumerate(vertices))
            for vertex in vertices]


def canonical(rows, partition=None):
    options = ['-q'] + ([] if partition is None else [f'-f{partition}'])
    result = run([BIN / 'labelg', *options], input=b''.join(row + b'\n' for row in rows),
                 capture_output=True, check=True).stdout.splitlines()
    assert len(result) == len(rows)
    return result


def frozen(name, digest, count):
    data = (ARCHIVE / name).read_bytes()
    rows = data.splitlines()
    assert sha256(data).hexdigest() == digest and len(rows) == len(set(rows)) == count
    assert canonical(rows) == rows
    return rows


def valid(graph, alpha, low, high, emin, emax):
    degrees = [row.bit_count() for row in graph]
    return (low <= min(degrees) and max(degrees) <= high and emin <= sum(degrees) // 2 <= emax
            and no_triangle(graph) and not has_independent(graph, alpha + 1))


def literal_extension(core, attachments):
    slots = len(attachments)
    size = len(core)
    root = size + slots
    graph = core.copy() + [column | (1 << root) for column in attachments] + [((1 << slots) - 1) << size]
    for index, column in enumerate(attachments, size):
        for vertex in range(size):
            if column & (1 << vertex):
                graph[vertex] |= 1 << index
    return graph


def rows_by_id(path, source_ids):
    result = {source: {} for source in source_ids}
    for line in path.read_bytes().splitlines():
        source, edge, key = line.split(b'\t')
        source, edge = int(source), int(edge)
        assert key not in result[source]
        result[source][key] = edge
    return result


def receipts(path, results):
    header, *rows = path.read_bytes().splitlines()
    assert header == RECEIPT_HEADER
    parsed = {}
    for line in rows:
        *counts, timing = line.split(b'\t')
        source, maximal, pairs, tuples, envelopes, nodes, completions, unique = map(int, counts)
        assert source not in parsed and unique == len(results[source])
        assert 0 <= unique <= completions <= nodes and 0 <= envelopes <= tuples and pairs <= maximal * (maximal + 1) // 2
        assert float(timing) >= 0
        parsed[source] = (maximal, pairs, tuples, envelopes, nodes, completions, unique)
    assert list(parsed) == list(results)
    return parsed


def groupdiff(expected, actual):
    assert expected.keys() == actual.keys()
    return [(source, relation, edge, plain, marked)
            for source in expected
            for relation, difference in (('missing', expected[source] - actual[source]),
                                         ('extra', actual[source] - expected[source]))
            for edge, plain, marked in sorted(difference)]


def small(executable):
    raw_cores = run([BIN / 'geng', '-qt', '5'], capture_output=True, check=True).stdout.splitlines()
    cores = [decode(row) for row in raw_cores if not has_independent(decode(row), 4)]
    sources = {index: graph for index, graph in enumerate(cores, 1)}
    assert len(raw_cores) == 14 and len(sources) > 1
    input_data = b''.join(str(source).encode() + b'\t' + graph6(core) + b'\n' for source, core in sources.items())
    profiles = [(3, 4, 0, 16), (2, 4, 10, 11), (3, 4, 12, 12)]
    literal = {bounds: {source: {} for source in sources} for bounds in profiles}
    repeats = partials = 0
    for source, core in sources.items():
        for columns in combinations_with_replacement(range(1 << 5), 3):
            graph = literal_extension(core, columns)
            edges = sum(row.bit_count() for row in graph) // 2
            passes = [bounds for bounds in profiles if valid(graph, 4, *bounds)]
            if not passes:
                continue
            repeats += len(set(columns)) < len(columns)
            partials += any(any(not (column & (1 << vertex) or core[vertex] & column)
                                for vertex in range(5)) for column in columns)
            for bounds in passes:
                literal[bounds][source][graph6(graph)] = edges
    assert repeats and partials
    all_small = run([BIN / 'geng', '-qt', '9'], capture_output=True, check=True).stdout.splitlines()
    for index, bounds in enumerate(profiles):
        output = run([executable, '4', '3', *map(str, bounds)], input=input_data, capture_output=True, check=True)
        Path(f'small{index}.raw.tsv').write_bytes(output.stdout)
        Path(f'small{index}.receipt.tsv').write_bytes(output.stderr)
        Path(f'small{index}.literal.tsv').write_bytes(b''.join(
            str(source).encode() + b'\t' + str(edges).encode() + b'\t' + row + b'\n'
            for source, bucket in literal[bounds].items() for row, edges in sorted(bucket.items())))
        fresh = rows_by_id(Path(f'small{index}.raw.tsv'), sources)
        receipts(Path(f'small{index}.receipt.tsv'), fresh)
        assert fresh == literal[bounds], (bounds, [(key, len(fresh[key]), len(literal[bounds][key])) for key in sources])
        expected = {key for key in canonical([row for row in all_small
                                              if 3 in map(int.bit_count, decode(row)) and valid(decode(row), 4, *bounds)])}
        got = set(canonical([row for bucket in fresh.values() for row in bucket]))
        assert expected == got and bool(got) == (index < 2), (
            bounds, len(expected), len(got), sorted(expected - got), sorted(got - expected))
        print(f'small {bounds}: all {len(sources)} cores, {sum(map(len, fresh.values()))} literal rows, '
              f'{len(got)} full-census classes, {sum(bool(value) for value in fresh.values())} positive cores')
        if got:
            first = next(source for source in sources if fresh[source])
            known = min(fresh[first])
            del fresh[first][known]
            assert fresh != literal[bounds] and set(literal[bounds][first]) - set(fresh[first]) == {known}
    assert any(not value for archive in literal.values() for value in archive.values())
    print(f'small corpus: {repeats} repeated-column and {partials} proper-subcolumn assignments; '
          'both removed-row controls detected')


def read_expected(sources, archived):
    lookup = {row: source for source, row in sources.items()}
    residue, rerooted, owners = [], [], []
    class_edges = Counter()
    for plain in archived:
        graph = decode(plain)
        assert len(graph) == 33 and min(map(int.bit_count, graph)) == 5
        edges = sum(map(int.bit_count, graph)) // 2
        assert valid(graph, 8, 5, 8, 0, 130)
        class_edges[edges] += 1
        for root in range(33):
            if graph[root].bit_count() != 5:
                continue
            rest = [vertex for vertex in range(33) if vertex != root and not graph[root] & (1 << vertex)]
            adjacent = [vertex for vertex in range(33) if graph[root] & (1 << vertex)]
            residue.append(graph6(relabel(graph, rest)))
            rerooted.append(graph6(relabel(graph, rest + adjacent + [root])))
            owners.append((edges, plain))
    assert class_edges == LEVELS
    expected = {source: set() for source in sources}
    for core, marked, (edges, plain) in zip(canonical(residue), canonical(rerooted, 'a^32b'), owners, strict=True):
        expected[lookup[core]].add((edges, plain, marked))
    print(f'archive: {len(archived)} unrooted classes; {len(owners)} explicit degree-five roots, '
          f'{sum(map(len, expected.values()))} rooted orbits across {len(sources)} sources', flush=True)
    return expected


def prepare(sources, expected):
    assert all(expected.values())
    pilot = set(range(1, 119, 17)) | {118, min(expected, key=lambda key: (len(expected[key]), key)),
                                    min(expected, key=lambda key: (-len(expected[key]), key))}
    for level in (123, 130):
        pilot.add(min(source for source in expected if any(edge == level for edge, _, _ in expected[source])))
    for group, subset in [('pilot', pilot), ('tail', sources.keys() - pilot), ('all', sources)]:
        Path(f'{group}.in.tsv').write_bytes(b''.join(str(source).encode() + b'\t' + sources[source] + b'\n'
                                                    for source in sorted(subset)))
    print(f'pilot source IDs: {sorted(pilot)} ({len(pilot)}/{len(sources)})')


def hash_rows(rows):
    return sha256(b''.join(row + b'\n' for row in sorted(rows))).hexdigest()


def compare(group, sources, expected):
    selected = {}
    for line in Path(f'{group}.in.tsv').read_bytes().splitlines():
        source, row = line.split(b'\t')
        source = int(source)
        assert source not in selected and row == sources[source]
        selected[source] = row
    assert list(selected) == sorted(selected)
    if group == 'all':
        assert selected == sources
    induced = {source: decode(row) for source, row in selected.items()}
    expected = {source: expected[source] for source in selected}
    raw = rows_by_id(Path(f'{group}.raw.tsv'), selected)
    audit = receipts(Path(f'{group}.receipt.tsv'), raw)
    payload = [(source, edge, row) for source, bucket in raw.items() for row, edge in bucket.items()]
    rows = [row for _, _, row in payload]
    unrooted = canonical(rows)
    rooted = canonical(rows, 'a^32b')
    plain_checked = set()
    found, records = ({key: set() for key in selected} for _ in range(2))
    non_mtf = repeated = partial = 0
    for (source, edges, row), plain, marked in zip(payload, unrooted, rooted, strict=True):
        core = induced[source]
        graph = decode(row)
        assert len(graph) == 33 and graph[-1] == ((1 << 5) - 1) << 27
        attachments = [row_mask & ((1 << 27) - 1) for row_mask in graph[27:32]]
        assert attachments == sorted(attachments)
        assert all(row_mask & ~((1 << 27) - 1) == 1 << 32 for row_mask in graph[27:32])
        assert relabel(graph, list(range(27))) == core
        assert edges == sum(map(int.bit_count, graph)) // 2
        if plain not in plain_checked:
            assert valid(graph, 8, 5, 8, 0, 130)
            plain_checked.add(plain)
        non_mtf += any(not ((graph[first] & graph[second]) or (graph[first] & (1 << second)))
                       for first in range(33) for second in range(first))
        repeated += len(set(attachments)) < 5
        partial += any(any(not (column & (1 << vertex) or core[vertex] & column) for vertex in range(27))
                       for column in attachments)
        found[source].add((edges, plain, marked))
        records[source].add(row)
    expected_classes = {plain: edges for bucket in expected.values() for edges, plain, _ in bucket}
    found_classes = {plain: edges for bucket in found.values() for edges, plain, _ in bucket}
    discrepancies = groupdiff(expected, found)
    Path(f'{group}.diff.tsv').write_bytes(b''.join(
        f'{source}\t{relation}\t{edge}\t'.encode() + plain + b'\t' + marked + b'\n'
        for source, relation, edge, plain, marked in discrepancies))
    assert not discrepancies and found_classes == expected_classes, (group, discrepancies[:5])
    Path(f'{group}.classes.g6').write_bytes(b''.join(row + b'\n' for row in sorted(found_classes)))
    with Path(f'{group}.coverage.tsv').open('w') as output:
        print('source\tcore_sha\tmaximal\tpairs\tpairwise_tuples\tenvelopes\tbranches\tenvelope_models\t'
              'unique_sorted\trooted\tunrooted\tedge_hist_rooted\trooted_sha\tlabelled_sha', file=output)
        for source in selected:
            by_edge = Counter(edges for edges, _, _ in found[source])
            rooted_sha = hash_rows({marked for _, _, marked in found[source]})
            local_classes = len({plain for _, plain, _ in found[source]})
            print(source, sha256(selected[source]).hexdigest(), *audit[source], len(found[source]), local_classes,
                  ','.join(f'{edges}:{count}' for edges, count in sorted(by_edge.items())), rooted_sha,
                  hash_rows(records[source]), sep='\t', file=output)
    absent = min(expected_classes)
    mutated = {source: {entry for entry in bucket if entry[1] != absent} for source, bucket in found.items()}
    missing = groupdiff(expected, mutated)
    assert missing and all(relation == 'missing' and plain == absent for _, relation, _, plain, _ in missing)
    false_sources = sorted({source for source, _, _, _, _ in missing})
    print(f'{group}: detected removal of global class {absent.decode()!r} at sources {false_sources}, '
          f'{len(missing)} rooted keys; coherent mutation leaves all other classes unchanged')
    if group == 'all':
        incidence = defaultdict(list)
        for source, bucket in found.items():
            for entry in sorted(bucket):
                incidence[entry[1]].append((source, entry))
        source, role = next(roles[0] for _, roles in sorted(incidence.items()) if len(roles) > 1)
        mutated = {key: bucket.copy() for key, bucket in found.items()}
        mutated[source].remove(role)
        assert {entry[1] for bucket in mutated.values() for entry in bucket} == set(found_classes)
        assert groupdiff(expected, mutated) == [(source, 'missing', *role)]
        print(f'all: detected one removed rooted role at source {source} while all {len(found_classes)} '
              'unrooted keys remained')
    print(f'{group}: {len(selected)} exact sources; {len(payload)} labelled multisets, '
          f'{sum(map(len, found.values()))} rooted orbits, {len(found_classes)} unrooted classes; '
          f'non-MTF/repeated/non-maximal labelled = {non_mtf}/{repeated}/{partial}')
    print(f'{group}: unrooted edge histogram {sorted(Counter(found_classes.values()).items())}')


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['small', 'prepare', 'pilot', 'all'])
    parser.add_argument('executable', nargs='?', type=Path)
    args = parser.parse_args()
    if args.mode == 'small':
        assert args.executable
        small(args.executable.resolve())
        return
    sources = dict(enumerate(frozen('survivors.g6', CORE_SHA, 118), 1))
    expected = read_expected(sources, frozen('full_e130.can.g6', CLASS_SHA, 984))
    if args.mode == 'prepare':
        prepare(sources, expected)
    else:
        compare(args.mode, sources, expected)


if __name__ == '__main__':
    main()
