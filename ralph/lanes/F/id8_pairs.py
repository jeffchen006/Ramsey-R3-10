"""Combine forced hole charts by linear equations, never branch on a global signing."""
from itertools import combinations
from pathlib import Path
import sys
from column_audit import insert,normal
from cyclic_proof import Formula,proof
from cyclic_check import check
from hole_branches import bank,cut,establish
from hole_price import support_list
from id8_local import target
from old_indicator import cycle_basis
from orbit_extend import vertices
from relift_audit import encode


def run(distances):
    base=target();keys,olds=bank(base,10,5); pairs=list(keys); idx={pair:index for index,pair in enumerate(pairs)};chart=list(map(int,Path('roles.chart').read_text().split()))
    for distance in distances:
        moved=[sum(2<<idx[tuple(sorted(( (pairs[index][0]+distance)%18,(pairs[index][1]+distance)%18 )))] for index in vertices(form>>1)) for form in chart];units=establish(keys,chart,63)
        for form in moved:
            eq=1
            for index in vertices(form>>1):eq^=keys[pairs[index]]
            insert(units,eq)
        base[distance][distance]=0; supports=[];marks={}
        for hole in (0,distance):
            for sites in support_list(base,hole,10):supports.append(((hole,),sites))
        if not base[0][distance]:
            available=sorted(site for site in range(18) if site not in (0,distance) and not (base[0][site] or base[distance][site]))
            for sites in combinations(available,6):supports.append(((0,distance),sites))
        rows=[]
        for full,sites in supports:
            mask=sum(1<<site for site in sites);code=(sum(1<<site for site in full)<<18)|mask
            marks[code]=full,sites;rows.append((code,cycle_basis(keys,sites,64)))
        if 1 in units:state='inconsistent';used=[]
        else:
            steps,extra,state=cut(rows+olds,units);used=steps+extra
        print('pair',distance,state,'receipt',len(used),flush=True)
        if state!='open':
            text=encode(base); formula=Formula(text,10)
            for full,sites in supports:
                if len(full)==1:formula.add(full,sites)
            for code in used:
                full,sites=marks[code] if code in marks else ((),tuple(vertices(code)))
                formula.add(full,sites)
            stem=Path('pair'+str(distance));formula.serialize(stem);assert proof(stem)=='dual' and check(text,10,stem)==len(formula.supports)
            print('dual LRAT + independent binding',len(formula.supports),flush=True)
        base[distance][distance]=1


if __name__=='__main__':run(list(map(int,sys.argv[1:])))
