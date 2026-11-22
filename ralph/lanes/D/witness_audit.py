"""Independent semantic checks for the additional-star frontier and the conditional P8 deck."""
from collections import Counter,defaultdict
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import sys

from induced_pilot import graph_key,planted,flip
from path_growth import bits,read_profiles
from punct_path import profile_key
from punctured import certificate
from witness_obstructions import independent


def audit_controls(dest):
    prev=dest.parent/'ind10';keys=[profile_key(row) for row in read_profiles(prev/'control-join.tsv')];expected=defaultdict(set);physical=0
    for graph,core in planted():
        physical+=1
        for ordered in (core,(core[1],core[0])+tuple(reversed(core[2:]))):
            key=graph_key(graph,ordered)
            if key in keys:expected[keys.index(key)].add(certificate(graph,[[point] for point in ordered]+[sorted(set(range(22))-set(ordered))]))
            else:assert flip(key) in keys
    for filename in sorted(dest.glob('deck8cal*.out')):
        actual=defaultdict(set);idx=0
        for line in filename.open():
            words=line.split()
            if words[0]=='model':actual[idx].add(certificate([set(bits(int(field))) for field in words[1:]],[[point] for point in range(10)]+[list(range(10,22))]))
            else:assert int(words[0])==idx and words[1]=='0';idx+=1
        assert idx==len(keys) and actual==expected
        print(filename.name,'PASS',physical,'real marks',sum(map(len,actual.values())),'coloured graphs in',len(actual),'of',idx,'join keys')


def audit_front(dest):
    order=40;checked=0
    for line in (dest/'all3840.out').open():
        if not line.startswith('child'):continue
        fixed,*graph=map(int,line.split()[1:]);upper=graph.copy()
        for left,right in combinations(range(order),2):
            if not (fixed&((1<<left)|(1<<right))) and not graph[left]&graph[right]:upper[left]|=1<<right;upper[right]|=1<<left
        assert independent(upper,(1<<order)-1,10) is None;checked+=1
    print('PASS all',checked,'retained frontiers also pass direct I10 (not complete graphs).')
    directory=dest/'branch-cert';proofs=[entry.split('\t') for entry in (directory/'witnesses.tsv').read_text().splitlines()];by_tag={row[0]:row for row in proofs};assert len(by_tag)==1351
    certs={}
    for path in sorted(directory.glob('certs-*-2-0.tsv')):
        for line in path.open():
            tag,child,form,proof,solver,checker,cake=line.split();assert tag not in certs and (child,form)==(by_tag[tag][1],by_tag[tag][4]);certs[tag]=proof
            for ext,digest in [('cnf',form),('lrat',proof),('cadical.log',solver),('lrat-check.log',checker),('cake_lpr.log',cake)]:assert sha256((directory/(tag+'.'+ext)).read_bytes()).hexdigest()==digest
            assert 's VERIFIED UNSAT' in (directory/(tag+'.cake_lpr.log')).read_text() and 'c VERIFIED' in (directory/(tag+'.lrat-check.log')).read_text()
    assert set(certs)==set(by_tag)
    print('PASS',len(certs),'distinct formula+LRAT dual receipts bound to rejected child and proof-producing graph witness')


if __name__=='__main__':
    dest=Path(sys.argv[1]).resolve();(audit_controls if sys.argv[2]=='control' else audit_front)(dest)
