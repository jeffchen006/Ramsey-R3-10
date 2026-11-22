import argparse
from collections import Counter, defaultdict
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import sys
from time import process_time

from reciprocal_audit import ROOT, SCOUT, SOURCE22, decode, host_masks, keys, merge, vertices, witness_check


RIGHT = ROOT/'scratch/B/val/r3_7_21.g6'
LEFT_CARDS = SCOUT/'wide22.tsv'
TOTAL = 1_118_436
Q = TOTAL//4
PILOTS = [(q*Q+offset, q*Q+offset+4096)
          for q, offset in enumerate((20_480, 131_072, 16_384, 245_760))]
EXPECTED = {SOURCE22: '228d886ee01b3003d90c768af57804954f7adccbca901a3eeb3c69ccc020e8c5',
            RIGHT: 'f8b413af3681d32a217960bdf4e80eeb5276cdfe5c26fb1f013dc7ce72070ba9'}
ROUNDS = ('stage', 'full')


def digest(path):
    with path.open('rb') as source:
        return sha256(source.read()).hexdigest()


def prepare():
    for source, expected in EXPECTED.items():
        assert digest(source) == expected
    rows = RIGHT.read_bytes().splitlines(keepends=True)
    assert len(rows) == TOTAL and all(len(row) == 37 and row[0] == 84 and row[-1] == 10 for row in rows)
    assert len(SOURCE22.read_bytes().splitlines()) == 191
    workers = {(stage, worker): [] for stage in ROUNDS for worker in range(4)}
    for quartile, (first, last) in enumerate(PILOTS):
        workers['stage', quartile].append((first, last))
        cursor = quartile
        for beg, end in [(quartile*Q, first), (last, (quartile+1)*Q)]:
            for start in range(beg,end,16_384):
                workers['full', cursor%4].append((start,min(start+16_384,end)))
                cursor += 1
    intervals = sorted(item for group in workers.values() for item in group)
    assert intervals[0][0] == 0 and intervals[-1][1] == TOTAL
    assert all(a[1] == b[0] for a,b in zip(intervals,intervals[1:]))
    with Path('inputs.tsv').open('w') as log:
        for stage in ROUNDS:
            for worker in range(4):
                with Path(f'{stage}-{worker}.batch').open('w') as batch:
                    for start,end in workers[stage,worker]:
                        folder = Path(f'{start:07d}-{end:07d}')
                        folder.mkdir(exist_ok=True)
                        source = folder/'hosts.g6'
                        source.write_bytes(b''.join(rows[start:end]))
                        print(start,end,source,folder/'maps.tsv',sep='\t',file=batch)
                        print(stage,worker,start,end,source,digest(source),sep='\t',file=log)


def audit(start, end, merge_method):
    sys.path.append(str(SCOUT))
    from join import bijections, forced_allows, triples
    started = process_time()
    left = [host_masks(decode(line)) for line in SOURCE22.read_text().splitlines()]
    right = [host_masks(decode(line)) for line in Path('hosts.g6').read_text().splitlines()]
    assert len(right) == end-start
    if merge_method != 'legacy':
        from reciprocal_replay_merge import factory
        fast_merge = factory(left,right)

    @lru_cache(maxsize=None)
    def marks(lane, idx, core):
        result = [tuple(sorted(mark)) for mark in triples((left,right)[lane][idx],core,5,9)]
        assert len(result) == len(set(result))
        return result

    def groups(which, name):
        result = defaultdict(list)
        with Path(name).open() as journal:
            for row in journal:
                color, host, core, multiplicity = map(int,row.split())
                regenerated = marks(which,host,core)
                if which == 0:
                    assert len(regenerated) == multiplicity, (name, host, core)
                else:
                    assert len(regenerated) <= multiplicity, (name, host, core)
                if regenerated:
                    result[color].append((host,core,regenerated,vertices(core)))
        return result

    first = groups(0,'scout-left-live.tsv')
    second = groups(1,'scout-right-live.tsv')
    assert second.keys() <= first.keys()
    actual = keys('maps.tsv')
    verdicts = Counter()
    unresolved = 0
    disagreement = 0
    with Path('unresolved.tsv').open('w') as open_cases:
        for shade, right_forms in second.items():
            for rid, rcore, rmarks, _ in right_forms:
                for lid, lcore, lmarks, left_sites in first[shade]:
                    for correspondence in bijections(left[lid],lcore,right[rid],rcore,9):
                        mapping = tuple(correspondence[src] for src in left_sites)
                        for lmark in lmarks:
                            for rmark in rmarks:
                                key = (lid,lcore,*lmark,rid+start,rcore,*rmark,*mapping)
                                reason, witness = actual.pop(key)
                                if merge_method == 'legacy':
                                    lower, ll, rr = merge(left[lid],right[rid],key,3)
                                else:
                                    lower = fast_merge(lid,lcore,lmark,rid,rcore,mapping,rmark)
                                    ll,rr = 13,12
                                    if merge_method == 'compare':
                                        assert (lower,ll,rr) == merge(left[lid],right[rid],key,3), key
                                direct = witness_check(lower,ll,rr,9,5,reason,witness)
                                verdicts[reason] += 1
                                if direct is not None:
                                    assert direct, (key,reason,witness)
                                else:
                                    alternate = forced_allows(lower,ll,9,5,True,rr)
                                    verdicts[f'audit:{alternate}'] += 1
                                    if alternate == 'live':
                                        unresolved += 1
                                        disagreement += reason != 'live'
                                    if reason == 'live' or alternate == 'live':
                                        print(*key,reason,witness,alternate,sep='\t',file=open_cases)
    assert not actual, (len(actual),next(iter(actual),None))
    count = sum(total for reason,total in verdicts.items() if not reason.startswith('audit:'))
    print(start,end,count,unresolved,round(process_time()-started,6),dict(sorted(verdicts.items())),flush=True)
    assert disagreement == 0, (disagreement, count)
    assert unresolved*100 <= max(count,1), (unresolved,count)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['prepare', 'audit'])
    parser.add_argument('limits', nargs='*', type=int)
    parser.add_argument('--merge',choices=['legacy','compare','cached'],default='cached')
    args = parser.parse_args()
    prepare() if args.mode == 'prepare' else audit(*args.limits,args.merge)
