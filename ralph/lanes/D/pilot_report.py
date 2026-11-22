"""Stratified P8 join estimates; sampling is without replacement per fingerprint."""

import csv
from collections import Counter,defaultdict
from pathlib import Path
import sys


def report(path):
    buckets=[{key:float(value) for key,value in row.items()} for row in csv.DictReader((path/'buckets.tsv').open(),delimiter='\t')]
    hist=Counter();by_mult=defaultdict(Counter);kept=0;per=defaultdict(list);screens=iter((path/'filter.out').open());unc=0;var=0
    factor=lambda bucket:bucket['population']/bucket['sample']
    print('dir',path,'buckets',len(buckets),'population',int(sum(row['population']for row in buckets)))
    for text in (path/'cases.tsv').read_text().splitlines()[1:]:
        index,rank,left,right,number,canonical=map(int,text.split());bucket=buckets[index];weight=factor(bucket);hist[number]+=weight
        label=next(cap for cap in (100,1000,10000,100000,1000000,10000000) if bucket['population']<=cap);sub=by_mult[label];sub['pairs']+=weight;sub['sample']+=1;sub['labelled']+=number*weight;sub['canon']+=canonical*weight;per[index].append(canonical);sub['max']=max(number,sub['max'])
        for _ in range(canonical):
            row=next(screens).split();assert int(row[0])==kept;kept+=1
            if int(row[1])==0:unc+=weight;sub['basic_live']+=weight
    assert next(screens,None) is None
    for index,data in per.items():
        n=len(data);pop=buckets[index]['population'];mean=sum(data)/n
        if n>1:var+=pop**2*(1-n/pop)*sum((x-mean)**2 for x in data)/(n-1)/n
    for key in ('sample','index_pairs','by_c1','by_c2','by_c3','labelled','canonical','bytes','elapsed'):
        print(key,'observed',round(sum(row[key] for row in buckets),4),'stratified estimate',round(sum(row[key]*factor(row)for row in buckets),3))
    print('design-based 1SE canonical',round(var**.5),'basic live estimate',round(unc),'max matched fingerprint size',max(int(row['population'])for row in buckets))
    total=sum(hist.values());running=0;quant=[.5,.9,.95,.99,.999]
    for size,freq in sorted(hist.items()):
        running+=freq
        while quant and running>=quant[0]*total:print('weighted quantile',quant.pop(0),size)
    print('observed maximum',max(hist))
    print('bucket_population<=\tpairs\tsample\tlabelled\tcanon\tmax\tbasic_live')
    for label,counts in sorted(by_mult.items()):print(label,*(round(counts[key]) for key in ('pairs','sample','labelled','canon','max','basic_live')),sep='\t')


if __name__=='__main__':
    for name in sys.argv[1:]:report(Path(name))
