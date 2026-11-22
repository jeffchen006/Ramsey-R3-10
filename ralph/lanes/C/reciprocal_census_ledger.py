import argparse
import ast
from collections import Counter
import csv
from hashlib import sha256
from pathlib import Path

from reciprocal_census import EXPECTED, Q, RIGHT, ROUNDS, TOTAL, digest


CATEGORIES = {'cap', 'degree', 'fixed-undominated', 'upper-IS',
              'domain-IS', 'row-column', 'row-empty', 'forced-domain', 'live'}


def live_coverage():
    folder = Path('live-proofs')
    expected = {}
    assert (folder/'unclosed.tsv').stat().st_size == 0
    for row in Path('live.tsv').read_text().splitlines():
        filename,raw = row.split(':',1)
        *fields,reason,witness = raw.split()
        key = tuple(map(int,fields))
        assert (reason,witness) == ('live','0') and key not in expected
        expected[key] = Path(filename).parent
    with (folder/'receipts.tsv').open() as source:
        for row in csv.DictReader(source,delimiter='\t'):
            tag = row['key']
            key = tuple(map(int,row['role_map'].split(',')))
            assert key in expected and row['status'] == 'dual-LRAT'
            for suffix in ('cnf','lrat'):
                assert digest(folder/f'{tag}.{suffix}') == row[f'{suffix}_sha256']
            assert 's VERIFIED UNSAT' in (folder/f'{tag}.cake_lpr').read_text()
            assert 'c VERIFIED' in (folder/f'{tag}.lrat-check').read_text()
            expected[key] = (expected[key],tag)
    assert all(isinstance(value,tuple) for value in expected.values())
    return expected


def staged_records():
    entries = []
    for row in Path('inputs.tsv').read_text().splitlines():
        stage, worker, start, end, path, input_hash = row.split()
        assert stage in ROUNDS and worker in '0123'
        start, end = int(start), int(end)
        assert start < end and start//Q == (end-1)//Q
        source = Path(path)
        assert source == Path(f'{start:07d}-{end:07d}/hosts.g6')
        entries.append((start,end,stage,worker,source,input_hash))
    entries.sort()
    assert entries[0][0] == 0 and entries[-1][1] == TOTAL
    assert all(first[1] == second[0] for first,second in zip(entries,entries[1:]))
    return entries


def cpu(path):
    user, system, *_ = map(float,path.read_text().splitlines()[-1].split())
    return user+system


