from reciprocal_audit import ROOT, merge
from reciprocal_proof_pilot import child_cpu, digest, formula, process_time, run


def proof(label, key, degree, first, second, roots, positive, folder, thin, build=formula):
    start = process_time()
    lower,left,right = merge(first,second,key,roots)
    var, clauses = build(lower,left,right,degree,thin,control_pins=positive)
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

