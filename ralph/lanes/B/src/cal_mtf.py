"""Cross-check gluefast -X against glue2 filtered for maximality on known inputs."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path.cwd().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from check_graph import parse_graph6, to_graph6


def is_mtf(adj):
    return all(adj[x] >> y & 1 or adj[x] & adj[y]
               for y in range(len(adj)) for x in range(y))


def dual(adj, vertex):
    kept = [x for x in range(len(adj)) if x != vertex and not (adj[vertex] >> x & 1)]
    return [sum((adj[x] >> y & 1) << pos for pos, y in enumerate(kept)) for x in kept]


def canon(data):
    return set(subprocess.run([ROOT / 'opt/bin/labelg', '-q'], input=data,
                              text=True, capture_output=True, check=True).stdout.splitlines())


def glue(program, input_graph, *options):
    process = subprocess.run(['timeout', '180', Path('build').resolve() / program, *options],
                             input=input_graph + '\n', text=True, capture_output=True, check=True)
    print(process.stderr.strip(), flush=True)
    return process.stdout.splitlines()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('graph_file')
    parser.add_argument('alpha', type=int)
    parser.add_argument('--number', type=int, default=1)
    parser.add_argument('--program', default='gluefast')
    args = parser.parse_args()
    done = 0
    for graph in Path(args.graph_file).read_text().splitlines():
        adj = parse_graph6(graph)
        if not is_mtf(adj):
            continue
        degrees = [row.bit_count() for row in adj]
        edges = sum(degrees) // 2
        root = max(range(len(adj)), key=degrees.__getitem__)
        h = to_graph6(dual(adj, root))
        opts = ('-k', str(args.alpha), '-d', str(degrees[root]), '-m', str(min(degrees)),
                '-e', str(edges), '-E', str(edges))
        baseline = '\n'.join(out for out in glue('glue2', h, *opts) if is_mtf(parse_graph6(out)))
        fast = '\n'.join(glue(args.program, h, '-X', *opts))
        expected = canon(baseline)
        obtained = canon(fast)
        if expected != obtained or not canon(graph) <= obtained:
            raise ValueError(f'failed MTF comparison: {graph}, distinct {len(expected)} vs {len(obtained)}')
        done += 1
        print(f'MTF comparison {done}: identical {len(obtained)} classes including input', flush=True)
        if done >= args.number:
            break
    if done != args.number:
        raise ValueError('insufficient MTF controls')
