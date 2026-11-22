import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path

from reciprocal_audit import SOURCE22, decode, host_masks
from reciprocal_census import PILOTS
from reciprocal_proof_pilot import proof


DOMAIN = {'row-empty', 'row-column', 'domain-IS', 'forced-domain'}
HEADER = ('key status clauses cnf_bytes lrat_bytes cnf_sha256 lrat_sha256 '
          'generation_cpu solver_cpu dual_check_cpu role_map').replace(' ','\t')


def sample(quartile, budget, interval):
    lo, hi = interval if interval else PILOTS[quartile]
    shard = Path(f'{lo:07d}-{hi:07d}')
    left, right = ([host_masks(decode(row)) for row in path.read_text().splitlines()]
                   for path in (SOURCE22, shard/'hosts.g6'))
    groups = defaultdict(list)
    with (shard/'maps.tsv').open() as source:
        for row in source:
            *fields, reason, _ = row.split()
            if reason in DOMAIN:
                key = tuple(map(int,fields))
                groups[reason].append((sha256(row.encode()).digest(), key))
    output = Path(f'proof-extra-{lo:07d}-{hi:07d}' if interval else f'proof-stage-{quartile}')
    output.mkdir(exist_ok=True)
    counts = Counter()
    with (output/'queue.tsv').open('w') as queue:
        for kind, entries in sorted(groups.items()):
            limit = 3 * budget if kind == 'forced-domain' else budget
            for index, (_, key) in enumerate(sorted(entries)[:limit]):
                print(f'{kind}-{index:03d}',*key,sep='\t',file=queue)
    for thin in (True,False):
        folder = output/('thin' if thin else 'dense')
        folder.mkdir(exist_ok=True)
        with (folder/'receipts.tsv').open('w') as log, (folder/'incomplete.tsv').open('w') as incomplete:
            print(HEADER,file=log)
            for row in (output/'queue.tsv').read_text().splitlines():
                label, *fields = row.split()
                key = tuple(map(int,fields))
                assert lo <= key[5] < hi
                try:
                    receipt = proof(label,key,9,left[key[0]],right[key[5]-lo],3,False,folder,thin)
                except (AssertionError, RuntimeError, TimeoutError) as error:
                    print(row,repr(error),sep='\t',file=incomplete,flush=True)
                    raise
                print(*receipt,sep='\t',file=log,flush=True)
                counts['thin' if thin else 'dense'] += 1
    print(dict(counts))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('quartile', type=int, choices=range(4))
    parser.add_argument('--budget', type=int, default=8)
    parser.add_argument('--interval',type=int,nargs=2)
    args = parser.parse_args()
    sample(args.quartile,args.budget,args.interval)
