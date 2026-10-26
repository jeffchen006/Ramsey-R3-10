import sys, subprocess
sys.path.insert(0,'./cert')
import sb, codish
n,s=int(sys.argv[1]),int(sys.argv[2])
nedge=n*(n-1)//2
r=subprocess.run([sys.executable,'gen.py','full',str(n),str(s)],capture_output=True,text=True).stdout
base=[[int(t) for t in l.split()[:-1]] for l in r.splitlines() if l and not l.startswith(('c','p'))]
lexc,maxvar,struct=codish.lex_rows(n,[(0,n)],nedge)
def wopb(path,cls,nv):
    with open(path,'w') as f:
        f.write('* #variable= %d #constraint= %d\n'%(nv,len(cls)))
        for c in cls: f.write(sb.opb_clause(c)+' ;\n')
wopb('scratch/c_in.opb',base,maxvar); wopb('scratch/c_out.opb',base+lexc,maxvar)
# proof: header + order via sb.write_veripb with no sb, then splice
sb.write_veripb('scratch/c_hdr.pbp',n,len(base),[])
hdr=open('scratch/c_hdr.pbp').read().split('\n')
k=[i for i,l in enumerate(hdr) if l.startswith('load_order lexmax')][0]
P=codish.Proof()
keep=codish.derive(P,n,struct)
assert len(keep)==len(lexc)
with open('scratch/c.pbp','w') as f:
    f.write('\n'.join(hdr[:k+1])+'\n'+'\n'.join(P.lines)+'\n')
    f.write('load_order ;\ncore id %s ;\noutput EQUISATISFIABLE FILE ;\nconclusion NONE ;\nend pseudo-Boolean proof ;\n'%' '.join(map(str,keep)))
print('lex clauses',len(lexc),'proof lines',len(P.lines))
