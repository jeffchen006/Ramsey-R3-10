"""Exact constant-on-rotation baseline, then free triangle-preserving signing descent."""

from argparse import ArgumentParser
from itertools import combinations
from pathlib import Path
from dihedral_score import nullspace,ev
from relift_audit import decode,pairs,explicit_lift
from orbit_extend import to_graph6,parse_graph6
from block_score_check import count


def score(text,target):
    matrix=decode(text);size=len(matrix);long=2*size//5
    rotation=[start+(pos+1)%length for start,length in [(0,long),(long,long),(2*long,long//2)] for pos in range(length)]
    singles=[pair for pair in pairs(size) if pair[0]!=pair[1] and matrix[pair[0]][pair[1]]==1]
    marks={pair:1<<idx for idx,pair in enumerate(singles)};columns=[];seen=set();forest=[];parts=[{vertex} for vertex in range(size)]
    for source in singles:
        left,right=source
        if parts[left]!=parts[right]:
            joint=parts[left]|parts[right];forest.append(marks[source]);
            for vertex in joint:parts[vertex]=joint
        if source in seen:continue
        edge=source;column=0
        while edge not in seen:
            seen.add(edge);column|=marks[edge];edge=tuple(sorted(rotation[vertex] for vertex in edge))
        assert edge==source;columns.append(column)
    triangles=[]
    for triple in combinations(range(size),3):
        edges=list(combinations(triple,2))
        if all(edge in marks for edge in edges):triangles.append(sum(marks[edge] for edge in edges))
    projected=[sum(1<<pos for pos,column in enumerate(columns) if (row&column).bit_count()%2) for row in triangles]
    restricted=nullspace(len(columns),projected);directions=[]
    for vector in restricted:directions.append(sum(column for pos,column in enumerate(columns) if vector&(1<<pos)))
    def lift(point):return explicit_lift(matrix,iter(int(not (point&(1<<index))) for index in range(len(singles))))
    point=0;best=1<<62;bestpoint=0
    for number in range(1<<len(directions)):
        if number:point^=directions[(number&-number).bit_length()-1]
        value=ev.indep(lift(point),target,best+1)
        if value<best:best,bestpoint=value,point
    baseline=best;original=to_graph6(lift(bestpoint));moves=nullspace(len(singles),triangles+forest)
    while True:
        current=bestpoint
        for delta in moves:
            value=ev.indep(lift(current^delta),target,best+1)
            if value<best:best,bestpoint=value,current^delta
        if bestpoint==current:break
    return baseline,best,len(restricted),len(moves),original,to_graph6(lift(bestpoint))


def audit(matrix,target,value,text):
    graph=parse_graph6(text);size=len(matrix)
    for left in range(2*size):
        for right in range(2*size):
            assert (graph[left]>>right)&1==(graph[left^1]>>(right^1))&1
            if graph[left]&(1<<right):assert not(graph[left]&graph[right])
        for fiber in range(size):assert ((graph[left]>>(2*fiber))&3).bit_count()==matrix[left//2][fiber]
    assert count(graph,target)==value


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__);parser.add_argument('source');parser.add_argument('target',type=int);parser.add_argument('indices');args=parser.parse_args();rows=Path(args.source).read_text().splitlines()
    for index in map(int,Path(args.indices).read_text().split()):
        text=rows[index];base=decode(text);restricted,value,dim,free,original,lifted=score(text,args.target)
        for scorevalue,graph in ((restricted,original),(value,lifted)):audit(base,args.target,scorevalue,graph)
        print(index,sum(map(sum,base)),restricted,value,dim,free,original,lifted,flush=True)
