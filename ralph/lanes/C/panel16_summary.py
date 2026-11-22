#!/usr/bin/env python3
import argparse
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path


DENOMINATOR = 15_051_526_031
BUCKETS = {(66,4):6_301_695_100, (67,5):2_908_149_371, (68,4):4_368_270_858,
           (69,5):822_786_130, (70,4):615_165_768, (71,5):35_458_804}
SHAPES = ({'2233','2333'}, {'2334','3333','3334'})


def read_rows(path):
    with Path(path).open() as stream:
        header = stream.readline().split()
        for line in stream:
            fields = line.split()
            assert len(fields) == len(header), (path,line)
            yield dict(zip(header,fields))


def sorted_shape(text):
    return ''.join(sorted(text))


def manifest(source, destination):
    source = Path(source)
    strata, sizes, keys = {}, {}, Counter()
    for row in read_rows(source/'strata.tsv'):
        total, neutral = map(int,(row['D16'],row['d16']))
        shapes = tuple(sorted_shape(row[name]) for name in ('shape16','shape17'))
        assert shapes[0] in SHAPES[0] and shapes[1] in SHAPES[1]
        index = total, neutral, *shapes
        counts = (int(row['frames16']),int(row['frames17']))
        assert total+9 == int(row['D17']) and 9-neutral == int(row['d17'])
        count = int(row['ordered_headers'])
        assert index not in strata and count == counts[0]*counts[1] > 0
        strata[index] = count
        sizes[index] = counts
        keys[total,neutral] += count
    assert len(strata) == 34 and keys == BUCKETS and sum(strata.values()) == DENOMINATOR
    ranks = defaultdict(set)
    pilot = {}
    with (source/'pilot.bound.tsv').open() as bound, (source/'pilot.frames').open() as frames:
        for ordinal, (info,line,raw) in enumerate(zip(read_rows(source/'pilot.index.tsv'),bound,frames,strict=True)):
            values = list(map(int,line.split()))
            assert len(values) == 18
            left,right,*_ = values
            assert int(info['pilot_row']) == ordinal and int(info['frame16']) == left and int(info['frame17']) == right
            physical = values[:8]+values[10:16]
            assert list(map(int,raw.split())) == physical[2:]
            total, neutral = values[8:10]
            assert [total+9,9-neutral] == values[16:18]
            assert [total,neutral] == [int(info['D16']),int(info['d16'])]
            index = total,neutral,*(sorted_shape(info[name]) for name in ('shape16','shape17'))
            rank = int(info['bucket_ordinal'])
            ranks_left, ranks_right = sizes[index]
            rank_left, rank_right = int(info['rank16']),int(info['rank17'])
            assert 0 <= rank_left < ranks_left and 0 <= rank_right < ranks_right
            assert rank == rank_left*ranks_right + rank_right and rank not in ranks[index]
            assert (left,right) not in pilot
            ranks[index].add(rank)
            pilot[left,right] = (index,physical)
    assert len(pilot) == 544 and ranks.keys() == strata.keys()
    for index, taken in ranks.items():
        total = strata[index]
        assert len(taken) == 16 and {0,total//2,total-1} <= taken
    if destination:
        with Path(destination).open('w') as stream:
            for _, physical in pilot.values():
                print(*physical,file=stream)
    return pilot,strata


def stats(path, keys):
    result = {}
    for entry in read_rows(path):
        index = int(entry['left']),int(entry['right'])
        assert index not in result and index in keys
        result[index] = entry
    assert result.keys() == keys
    return result


def cpu(row, *fields):
    return sum(Decimal(row[field]) for field in fields)


def percentile(values, hundredile):
    return sorted(values)[(len(values)*hundredile-1)//100]


def summarize(source, directory):
    pilot,strata = manifest(source,None)
    directory = Path(directory)
    data = stats(directory/'pilot.stats',pilot.keys())
    fast = stats(directory/'preflight.stats',pilot.keys())
    verify = {}
    with (directory/'audit.log').open() as stream:
        for line in stream:
            columns = line.split()
            if len(columns) == 5 and columns[2] in ('empty','join'):
                left,right = map(int,columns[:2])
                assert (left,right) not in verify and (left,right) in pilot
                verify[left,right] = tuple(columns[2:])
    assert verify.keys() == pilot.keys()
    assert not (directory/'pilot.fills').stat().st_size
    groups = defaultdict(Counter)
    prices = defaultdict(dict)
    tails = []
    for identity, row in data.items():
        index, _ = pilot[identity]
        assert tuple(row[name] for name in ('shape_l','shape_r')) == index[2:]
        before,after = (tuple(map(int,row[name].split(','))) for name in ('before','after'))
        assert len(before) == len(after) == 8 and 0 in after
        assert all(value >= kept for value,kept in zip(before,after))
        alive = 0 not in before
        assert alive == bool(int(fast[identity]['survive'])) == (verify[identity][0]=='join')
        assert row['filtered_cap'] == 'no' and row['literal_cap'] in ('no','probes')
        assert not any(int(row[name]) for name in ('degree','triangle','codegree','I','live'))
        metrics = groups[index]
        metrics['sample'] += 1
        metrics['empty_left'] += not all(before[::2])
        metrics['empty_right'] += not all(before[1::2])
        metrics['both_nonempty'] += alive
        metrics['literal_caps'] += row['literal_cap'] != 'no'
        metrics['hits'] += int(fast[identity]['hits'])
        metrics['misses'] += int(fast[identity]['misses'])
        old_setup = cpu(row,'atlas_ms','domain_ms')
        new_setup = cpu(fast[identity],'atlas_ms','preflight_ms') + (cpu(row,'domain_ms') if alive else 0)
        filter_cost = cpu(row,'copy_filter_ms','filtered_ms')
        costs = {'cold_atlas': cpu(row,'atlas_ms'), 'domains': cpu(row,'domain_ms'),
                 'literal_join': cpu(row,'literal_ms'), 'filtered_join': filter_cost,
                 'preflight_only': cpu(fast[identity],'preflight_ms'),
                 'baseline_literal': old_setup + cpu(row,'literal_ms'), 'baseline_filtered': old_setup+filter_cost,
                 'cached_filtered_model': new_setup+(filter_cost if alive else 0),
                 'warm_filtered': cpu(row,'domain_ms')+filter_cost,
                 'warm_cached_model': new_setup-cpu(fast[identity],'atlas_ms')+(filter_cost if alive else 0),
                 'independent': 1000*Decimal(verify[identity][1])}
        prices[identity] = costs
        for metric,value in costs.items():
            metrics[metric] += value
        if row['literal_cap'] != 'no':
            tails.append((identity, row['literal_ms'], verify[identity][1], verify[identity][2]))
    print('denominator',DENOMINATOR,'sample',len(pilot),'unresolved',DENOMINATOR-len(pilot),'strata',len(strata))
    print('paired direction counts; neither direction is treated as new IDs')
    metrics = sum(groups.values(),Counter())
    for metric in ('empty_left','empty_right','both_nonempty','literal_caps','hits','misses'):
        print(metric,metrics[metric])
    print('probe-capped direct IDs (literal ms, independent s, independent probes)')
    for record in tails:
        print(*record)
    print('metric pilot_total_CPU_ms p50_ms p95_ms max_ms max_ID stratum_weighted_CPU_hours')
    for metric in next(iter(prices.values())):
        peak = max(prices,key=lambda identity:prices[identity][metric])
        values = [entry[metric] for entry in prices.values()]
        projected = sum(strata[index]*detail[metric]/detail['sample'] for index,detail in groups.items())/3_600_000
        print(metric,sum(values),percentile(values,50),percentile(values,95),max(values),peak,f'{projected:.2f}')
    print('D16 d16 shape16 shape17 labelled_headers sample both_nonempty literal_caps filtered_ms cached_model_ms independent_ms')
    for index, total in sorted(strata.items(), key=lambda entry:(-entry[1],entry[0])):
        group = groups[index]
        print(*index,total,*(group[name] for name in ('sample','both_nonempty','literal_caps',
                                                    'baseline_filtered','cached_filtered_model','independent')))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode',choices=('manifest','summary'))
    parser.add_argument('source')
    parser.add_argument('destination')
    args = parser.parse_args()
    if args.mode == 'manifest':
        manifest(args.source,args.destination)
    else:
        summarize(args.source,args.destination)


if __name__ == '__main__':
    main()