def stream_statistics(require_complete):
    intervals = {}
    for done in sorted(Path('.').glob('*.done.tsv')):
        lines = iter(done.with_name(done.name.replace('.done.tsv','.stream.log')).read_text().splitlines())
        assert next(lines).startswith('left hosts 191 marks 7791069 cards 2883465 indexed keys 12482 cpu ')
        for row in done.read_text().splitlines():
            start,end,*_ = row.split()
            start,end = int(start),int(end)
            for progress in range((end-start)//2048+1):
                selected = next(lines)
            measurements,_,tail = selected.partition(' total CPU ')
            fields = measurements.split()
            assert fields[:3] == ['right','hosts',str(end-start)] and fields[20:22] == ['role','maps']
            statuses = tail.split()[1:]
            reasons = Counter({name:int(total) for name,total in zip(statuses[::2],statuses[1::2],strict=True)})
            assert reasons.keys() <= CATEGORIES and sum(reasons.values()) == int(fields[22])
            assert (start,end) not in intervals
            intervals[start,end] = reasons
        if require_complete:
            assert next(lines,None) is None
    return intervals


def summarize(require_complete):
    entries = staged_records()
    completion = {}
    for stage in ROUNDS:
        for worker in range(4):
            prefix = f'{stage}-{worker}'
            path = Path(prefix+'.done.tsv')
            if not path.exists():
                continue
            for row in path.read_text().splitlines():
                start,end,output,runtime = row.split()
                assert (int(start),int(end)) not in completion
                completion[int(start),int(end)] = (prefix,Path(output),float(runtime))

    full_input = {path: digest(path) for path in EXPECTED} if require_complete else {}
    assert not full_input or full_input == EXPECTED
    aggregate = sha256()
    counts, intervals, cpu_total, shard_sizes = (Counter() for _ in range(4))
    stream_counts = Counter()
    quartiles = [Counter() for _ in range(4)]
    statistics = stream_statistics(require_complete)
    certified = live_coverage() if Path('live-proofs/receipts.tsv').exists() else {}
    output = Path('coverage.tsv' if require_complete else 'coverage.partial.tsv')
    with output.open('w') as ledger:
        for start,end,stage,worker,source,expected_hash in entries:
            folder = source.parent
            result = folder/'audit.log'
            bracket = (start,end)
            if bracket not in completion:
                continue
            prefix,journal,stream_cpu = completion.pop(bracket)
            assert prefix == stage+'-'+worker and journal == folder/'maps.tsv'
            streamed = statistics.pop(bracket)
            stream_counts.update(streamed)
            cpu_total['stream'] += stream_cpu
            shard_sizes['stream_hosts'] += end-start
            shard_sizes['map_bytes'] += journal.stat().st_size
            if not result.exists() or not (folder/'audit.sha256').exists():
                continue
            lo,hi,maps,unresolved,_,data = result.read_text().strip().split(maxsplit=5)
            assert (int(lo),int(hi)) == bracket
            terminal = Counter(ast.literal_eval(data))
            audit = {reason: terminal.pop(reason) for reason in list(terminal) if reason.startswith('audit:')}
            assert terminal.keys() <= CATEGORIES
            assert terminal == streamed
            assert int(maps) == sum(terminal.values())
            pending = set()
            for line in (folder/'unresolved.tsv').read_text().splitlines():
                *fields,reason,witness,alternate = line.split('\t')
                key = tuple(map(int,fields))
                assert key not in pending and (reason,witness) == ('live','0')
                linked,tag = certified.pop(key)
                assert linked == folder
                pending.add(key)
            assert len(pending) == terminal['live'] and 0 <= int(unresolved) <= len(pending)
            assert sum(audit.values()) == sum(terminal[reason] for reason in
                   ('degree','domain-IS','row-column','row-empty','forced-domain','live'))
            intervals['shards'] += 1
            intervals['hosts'] += end-start
            counts.update(terminal)
            quartiles[start//Q].update(terminal)
            scout_summary = (folder/'scout.log').read_text().split()
            assert scout_summary[:2] == ['hosts',str(end-start)]
            for label in ('scout','index','audit'):
                cpu_total[label] += cpu(folder/(label+'.time'))
            if require_complete:
                blob = source.read_bytes()
                assert len(blob) == 37*(end-start) and sha256(blob).hexdigest() == expected_hash
                aggregate.update(blob)
                live_from_source = set()
                with journal.open('rb') as handle:
                    read_maps = 0
                    for line in handle:
                        fields = line.split()
                        assert len(fields) == 21 and start <= int(fields[5]) < end
                        if fields[-2:] == [b'live',b'0']:
                            live_from_source.add(tuple(map(int,fields[:-2])))
                        read_maps += 1
                assert live_from_source == pending and read_maps == int(maps)
                bound = [line.split() for line in Path(prefix+'.stream.sha256.tsv').read_text().splitlines()]
                matched, = [item for item in bound if item[:2] == [str(start),str(end)]]
                assert matched == [str(start),str(end),maps,str(journal.stat().st_size),
                                   expected_hash,str(source),digest(journal),str(journal)]
                for line in (folder/'audit.sha256').read_text().splitlines():
                    hashed,name = line.split()
                    if name == 'scout-right.tsv' and not (folder/name).exists():
                        continue
                    assert digest(folder/name) == hashed
            print(start,end,prefix,maps,unresolved,stream_cpu,
                  round(sum(cpu(folder/(label+'.time')) for label in ('scout','index','audit')),3),
                  journal.stat().st_size,expected_hash,sep='\t',file=ledger)
    assert not completion and not statistics, (completion,statistics)
    if require_complete:
        assert not certified
        assert (intervals['hosts'],intervals['shards']) == (TOTAL,len(entries))
        assert aggregate.hexdigest() == EXPECTED[RIGHT]
    print('audited',dict(intervals),'streamed',dict(shard_sizes))
    print('CPU seconds', {name:round(value,3) for name,value in cpu_total.items()})
    print('stream totals',dict(sorted(stream_counts.items())), 'maps',sum(stream_counts.values()))
    print('totals',dict(sorted(counts.items())), 'maps',sum(counts.values()))
    for quartile, stats in enumerate(quartiles):
        print('quartile',quartile+1,dict(sorted(stats.items())),'maps',sum(stats.values()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--complete',action='store_true')
    summarize(parser.parse_args().complete)
