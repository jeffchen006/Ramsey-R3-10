"""Certify the supplied reducible 32/e108 list at MTF d7 roots."""

import argparse
from array import array
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from mmap import ACCESS_READ, mmap
from pathlib import Path
from struct import unpack_from
import subprocess
import sys
from time import monotonic

from e108_r14 import (
    CATALOGUE, CATALOGUE_SHA, CHECKERS, PILOT, PILOT_CLIQUE_SHA, PILOT_SHA,
    TOTAL, TRANCHE, adverse, check_cover, check_proof_index, controls, cpu,
    digest, graph, independent_core, induced, make_core, read_masks, root, run, scan, verify,
    verify_clique,
)
from root_core import clauses_for, dimacs, vertices


OLD14 = Path('work/e108_r14')
OLD6 = Path('work/e108_r6_unit')
COUNT = 2_065_471
MODULUS = 257
RECORD = 85
ARCHIVE = ('cliques.tsv', 'proofs.tsv', 'proofs.pack')
ENTRY = Path(__file__).resolve()
MAX_CHILD_OVERRUN = 32
MAX_STORAGE = 2 * 1024**3
MAX_PROOF = 16 * 1024**2
MAX_PACK = 24 * 1024**2


def hash_file(path):
    with path.open('rb') as stream:
        return sha256_file(stream)


def sha256_file(stream):
    accumulator = sha256()
    for block in iter(lambda: stream.read(1024**2), b''):
        accumulator.update(block)
    return accumulator.hexdigest()


