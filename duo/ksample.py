# Uniform reproducible sample of S kernels from catalogue M (all parts), plus counts by e and by group key.
# Usage: ksample.py M S seed -> runs/duo/kern2/cat/M{M}_sample.g6, M{M}_groups.txt, M{M}_bye.txt
import sys, glob, random, collections
M,S,seed=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]); D='./runs/duo/kern2/cat'
rng=random.Random(seed); res=[]; cnt=collections.Counter(); bye=collections.Counter(); t=0
for f in sorted(glob.glob(f'{D}/M{M}_p*.txt')):
    for l in open(f):
        key,g=l.rstrip('\n').split('\t'); cnt[key]+=1; bye[int(key.split('|')[0])]+=1; t+=1
        if len(res)<S: res.append((key,g))
        else:
            j=rng.randrange(t)
            if j<S: res[j]=(key,g)
open(f'{D}/M{M}_sample.g6','w').write(''.join(g+'\n' for _,g in res))
open(f'{D}/M{M}_sample_keys.txt','w').write(''.join(k+'\n' for k,_ in res))
open(f'{D}/M{M}_groups.txt','w').write(''.join(f'{c} {k}\n' for k,c in cnt.most_common()))
open(f'{D}/M{M}_bye.txt','w').write(''.join(f'{e} {bye[e]}\n' for e in sorted(bye)))
print('M',M,'total',t,'groups',len(cnt),'by e',dict(sorted(bye.items())))
