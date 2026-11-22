"""Pure propagation on translated forced charts and physical independent supports."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

from column_audit import insert,normal
from cyclic_check import check
from cyclic_proof import Formula,proof
from hole_branches import bank,cut
from id8_local import target
from old_indicator import cardspace,cycle_basis
from orbit_extend import vertices
from relift_audit import encode


def constraints(keys,holes,chart):
    pairs=list(keys); units={}
    for shift in holes:
        for form in chart:
            eq=1
            for index in vertices(form>>1):
                left,right=pairs[index];eq^=keys[tuple(sorted(((left+shift)%18,(right+shift)%18)))]
            insert(units,eq)
    return units


def occupied(base,holes):
    for count in range(1,min(5,len(holes))+1):
        for full in combinations(holes,count):
            if any(base[left][right] for left,right in combinations(full,2)):continue
            pool=sorted(site for site in range(18) if site not in full and not any(base[site][other] for other in full))
            for sites in combinations(pool,10-2*count):yield full,sites


def witness(base,stem,selected):
    text=encode(base);formula=Formula(text,10)
    for code in sorted(set(selected)):formula.add(tuple(vertices(code>>18)),tuple(vertices(code%262144)))
    formula.serialize(stem);state=proof(stem);print('received',len(formula.supports),state,flush=True);assert state=='dual' and check(text,10,stem)==len(formula.supports)
    Path(str(stem)+'.masks').write_text(''.join(f'{code}\n' for code in sorted(set(selected))))


def main(sets):
    base=target();keys={pair:form<<1 for pair,form in cardspace(base).items()};chart=list(map(int,Path('roles.chart').read_text().split()));
    for holes in sets:
        for site in range(18):base[site][site]=int(site not in holes)
        units=constraints(keys,holes,chart);rank=len(units);rows=[];required=[]
        for full,sites in occupied(base,holes):
            code=(sum(1<<site for site in full)<<18)+sum(1<<site for site in sites)
            rows.append((code,cycle_basis(keys,sites,64)))
            if len(full)==1:required.append(code)
        if 1 in units:status='inconsistent';selected=[]
        else:
            local={pair:normal(units,form) for pair,form in keys.items()}; old=[]
            for sites in combinations(range(18),10):
                forms=cycle_basis(local,sites,4)
                if forms is not None and 1 not in forms:old.append((sum(1<<site for site in sites),forms))
            old.sort(key=lambda item:len(item[1])); print('conditional singleton bank',Counter(len(flat) for _,flat in old),flush=True)
            steps,extra,status=cut(rows+old,units);selected=steps+extra
        print(holes,'rank',rank,'supports',len(rows),'status',status,len(selected),flush=True)
        if status!='open':witness(base,Path('marks.'+'-'.join(map(str,holes))),required+selected)


if __name__=='__main__':main([tuple(map(int,arg.split(','))) for arg in sys.argv[1:]])
