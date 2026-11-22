from pathlib import Path
from random import Random
import sys
from eight_chart import roots

def main():
    seeds=roots();regions=sorted({key>>18 for key in seeds});retired={key>>12 for key in seeds};assert len(regions)==len(retired)==3;random=Random(23003218);sample=set()
    for key in seeds:
        sample.update(key^(1<<index) for index in range(12,18));allowed=[candidate for candidate in range((key>>18)<<18,((key>>18)+1)<<18) if candidate>>12 not in retired];sample.update(random.sample(allowed,48))
    assert all(key>>18 in regions and key>>12 not in retired for key in sample);Path('pilot.keys').write_text(''.join(f'{key}\n' for key in sorted(sample)));count=0;streams=[Path(f'slot{slot}.keys').open('x') for slot in range(4)]
    try:
        for region in regions:
            for key in range(region<<18,(region+1)<<18):
                if key>>12 in retired or key in sample:continue
                print(key,file=streams[count%4]);count+=1
    finally:
        for stream in streams:stream.close()
    print('3 disjoint high-12 regions',regions,'minus high-18 regions',sorted(retired),'fresh raw',count+len(sample),'physical pilot',len(sample),'untouched',count)
if __name__=='__main__':main()
