"""Rebuild exact upstream inputs in small resumable jobs; run from scratch/B."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import itertools
from pathlib import Path
import subprocess


ROOT = Path.cwd().parents[1]
if Path.cwd() != ROOT / 'scratch/B':
    raise SystemExit('run from scratch/B')
SHORTG = ROOT / 'opt/bin/shortg'
PICKG = ROOT / 'opt/bin/pickg'
SRC = ROOT / 'ralph/lanes/B/src'


def run(command, **kwargs):
    return subprocess.run(['timeout', '--kill-after=30s', '1h', *map(str, command)],
                          check=True, **kwargs)


def filtered(input_file, max_edges):
    target = Path('work') / f'{input_file.stem}_e_le{max_edges}.g6'
    if not target.exists():
        temporary = target.with_suffix('.tmp')
        run([PICKG, '-q', f'-e0:{max_edges}', input_file, temporary])
        temporary.replace(target)
    return target


def calibrate_increments(k, order, edges, increments):
    if not increments:
        return
    args = ','.join(f'{degree}:{inc}' for degree, inc in increments.items())
    result = run(['python3', SRC / 'tcheck.py', k, order, edges, args],
                 text=True, stdout=subprocess.PIPE).stdout
    print(result, end='', flush=True)
    if not result.rstrip().endswith('OK: increments suffice'):
        raise ValueError(f'insufficient increments: {args}')


def preprocess(directory, steps, chunk):
    jobs = []
    for degree, infile, arguments in steps:
        with infile.open('rb') as source:
            for seq in itertools.count():
                block = list(itertools.islice(source, chunk))
                if not block:
                    break
                prefix = directory / f'd{degree}_{seq:05d}'
                output = prefix.with_suffix('.canon')
                if not output.exists():
                    prefix.with_suffix('.in').write_bytes(b''.join(block))
                    jobs.append((prefix, len(block), arguments))
    return jobs


def worker(job):
    prefix, count, arguments = job
    input_path = prefix.with_suffix('.in')
    input_digest = hashlib.sha256(input_path.read_bytes()).hexdigest()
    with input_path.open('rb') as source, \
            prefix.with_suffix('.raw').open('wb') as out, \
            prefix.with_suffix('.log').open('w') as log:
        run(arguments, stdin=source, stdout=out, stderr=log)
        print(f'input_sha256={input_digest}', file=log)
    log_text = prefix.with_suffix('.log').read_text()
    if f'in={count} ' not in log_text or 'bad graph6' in log_text:
        raise ValueError(f'incomplete: {prefix}')
    with prefix.with_suffix('.tmp').open('wb') as tmp:
        run([SHORTG, '-q', '-Twork', prefix.with_suffix('.raw'), '-'], stdout=tmp)
    if 'out=0 ' not in log_text and prefix.with_suffix('.tmp').stat().st_size == 0:
        raise ValueError(f'nonempty output lost in canonicalization: {prefix}')
    prefix.with_suffix('.tmp').replace(prefix.with_suffix('.canon'))
    prefix.with_suffix('.raw').unlink()
    input_path.unlink()
    print(f'{prefix}: {log_text.strip()}', flush=True)


def generate(name, steps, chunk, workers, expected=''):
    target = Path('val') / f'{name}.g6'
    if target.exists():
        return
    directory = Path('work') / name
    directory.mkdir(exist_ok=True)
    jobs = preprocess(directory, steps, chunk)
    print(f'{name}: {len(jobs)} remaining chunks; {workers} workers', flush=True)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for _ in pool.map(worker, jobs):
            pass
    combined = directory / 'combined.g6'
    with combined.open('wb') as out:
        for path in sorted(directory.glob('*.canon')):
            with path.open('rb') as infile:
                for data in iter(lambda: infile.read(1 << 20), b''):
                    out.write(data)
    temporary = target.with_suffix('.tmp')
    run([SHORTG, '-q', '-Twork', combined, temporary])
    if expected:
        run(['python3', SRC / 'ecount.py', temporary, expected])
    temporary.replace(target)
    combined.unlink()


def lower_seed(workers):
    minimum = {12: 11, 13: 15, 14: 20, 15: 25, 16: 32, 17: 40}
    for order, edges, expected in [(15, 16, ''), (16, 22, '20:2,21:15,22:201'),
                                  (17, 28, '25:2,26:30,27:642,28:13334'),
                                  (18, 33, '30:1,31:15,32:382,33:8652'),
                                  (19, 39, '37:11,38:417,39:10447')]:
        steps = []
        for degree in range(1, 7):
            inner = order - degree - 1
            top = edges - degree * degree
            if inner > 17 or (inner in minimum and top < minimum[inner]):
                continue
            seed = Path(f'val/r3_6_{inner}.g6')
            steps.append((degree, filtered(seed, top),
                          ['build/glue5', '-k', 6, '-d', degree, '-e', edges]))
        generate(f'r37_{order}_le{edges}', steps, 4096, workers, expected)


def upper_seed(workers, program, extra52):
    expected = {22: '42:21,43:1521,44:72353',
                23: '49:102,50:8241,51:356041',
                24: '56:51,57:3419,58:129347'}
    minimum = {15:15, 16:20, 17:25, 18:30, 19:37, 20:44}
    seed_file = {
        15: Path('val/r37_15_le16.g6'), 16: Path('val/r37_16_le22.g6'),
        17: Path('val/r37_17_le28.g6'), 18: Path('val/r37_18_le33.g6'),
        19: Path('val/r37_19_le39.g6'), 20: Path('ref/Ramseygraphs_3_7_20_e44.g6'),
    }
    specifications = [(22, 44, {3:2, 4:4, 5:3, 6:2}),
                      (24, 58, {3:1, 4:3, 5:4, 6:2})]
    if extra52:
        specifications.append((23, 52, {3:1, 4:4, 5:4, 6:2}))
        expected[23] += ',52:10326716'
    else:
        specifications.append((23, 51, {3:1, 4:4, 5:4, 6:2}))
    for order, edges, increments in specifications:
        calibrate_increments(8, order, edges, increments)
        steps = []
        for degree, increment in increments.items():
            inner = order - degree - 1
            edges_h = minimum[inner] + increment - 1
            if inner == 17 and edges_h > 28:
                raise ValueError('n17 seed too small')
            steps.append((degree, filtered(seed_file[inner], edges_h),
                          [f'build/{program}', '-k', 7, '-d', degree, '-e', edges,
                           '-m', 1, '-M', 7]))
        generate(f'r38_{order}_le{edges}', steps, 128, workers, expected[order])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['small', 'upper', 'upper52'])
    parser.add_argument('--workers', type=int, required=True)
    parser.add_argument('--program', default='glue5')
    args = parser.parse_args()
    if args.phase == 'small':
        lower_seed(args.workers)
    else:
        upper_seed(args.workers, args.program, args.phase == 'upper52')
