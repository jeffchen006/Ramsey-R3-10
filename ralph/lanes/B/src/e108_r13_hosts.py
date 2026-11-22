import itertools
import os
from pathlib import Path
import re
import resource
import sys

from critical_witness import edges, parse_graph6
from e108_r13 import BUILD, KNOWN, ROOT, SCOUT, TOOLS, WORK, Budget, canon, digest, lines, validate


ASTRA = Path('../ideas/astra_N')
N = Path('../ideas/r012_N')
SOURCE = Path('../critic/r12/N-e122-children.g6')


def edge_set(row):
    return set(edges(parse_graph6(row.decode().strip())))


def card_edges(host, removed):
    return {(left - (left > removed), right - (right > removed))
            for left, right in host if removed not in (left, right)}


def descent(budget, out, name, bound, target, parents):
    count = len(parents.splitlines())
    raw, stderr = budget.run([out / 'descend', str(bound), str(target)], parents)
    assert re.fullmatch(rb'sources %d cards \d+ nodes \d+ critical_leaves %d cpu [\d.]+\n'
                        % (count, len(raw.splitlines())), stderr)
    (out / f'{name}.raw').write_bytes(raw)
    (out / f'{name}.log').write_bytes(stderr)
    keys = canon(budget, raw)
    (out / f'{name}.keys').write_bytes(keys)
    return keys


def control(budget, out):
    val = ROOT / 'gluing/val'
    small = (val / 'r3_4_8.g6').read_bytes()
    reference, _ = budget.run([TOOLS / 'pickg', '-qe6', val / 'r3_4_7.g6'])
    assert len(reference.splitlines()) == 1
    assert descent(budget, out, 'small_positive', 3, 6, small) == canon(budget, reference)
    adverse = small.splitlines(keepends=True)[0]
    chosen = list(itertools.combinations(range(7), 4))
    fours = [set(itertools.combinations(independent, 2)) for independent in chosen]
    checks = 0
    host = edge_set(adverse)
    for drop in range(8):
        card = card_edges(host, drop)
        for remaining in itertools.combinations(card, 5):
            checks += 1
            assert any(set(remaining).isdisjoint(four) for four in fours)
    assert checks > 0 and not descent(budget, out, 'small_adverse', 3, 5, adverse)

    archived = (ASTRA / 'sample122.g6').read_bytes()
    expected, *_ = (ASTRA / 'hold.raw').read_bytes().splitlines(keepends=True)
    expected_key = canon(budget, expected)
    assert expected_key in lines(KNOWN.read_bytes())
    subgraph = edge_set(expected)
    matches = [(index, graph, drop) for index, graph in enumerate(archived.splitlines(keepends=True), 1)
               for host_edges in [edge_set(graph)] for drop in range(33)
               if subgraph <= card_edges(host_edges, drop)]
    assert matches
    index, host, drop = matches[0]
    control_key = canon(budget, host)
    validate(budget, out, 'held_out.host', control_key, 33, 122, False)
    validate(budget, out, 'held_out.expected', expected_key, 32, 108, True)
    (out / 'held_out.host.g6').write_bytes(host)
    (out / 'held_out.expected.g6').write_bytes(expected_key)
    index_path = out / 'held_out.witness.tsv'
    added_back = sorted(card_edges(edge_set(host), drop) - subgraph)
    index_path.write_text(f'archive_row\tdeleted_vertex_0based\tcard_edges_to_remove_0based\n'
                          f'{index}\t{drop}\t{added_back}\n')
    assert expected_key in lines(descent(budget, out, 'held_out', 8, 108, host))
    print(f'PASS: exact small positive, adverse zero ({checks} brute labelled 5-edge subsets), '
          f'archived 33/e122 held-out positive # {index}, drop {drop}.', flush=True)


