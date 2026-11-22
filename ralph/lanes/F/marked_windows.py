"""Price known independent mate subsets by the sizes and edges of their common non-neighbors."""
from functools import lru_cache
from pathlib import Path
import sys

from orbit_extend import ROOT, vertices

sys.path.insert(0,str(ROOT/'cases'))
from etables import E


def floor(target, order):
    if order < target: return 0
    if target == 1: return 999
    if target == 2: return 1 if order == 2 else 999
    value=E[target].get(order)
    return 999 if value is None else value


class Windows:
    def __init__(self, size, target):
        self.size=size; self.target=target; self.all=(1<<size)-1
        self.adj=[sum(1<<other for other in range(size) if (abs(site-other)==1 if size==3 else 6<=abs(site-other)<=12)) for site in range(size)]

    @lru_cache(None)
    def signless(self,mask):
        if not mask:return 0,0,0
        bit=mask&-mask; rest=mask^bit; neighbors=self.adj[bit.bit_length()-1]; seen,twice,edges=self.signless(rest)
        return seen|neighbors,twice|(seen&neighbors),edges+(rest&neighbors).bit_count()

    def bounds(self,occupied,doubles,chosen,mode):
        clear=self.all^occupied; singles=occupied^doubles; free=clear
        base=chosen.bit_count(); pins=singles^chosen
        if mode=='pole': base+=1
        elif mode=='holes': base+=2*doubles.bit_count(); free &= ~self.signless(doubles)[0]
        elif mode=='both': base=2; pins=0
        else: raise ValueError(mode)
        seen,twice,_=self.signless(chosen); wholes=free&~seen; rest=free&~twice
        order=wholes.bit_count()+rest.bit_count()+pins.bit_count()
        edges=wholes.bit_count()+self.signless(rest|pins)[2]+self.signless(wholes)[2]-self.signless(pins)[2]
        threshold=self.target-base
        return threshold,order,edges,floor(threshold,order) if threshold>0 else 999

    def cut(self,occupied,doubles,exterior=False):
        singles=occupied^doubles
        for mode in (('both','pole','holes') if doubles else ('pole',)):
            if exterior and mode=='both':continue
            chosen=0 if mode=='both' else singles
            while True:
                threshold,order,edges,limit=self.bounds(occupied,doubles,chosen,mode)
                if edges<limit: return mode,chosen,threshold,order,edges,limit
                if not chosen:break
                chosen=(chosen-1)&singles
        return None


def main():
    small=sys.argv[1] in ('control','smallpole'); size,target=(3,4) if small else (17,10); windows=Windows(size,target)
    src,dest,stride=sys.argv[2:]; passed=[]; failed=[]
    for line in Path(src+'.rows').read_text().splitlines()[::int(stride)]:
        occupied,doubles,orbit=map(int,line.split()); failure=windows.cut(occupied,doubles,sys.argv[1] in ('pole','smallpole'))
        if failure:failed.append(' '.join(map(str,[occupied,doubles,orbit,*failure])))
        else:passed.append(line)
    for kind,rows in [('rows',passed),('rejects',failed)]:Path(dest+'.'+kind).write_text(''.join(row+'\n' for row in rows))
    print('surviving reps,labels',len(passed),sum(int(line.split()[2]) for line in passed),'rejected',len(failed),sum(int(line.split()[2]) for line in failed))


if __name__=='__main__': main()
