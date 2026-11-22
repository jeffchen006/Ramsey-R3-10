"""Independent literal background and scalar shore test, then reverse fixed join."""
from collections import Counter
from csv import DictReader
from ctypes import CDLL, POINTER, c_int, c_uint32, c_ubyte
from itertools import combinations, combinations_with_replacement, permutations
from pathlib import Path
from time import process_time
import json
import sys

from wing20_audit import Audit


def array(items):
    return (c_uint32 * len(items))(*items)


class Auditor(Audit):
    def __init__(self, lib, margins, short_pairs, long_pairs):
        super().__init__(margins, short_pairs, long_pairs)
        self.fn = CDLL(str(lib.resolve())).test_profiles
        self.fn.restype = None
        self.fn.argtypes = [c_int,c_int,POINTER(c_uint32),c_int,POINTER(c_uint32),c_int,POINTER(c_uint32),POINTER(c_ubyte)]
        profiles = self.shorts+self.longs
        self.packed = array([sum(1 << pos for pos,site in enumerate(self.types) if level >> site & 1)
                             for word in profiles for level in word])
        self.flags = (c_ubyte * len(profiles))()

    def flags_for(self,rows):
        self.fn(self.order,len(rows),array(rows),len(self.types),array(self.types),len(self.flags),self.packed,self.flags)
        return bytes(self.flags)

    def count(self,rows):
        flags = self.flags_for(rows)
        assert 2 not in flags
        split = len(self.shorts)
        long_flags = flags[split:]
        old = sum(1<<idx for idx,flag in enumerate(flags[:split]) if flag & 1)
        new = sum(1<<idx for idx,flag in enumerate(flags[:split]) if flag & 2)
        actions = []
        totals = {}
        for tail in permutations(self.poles[1:]):
            perm = (0,*tail)
            if sorted(self.moved(site,perm) for site in rows) != sorted(rows):
                continue
            key = ''.join(map(str,perm))
            fixed_short, fixed_long = self.stabilized(perm)
            totals[key] = [0,0]
            actions.append((fixed_long,fixed_short & old,fixed_short & new,totals[key]))
        columns = sorted([(sum(site & pair == pair for site in rows),pair,col) for pair,col in zip(self.pairs,self.columns)],reverse=True)
        assert columns[0][0]<=2
        for index, (present,repeated) in enumerate(self.longs):
            flag = long_flags[index]
            if not flag:
                continue
            allowed = self.all_short
            for base,site,column in columns:
                allowed &= column[base+((present>>site)&1)+((repeated>>site)&1)]
                if not allowed:
                    break
            if allowed:
                for fixed_long,old_short,new_short,values in actions:
                    if fixed_long[index]:
                        values[0] += (allowed & old_short).bit_count()
                        if flag & 2:
                            values[1] += (allowed & new_short).bit_count()
        return totals,(old.bit_count(),sum(flag & 1 for flag in long_flags)),(new.bit_count(),sum(bool(flag & 2) for flag in long_flags))


def toy(lib):
    sample = Auditor(lib,[2,2,1],1,1)
    tests = cuts = 0
    for size in range(5):
        for rows in combinations_with_replacement((3,5,6,7),size):
            flags = sample.flags_for(rows)
            for idx, (seen,repeated) in enumerate(sample.shorts):
                sites = [site for layer in [seen,repeated] for site in sample.types if layer >> site & 1]
                literal = [(0,pole) for pole in sample.poles]+[(1,row) for row in rows]+[(2,site) for site in sites]
                def edge(left,right):
                    kind, contact = left
                    other, tail = right
                    if kind == other and kind != 1: return False
                    if kind == 0: return (tail >> contact) & 1
                    return not (tail & contact)
                cut = any(not any(edge(left,right) for left,right in combinations(pick,2))
                          for pick in combinations(literal,5))
                assert cut == (not flags[idx] & 2)
                tests += 1
                cuts += cut
    assert (tests,cuts)==(210,198)
    print('literal five-site independent sets vs native small-profile flags',tests,cuts)


def synthetic(lib):
    start = process_time()
    checker = Auditor(lib,[1]+[2]*6,5,6)
    setup = process_time()-start
    start = process_time()
    totals,before,after = checker.count([7,9,10,12,17,18,20,33,34,36,65,66,68,24])
    projected = setup+159*(process_time()-start)
    print('synthetic (not roster) action count',len(totals),'old/new margins',before,after,'setup+159 CPU-s', round(projected,2))
    assert projected < 60


def target(lib,roster,baseline,receipt):
    def read(path):
        with path.open() as source:
            table = list(DictReader(source,delimiter='\t'))
        answer = {int(row['row']):row for row in table}
        assert len(answer)==len(table)
        return answer
    def pairs(text):
        entries = [item.split(':') for item in text.split(',')]
        result = {key:int(num) for key,num in entries}
        assert len(result)==len(entries)
        return result
    checker = Auditor(lib,[1]+[2]*6,5,6)
    assert (len(checker.shorts),len(checker.longs)) == (4062,6202)
    old, new = read(baseline),read(receipt)
    supports = {lineno:host for lineno,host in enumerate(map(json.loads,roster.read_text().splitlines()),1) if host['status']=='pass'}
    assert old.keys()==supports.keys() and len(old)==162
    assert set(old)-set(new)=={255,345,350} and set(new)=={line for line in old if int(old[line]['identity'])>0}
    summary = Counter()
    zeros = []
    for line in sorted(new):
        support = supports[line]
        for table in [old,new]:
            assert (int(table[line]['triple']),table[line]['word'])==(support['triple'],support['word'])
        rows = [support['triple']]+[site for digit,site in zip(support['word'],checker.pairs) for _ in range(int(digit))]
        assert len(rows)==14
        fixes,oldm,newm = checker.count(rows)
        group = len(fixes)
        assert group==int(old[line]['group'])==int(new[line]['group'])==support['aut']
        for field,expected in [('short',(oldm[0],newm[0])),('long',(oldm[1],newm[1]))]:
            assert tuple(int(table[line][field]) for table in (old,new))==expected
        for pos,table in enumerate((old,new)):
            counts = {perm:values[pos] for perm,values in fixes.items()}
            assert counts==pairs(table[line]['fixed'])
            assert (counts['0123456'],sum(counts.values()))==(int(table[line]['identity']),group*int(table[line]['orbits']))
        deltas = {perm:left-right for perm,(left,right) in fixes.items()}
        assert min(deltas.values())>=0 and deltas==pairs(new[line]['delta_fixed'])
        assert (deltas['0123456'],sum(deltas.values()))==(int(new[line]['delta_identity']),group*int(new[line]['delta_orbits']))
        status = ('positive' if fixes['0123456'][1] else {(True,True):'both',(True,False):'short',(False,True):'long',(False,False):'join'}[tuple(not size for size in newm)])
        assert status==new[line]['result']
        if status!='positive': zeros.append((line,status,*newm))
        summary.update(dict(hosts=1,actions=group,old=fixes['0123456'][0],new=fixes['0123456'][1],
                            old_orbits=sum(item[0] for item in fixes.values())//group,new_orbits=sum(item[1] for item in fixes.values())//group))
    print('independent old/new and delta, all margins/actions/orbit sums agree:',dict(summary))
    print('new zero roster lines and causes, short/long margins:',zeros)


if __name__ == '__main__':
    library = Path(sys.argv[1])
    if sys.argv[2:] == ['controls']:
        toy(library)
        synthetic(library)
    else:
        target(library,*map(Path,sys.argv[2:]))
