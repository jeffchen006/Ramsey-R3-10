"""Compare exact dihedrally invariant signings with triangle-preserving descent on the same base."""

from itertools import combinations
from pathlib import Path
import argparse
import sys
from time import process_time

from relift_audit import decode, pairs, explicit_lift, quotient, walk_score
from orbit_extend import to_graph6

sys.path.insert(0,str(Path('../r8').resolve()))
import ev


def nullspace(size, equations):
    basis={}
    for form in equations:
        while form and (pivot:=form.bit_length()-1) in basis:
            form ^= basis[pivot]
        if form: basis[form.bit_length()-1]=form
    moves=[]
    for index in range(size):
        if index in basis: continue
        vector=1<<index
        for pivot in sorted(basis):
            if (basis[pivot]&vector).bit_count()%2: vector|=1<<pivot
        moves.append(vector)
    return moves


def score(text,target,rotation_only=False):
    base=decode(text); size=len(base); half=size//2
    singles=[pair for pair in pairs(size) if pair[0]!=pair[1] and base[pair[0]][pair[1]]==1]
    indices={edge:1<<index for index,edge in enumerate(singles)}
    equations=[]
    for triple in combinations(range(size),3):
        edges=list(combinations(triple,2))
        if all(edge in indices for edge in edges): equations.append(sum(indices[edge] for edge in edges))
    triangle=equations.copy(); reached=set()
    for vertex in range(size):
        if vertex in reached: continue
        reached.add(vertex);queue=[vertex]
        for left in queue:
            for right in range(size):
                edge=tuple(sorted((left,right)))
                if right not in reached and edge in indices:
                    reached.add(right);queue.append(right);equations.append(indices[edge])
    free=nullspace(len(singles),equations)
    def lift(point): return explicit_lift(base,iter(0 if (1<<index)&point else 1 for index in range(len(singles))))
    classes={}
    for (left,right),bit in indices.items():
        delta=(right-left)%half
        tag=(left//half if rotation_only else 0,min(delta,(-delta)%half)) if left//half==right//half else (2,delta)
        classes[tag]=classes.get(tag,0)|bit
    trials=[0]
    for column in classes.values(): trials += [point ^ column for point in trials]
    start=process_time(); best=1<<62; baseline=0; evaluated=0
    for point in trials:
        if any((point&form).bit_count()%2 for form in triangle): continue
        result=ev.indep(lift(point),target,best+1); evaluated+=1
        if result<best: best,baseline=result,point
    baseline_time=process_time()-start
    assert ev.tri(lift(baseline))==0
    restricted=best; point=baseline; start=process_time(); trials=0
    while True:
        pivot=point
        for move in free:
            result=ev.indep(lift(point^move),target,best+1);trials+=1
            if result<best: best,pivot=result,point^move
        if pivot==point: break
        point=pivot
    elapsed=process_time()-start
    witness=lift(point)
    assert quotient(witness)==base and ev.tri(witness)==0 and ev.indep(witness,target)==best
    return (restricted,best,evaluated,trials,baseline_time,elapsed,to_graph6(witness))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source');parser.add_argument('target',type=int);parser.add_argument('indices',nargs='?')
    parser.add_argument('--rotation-only',action='store_true')
    args=parser.parse_args();rows=Path(args.source).read_text().splitlines()
    for index in (list(map(int,Path(args.indices).read_text().split())) if args.indices else range(len(rows))):
        print(index,*score(rows[index],args.target,args.rotation_only),sep='\t',flush=True)
