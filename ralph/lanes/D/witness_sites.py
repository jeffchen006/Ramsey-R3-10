"""Candidate positions of the unique common defect witness, up to exterior cells."""
from pathlib import Path
import sys


def expand(source, dest):
    records=[]
    for idx,text in enumerate(source.read_text().splitlines()):
        cells=[tuple(map(int,field.split(':'))) for field in text.split()];n=40 if sum(pop for _,pop in cells)==31 else 22;keysize=9;assert sum(pop for _,pop in cells)==n-keysize
        graph=[0]*n
        def link(first,last):graph[first]|=1<<last;graph[last]|=1<<first
        link(0,1)
        for point in range(2,keysize):
            link(point%2,point)
            if point+1<keysize:link(point,point+1)
        sites=list(range(keysize));start=keysize
        for mask,pop in cells:
            sites.append(start)
            for point in range(start,start+pop):
                for side in range(keysize):
                    if mask>>side&1:link(point,side)
            start+=pop
        possible=(1<<n)-1
        for first in range(keysize):
            for last in range(first):
                overlap=graph[first]&graph[last]
                if overlap.bit_count()==1:possible&=overlap
        for site in sites:
            if possible>>site&1:records.append((idx,site,text))
    dest.write_text(''.join(f'{1<<site} {text}\n' for idx,site,text in records));dest.with_suffix('.ids').write_text(''.join(f'{idx} {site}\n' for idx,site,text in records));print('inputs',len(source.read_text().splitlines()),'site records',len(records))


if __name__=='__main__':expand(*map(Path,sys.argv[1:]))
