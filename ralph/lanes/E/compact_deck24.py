#!/usr/bin/env python3
"""Physical CNF binding, bounded LRAT production and append-only shard archives."""

import argparse
from collections import Counter
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from resource import getrusage, RUSAGE_CHILDREN, RUSAGE_SELF
import subprocess

from bind_width74 import dimacs
from cover_deck24 import factory
from involution_sat import from_graph6, to_graph6
from m11_sat import FastCuts
from m11_support import Supports
from project_deck23 import Projection, control
from rebind_projection23 import formula, ledgers, TOOLS


ROOT = Path('../r23_deck')
MAX_PROOF = 32 * 1024**2
DEFAULT_ARCHIVE = 136 * 1024**2


def cpu():
    return sum(use.ru_utime + use.ru_stime for use in (getrusage(RUSAGE_CHILDREN), getrusage(RUSAGE_SELF)))


def digest(blob):
    return sha256(blob).hexdigest()


def load(path):
    return [json.loads(line) for line in path.read_bytes().splitlines()]


def launch(tool, flags, cnf, proof, limit):
    return subprocess.run(['timeout', '-k', '2s', f'{2*limit}s', 'prlimit', f'--cpu={limit}:{limit+1}',
                           f'--fsize={MAX_PROOF}:{MAX_PROOF}', '--', str(TOOLS/tool),
                           *flags, str(cnf), str(proof)], capture_output=True, check=False)


def dual(cnf, proof, limit=10):
    for tool, flags, marker in (('cake_lpr', ('--CML_HEAP_SIZE=256', '--CML_STACK_SIZE=64'), b's VERIFIED UNSAT'),
                                ('lrat-check', (), b'c VERIFIED')):
        run = launch(tool, flags, cnf, proof, limit)
        if run.returncode != 0 or marker not in map(bytes.rstrip, run.stdout.splitlines()):
            return f'OPEN_{tool}_{run.returncode}'
    return 'CHECKED'


def make(cnf, proof, limit):
    proof.unlink(missing_ok=True)
    run = launch('cadical', ('-q', '--lrat', '--no-binary'), cnf, proof, limit)
    if run.returncode != 20 or not proof.exists() or proof.stat().st_size >= MAX_PROOF:
        return f'OPEN_SOLVE_{run.returncode}', b''
    status = dual(cnf, proof, limit)
    return status, proof.read_bytes() if status == 'CHECKED' else b''


def worker(plan, ids, output, archive_limit, lazy, limit, fast):
    rows = load(plan)
    output.parent.mkdir(parents=True, exist_ok=True)
    cnf, proof = output.with_suffix('.tmp.cnf'), output.with_suffix('.tmp.lrat')
    statuses = Counter()
    checked_bytes = 0
    with output.with_suffix('.bin').open('xb') as archive, output.with_suffix('.tsv').open('x', buffering=1) as ledger:
        for index in ids:
            start = cpu()
            if archive.tell() >= archive_limit:
                status, witnesses, formula_hash, proof_hash, offset, length = 'OPEN_DISK', (), '-', '-', -1, 0
            else:
                projected = Projection(*rows[index], fast, 3)
                status, witnesses, card = projected.discover(lazy, 25_000)
                formula_hash, proof_hash, offset, length = '-', '-', -1, 0
                if card is not None:
                    with output.with_suffix('.cards.jsonl').open('a', encoding='ascii') as pending:
                        print(json.dumps((index, to_graph6(card), witnesses)), file=pending)
                if status == 'UNSAT_FOR_LRAT':
                    source = formula(rows[index], witnesses)
                    original = dimacs(projected.variables, (*projected.base, *(projected.clause(*row) for row in witnesses)))
                    assert source == original, index
                    formula_hash = digest(source)
                    cnf.write_bytes(source)
                    status, raw = make(cnf, proof, limit)
                    if status == 'CHECKED':
                        compressed = gzip.compress(raw, compresslevel=3, mtime=0)
                        if archive.tell()+len(compressed) > archive_limit:
                            status = 'OPEN_DISK'
                        else:
                            offset, length, proof_hash = archive.tell(), len(compressed), digest(raw)
                            archive.write(compressed)
                            archive.flush()
                            checked_bytes += length
                    cnf.unlink(missing_ok=True)
                    proof.unlink(missing_ok=True)
            flags = (index, status, formula_hash, proof_hash, offset, length, f'{cpu()-start:.5f}',
                     json.dumps(witnesses, separators=(',', ':')))
            print(*flags, sep='\t', file=ledger)
            statuses[status] += 1
    print('compact terminals', str(output), dict(statuses), 'archive bytes', checked_bytes, 'cpu', cpu(), flush=True)


def old_rows():
    originals = {int(index): (ROOT/folder, row) for index, (folder, row) in json.loads(Path('2c4.old.json').read_bytes()).items()}
    repairs = set(map(int, Path('2c4.repair.ids').read_text().split()))
    repaired = {}
    for log in Path('2c4.repair').glob('worker.*.jsonl'):
        for terminal in load(log):
            index = terminal[0]
            assert index in repairs and index not in repaired
            repaired[index] = Path('2c4.repair'), terminal
    assert set(repaired) == repairs and originals.keys().isdisjoint(repaired)
    return originals | repaired


