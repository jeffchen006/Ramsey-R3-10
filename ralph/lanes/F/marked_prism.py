"""Count one-pole exclusions from three-face identities; all supports live off the mark."""
from collections import defaultdict,Counter
from itertools import combinations
from functools import lru_cache
from pathlib import Path
import sys

from column_audit import normal,insert
from marked_joint import read
from orbit_extend import vertices,independent_sets


class Prisms:
    def __init__(self,adj,size):
        self.adj=adj; self.supportsize=size; self.sites=len(adj)
        self.ids={(left,right):2<<idx for idx,(left,right) in enumerate(combinations(range(self.sites),2)) if adj[left]>>right&1}
        triangles=[sites for sites in combinations(range(self.sites),3) if all(edge in self.ids for edge in combinations(sites,2))]
        self.rels={};self.prisms=[];self.faces=set()
        for triangle in triangles:insert(self.rels,sum(self.ids[edge] for edge in combinations(triangle,2)))
        for left,right in combinations(triangles,2):
            if set(left)&set(right):continue
            match=[(src,dst) for src in left for dst in right if adj[src]>>dst&1]
            if len(match)!=3 or len(set(src for src,dst in match))!=3 or len(set(dst for src,dst in match))!=3:continue
            faces=[]
            for (first,dest),(second,end) in combinations(match,2):
                sides=[(first,dest),(dest,end),(end,second),(second,first)];raw=sum(self.ids[tuple(sorted(edge))] for edge in sides);faces.append(normal(self.rels,raw))
            assert all(faces) and faces[0]^faces[1]^faces[2]==0
            self.prisms.append(tuple(faces));self.faces.update(faces)

    @lru_cache(None)
    def parts(self,mask):
        result=[]
        while mask:
            part=mask&-mask;todo=part;mask^=part
            while todo:
                bit=todo&-todo;todo^=bit;more=self.adj[bit.bit_length()-1]&mask;mask^=more;part|=more;todo|=more
            result.append(part)
        return tuple(result)

    def supports(self):
        bank=defaultdict(list)
        for group in combinations(range(self.sites),self.supportsize):
            lifted={}
            for edge in combinations(group,2):
                if edge in self.ids:
                    left,right=edge;insert(lifted,(1<<(256+left))^(1<<(256+right))^self.ids[edge])
            residual={}
            for pivot,row in lifted.items():
                if pivot<1<<256:insert(residual,normal(self.rels,row))
            if len(residual)==1:
                face=next(iter(residual.values()))
                if face in self.faces:bank[face].append(sum(1<<idx for idx in group))
        return bank

    def sieve(self,bank,rows):
        passed=[];failed=[];populated=sum(all(face in bank for face in prism) for prism in self.prisms)
        for occupied,doubles,weight in rows:
            recipes={}
            for face,group in bank.items():
                for support in group:
                    if support&doubles:continue
                    if all(len(self.parts(occupied&part))<=1 for part in self.parts(support)):
                        recipes[face]=support;break
            proof=next((tuple(recipes[face] for face in prism) for prism in self.prisms if all(face in recipes for face in prism)),None)
            entry=occupied,doubles,weight
            if proof:failed.append((*entry,*proof))
            else:passed.append(entry)
        print('prisms',len(self.prisms),'supported',populated,'face types',len(bank),'bank supports',sum(map(len,bank.values())),'rows',len(rows),'passed',len(passed),sum(row[2] for row in passed),'cuts',len(failed),flush=True)
        return passed,failed


def prismctl():
    adj=[sum(1<<other for other in range(6) if site!=other and (site//3==other//3 or site%3==other%3)) for site in range(6)]
    engine=Prisms(adj,5);bank=engine.supports();passed,failed=engine.sieve(bank,[(0,0,1),(17,0,1)])
    assert [row[0] for row in passed]==[17] and [row[0] for row in failed]==[0]
    for contact in (0,(1<<0)|(1<<9)):
        physical=[1<<(idx^1) for idx in range(12)]+[contact]
        for left,right in engine.ids:
            parity=int((left,right)!=(2,5))
            for bit in range(2):
                src=2*left+bit;dst=2*right+(bit^parity);physical[src]|=1<<dst;physical[dst]|=1<<src
        for site in vertices(contact):physical[site]|=1<<12
        assert not any(physical[left]&physical[right] for left,right in combinations(range(13),2) if physical[left]>>right&1)
        bad=next(independent_sets(physical,8191,6),None);assert (bad is None)==bool(contact);print('13-vertex control',contact,'literal I6',bad)


def target(mode):
    adj=[sum(1<<right for right in range(17) if 6<=abs(left-right)<=12) for left in range(17)];engine=Prisms(adj,9)
    if mode=='bank':
        bank=engine.supports();Path('prism.bank').write_text(''.join(' '.join(map(str,[face,*rows]))+'\n' for face,rows in sorted(bank.items())));print('bank',[(len(rows)) for face,rows in sorted(bank.items())]);return
    bank={row[0]:row[1:] for row in read('prism.bank')};rows=read('wpole.rows');pilot=mode=='pilot'
    passed,failed=engine.sieve(bank,rows[::64] if pilot else rows)
    prefix='pprism' if pilot else 'prism';Path(prefix+'.rows').write_text(''.join(' '.join(map(str,row))+'\n' for row in passed));Path(prefix+'.rejects').write_text(''.join(' '.join(map(str,row))+'\n' for row in failed))


if __name__=='__main__':
    if sys.argv[1]=='control':prismctl()
    else:target(sys.argv[1])
