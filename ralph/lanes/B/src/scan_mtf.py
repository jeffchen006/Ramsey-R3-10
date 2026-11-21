"""Scan one e-level for MTF completions, with checked resumable chunks."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from seed import PICKG, ROOT, preprocess, worker, run


def scan(input_path, edges, workers, label):
    directory = Path('work') / f'mtf_{label}_e{edges}'
    directory.mkdir(exist_ok=True)
    selected = directory / 'inputs.g6'
    if not selected.exists():
        temporary = selected.with_suffix('.tmp')
        run([PICKG, '-q', f'-e{edges}', input_path, temporary])
        temporary.replace(selected)
    command = ['build/mtfcover', '-k', 9, '-d', 9, '-m', 6, '-M', 9, '-E', 161, '-X']
    jobs = preprocess(directory, [(9, selected, command)], 1024)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for _ in pool.map(worker, jobs):
            pass
    found = b''.join(file.read_bytes() for file in sorted(directory.glob('*.canon')))
    print(f'MTF {label} e={edges} checked all input chunks; output {found.count(bytes([10]))} graphs', flush=True)
    if found:
        candidate = ROOT / 'ralph/found' / f'B_{label}_e{edges}.g6'
        candidate.write_bytes(found)
        run(['python3', ROOT / 'tools/check_graph.py', '--n', 40, '--k', 10, candidate])
        run(['python3', ROOT / '.hmz/flows/r310_ralph/gate.py', ROOT, 'check', candidate, '40', '10'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('--workers', type=int, required=True)
    parser.add_argument('--edge', type=int, required=True)
    parser.add_argument('--label', required=True)
    args = parser.parse_args()
    scan(args.input, args.edge, args.workers, args.label)