def replay_old(plan, ids, output):
    rows, source_rows = load(plan), old_rows()
    assert set(source_rows) == set(range(len(rows)))
    output.parent.mkdir(parents=True, exist_ok=True)
    cnf, proof = output.with_suffix('.tmp.cnf'), output.with_suffix('.tmp.lrat')
    statuses = Counter()
    with output.with_suffix('.tsv').open('x', buffering=1) as ledger:
        for index in ids:
            start = cpu()
            root, receipt = source_rows[index]
            _, status, formula_hash, proof_hash, size, count, _ = receipt
            if status == 'CHECKED':
                folder = root/f'{index:07d}'
                witnesses = json.loads((folder/'witnesses.json').read_bytes())
                assert len(witnesses) == count
                source = formula(rows[index], witnesses)
                raw = gzip.decompress((folder/'proof.lrat.gz').read_bytes())
                assert (digest(source), digest(raw), len(raw)) == (formula_hash, proof_hash, size), index
                cnf.write_bytes(source)
                proof.write_bytes(raw)
                status = dual(cnf, proof)
                cnf.unlink()
                proof.unlink()
            print(index, status, formula_hash, proof_hash, size, count, f'{cpu()-start:.5f}', sep='\t', file=ledger)
            statuses[status] += 1
    print('legacy fresh dual replay', str(output), dict(statuses), 'cpu', cpu(), flush=True)


def replay_packed(plan, ids, archive_name, output):
    rows = load(plan)
    receipts = {}
    for line in archive_name.with_suffix('.tsv').read_text(encoding='ascii').splitlines():
        index, status, formula_hash, proof_hash, offset, length, _, witnesses = line.split('\t')
        index = int(index)
        assert index not in receipts
        receipts[index] = status, formula_hash, proof_hash, int(offset), int(length), json.loads(witnesses)
    cnf, proof = output.with_suffix('.tmp.cnf'), output.with_suffix('.tmp.lrat')
    with archive_name.with_suffix('.bin').open('rb') as archive, output.with_suffix('.tsv').open('x', buffering=1) as ledger:
        for index in ids:
            status, formula_hash, proof_hash, offset, length, witnesses = receipts[index]
            assert status == 'CHECKED' and offset >= 0 and length > 0
            archive.seek(offset)
            packed = archive.read(length)
            assert len(packed) == length
            raw = gzip.decompress(packed)
            source = formula(rows[index], witnesses)
            assert (digest(source), digest(raw)) == (formula_hash, proof_hash), index
            cnf.write_bytes(source)
            proof.write_bytes(raw)
            assert dual(cnf, proof) == 'CHECKED', index
            cnf.unlink()
            proof.unlink()
            print(index, 'CHECKED', formula_hash, proof_hash, sep='\t', file=ledger)
    print('fresh archive replay', str(archive_name), len(ids), 'cpu', cpu(), flush=True)


def calibrate(fast):
    control(fast)
    toy, columns = (2, 1, 8, 4, 32, 16, 128, 64), factory((2, 1, 8, 4, 32, 16, 128, 64))
    old = Supports(toy, 6)
    profiles = [degree for degree in product(range(1, 4), repeat=4) if sum(degree) in (6, 7, 8)]
    assert profiles
    for degree in profiles:
        target = (*degree, 1, 1, 1, 1)
        assert set(columns(target)) == set(old.options(target)), target
    for root, profile in (('G?r@`_', (3, 3, 1, 1, 1, 1, 1, 1)), ('G?qa`_', (1, 2, 1, 1, 1, 1, 1, 2))):
        core = tuple(from_graph6(root))
        assert factory(core)(profile) == Supports(core, 6).options(profile)
    import os
    os.chdir(ROOT)
    plan, mapping = ledgers(Path('projected.plan.jsonl'))
    for index in (0, 17, 333, 1200, 6000, len(plan)-1):
        directory, row = mapping[index]
        witnesses = json.loads((directory/'witnesses.json').read_bytes())
        assert digest(formula(json.loads(plan[index]), witnesses)) == row[2]
    print('independent columns, smaller matching', len(profiles), 'and e10 byte regression', 6, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('control', 'run', 'old', 'replay'))
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--indexes', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--archive-limit', type=int, default=DEFAULT_ARCHIVE)
    parser.add_argument('--lazy', type=int, default=8)
    parser.add_argument('--limit', type=int, default=14)
    parser.add_argument('--fast', type=Path, default=Path('../r6_e11/m11_fastcuts.so'))
    args = parser.parse_args()
    if args.mode == 'control':
        calibrate(FastCuts(args.fast))
        return
    ids = list(map(int, args.indexes.read_text().split()))
    assert ids and len(ids) == len(set(ids)) and min(ids) >= 0
    if args.mode == 'old':
        replay_old(args.plan, ids, args.output)
    elif args.mode == 'replay':
        replay_packed(args.plan, ids, args.archive, args.output)
    else:
        worker(args.plan, ids, args.output, args.archive_limit, args.lazy, args.limit, FastCuts(args.fast))


if __name__ == '__main__':
    main()
