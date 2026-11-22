#!/usr/bin/env python3
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

from panel17_round14 import check, read_terminal
from panel17_round15 import C_GATE_MS, HEADER_TOTALS, HIGH, PY_GATE_MS, expected


def summarize(work, coverage):
    checked, unfinished = [], []
    global_terminal = sha256()
    for low, high in HIGH:
        directory = work / f'{low:05d}-{high:05d}'
        bit0, bit1, digest = coverage[low, high, 'HHrep']
        direct = bit0 + bit1
        diagonal = sum(coverage[low, high, 'HHdiag'][:2])
        transferred = direct - diagonal
        if not (directory / 'result.json').is_file():
            unfinished.append((low, high, direct, transferred))
            continue
        result = json.loads((directory / 'result.json').read_text())
        screen = json.loads((directory / 'screen.json').read_text())
        check((result['low'], result['high']) == (low, high) and result['roster_sha256'] == digest
              and result['counts'][0] == direct and result['diagonal'] == diagonal
              and result['by_exchange'] == transferred, f'incorrect receipt or roster: {directory}')
        check(screen and all(result[key] == value for key, value in screen.items()), 'screen/terminal receipt drift')
        for record, bit_count in enumerate((bit0, bit1)):
            match = re.search(rf'^flip={record} raw/header/fwd/rev/local/panel: (.+)$',
                              (directory / 'A.screen.log').read_text(), re.MULTILINE)
            check(match and int(match.group(1).split()[1]) == bit_count, 'scanner bit binding drift')
        panels = [tuple(map(int, line.split())) for line in (directory / 'panels.ids').read_text().splitlines()]
        counts = result['counts']
        check(all(first >= second for first, second in zip(counts, counts[1:])) and
              counts[4] == len(panels) and counts[3] >= 100 * counts[4] and
              panels == sorted(set(panels)) and
              all(low <= left < high and left <= right < HIGH[-1][1] and bit in (0, 1)
                  for left, right, bit in panels), 'incorrect panel / stage count or key')
        keyed = []
        tails = []
        for name in ('C.terminal', 'scout.terminal'):
            raw = read_terminal(directory / name, panels)
            keyed.append([row for row, _ in raw])
            tails.append(max((ms for _, ms in raw), default=0))
        check(keyed[0] == keyed[1] and all(row[7] == 0 for row in keyed[0]) and result['unresolved'] == 0,
              'unresolved or disagreeing terminal entry')
        dispositions = [sum(row[index] for row in keyed[0]) for index in range(3, 8)]
        check(result['fillings'] == dispositions and result['joint'] == sum(any(row[3:]) for row in keyed[0])
              and result['tail_ms'] == tails and tails[0] <= C_GATE_MS and tails[1] <= PY_GATE_MS,
              'terminal derived counts or gate drift')
        data = ''.join(' '.join(map(str, row)) + '\n' for row in keyed[0]).encode()
        check((directory / 'terminal.keyed').read_bytes() == data and sha256(data).hexdigest() == result['terminal_sha256'],
              'terminal vector stream drift')
        global_terminal.update(data)
        checked.append(result)
    return checked, unfinished, global_terminal.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('work', type=Path)
    parser.add_argument('--require-full', action='store_true')
    args = parser.parse_args()
    rows, unfinished, digest = summarize(args.work, expected(args.work / 'A.census.tsv'))
    prefix_direct = sum(HEADER_TOTALS[:2])
    high_direct = sum(result['counts'][0] for result in rows)
    high_exchange = sum(result['by_exchange'] for result in rows)
    unresolved_representatives = sum(record[2] for record in unfinished)
    unresolved_exchanges = sum(record[3] for record in unfinished)
    high_diag = sum(result['diagonal'] for result in rows)
    check(high_direct + high_exchange + unresolved_representatives + unresolved_exchanges == HEADER_TOTALS[3],
          'incomplete HH transfer accounting')
    print('low high HH_direct HH_by_exchange diagonal HH_unresolved joint panels')
    for result in rows:
        print(result['low'], result['high'], result['counts'][0], result['by_exchange'], result['diagonal'],
              0, result['joint'], result['counts'][4])
    for low, high, direct, exchanged in unfinished:
        print(low, high, 0, 0, 0, direct + exchanged, 0, 0)
    data = dict(ordered_direct=prefix_direct + high_direct, ordered_by_exchange=HEADER_TOTALS[2] + high_exchange,
                ordered_unresolved=unresolved_representatives + unresolved_exchanges,
                prefix_direct=prefix_direct, HL_by_exchange=HEADER_TOTALS[2], HH_direct=high_direct,
                HH_by_exchange=high_exchange, HH_diagonals_direct=high_diag,
                HH_representatives_missing=unresolved_representatives, HH_joint=sum(row['joint'] for row in rows),
                HH_stages=[sum(row['counts'][index] for row in rows) for index in range(5)],
                HH_fillings=[sum(row['fillings'][index] for row in rows) for index in range(5)],
                HH_terminal_sha256=digest, HH_shards=len(rows), HH_cpu_s=round(sum(row['cpu_s'] for row in rows), 3),
                HH_screen_cpu_s=round(sum(row['screen_cpu_s'] for row in rows), 3),
                HH_max_tail_ms=[max((row['tail_ms'][index] for row in rows), default=0) for index in range(2)])
    print(json.dumps(data, sort_keys=True))
    if args.require_full:
        check(not unfinished, 'unresolved HH representative shards')


if __name__ == '__main__':
    main()
