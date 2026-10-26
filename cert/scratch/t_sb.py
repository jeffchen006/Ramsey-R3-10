import sys; sys.path.insert(0,'./cert')
import sb
n,s,depth=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
base=open(sys.argv[4]).read().split('\n')
hdr=[l for l in base if l.startswith('p ')][0].split()
ncl=int(hdr[3])
S=sb.static_clauses(n,depth)
print(len(S),'sb clauses')
sb.write_veripb(sys.argv[5],n,ncl,S)
body=[l for l in base if l and not l.startswith(('c','p'))]
with open(sys.argv[6],'w') as f:
    f.write('p cnf %s %d\n'%(hdr[2],ncl+len(S)))
    for l in body: f.write(l+'\n')
    for cl,pi in S: f.write(' '.join(map(str,cl))+' 0\n')
