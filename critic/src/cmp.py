import re, sys, collections
m=[x for x in open(sys.argv[1]).read().split('\n') if x]; t=[x for x in open(sys.argv[2]).read().split('\n') if x]
assert len(m)==len(t), (len(m),len(t))
bad=0
for a,b in zip(m,t):
    A=re.findall(r'-?\d+',a)
    B=list(re.findall(r'n=(\d+) e=(\d+) deg=\[(\d+),(\d+)\] triangle_free=(\w+) alpha=(\d+) \(3,\d+\)-graph=(\w+)',b)[0])
    B=[x.replace('True','1').replace('False','0') for x in B]
    if A!=B: bad+=1; print(a,'|',b)
print('mismatch',bad,'of',len(m))
c=collections.Counter((int(A[0]),int(A[5])) for A in (re.findall(r'-?\d+',x) for x in m) if A[4]=='1' and int(A[0])>=30)
print(sorted(c.items()))
