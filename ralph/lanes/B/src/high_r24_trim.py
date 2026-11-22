"""Keep the dependency cone of a textual CaDiCaL LRAT empty clause."""

import argparse
from pathlib import Path


def trim(original, result, initial_clauses):
    rows = original.read_bytes().splitlines(keepends=True)
    needed = set()
    selected = set()
    retained = []
    has_rat = False
    for index in range(len(rows) - 1, -1, -1):
        line = rows[index]
        add_id, rest = line.split(maxsplit=1)
        if rest.startswith(b'd '):
            continue
        add_id = int(add_id)
        if not retained and not rest.startswith(b'0 '):
            continue
        if retained and add_id not in needed:
            continue
        tokens = rest.split()
        separator = tokens.index(b'0')
        assert tokens[-1] == b'0' and add_id > initial_clauses
        for token in tokens[separator + 1:-1]:
            signed = int(token)
            assert 0 < abs(signed) < add_id
            need = abs(signed)
            if need > initial_clauses:
                needed.add(need)
            has_rat |= signed < 0
        selected.add(add_id)
        retained.append(index)
    if not retained or not needed <= selected:
        raise ValueError('empty-clause dependency cone incomplete')
    keep = set(retained)
    with result.open('wb') as output:
        for index in range(retained[0] + 1):
            if index in keep:
                output.write(rows[index])
            elif has_rat:
                add_id, rest = rows[index].split(maxsplit=1)
                if rest.startswith(b'd '):
                    tokens = rest.split()[1:-1]
                    tokens = [token for token in tokens if int(token) <= initial_clauses or int(token) in selected]
                    if tokens:
                        output.write(add_id + b' d ' + b' '.join(tokens) + b' 0\n')
    print(f'trim adds={len(retained)} rat={int(has_rat)} bytes={original.stat().st_size}->{result.stat().st_size}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cnf', type=Path)
    parser.add_argument('original', type=Path)
    parser.add_argument('result', type=Path)
    args = parser.parse_args()
    with args.cnf.open('rb') as source:
        initial_clauses = next(int(row.split()[-1]) for row in source if row.startswith(b'p cnf '))
    trim(args.original, args.result, initial_clauses)


if __name__ == '__main__':
    main()