def inventory(budget, out):
    children, _ = budget.run([BUILD / 'edgeup'], (N / 'handoff.g6').read_bytes())
    assert len(children.splitlines()) == 116
    candidate = canon(budget, children)
    assert candidate == canon(budget, SOURCE.read_bytes()) and len(lines(candidate)) == 77
    validate(budget, out, 'children', candidate, 33, 122, False)
    old_files = [ASTRA / name for name in
                 ('sample121.g6', 'sample122.g6', 'stratified.g6', 'sample5.g6', 'five33.g6')]
    old_files += [ROOT / 'ralph/lanes/G/root_certs/complete33_le119.g6', N / 'handoff.g6']
    old_files += [WORK / f'e108_r8_hosts/{level}.hosts.g6' for level in (120, 121, 122, 123)]
    candidates = lines(candidate)
    previous = set()
    with (out / 'inventory.tsv').open('w') as receipt:
        receipt.write('path\tsha256\trows\te122\tintersection\n')
        for path in old_files + [SCOUT / 'strong33.in']:
            source = path.read_bytes()
            picked, _ = budget.run([TOOLS / 'pickg', '-qe122'], source)
            keys = lines(canon(budget, picked))
            intersection = keys & candidates
            receipt.write(f'{path}\t{digest(source)}\t{len(source.splitlines())}\t'
                          f'{len(keys)}\t{len(intersection)}\n')
            if path in old_files:
                previous.update(keys)
    (out / 'prior.122.g6').write_bytes(b''.join(sorted(previous)))
    overlap = candidates & previous
    (out / 'overlap.g6').write_bytes(b''.join(sorted(overlap)))
    fresh = b''.join(sorted(candidates - previous))
    (out / 'fresh.122.g6').write_bytes(fresh)
    print(f'Source: 116 legal edge additions, 77 exact hosts; '
          f'{len(previous)} named prior direct e122 hosts, {len(overlap)} overlaps, {len(lines(fresh))} fresh.', flush=True)
    return fresh


def main(out):
    budget = Budget(60)
    source_dir = ROOT / 'ralph/lanes/B/src'
    budget.run(['gcc', '-O3', '-march=native', '-Wall', '-Wextra', '-I', source_dir,
                '-o', out / 'descend', ASTRA / 'descend.c'])
    fresh = inventory(budget, out)
    control(budget, out)
    assert not (lines(canon(budget, (out / 'held_out.host.g6').read_bytes())) & lines(fresh))
    if not fresh:
        print('STOP: no fresh hosts; zero searches on candidate hosts.', flush=True)
        return
    rows = len(fresh.splitlines())
    projection = rows * 1.123 / 327
    print(f'Priced before target run: {projection:.3f} CPU-s descent using scout critical-host '
          'rate (descriptive, not a bound); 60 CPU-s total cap.', flush=True)
    before = budget.spent()
    outputs = descent(budget, out, 'target', 8, 108, fresh)
    elapsed = budget.spent() - before
    count = len(lines(outputs))
    validate(budget, out, 'target', outputs, 32, 108, True)
    known = lines(KNOWN.read_bytes())
    assert len(known) == 1875
    combined = b''.join(sorted(known | lines(outputs)))
    validate(budget, out, 'novelty', combined, 32, 108, False)
    novel = lines(outputs) - known
    (out / 'novel.g6').write_bytes(b''.join(sorted(novel)))
    print(f'PASS host pilot: fresh={rows} distinct_critical={count} novel={len(novel)} '
          f'descent+canon={elapsed:.3f} CPU-s total={budget.spent():.3f} CPU-s', flush=True)
    if not novel:
        print('STOP: zero new critical e108 keys; no larger host wave.', flush=True)


if __name__ == '__main__':
    os.environ.update(LC_ALL='C', PYTHONDONTWRITEBYTECODE='1')
    resource.setrlimit(resource.RLIMIT_AS, (16 << 30, 16 << 30))
    destination = Path(sys.argv[1])
    destination.mkdir()
    os.environ['TMPDIR'] = str(destination.resolve())
    main(destination)
