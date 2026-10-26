import sys, subprocess, itertools
sys.path.insert(0,'./cert')
import card, codish, sb
# random test: lits over 8 vars (some negated), all K
import random; random.seed(3)
ok=True
for trial in range(12):
    m=random.randint(2,8); K=random.randint(0,m)
    lits=[(v if random.random()<0.6 else -v) for v in range(1,m+1)]
    cls,s,mx=card.sinz(lits,K,m)
    P=codish.Proof('S')
    inp=['@bnd '+card.pb([(1,-l) for l in lits], m-K)] if K<m else []
    keep=card.sinz_derive(P,lits,K,s,'@bnd') if K<m else []
    open('scratch/s_in.opb','w').write('* #variable= %d #constraint= %d\n'%(mx,len(inp))+''.join(c+' ;\n' for c in inp))
    out=inp+[sb.opb_clause(c) for c in cls]
    open('scratch/s_out.opb','w').write('* #variable= %d #constraint= %d\n'%(mx,len(out))+''.join(c+' ;\n' for c in out))
    with open('scratch/s.pbp','w') as f:
        f.write('pseudo-Boolean proof version 3.0\nf %d ;\n'%len(inp)+'\n'.join(P.lines)+'\n')
        if keep: f.write('core id %s ;\n'%' '.join(keep))
        f.write('output EQUISATISFIABLE FILE ;\nconclusion NONE ;\nend pseudo-Boolean proof ;\n')
    r=subprocess.run(['./tools/bin/veripb','scratch/s_in.opb','scratch/s.pbp','scratch/s_out.opb'],capture_output=True,text=True)
    v='s VERIFIED OUTPUT EQUISATISFIABLE' in r.stdout.splitlines()
    # semantic check of the encoding: for every assignment of lits, the CNF (projected) is SAT iff sum<=K
    good=True
    for bits in itertools.product([0,1],repeat=m):
        val={v_:b for v_,b in zip(range(1,m+1),bits)}
        cnt=sum(1 for l in lits if (val[abs(l)]==1)==(l>0))
        from pysat.solvers import Cadical195
        S=Cadical195(); [S.add_clause(c) for c in cls]
        sat=S.solve(assumptions=[v_ if val[v_] else -v_ for v_ in range(1,m+1)])
        if sat!=(cnt<=K): good=False
    print(m,K,'veripb',v,'semantics',good, [l for l in (r.stdout+r.stderr).splitlines() if 'Caused' in l or 'not' in l][:1])
    ok&=v and good
print('ALL', ok)
