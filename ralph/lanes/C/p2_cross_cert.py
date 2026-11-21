#!/usr/bin/env python3
import argparse
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import subprocess
import time


def decode(text):
    order = ord(text[0]) - 63
    assert 0 < order < 63 and len(text) == 1 + (order * (order - 1) // 2 + 5) // 6
    graph = [0] * order
    cursor = 0
    for second in range(order):
        for first in range(second):
            if (ord(text[1 + cursor // 6]) - 63) & (32 >> (cursor % 6)):
                edge(graph, first, second)
            cursor += 1
    return graph


def bits(word):
    while word:
        low = word & -word
        yield low.bit_length() - 1
        word ^= low


def mask(vertices):
    return sum(1 << vertex for vertex in vertices)


def edge(graph, first, second):
    assert first != second
    graph[first] |= 1 << second
    graph[second] |= 1 << first


def project(graph, keep):
    new = [0] * len(keep)
    for first, second in combinations(range(len(keep)), 2):
        if (graph[keep[first]] >> keep[second]) & 1:
            edge(new, first, second)
    return new


def combine(left, root_left, shared_left, right, root_right, shared_right, columns_right,
            left_pack, right_pack):
    columns_left = list(bits(left[root_left]))
    assert len(columns_left) == len(columns_right) and mask(columns_right) == right[root_right]
    cap, width = len(columns_left), len(left_pack)
    assert len(shared_left) == len(shared_right) and len(right_pack) == width
    order = len(left) + len(right) - cap - len(shared_left) + 2 * width
    fixed = [0] * order
    root_count = 2
    wing_left = list(range(root_count + cap, root_count + cap + width))
    wing_right = list(range(wing_left[-1] + 1, wing_left[-1] + 1 + width))
    images = []
    private = []
    first_shared = wing_right[-1] + 1
    next_private = first_shared + len(shared_left)
    common = mask(range(root_count, root_count + cap)) | mask(range(first_shared, next_private))
    for root, graph, shared, columns, wing, pack in (
            (0, left, shared_left, columns_left, wing_left, left_pack),
            (1, right, shared_right, columns_right, wing_right, right_pack)):
        own_root = [root_left, root_right][root]
        image = {own_root: root}
        image.update({vertex: root_count + index for index, vertex in enumerate(columns)})
        image.update({vertex: first_shared + index for index, vertex in enumerate(shared)})
        start = next_private
        for vertex in range(len(graph)):
            if vertex not in image:
                image[vertex] = next_private
                next_private += 1
        private.append(list(range(start, next_private)))
        assert mask(image.values()) & common == common
        assert set(bits(pack[0] | pack[1] | (pack[2] if width == 3 else 0))) == {
            vertex for vertex in image if image[vertex] >= start}
        for first, second in combinations(range(len(graph)), 2):
            if (graph[first] >> second) & 1:
                edge(fixed, image[first], image[second])
            elif (1 << image[first]) & common and (1 << image[second]) & common:
                assert not (fixed[image[first]] >> image[second]) & 1
        for wing_vertex, row in zip(wing, pack):
            edge(fixed, root, wing_vertex)
            for neighbor in bits(row):
                edge(fixed, wing_vertex, image[neighbor])
        images.append(image)
    assert order == next_private
    for first in wing_left:
        for second in wing_right:
            edge(fixed, first, second)
    for graph, image in zip((left, right), images):
        assert project(fixed, [image[vertex] for vertex in range(len(graph))]) == graph
    return fixed, *private, images, wing_left, wing_right


def independence_clauses(fixed, variable, limit):
    clauses = set()

    def visit(available, remaining, chosen, clause):
        if not remaining:
            clauses.add(tuple(sorted(clause)))
            return
        while available.bit_count() >= remaining:
            low = available & -available
            current = low.bit_length() - 1
            available ^= low
            new_clause = tuple(variable[other, current] for other in chosen if (other, current) in variable)
            visit(available & ~fixed[current], remaining - 1, chosen + (current,), clause + new_clause)

    visit((1 << len(fixed)) - 1, limit, (), ())
    return sorted(clauses)


def encode(fixed, rows, columns, degree):
    order = len(fixed)
    variable = {}
    incident = [[] for _ in fixed]
    for first in rows:
        for second in columns:
            if not fixed[first] & fixed[second]:
                assert first < second
                variable[first, second] = number = len(variable) + 1
                incident[first].append(number)
                incident[second].append(number)
    clauses = []
    for vertex in range(order):
        need = degree - fixed[vertex].bit_count()
        domain = incident[vertex]
        if not 0 <= need <= len(domain):
            clauses.append(())
            continue
        clauses.extend(tuple(-literal for literal in row) for row in combinations(domain, need + 1))
        clauses.extend(combinations(domain, len(domain) - need + 1))
    for first, second, third in combinations(range(order), 3):
        pairs = ((first, second), (first, third), (second, third))
        if any(not (fixed[vertex] >> other) & 1 and (vertex, other) not in variable for vertex, other in pairs):
            continue
        clauses.append(tuple(-variable[pair] for pair in pairs if pair in variable))
    alpha = independence_clauses(fixed, variable, degree + 1)
    clauses.extend(alpha)
    return variable, clauses, len(alpha)


def read_windows(path):
    windows = {}
    for line in path.read_text().splitlines():
        source, root, text = line.split('\t')
        key = int(source), int(root)
        assert key not in windows
        windows[key] = decode(text)
    return windows


def load_boundary(row, windows):
    fields = row.split('\t')
    first, root_first, shared = map(int, fields[:3])
    second, root_second, share_one, share_two = map(int, fields[3:7])
    right_columns = list(map(int, fields[7].rstrip(',').split(',')))
    packs = list(map(int, fields[8:]))
    assert len(packs) == 6
    other_shared = [share_one, share_two]
    return combine(windows[first, root_first], root_first, list(bits(shared)), windows[second, root_second],
                   root_second, other_shared, right_columns, packs[:3], packs[3:])[:3]


def write_cnf(path, variables, clauses):
    with path.open('x') as stream:
        stream.write(f'p cnf {len(variables)} {len(clauses)}\n')
        for clause in clauses:
            stream.write(' '.join(map(str, (*clause, 0))) + '\n')


def process(binary, arguments, seconds):
    try:
        return subprocess.run(['timeout', '--foreground', '--kill-after=2', str(seconds), str(binary), *map(str, arguments)],
                              capture_output=True, text=True, check=False)
    except (OSError, UnicodeError) as error:
        raise RuntimeError((binary, arguments)) from error


def terminal(bin_dir, cnf, lrat, seconds, verify, textual=False):
    if not verify:
        assert not lrat.exists()
        options = ['-q', '--lrat'] + (['--no-binary'] if textual else [])
        result = process(bin_dir / 'cadical', [*options, cnf, lrat], seconds)
        if result.returncode == 124:
            return 'TIMEOUT', '-'
        if result.returncode in (137, -9, 143, -15):
            return 'KILLED', '-'
        if result.returncode == 10 and 's SATISFIABLE' in result.stdout:
            return 'SAT', result.stdout
        assert result.returncode == 20 and 's UNSATISFIABLE' in result.stdout, (cnf, result)
    check = process(bin_dir / 'cake_lpr', [cnf, lrat], 20)
    assert check.returncode == 0 and 's VERIFIED' in check.stdout, (cnf, check)
    if textual:
        check = process(bin_dir / 'lrat-check', [cnf, lrat], 20)
        assert check.returncode == 0 and 'c VERIFIED' in check.stdout, (cnf, check)
    return 'VERIFIED', sha256(lrat.read_bytes()).hexdigest()


def run(args):
    args.work.mkdir(exist_ok=True)
    windows = read_windows(args.windows)
    cases = args.cases.read_text().splitlines()
    assert cases and len(set(cases)) == len(cases)
    for index in range(args.begin, min(len(cases), args.end), args.step):
        start = time.monotonic()
        fixed, rows, columns = load_boundary(cases[index], windows)
        variables, clauses, n_alpha = encode(fixed, rows, columns, 9)
        base = args.work / f'pack-{index:05d}'
        cnf = base.with_suffix('.cnf')
        lrat = (args.proof_dir or args.work) / base.with_suffix('.lrat').name
        write_cnf(cnf, variables, clauses)
        status, data = terminal(args.bin, cnf, lrat, args.seconds, args.verify, args.textual)
        if status == 'SAT':
            base.with_suffix('.model').write_text(data)
            data = sha256(data.encode()).hexdigest()
        hashes = [sha256(cases[index].encode()).hexdigest(), sha256(cnf.read_bytes()).hexdigest(), data]
        print(index, len(variables), len(clauses), n_alpha, status, *hashes, f'{time.monotonic()-start:.4f}',
              sep='\t', flush=True)


def control(args):
    seen = 0
    args.work.mkdir(exist_ok=True)
    for graph in map(decode, args.census.read_text().splitlines()):
        assert len(graph) == 22 and all(row.bit_count() == 6 for row in graph)
        for first, second in combinations(range(len(graph)), 2):
            common = graph[first] & graph[second]
            if common.bit_count() != 4:
                continue
            wing_l, wing_r = graph[first] ^ common, graph[second] ^ common
            if any(graph[vertex] & wing_r != wing_r for vertex in bits(wing_l)):
                continue
            roots = (1 << first) | (1 << second)
            core = ((1 << len(graph)) - 1) & ~(roots | common | wing_l | wing_r)
            rows_l, rows_r = [graph[vertex] & core for vertex in bits(wing_l)], [graph[vertex] & core for vertex in bits(wing_r)]
            shared = core & ~(rows_l[0] | rows_l[1] | rows_r[0] | rows_r[1])
            assert not (rows_l[0] | rows_l[1]) & (rows_r[0] | rows_r[1])
            incl_l = list(bits((1 << first) | common | shared | rows_l[0] | rows_l[1]))
            incl_r = list(bits((1 << second) | common | shared | rows_r[0] | rows_r[1]))
            fixed, rows, columns, images, wing_left, wing_right = combine(
                project(graph, incl_l), incl_l.index(first), [incl_l.index(vertex) for vertex in bits(shared)],
                project(graph, incl_r), incl_r.index(second), [incl_r.index(vertex) for vertex in bits(shared)],
                [incl_r.index(vertex) for vertex in bits(common)],
                [mask(incl_l.index(vertex) for vertex in bits(row)) for row in rows_l],
                [mask(incl_r.index(vertex) for vertex in bits(row)) for row in rows_r])
            flip = {**{image: incl_l[orig] for orig, image in images[0].items()},
                    **{image: incl_r[orig] for orig, image in images[1].items()},
                    **dict(zip(wing_left, bits(wing_l))), **dict(zip(wing_right, bits(wing_r)))}
            assert len(flip) == len(graph) and len(set(flip.values())) == len(graph)
            variables, clauses, _ = encode(fixed, rows, columns, 6)
            planted = {number if graph[flip[one]] & (1 << flip[two]) else -number
                       for (one, two), number in variables.items()}
            assert all(any(literal in planted for literal in clause) for clause in clauses)
            positive = args.work / f'positive-{seen}.cnf'
            write_cnf(positive, variables, clauses)
            solved = process(args.bin / 'cadical', ['-q', positive], 15)
            assert solved.returncode == 10 and 's SATISFIABLE' in solved.stdout
            vertex = next(vertex for vertex in rows if fixed[vertex].bit_count() < 6)
            negative = args.work / f'negative-{seen}.cnf'
            write_cnf(negative, variables, clauses + [(-number,) for (one, _), number in variables.items() if one == vertex])
            status, _ = terminal(args.bin, negative, negative.with_suffix('.lrat'), 15, False)
            assert status == 'VERIFIED'
            seen += 1
    assert seen == 7
    print(f'PASS C22 planted assignments and SATs={seen}, bad-degree checked negative controls={seen}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Proof checking for a fixed complementary window join')
    sub = parser.add_subparsers(dest='mode', required=True)
    production = sub.add_parser('run')
    calibration = sub.add_parser('control')
    for command in (production, calibration):
        command.add_argument('bin', type=Path)
        command.add_argument('work', type=Path)
    calibration.add_argument('census', type=Path)
    production.add_argument('windows', type=Path)
    production.add_argument('cases', type=Path)
    production.add_argument('--begin', type=int, default=0)
    production.add_argument('--end', type=int, default=1 << 60)
    production.add_argument('--step', type=int, default=1)
    production.add_argument('--seconds', type=int, default=30)
    production.add_argument('--verify', action='store_true')
    production.add_argument('--proof-dir', type=Path)
    production.add_argument('--textual', action='store_true')
    arguments = parser.parse_args()
    if arguments.mode == 'run' and arguments.proof_dir:
        assert arguments.verify and arguments.proof_dir.resolve() != arguments.work.resolve()
    (run if arguments.mode == 'run' else control)(arguments)
