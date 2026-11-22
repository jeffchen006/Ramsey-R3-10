from pathlib import Path
from collections import Counter
import gzip,json,sys

def rows():
    for label in ('trial','price','strata'):
        for path in Path('.').glob(label+'*.rows'):yield from path.read_bytes().splitlines()
    for label in ('first','all'):
        for table in Path('work_'+label).glob('w*.jsonl'):
            for line in table.read_text().splitlines():
                entry=json.loads(line)
                if entry['status']=='scanned':yield from gzip.decompress((table.parent/f"s{entry['index']:05d}.rows.gz").read_bytes()).splitlines()

def main():
    keys=[];caps=[];deep=[];counts=Counter();regions={region:Counter() for region in (92,305,504,511)}
    for line in rows():
        fields=line.split();key=int(fields[0]);kind=fields[1].decode();counts[kind]+=1
        if key>>26 in regions:regions[key>>26][kind]+=1
        if kind=='cap':caps.append(key);keys.append(key)
        if kind=='multi' and int(fields[5]):keys.append(key)
        if kind=='multi' and int(fields[6]):deep.append(key)
    assert len(keys)==len(set(keys)) and len(caps)==len(set(caps));Path('five.keys').write_text(''.join(f'{key}\n' for key in sorted(keys)));Path('allcaps.keys').write_text(''.join(f'{key}\n' for key in sorted(caps)));Path('triple.keys').write_text(''.join(f'{key}\n' for key in sorted(deep)));print('all bare signs',sum(counts.values()),dict(counts),'five-pole source keys',len(keys),'allcaps',len(caps),'independent triple attained (noncaps)',len(deep));print('by selected high-nine prefix',regions)
if __name__=='__main__':main()
