"""Small final replay. All source masks are checked directly in original edge coordinates."""
from collections import Counter
from fractions import Fraction
from math import ceil,gcd
from pathlib import Path

from column_audit import put
from column_bind import bind
from cyclic_check import read_base
from old_indicator import independent_check
from orbit_extend import vertices


def copies(source,order,prefix):
    independent_check(source,order,prefix);base=read_base(Path(source).read_text().strip());size=len(base);masks=list(map(int,Path(prefix+'.witness').read_text().split()))
    copies=set();perms=[]
    for unit in range(1,size):
        if gcd(unit,size)!=1:continue
        for shift in range(size):
            perm=[(unit*site+shift)%size for site in range(size)]
            if any(base[left][right]!=base[perm[left]][perm[right]] for right in range(size) for left in range(right+1)):continue
            perms.append(perm);copies.add(tuple(sorted(sum(1<<perm[site] for site in vertices(mask)) for mask in masks)))
    freq=Counter(mask for copy in copies for mask in copy);costs={}
    for mask in freq:
        sites=set(vertices(mask));parts=0
        while sites:
            stack=[sites.pop()];parts+=1
            while stack:
                site=stack.pop();neighbors={other for other in sites if base[site][other]};sites-=neighbors;stack.extend(neighbors)
        costs[mask]=2**parts
    price=max(Fraction(occurs,costs[mask]) for mask,occurs in freq.items());lower=2*ceil(Fraction(len(copies),2)/price)
    print(prefix,'group',len(perms),'distinct proof copies',len(copies),'distinct supports',len(freq),'max multiplicity / physical sets',str(price),'I%d >= %d'%(order,lower));return lower


def freeze():
    bind();assert copies('oldpath.q',5,'oldpath')>=2
    parents=Path('../r13/max.q').read_text().splitlines();assert all(Path(f'old{index}.q').read_text().strip()==parents[index] for index in (8,15,21,43,81));assert len(parents)==120
    entries=[line.split() for line in Path('old43.flat').read_text().splitlines()];tag,*indices=Path('old43.xor').read_text().split();assert tag=='43' and len(indices)==7
    selected=[entries[int(index)] for index in indices];assert all(name=='43' and poles=='0' for name,poles,*_ in selected)
    put('seven43.witness',[fields[2] for fields in selected]);copies('old43.q',10,'seven43');copies('old81.q',10,'cube81')
    print('cyclic 36-card previous five -> residual 8 and 21 only; zero complete-target models tested')


if __name__=='__main__':freeze()
