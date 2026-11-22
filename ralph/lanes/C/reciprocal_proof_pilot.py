import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from random import Random
from resource import RUSAGE_CHILDREN, getrusage
import subprocess
from time import process_time

from reciprocal_audit import ROOT, SOURCE22, decode, host_masks, keys, merge, vertices


def formula(lower, left, right, degree, thin=False, control_pins=False):
    split = left+right
    assert all(row.bit_count() == degree for row in lower[split:])
    clauses = []
    variables = { (src,dst): 1+src*right+dst-left for src in range(left) for dst in range(left,split) }
    usable = [[] for _ in lower[:split]]
    allowed = {}
    for (src,dst), var in variables.items():
        assert not (lower[src] >> dst & 1)
        if lower[src] & lower[dst]:
            clauses.append((-var,))
        else:
            usable[src].append((dst,var))
            usable[dst].append((src,var))
            allowed[src,dst] = var
    for vertex, row in enumerate(usable):
        deficit = degree-lower[vertex].bit_count()
        if not 0 <= deficit <= len(row):
            clauses.append(())
            continue
        for choice in combinations(row,deficit+1):
            clauses.append(tuple(-var for _,var in choice))
        for choice in combinations(row,len(row)-deficit+1):
            clauses.append(tuple(var for _,var in choice))
        for (other1,var1),(other2,var2) in combinations(row,2):
            if lower[other1] >> other2 & 1:
                clauses.append((-var1,-var2))

    def blocking(graph, picked, available, needed):
        if not needed:
            all_left = picked & ((1 << left)-1)
            all_right = (picked & ((1 << split)-1)) ^ all_left
            yield tuple(allowed[src,dst] for src in vertices(all_left) for dst in vertices(all_right)
                        if (src,dst) in allowed)
            return
        while available.bit_count() >= needed:
            bit = available & -available
            available ^= bit
            yield from blocking(graph,picked | bit,available & ~graph[bit.bit_length()-1],needed-1)

    whole = (1 << len(lower))-1
    if not thin:
        return variables, clauses+sorted(set(blocking(lower,0,whole,degree+1)))

    from itertools import islice
    from pysat.solvers import Cadical195
    envelope = list(lower)
    for src,dst in allowed:
        envelope[src] |= 1 << dst
        envelope[dst] |= 1 << src
    if next(blocking(envelope,0,whole,degree+1),None) == ():
        return variables, clauses+[()]
    addition = set()
    with Cadical195(bootstrap_with=clauses) as solver:
        for iteration in range(128):
            if not solver.solve():
                return variables, clauses+sorted(addition)
            positive = set(solver.get_model())
            current = list(lower)
            for (src,dst), var in allowed.items():
                if var in positive:
                    current[src] |= 1 << dst
                    current[dst] |= 1 << src
            cuts = set(islice(blocking(current,0,whole,degree+1),32))
            if not cuts:
                assert control_pins, 'completion candidate found; no exclusion'
                return variables, clauses+sorted(addition)+[(lit,) for lit in sorted(positive)]
            assert not cuts & addition
            addition |= cuts
            for cut in sorted(cuts):
                solver.add_clause(cut)
    raise RuntimeError('128-model thin CNF generation limit; no verdict')


