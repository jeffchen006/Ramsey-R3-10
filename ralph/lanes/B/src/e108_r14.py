"""Price a deterministic tranche of the supplied reducible 32/e108 list."""

import argparse
from collections import Counter
from contextlib import contextmanager
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import resource
import subprocess
from time import monotonic

from e107_core_proofs import graph, make_core, root, verify, verify_clique
from root_core import check_witness, induced


CATALOGUE = Path('work/e108_r5/reducible.g6')
CATALOGUE_SHA = 'c816d7f02fd929d4503a39cf3b7c0fed5f9d79e5fe542389661932f967f43f91'
TOTAL = 2_102_271
TRANCHE = 32_768
PILOT = Path('work/e108_r6_pilot')
PILOT_SHA = '70857b0546f02fa68017366afd7ec23aa27a42308b2413d7e2988482fa14bb83'
PILOT_CLIQUE_SHA = '33c914fd359fb262b5343e2e8f2de4a652cfb73a5a0fe534a36c8f3ebd226a3a'
CHECKERS = [('lrat-check', 'c VERIFIED'), ('cake_lpr', 's VERIFIED UNSAT')]


def digest(data):
    return sha256(data).hexdigest()


def cpu():
    usages = [resource.getrusage(kind) for kind in (resource.RUSAGE_SELF, resource.RUSAGE_CHILDREN)]
    return sum(usage.ru_utime + usage.ru_stime for usage in usages)


@contextmanager
def stage(name):
    started_cpu, started_wall = cpu(), monotonic()
    yield
    print(f'stage {name}: cpu={cpu()-started_cpu:.5f} wall={monotonic()-started_wall:.5f}', flush=True)


def run(seconds, command, data=b'', allowed=(0,)):
    result = subprocess.run(['timeout', '--kill-after=2s', f'{seconds}s', *command],
                            input=data, capture_output=True)
    if result.returncode not in allowed:
        raise RuntimeError((command, result.returncode, result.stdout[-2000:], result.stderr[-2000:]))
    return result


def bind(path, data, write):
    if write:
        path.write_bytes(data)
    else:
        assert path.read_bytes() == data, f'byte binding failed: {path}'