def old_cover():
    old6 = (PILOT / 'input.g6').read_bytes()
    masks6 = (PILOT / 'clique.cliq.tsv').read_bytes()
    assert digest(old6) == PILOT_SHA and digest(masks6) == PILOT_CLIQUE_SHA
    rows6 = old6.splitlines(keepends=True)
    rows14 = (OLD14 / 'input.g6').read_bytes().splitlines(keepends=True)
    assert len(rows6) == len(set(rows6)) == 4096 and len(rows14) == len(set(rows14)) == TRANCHE
    kinds6 = read_masks(masks6, len(rows6), 8)
    kinds14 = read_masks((OLD14 / 'cliques.tsv').read_bytes(), len(rows14), 8)
    proofs6 = [idx for idx in range(1, len(rows6) + 1) if idx not in kinds6]
    assert len(proofs6) == 173 and len(kinds14) == 31407
    check_proof_index(OLD6 / 'proofs', proofs6)
    for phase in ('production', 'replay'):
        lines = (OLD6 / f'{phase}.log').read_text().splitlines()
        footer = {'production': "counts 173 {'rup': 149, 'cadical': 24, 'replay': 0}",
                  'replay': "counts 173 {'rup': 0, 'cadical': 0, 'replay': 173}"}
        assert lines.pop() == footer[phase] and len(lines) == len(proofs6)
        actual = []
        for idx, line in zip(proofs6, lines, strict=True):
            ident, cnf_hash, proof_hash, method = line.split()
            assert int(ident) == idx and len(cnf_hash) == 64
            assert hash_file(OLD6 / 'proofs' / f'{idx:07d}.lrat') == proof_hash
            assert method in ({'rup', 'cadical'} if phase == 'production' else {'replay'})
            actual.append((ident, cnf_hash, proof_hash))
        if phase == 'production':
            produced = actual
        else:
            assert produced == actual
    rank14 = [1 + ((2 * idx + 1) * TOTAL) // (2 * TRANCHE) for idx in range(TRANCHE)]
    assert (OLD14 / 'source-ids.tsv').read_text().splitlines() == [
        f'{local}\t{rank}' for local, rank in enumerate(rank14, 1)
    ]
    rows = {key: (None, idx, 'C6' if idx in kinds6 else 'P6') for idx, key in enumerate(rows6, 1)}
    overlap = Counter()
    for idx, (key, rank) in enumerate(zip(rows14, rank14, strict=True), 1):
        kind = 'C14' if idx in kinds14 else 'P14'
        if key in rows:
            _, prior_idx, prior_kind = rows[key]
            assert prior_kind[0] == kind[0] and kinds6.get(prior_idx) == kinds14.get(idx)
            overlap[kind[0]] += 1
        rows[key] = (rank, idx, kind)
    assert overlap == {'C': 61, 'P': 3} and len(rows) == 36800
    return rows


def source_partition():
    old_keys = old_cover()
    adopted = {}
    ranks = array('I')
    assert ranks.itemsize == 4 and sys.byteorder == 'little'
    accumulator = sha256()
    previous = b''
    with CATALOGUE.open('rb') as source:
        for rank, key in enumerate(source, 1):
            assert len(key) == RECORD and key[:1] == b'_' and key[-1:] == b'\n' and previous < key
            accumulator.update(key)
            previous = key
            old = old_keys.pop(key, None)
            if old is None:
                ranks.append(rank)
            else:
                expected_rank, local, kind = old
                assert expected_rank is None or rank == expected_rank
                adopted[rank] = (kind, local)
    assert not old_keys and rank == TOTAL and len(ranks) == COUNT
    assert accumulator.hexdigest() == CATALOGUE_SHA
    return adopted, ranks


def prepare(base):
    assert base.is_dir() and not (base / 'plan.json').exists()
    report = subprocess.run(
        ['timeout', '30s', 'sha256sum', '-c', 'ralph/lanes/B/ROUND14.sha256'],
        cwd=root, check=True, capture_output=True,
    )
    (base / 'prior-freeze.log').write_bytes(report.stdout)
    adopted, ranks = source_partition()
    (base / 'residual.u32').write_bytes(ranks.tobytes())
    (base / 'adopted.tsv').write_text(''.join(f'{rank}\t{kind}\t{local}\n' for rank, (kind, local) in adopted.items()))
    plan = {'source': CATALOGUE_SHA, 'source_count': TOTAL, 'adopted': len(adopted), 'residual': COUNT,
            'modulus': MODULUS, 'rank_bytes_sha256': hash_file(base / 'residual.u32')}
    (base / 'plan.json').write_text(json.dumps(plan, sort_keys=True) + '\n')
    print(f'PASS plan {plan}', flush=True)


def shard_ranks(base, identifier):
    assert 0 <= identifier < MODULUS
    with (base / 'residual.u32').open('rb') as stream, mmap(stream.fileno(), 0, access=ACCESS_READ) as table:
        assert len(table) == COUNT * 4
        ranks = [unpack_from('<I', table, idx * 4)[0] for idx in range(identifier, COUNT, MODULUS)]
    assert 0 < ranks[0] <= ranks[-1] <= TOTAL and all(left < right for left, right in zip(ranks, ranks[1:]))
    return ranks


def residue_keys(ranks):
    with CATALOGUE.open('rb') as stream, mmap(stream.fileno(), 0, access=ACCESS_READ) as source:
        assert len(source) == TOTAL * RECORD
        return [source[(rank - 1) * RECORD:rank * RECORD] for rank in ranks]


def check_inputs(ranks, keys):
    accumulator = sha256()
    for rank, key in zip(ranks, keys, strict=True):
        accumulator.update(rank.to_bytes(4, 'little'))
        accumulator.update(key)
    return accumulator.hexdigest()


def check_dispositions(ranks, masks, proof_ranks):
    assert list(masks) == sorted(masks) and all(1 <= local <= len(ranks) for local in masks)
    assert proof_ranks == [rank for local, rank in enumerate(ranks, 1) if local not in masks]


def producer_core(text, pins):
    if not pins or len(pins) == 7:
        return make_core(text, pins or None).encode()
    rows = graph.parse_graph6(text)
    assert len(pins) == 6
    verify_clique(rows, 5, pins)
    variables, clauses = clauses_for(rows, 7, 9)
    clauses.extend((index * len(rows) + vertex + 1,)
                   for index, mask in enumerate(pins) for vertex in vertices(mask))
    return ''.join(dimacs(variables, clauses)).encode()


def replay_core(text, pins):
    if not pins or len(pins) == 7:
        return independent_core(text, pins or None)
    assert len(pins) == 6
    rows = graph.parse_graph6(text)
    verify_clique(rows, 5, pins)
    header, body = independent_core(text, None).split(b'\n', 1)
    _, _, variables, clauses = header.split()
    units = [index * len(rows) + vertex + 1 for index, demand in enumerate(pins)
             for vertex in range(len(rows)) if demand & (1 << vertex)]
    return b'p cnf %s %d\n' % (variables, int(clauses) + len(units)) + body + b''.join(
        b'%d 0\n' % literal for literal in units
    )


def positive_six_pin(out):
    text = ']paRWpG?oHcCPPSDD@[`c_OH_O?WG{FAC?SGU??ZAODB@Ok@DAC?bFCCCXACd@H?@OTG????Nw'
    rows = graph.parse_graph6(text)
    root_site = 28
    assert len(rows) == 30 and graph.triangle_free(rows) and graph.alpha(rows) < 9
    assert all(rows[left] & (1 << right) or rows[left] & rows[right]
               for left, right in combinations(range(len(rows)), 2))
    attachment = list(vertices(rows[root_site]))
    assert len(attachment) == 7
    exterior_mask = ((1 << len(rows)) - 1) & ~(rows[root_site] | (1 << root_site))
    exterior = tuple(vertices(exterior_mask))
    residual = induced(rows, exterior_mask)
    key = graph.to_graph6(residual)
    masks = (327680, 2105344, 135168, 4104, 257, 129)
    assert scan([(key + '\n').encode()], 6)[1] == {1: masks}
    selected = []
    for mask in masks:
        witness = [row for row in attachment if all(rows[row] & (1 << exterior[index]) for index in vertices(mask))]
        assert len(witness) == 1 and witness[0] not in selected
        selected.extend(witness)
    selected.extend(row for row in attachment if row not in selected)
    values = [False] + [bool(rows[row] & (1 << vertex)) for row in selected for vertex in exterior]
    for left, right in combinations(range(len(exterior)), 2):
        if not (residual[left] & (1 << right) or residual[left] & residual[right]):
            values.extend(bool(rows[row] & (1 << exterior[left])) and bool(rows[row] & (1 << exterior[right]))
                          for row in selected)
    cnf = replay_core(key, masks)
    assert cnf == producer_core(key, masks)
    header, *clauses = cnf.decode().splitlines()
    assert int(header.split()[2]) + 1 == len(values)
    assert all(any(values[abs(lit)] == (lit > 0) for lit in map(int, line.split()[:-1])) for line in clauses)
    path = out / 'six-positive.cnf'
    path.write_bytes(cnf)
    assert b's SATISFIABLE' in run(12, [root / 'opt/bin/cadical', path], allowed=(10,)).stdout.splitlines()
    adverse('repeated six-pin demand', lambda: replay_core(key, (masks[1], *masks[1:])))
    print('control order 30: renormalized six-pin physical assignment and independent SAT both pass')


def generate(out, ranks, keys, cap):
    raw, masks = scan(keys, 8)
    (out / 'cliques.tsv').write_bytes(raw)
    missing = [local for local in range(1, len(ranks) + 1) if local not in masks]
    _, pins = scan([keys[local - 1] for local in missing], 7) if missing else (b'', {})
    residual = [ordinal for ordinal in range(1, len(missing) + 1) if ordinal not in pins]
    if residual:
        _, short = scan([keys[missing[ordinal - 1] - 1] for ordinal in residual], 6)
        pins.update((original, short.get(index, ())) for index, original in enumerate(residual, 1))
    assert len(pins) == len(missing)
    cnf_path, proof_path = out / 'core.cnf', out / 'core.lrat'
    with (out / 'proofs.tsv').open('w') as index, (out / 'proofs.pack').open('wb') as pack:
        for ordinal, local in enumerate(missing, 1):
            rank = ranks[local - 1]
            try:
                cap(rank)
                pin = pins[ordinal]
                cnf = producer_core(keys[local - 1].decode().strip(), pin)
                cnf_path.write_bytes(cnf)
                result = run(5, ['build/unit_lrat', cnf_path, proof_path], allowed=(10, 20))
                method = 'rup'
                if result.returncode == 10:
                    method = 'cadical'
                    run(10, ['prlimit', '--cpu=6:7', '--', root / 'opt/bin/cadical', '--lrat', '--no-binary',
                             cnf_path, proof_path], allowed=(20,))
                proof = proof_path.read_bytes()
                assert 0 < len(proof) <= MAX_PROOF and pack.tell() + len(proof) < MAX_PACK
                fields = [str(rank), str(pack.tell()), str(len(proof)), digest(cnf), digest(proof), method,
                          *(f'{mask:x}' for mask in pin)]
                pack.write(proof)
                index.write('\t'.join(fields) + '\n')
                proof_path.unlink()
            except Exception as error:
                raise RuntimeError(f'production failed; source rank {rank}') from error
    cnf_path.unlink(missing_ok=True)


def replay(out, scratch, ranks, keys, cap, check_lrat=True):
    masks = read_masks((out / 'cliques.tsv').read_bytes(), len(ranks), 8)
    missing = [local for local in range(1, len(ranks) + 1) if local not in masks]
    index = [line.split('\t') for line in (out / 'proofs.tsv').read_text().splitlines()]
    check_dispositions(ranks, masks, [int(fields[0]) for fields in index])
    if check_lrat:
        complement = b''.join(f'{local}\t'.encode() + keys[local - 1] for local in missing)
        assert check_cover(keys, masks, complement) == missing
    cnf_path, proof_path = scratch / 'core.cnf', scratch / 'core.lrat'
    methods, widths = Counter(), Counter()
    with (out / 'proofs.pack').open('rb') as pack:
        for local, fields in zip(missing, index, strict=True):
            rank, offset, length = map(int, fields[:3])
            try:
                cap(rank)
                cnf_digest, proof_digest, method, *hex_pins = fields[3:]
                assert offset == pack.tell() and 0 < length <= MAX_PROOF and len(hex_pins) in {0, 6, 7}
                assert method in {'rup', 'cadical'} and len(cnf_digest) == 64
                proof = pack.read(length)
                assert len(proof) == length and digest(proof) == proof_digest
                if check_lrat:
                    pins = tuple(int(mask, 16) for mask in hex_pins)
                    cnf = replay_core(keys[local - 1].decode().strip(), pins)
                    assert digest(cnf) == cnf_digest
                    cnf_path.write_bytes(cnf)
                    proof_path.write_bytes(proof)
                    for checker, marker in CHECKERS:
                        verify(checker, cnf_path, proof_path, marker)
                methods[method] += 1
                widths[str(len(hex_pins))] += 1
            except Exception as error:
                raise RuntimeError(f'replay failed; source rank {rank}') from error
        assert not pack.read(1), 'unindexed proof suffix'
    if check_lrat:
        cnf_path.unlink(missing_ok=True)
        proof_path.unlink(missing_ok=True)
    return masks, methods, widths


def shard(base, identifier, quota, control=False):
    started, started_wall = cpu(), monotonic()

    def cap(rank):
        used = cpu() - started
        if used >= quota:
            raise RuntimeError(f'STOP CPU gate {used:.2f}/{quota} at source rank {rank}')

    out = base / f's{identifier:03}'
    out.mkdir()
    ranks = shard_ranks(base, identifier)
    keys = residue_keys(ranks)
    if control:
        backup = out / 'controls'
        backup.mkdir()
        controls(backup)
        positive_six_pin(backup)
        check_dispositions([1, 3, 8], {1: ()}, [3, 8])
        adverse('dropped proof rank', lambda: check_dispositions([1, 3, 8], {1: ()}, [3]))
        adverse('duplicate/misaligned rank', lambda: check_dispositions([1, 3, 8], {1: ()}, [1, 3, 8]))
        audit = run(35, ['build/audit_duals', '32', '108', '9', str(len(keys))], b''.join(keys))
        print((audit.stdout + audit.stderr).decode().strip(), flush=True)
        audit = run(35, ['build/irreducible', '9'], b''.join(keys))
        assert not audit.stdout and audit.stderr.startswith(f'irreducible: in={len(keys)} out=0 '.encode())
        print(audit.stderr.decode().strip(), flush=True)
    generate(out, ranks, keys, cap)
    production = cpu() - started
    masks, methods, widths = replay(out, out, ranks, keys, cap)
    cap(ranks[-1])
    receipt = {'shard': identifier, 'keys': len(ranks), 'cliques': len(masks), 'methods': dict(methods),
               'pins': dict(widths),
               'inputs': check_inputs(ranks, keys), 'sha256': {name: hash_file(out / name) for name in ARCHIVE},
               'production_cpu': production, 'cpu': cpu() - started, 'wall': monotonic() - started_wall}
    tmp = out / 'done.tmp'
    tmp.write_text(json.dumps(receipt, sort_keys=True) + '\n')
    tmp.replace(out / 'done.json')
    print(f'PASS shard {receipt}', flush=True)


def merge(base, require_full):
    adopted, residual = source_partition()
    assert residual.tobytes() == (base / 'residual.u32').read_bytes()
    assert (base / 'adopted.tsv').read_text().splitlines() == [
        f'{rank}\t{kind}\t{local}' for rank, (kind, local) in adopted.items()
    ]
    disposition = bytearray(TOTAL + 1)
    for rank, (kind, _) in adopted.items():
        disposition[rank] = {'C6': 1, 'P6': 2, 'C14': 3, 'P14': 4}[kind]
    outcomes = Counter()
    for identifier in range(MODULUS):
        out = base / f's{identifier:03}'
        done = out / 'done.json'
        ranks = residual[identifier::MODULUS]
        if not done.exists():
            outcomes['incomplete' if out.exists() else 'unstarted'] += len(ranks)
            for rank in ranks:
                assert not disposition[rank]
                disposition[rank] = 7 if out.exists() else 8
            continue
        info = json.loads(done.read_text())
        keys = residue_keys(ranks)
        assert info['shard'] == identifier and info['keys'] == len(ranks)
        assert info['inputs'] == check_inputs(ranks, keys)
        assert info['sha256'] == {name: hash_file(out / name) for name in ARCHIVE}
        masks, methods, widths = replay(out, out, ranks, keys, lambda _: None, check_lrat=False)
        assert info['cliques'] == len(masks) and info['methods'] == methods and info['pins'] == widths
        outcomes.update(methods)
        outcomes.update({f'pin{width}': count for width, count in widths.items()})
        for local, rank in enumerate(ranks, 1):
            assert not disposition[rank]
            disposition[rank] = 5 if local in masks else 6
    assert disposition[0] == 0 and disposition.count(0) == 1
    counts = Counter(disposition[1:])
    assert counts[7] == outcomes['incomplete'] and counts[8] == outcomes['unstarted']
    assert counts[6] == outcomes['rup'] + outcomes['cadical']
    ordered = base / 'rank-dispositions.tsv'
    labels = ('', 'C6', 'P6', 'C14', 'P14', 'C15', 'P15', 'incomplete', 'unstarted')
    with ordered.open('w') as stream, (base / 'unchecked-ranks.txt').open('w') as gaps:
        for rank, kind in enumerate(disposition[1:], 1):
            stream.write(f'{rank}\t{labels[kind]}\n')
            if kind >= 7:
                gaps.write(f'{rank}\n')
    summary = {'source': CATALOGUE_SHA, 'ordered_sha256': hash_file(ordered),
               'counts': {labels[kind]: number for kind, number in sorted(counts.items())}, 'outcomes': dict(outcomes)}
    (base / 'summary.json').write_text(json.dumps(summary, sort_keys=True) + '\n')
    print(f'MERGE {summary}', flush=True)
    if require_full:
        assert not counts[7] and not counts[8], 'incomplete coverage'


def campaign(base, first, stop, slots, budget):
    plan = json.loads((base / 'plan.json').read_text())
    assert hash_file(base / 'residual.u32') == plan['rank_bytes_sha256']
    assert 1 <= slots <= 14 and 0 < first < stop <= MODULUS and 0 < budget <= 14_400
    assert (base / 's000' / 'done.json').exists()
    cursor = first
    with (base / 'worker-times.tsv').open('a') as history:
        while cursor < stop:
            batch = list(range(cursor, min(cursor + slots, stop)))
            remaining = budget - cpu()
            quota = min(80, int(remaining / len(batch)) - MAX_CHILD_OVERRUN)
            if quota < 60:
                raise RuntimeError(f'STOP campaign CPU budget; first unstarted shard {cursor}')
            size = sum(path.stat().st_blocks * 512 for path in base.rglob('*') if path.is_file())
            if size + len(batch) * 32 * 1024**2 + 96 * 1024**2 >= MAX_STORAGE:
                raise RuntimeError(f'STOP disk budget; first unstarted shard {cursor}')
            workers = []
            for identifier in batch:
                assert not (base / f's{identifier:03}').exists()
                timer = base / f's{identifier:03}.time'
                log = base / f's{identifier:03}.log'
                with log.open('xb') as output:
                    proc = subprocess.Popen(['/usr/bin/time', '-f', '%U %S %e %M', '-o', timer,
                                             'timeout', '--kill-after=3s', '240s', sys.executable, ENTRY,
                                             'shard', base, str(identifier), str(quota)],
                                            stdout=output, stderr=subprocess.STDOUT)
                workers.append((identifier, proc, timer))
            print(f'launch shards {batch} quota={quota}s pids={[proc.pid for _, proc, _ in workers]}', flush=True)
            failed = []
            for identifier, worker, timer in workers:
                status = worker.wait()
                seconds = timer.read_text().splitlines()[-1]
                history.write(f'{identifier}\t{status}\t{seconds}\n')
                if status != 0 or not (base / f's{identifier:03}' / 'done.json').exists():
                    failed.append(identifier)
            history.flush()
            print(f'finished shards {batch}; campaign aggregate CPU={cpu():.3f}s', flush=True)
            if failed:
                raise RuntimeError(f'STOP shard failure: {failed}')
            cursor += len(batch)


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'shard', 'merge', 'campaign', 'recheck'))
    parser.add_argument('base', type=Path)
    parser.add_argument('params', type=int, nargs='*')
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--full', action='store_true')
    args = parser.parse_args()
    base = args.base
    if args.mode == 'prepare':
        prepare(base)
    elif args.mode == 'shard':
        shard(base, *args.params, control=args.control)
    elif args.mode == 'merge':
        merge(base, args.full)
    elif args.mode == 'campaign':
        campaign(base, *args.params)
    else:
        identifier, = args.params
        out = base / f's{identifier:03}'
        scratch = base / f'recheck{identifier:03}'
        scratch.mkdir()
        ranks = shard_ranks(base, identifier)
        keys = residue_keys(ranks)
        info = json.loads((out / 'done.json').read_text())
        assert info['inputs'] == check_inputs(ranks, keys)
        assert info['sha256'] == {name: hash_file(out / name) for name in ARCHIVE}
        masks, methods, widths = replay(out, scratch, ranks, keys, lambda _: None)
        assert info['cliques'] == len(masks) and info['methods'] == methods and info['pins'] == widths
        print(f'PASS independent CNF plus both LRAT checkers; shard {identifier}, {len(masks)} cliques, {dict(methods)}')


if __name__ == '__main__':
    main()