def child_cpu():
    usage = getrusage(RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


def run(*args):
    return subprocess.run(['nice','-n','5','timeout','20','prlimit','--cpu=12:14',*map(str,args)],
                          stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def proof(label, key, degree, first, second, roots, positive, folder, thin):
    start = process_time()
    lower,left,right = merge(first,second,key,roots)
    var, clauses = formula(lower,left,right,degree,thin,control_pins=positive)
    cnf = folder/f'{label}.cnf'
    lrat = folder/f'{label}.lrat'
    with cnf.open('w') as output:
        print(f'p cnf {len(var)} {len(clauses)}',file=output)
        for clause in clauses:
            print(*clause,0,file=output)
    generation = process_time()-start
    start = child_cpu()
    solver = run(ROOT/'opt/bin/cadical','--lrat','--binary=false',cnf,lrat)
    solve_time = child_cpu()-start
    cnf.with_suffix('.solve').write_text(solver.stdout)
    if positive:
        assert solver.returncode == 10 and 's SATISFIABLE' in solver.stdout, label
        model = {int(string) for line in solver.stdout.splitlines() if line.startswith('v ') for string in line.split()[1:] if string != '0'}
        assert len(model) == len(var) and len(set(map(abs,model))) == len(var)
        assert all(any(literal in model for literal in clause) for clause in clauses)
        if thin:
            _, dense = formula(lower,left,right,degree)
            assert all(any(literal in model for literal in clause) for clause in dense)
        status = 'SAT-model-checked'
        check_time = 0
    else:
        assert solver.returncode == 20, (label,solver.returncode)
        start = child_cpu()
        if () in clauses:
            lrat.write_text(f'{len(clauses)+1} 0 {clauses.index(())+1} 0\n')
        for checker, signature in [('cake_lpr','s VERIFIED UNSAT'),('lrat-check','c VERIFIED')]:
            checked = run(ROOT/'opt/bin'/checker,cnf,lrat)
            cnf.with_suffix(f'.{checker}').write_text(checked.stdout)
            assert checked.returncode == 0 and signature in checked.stdout, (label,checker,checked)
        check_time = child_cpu()-start
        status = 'dual-LRAT'
    return [label,status,str(len(clauses)),str(cnf.stat().st_size),str(lrat.stat().st_size),digest(cnf),digest(lrat),
            f'{generation:.6f}',f'{solve_time:.6f}',f'{check_time:.6f}',','.join(map(str,key))]


def run_pilot(controls, thin):
    folder = Path(('proof-control' if controls else 'proof-pilot')+('-thin' if thin else ''))
    folder.mkdir(exist_ok=True)
    if controls:
        left,right = [Path(f'cal-{order}.g6') for order in (10,11)]
        planted = [tuple(map(int,line.split())) for line in Path('cal-planted.tsv').read_text().splitlines()]
        picks = [(f'control-{index:03d}', planted[index]) for index in (0,95,175,394)]
    else:
        left,right = SOURCE22,Path('pilot-21.g6')
        grouped = {}
        for key,(reason,_) in keys('pilot.tsv').items():
            if reason != 'cap':
                grouped.setdefault(reason,[]).append(key)
        assert set(grouped) == {'upper-IS','fixed-undominated','domain-IS','row-column','row-empty','forced-domain'}
        rng = Random(31010540)
        picks = [(f'{category}-{index:02d}',key) for category,rows in sorted(grouped.items())
                 for index,key in enumerate(sorted(rng.sample(sorted(rows),8)))]
    lhs,rhs = ([host_masks(decode(line)) for line in path.read_text().splitlines()] for path in (left,right))
    count = Counter()
    generation = solver = checked = 0
    with (folder/'receipts.tsv').open('w') as journal:
        print('key status clauses cnf_bytes lrat_bytes cnf_sha256 lrat_sha256 generation_cpu solver_cpu dual_check_cpu role_map'.replace(' ','\t'),file=journal)
        for label,key in picks:
            row = proof(label,key,6 if controls else 9,lhs[key[0]],rhs[key[5]],2 if controls else 3,controls,folder,thin)
            print(*row,sep='\t',file=journal,flush=True)
            count[row[1]] += 1
            generation += float(row[7]); solver += float(row[8]); checked += float(row[9])
    print('terminal',count,'generation',round(generation,5),'solver',round(solver,5),'dual checking',round(checked,5))


def compare():
    import csv
    def receipts(folder):
        with (folder/'receipts.tsv').open() as source:
            return {row['key']:row for row in csv.DictReader(source,delimiter='\t')}
    def clause_set(path):
        with path.open() as source:
            header = next(source).split()
            assert header[:3] == ['p','cnf','156']
            rows = [tuple(map(int,line.split())) for line in source]
            assert len(rows) == int(header[3]) and all(row[-1] == 0 for row in rows)
            return set(rows)
    dense, thin = Path('proof-pilot'),Path('proof-pilot-thin')
    original, sliced = receipts(dense),receipts(thin)
    assert set(original) == set(sliced) and len(original) == 48
    for key, row in original.items():
        assert row['role_map'] == sliced[key]['role_map']
        assert row['status'] == sliced[key]['status'] == 'dual-LRAT'
        for folder, receipt in [(dense,row),(thin,sliced[key])]:
            for suffix in ('cnf','lrat'):
                assert digest(folder/f'{key}.{suffix}') == receipt[f'{suffix}_sha256']
        assert clause_set(thin/f'{key}.cnf') <= clause_set(dense/f'{key}.cnf'), key
    print('all 48 role keys and hashes agree; every thin CNF clause occurs in its dense counterpart')


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('mode',choices=['control','pilot','compare'])
    args.add_argument('--thin',action='store_true')
    options = args.parse_args()
    compare() if options.mode == 'compare' else run_pilot(options.mode == 'control',options.thin)
