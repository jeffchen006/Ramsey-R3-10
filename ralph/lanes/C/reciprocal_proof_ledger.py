from collections import Counter
import csv
from pathlib import Path

from reciprocal_census_ledger import stream_statistics
from reciprocal_census_proofs import DOMAIN
from reciprocal_proof_pilot import digest


def receipts(folder):
    result = {}
    with (folder/'receipts.tsv').open() as source:
        for row in csv.DictReader(source,delimiter='\t'):
            label = row['key']
            assert label not in result and row['status'] == 'dual-LRAT'
            for suffix in ('cnf','lrat'):
                path = folder/f'{label}.{suffix}'
                assert digest(path) == row[f'{suffix}_sha256'] and path.stat().st_size == int(row[f'{suffix}_bytes'])
            assert 's VERIFIED UNSAT' in (folder/f'{label}.cake_lpr').read_text()
            assert 'c VERIFIED' in (folder/f'{label}.lrat-check').read_text()
            result[label] = row
    return result


def clauses(filename):
    with filename.open() as source:
        cmd,fmt,variables,count = next(source).split()
        assert (cmd,fmt) == ('p','cnf')
        rows = [tuple(map(int,line.split())) for line in source]
        assert int(count) == len(rows)
        assert all(row[-1] == 0 and all(0 < abs(lit) <= int(variables) for lit in row[:-1]) for row in rows)
        return variables,set(rows)


def totals_by_category(groups):
    return {mode: {category: round(total[category]/count[category],8) for category in count}
            for mode,(total,count) in groups.items()}


def main():
    pricing = {'thin': (Counter(),Counter()), 'dense': (Counter(),Counter())}
    support_pricing = (Counter(),Counter())
    candidates = [*Path('.').glob('proof-stage-*'),*Path('.').glob('proof-extra-*')]
    for folder in sorted(path for path in candidates if path.is_dir()):
        expected = {}
        for row in (folder/'queue.tsv').read_text().splitlines():
            label,*key = row.split()
            assert label not in expected
            expected[label] = ','.join(key)
        dense_variable_count = '156'
        variants = {mode:receipts(folder/mode) for mode in pricing}
        if (folder/'support').exists():
            variants['support'] = receipts(folder/'support')
        for mode,rows in variants.items():
            assert expected == {tag:row['role_map'] for tag,row in rows.items()}
            total,count = support_pricing if mode == 'support' else pricing[mode]
            for label,row in rows.items():
                kind = label.rsplit('-',1)[0]
                assert kind in DOMAIN
                total[kind] += sum(float(row[key]) for key in ('generation_cpu','solver_cpu','dual_check_cpu'))
                count[kind] += 1
        for tag in expected:
            thin_vars,thin = clauses(folder/'thin'/f'{tag}.cnf')
            dense_vars,dense = clauses(folder/'dense'/f'{tag}.cnf')
            assert thin_vars == dense_vars == dense_variable_count and thin <= dense
        print(folder, len(expected), 'same-key dual LRATs and exact dense/thin clause containment')
    print('sample CPU-s per map',totals_by_category(pricing | {'support':support_pricing}))
    complete = Counter()
    for reasons in stream_statistics(True).values():
        complete.update(reasons)
    for mode,means in totals_by_category(pricing | {'support':support_pricing}).items():
        print('projection',mode,round(sum(complete[kind]*means[kind] for kind in DOMAIN)/3600,5),'CPU-h, proofs only')
    live = receipts(Path('live-proofs'))
    live_dense = receipts(Path('live-proofs-dense'))
    assert len(live) == len(live_dense) == 32 and set(live) == set(live_dense)
    assert all(live[tag]['role_map'] == live_dense[tag]['role_map'] for tag in live)
    print('32 repair keys each have checked support and original dense LRATs')


if __name__ == '__main__':
    main()
