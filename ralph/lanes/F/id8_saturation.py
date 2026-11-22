"""A pole missing an entire seven-site window needs two full contacts in its ten-site core."""
from itertools import combinations
from pathlib import Path
import subprocess
import sys

from cyclic_proof import proof
from orbit_extend import ROOT


def write(stem,sites,edges,cap,need):
    full={site:index for index,site in enumerate(sites,1)}
    bad={pair:index for index,pair in enumerate(sorted(edges),len(sites)+1)}
    clauses=[[-full[site] for site in group] for group in combinations(sites,cap+1)]
    clauses += [[-ident,full[left],full[right]] for (left,right),ident in bad.items()]
    for group in combinations(sites,need):
        clauses.append([ident for pair,ident in bad.items() if set(pair)<=set(group)])
    variables=len(full)+len(bad); stem.with_suffix('.cnf').write_text(f'p cnf {variables} {len(clauses)}\n'+''.join(' '.join(map(str,clause))+' 0\n' for clause in clauses))
    print(stem,variables,len(clauses),flush=True)


def control():
    sites=list(range(4));edges={(0,2),(0,3),(1,2),(1,3)}
    for cap in (1,2):
        stem=Path(f'satctl{cap}');write(stem,sites,edges,cap,3)
        if cap==1:assert proof(stem)=='dual'
        else:
            result=subprocess.run([ROOT/'opt/bin/cadical','-q',stem.with_suffix('.cnf')],capture_output=True,text=True);assert result.returncode==10 and 's SATISFIABLE' in result.stdout.splitlines()
    print('K2,2 basket: one full is refuted; two-full relaxation SAT')


def target():
    sites=[1,2,3,4,5,13,14,15,16,17];edges={pair for pair in combinations(sites,2) if 6<=pair[1]-pair[0]<=12}
    stem=Path('no_blind_pole');write(stem,sites,edges,1,9);assert proof(stem)=='dual'
    print('one ordinary local CNF; lrat-check and cake_lpr accepted')


if __name__=='__main__':{'control':control,'target':target}[sys.argv[1]]()