def sample(out, write):
    positions = [1 + ((2 * item + 1) * TOTAL) // (2 * TRANCHE) for item in range(TRANCHE)]
    target = iter(positions)
    selected = next(target)
    keys = []
    previous = b''
    source_hash = sha256()
    count = 0
    with CATALOGUE.open('rb') as stream:
        for count, record in enumerate(stream, 1):
            assert len(record) == 85 and record[:1] == b'_' and record[-1:] == b'\n' and previous < record
            previous = record
            source_hash.update(record)
            if count == selected:
                keys.append(record)
                selected = next(target, None)
    assert count == TOTAL and len(keys) == TRANCHE and selected is None
    assert source_hash.hexdigest() == CATALOGUE_SHA
    bind(out / 'input.g6', b''.join(keys), write)
    bind(out / 'source-ids.tsv', ''.join(f'{local}\t{pos}\n' for local, pos in enumerate(positions, 1)).encode(), write)
    print(f'bound source {count} keys SHA256={CATALOGUE_SHA}; tranche={len(keys)} IDs={positions[0]}..{positions[-1]}')
    return positions, keys


def read_masks(data, count, width):
    output = {}
    previous = 0
    for line in data.splitlines():
        identifier, *fields = line.split()
        index = int(identifier)
        assert previous < index <= count and len(fields) == width
        output[index] = tuple(int(field, 16) for field in fields)
        previous = index
    return output


def scan(keys, width):
    result = run(45, ['build/demand_clique', str(width)], b''.join(keys))
    masks = read_masks(result.stdout, len(keys), width)
    assert result.stderr.startswith(f'demand cliques: in={len(keys)} witnesses={len(masks)} '.encode())
    return result.stdout, masks


def check_cover(keys, masks, complement):
    for index, demands in masks.items():
        verify_clique(graph.parse_graph6(keys[index - 1].decode().strip()), 7, demands)
    missing = [index for index in range(1, len(keys) + 1) if index not in masks]
    expected = b''.join(f'{index}\t'.encode() + keys[index - 1] for index in missing)
    assert expected == complement, 'exact clique complement mismatch'
    return missing


def check_proof_index(directory, expected):
    assert {path.name for path in directory.iterdir()} == {f'{index:07d}.lrat' for index in expected}, 'proof index mismatch'


def adverse(label, action):
    try:
        action()
    except AssertionError:
        print(f'adverse {label}: rejected')
    else:
        raise RuntimeError(f'adverse {label}: unexpectedly passed')


def independent_core(text, pins):
    rows = graph.parse_graph6(text)
    order, degree = len(rows), 7
    assert graph.triangle_free(rows) and graph.alpha(rows) < 9
    neighbours = [tuple(vertex for vertex in range(order) if mask & (1 << vertex)) for mask in rows]
    rows_of_vars = [list(range(row * order + 1, (row + 1) * order + 1)) for row in range(degree)]
    clauses = []
    for variables in rows_of_vars:
        for vertex, adjacent in enumerate(neighbours):
            clauses.append([variables[vertex], *(variables[other] for other in adjacent)])
            for other in adjacent:
                if vertex < other:
                    clauses.append([-variables[vertex], -variables[other]])
    for vertex, adjacent in enumerate(neighbours):
        attachment = [variables[vertex] for variables in rows_of_vars]
        clauses.append(attachment)
        free = 9 - len(adjacent)
        if free < 0:
            clauses.append([])
        else:
            clauses.extend(tuple(-var for var in selected) for selected in combinations(attachment, free + 1))
    allocated = order * degree
    for left, right in combinations(range(order), 2):
        if right in neighbours[left] or rows[left] & rows[right]:
            continue
        witnesses = list(range(allocated + 1, allocated + degree + 1))
        allocated += degree
        for variables, witness in zip(rows_of_vars, witnesses, strict=True):
            clauses.extend(([-witness, variables[left]], [-witness, variables[right]]))
        clauses.append(witnesses)
    if pins is not None:
        verify_clique(rows, 6, pins)
        for variables, demand in zip(rows_of_vars, pins, strict=True):
            clauses.extend([literal] for vertex, literal in enumerate(variables) if demand & (1 << vertex))
    return (f'p cnf {allocated} {len(clauses)}\n' + ''.join(' '.join(map(str, (*clause, 0))) + '\n' for clause in clauses)).encode()


def controls(out):
    inputs = (root / 'ralph/lanes/G/root_certs/canon32_e104.g6').read_bytes().splitlines(keepends=True)
    _, witnesses = scan(inputs, 8)
    assert len(witnesses) == len(inputs) == 39
    assert check_cover(inputs, witnesses, b'') == []
    print('control e104: 39/39 checked eight-demand cliques')
    adverse('zero demand', lambda: check_cover(inputs, {**witnesses, 1: (0, *witnesses[1][1:])}, b''))
    adverse('dropped clique without matching complement', lambda: check_cover(
        inputs, {index: masks for index, masks in witnesses.items() if index != 1}, b''))
    adverse('missing LRAT index', lambda: check_proof_index(out, [123]))

    bipartite = [sum(1 << site for site in range(7, 16))] * 7 + [127] * 9
    assert graph.alpha(bipartite) == 9 and graph.triangle_free(bipartite)
    for vertex in range(7, 16):
        check_witness(bipartite, vertex, 9)
    exterior = induced(bipartite, sum(1 << site for site in range(8, 16)))
    literal = graph.to_graph6(exterior)
    assert scan([(literal + '\n').encode()], 8)[1] == {}
    cnf = independent_core(literal, None)
    assert cnf == make_core(literal, None).encode()
    cnf_path = out / 'positive.cnf'
    cnf_path.write_bytes(cnf)
    solver_path = root / 'opt/bin/cadical'
    result = run(15, [solver_path, cnf_path], allowed=(10,))
    assert b's SATISFIABLE' in result.stdout.splitlines()
    print('control K7,9: all nine d7 roots satisfy every necessary clause; independently rebuilt exterior SAT')

    exoo = graph.parse_graph6(Path('ref/exoo39.g6').read_text().strip())
    for left, right in combinations(range(len(exoo)), 2):
        if not (exoo[left] & (1 << right) or exoo[left] & exoo[right]):
            exoo[left] |= 1 << right
            exoo[right] |= 1 << left
    assert len(exoo) == 39 and graph.triangle_free(exoo) and graph.alpha(exoo) == 9
    for vertex in range(len(exoo)):
        check_witness(exoo, vertex, 9)
    print('control saturated Exoo39: all 39 actual rooted assignments satisfy the necessary clauses')

    old_proof = next(iter(sorted(Path('work/e108_r6_unit/proofs').glob('*.lrat'))))
    old_local = int(old_proof.stem)
    old_entries = dict(line.split('\t') for line in (PILOT / 'clique.missing.tsv').read_text().splitlines())
    old_positions = list(map(int, old_entries))
    pin_table = read_masks((PILOT / 'pins.tsv').read_bytes(), len(old_positions), 7)
    pins = pin_table[1 + old_positions.index(old_local)]
    old_text = old_entries[str(old_local)]
    old_cnf = independent_core(old_text, pins)
    assert old_cnf == make_core(old_text, pins).encode()
    old_cnf_path = out / 'negative.cnf'
    old_cnf_path.write_bytes(old_cnf)
    bad_proof = out / 'truncated.lrat'
    bad_proof.write_bytes(b'')
    for checker, marker in CHECKERS:
        verify(checker, old_cnf_path, old_proof, marker)
        for label, cnf in [('truncated-proof', old_cnf_path), ('wrong-sat-cnf', cnf_path)]:
            changed = bad_proof if label == 'truncated-proof' else old_proof
            result = subprocess.run(['timeout', '12s', root / 'opt/bin' / checker, cnf, changed],
                                    capture_output=True, text=True)
            assert result.returncode not in (124, 137) and marker not in result.stdout.splitlines()
            print(f'adverse {checker} {label}: rejected (rc={result.returncode})')


def check_pilot_overlap(out, positions, keys, masks, write):
    old_keys = (PILOT / 'input.g6').read_bytes()
    old_witnesses = (PILOT / 'clique.cliq.tsv').read_bytes()
    assert digest(old_keys) == PILOT_SHA and digest(old_witnesses) == PILOT_CLIQUE_SHA
    old_indexes = {key: index for index, key in enumerate(old_keys.splitlines(keepends=True), 1)}
    old_masks = read_masks(old_witnesses, len(old_indexes), 8)
    assert len(old_indexes) == 4096 and len(old_masks) == 3923
    overlaps, counts = [], Counter()
    for local, (position, key) in enumerate(zip(positions, keys, strict=True), 1):
        if key not in old_indexes:
            continue
        old = old_indexes[key]
        assert masks.get(local) == old_masks.get(old)
        disposition = 'clique' if local in masks else 'proof'
        overlaps.append(f'{local}\t{position}\t{old}\t{disposition}\n')
        counts[disposition] += 1
    bind(out / 'pilot-overlap.tsv', ''.join(overlaps).encode(), write)
    print(f'old pilot overlap: {len(overlaps)} = {counts["clique"]} clique + {counts["proof"]} proof')


def proofs(out, work, positions, keys, missing, pins, write):
    directory = out / 'proofs'
    receipt = out / 'proofs.tsv'
    sizes, counts = [], Counter()
    if write:
        directory.mkdir()
        archived = []
    else:
        archived = [line.split('\t') for line in receipt.read_text().splitlines()]
        assert len(archived) == len(missing)
    expected = [positions[local - 1] for local in missing]
    if not write:
        check_proof_index(directory, expected)
    cnf_path = work / 'core.cnf'
    phase = 'production' if write else 'replay'
    index_path = receipt if write else work / 'replay.tsv'
    with index_path.open('w') as index, (work / f'{phase}-timing.tsv').open('w') as timing:
        timing.write('source\tmethod\tcnf_cpu\tproof_cpu\tcheck_cpu\ttotal_cpu\twall\tproof_bytes\n')
        for ordinal, (local, position) in enumerate(zip(missing, expected, strict=True)):
            start_cpu, start_wall = cpu(), monotonic()
            pin = pins.get(ordinal + 1)
            text = keys[local - 1].decode().strip()
            cnf = make_core(text, pin).encode() if write else independent_core(text, pin)
            cnf_path.write_bytes(cnf)
            proof = directory / f'{position:07d}.lrat'
            encoded_cpu = cpu()
            if write:
                result = run(5, ['build/unit_lrat', cnf_path, proof], allowed=(10, 20))
                method = 'rup'
                if result.returncode == 10:
                    method = 'cadical'
                    run(10, ['prlimit', '--cpu=6:7', '--', root / 'opt/bin/cadical', '--lrat', '--no-binary',
                             cnf_path, proof], allowed=(20,))
            else:
                method = archived[ordinal][-1]
                assert method in {'rup', 'cadical'}
            generated_cpu = cpu()
            proof_bytes = proof.read_bytes()
            fields = [str(local), str(position), digest(cnf), digest(proof_bytes), str(len(proof_bytes)),
                      str(int(pin is not None)), method]
            if not write:
                assert fields == archived[ordinal], f'CNF/proof/receipt mismatch at source ID {position}'
            for checker, marker in CHECKERS[:1] if write else CHECKERS:
                verify(checker, cnf_path, proof, marker)
            end_cpu = cpu()
            index.write('\t'.join(fields) + '\n')
            timing.write(f'{position}\t{method}\t{encoded_cpu-start_cpu:.6f}\t{generated_cpu-encoded_cpu:.6f}'
                         f'\t{end_cpu-generated_cpu:.6f}\t{end_cpu-start_cpu:.6f}'
                         f'\t{monotonic()-start_wall:.6f}\t{len(proof_bytes)}\n')
            sizes.append(len(proof_bytes))
            counts[method] += 1
            if (ordinal + 1) % 256 == 0:
                print(f'{phase}: {ordinal+1}/{len(missing)} proofs checked', flush=True)
    cnf_path.unlink()
    check_proof_index(directory, expected)
    print(f'{phase}: {len(missing)} proofs, {len(pins)} pinned; {dict(counts)}, '
          f'proof bytes sum={sum(sizes)} max={max(sizes, default=0)}')


def process(out, work, write):
    with stage('bind_sample'):
        positions, keys = sample(out, write)
    if write:
        with stage('validity_and_reducibility'):
            data = b''.join(keys)
            result = run(45, ['build/audit_duals', '32', '108', '9', str(TRANCHE)], data)
            print((result.stdout + result.stderr).decode().strip())
            result = run(45, ['build/irreducible', '9'], data)
            assert not result.stdout and result.stderr.startswith(f'irreducible: in={len(keys)} out=0 '.encode())
            print(result.stderr.decode().strip())
        with stage('demand_clique_scan'):
            witness_data, masks = scan(keys, 8)
            bind(out / 'cliques.tsv', witness_data, True)
            complement = b''.join(f'{local}\t'.encode() + key for local, key in enumerate(keys, 1) if local not in masks)
            bind(out / 'complement.tsv', complement, True)
    else:
        complement = (out / 'complement.tsv').read_bytes()
        masks = read_masks((out / 'cliques.tsv').read_bytes(), len(keys), 8)
    with stage(('production' if write else 'replay') + '_clique_verification'):
        missing = check_cover(keys, masks, complement)
        check_pilot_overlap(out, positions, keys, masks, write)
        print(f'verified exact partition: {len(masks)} eight-cliques + {len(missing)} complementary roots')
    if write:
        with stage('pin_scan'):
            pin_data, pins = scan([keys[local - 1] for local in missing], 7)
            bind(out / 'pins.tsv', pin_data, True)
    else:
        pins = read_masks((out / 'pins.tsv').read_bytes(), len(missing), 7)
    with stage('proof_production' if write else 'independent_cnf_dual_lrat_replay'):
        proofs(out, work, positions, keys, missing, pins, write)


def main():
    if not __debug__:
        raise RuntimeError('assertions must be enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('control', 'tranche', 'replay'))
    parser.add_argument('out', type=Path)
    parser.add_argument('replay', type=Path, nargs='?')
    args = parser.parse_args()
    if args.mode == 'control':
        args.out.mkdir()
        with stage('controls'):
            controls(args.out)
        return
    if args.replay is None:
        parser.error('tranche and replay require a new replay directory')
    if args.mode == 'tranche':
        args.out.mkdir()
        process(args.out, args.out, True)
    args.replay.mkdir()
    process(args.out, args.replay, False)
    assert (args.out / 'proofs.tsv').read_bytes() == (args.replay / 'replay.tsv').read_bytes()
    print('PASS: exact deterministic tranche with independently rebuilt CNFs and dual-checked LRATs', flush=True)


if __name__ == '__main__':
    main()
