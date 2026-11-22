"""Read-only receipt checker: original edges, literal endpoints, no switching gauge."""
from collections import Counter
from itertools import combinations, product
from pathlib import Path


def bits(number):
    while number:
        bit=number&-number
        yield bit
        number^=bit


def reduce_row(space,row):
    for pivot in sorted(space,reverse=True):
        if row&pivot:row^=space[pivot]
    return row


def append(space,row):
    row=reduce_row(space,row)
    if row:space[1<<(row.bit_length()-1)]=row


class Original:
    def __init__(self,size,pairs):
        self.size=size;self.keys={edge:2<<idx for idx,edge in enumerate(sorted(pairs,key=lambda item:(item[1],item[0]),reverse=True))};self.threshold=2<<len(pairs)
        self.triangle={};self.supports={}
        for triple in combinations(range(size),3):
            sides=list(combinations(triple,2))
            if all(edge in pairs for edge in sides):append(self.triangle,sum(self.keys[edge] for edge in sides))

    def translate(self,word):
        original=sorted(self.keys);assert not word&1 and word<self.threshold
        return sum(self.keys[original[bit.bit_length()-2]] for bit in bits(word))

    def room(self,chart,point):
        assert point < 1<<len(chart);space=self.triangle.copy()
        for idx,raw in enumerate(chart):append(space,self.translate(raw)^(point>>idx&1))
        assert 1 not in space and len(space)==len(self.triangle)+len(chart)
        return space

    def flat(self,space,mask):
        assert not mask>>self.size
        if mask not in self.supports:
            combined={}
            for pair,edge in self.keys.items():
                left,right=pair
                if mask>>left&mask>>right&1:
                    endpoints=(1<<left)^(1<<right);append(combined,self.threshold*endpoints^edge)
            self.supports[mask]=[value for pivot,value in combined.items() if pivot<self.threshold]
        remaining={}
        for eq in self.supports[mask]:append(remaining,reduce_row(space,eq))
        return None if 1 in remaining else list(remaining.values())


def indicator(forms):
    factors=[([0] if not form&1 else [])+list(bits(form&~1)) for form in forms];poly=set()
    for pick in product(*factors):
        term=frozenset(pick)-{0};poly.symmetric_difference_update([term])
    return poly


def validate_branch(original,space,point,receipt,order):
    header,steps,proof=receipt.splitlines();state,role=header.split();assert int(role)==point and state in ('rank0','xor')
    units=list(map(int,steps.split()));masks=list(map(int,proof.split()));assert (not masks)==(state=='rank0') and (masks or units)
    for index,mask in enumerate(units):
        assert mask.bit_count()==order;flat=original.flat(space,mask)
        if state=='rank0' and index==len(units)-1:assert flat==[]
        else:
            assert flat is not None and len(flat)==1;append(space,flat[0]^1);assert 1 not in space
    if masks:
        acc=set()
        for mask in masks:
            assert mask.bit_count()==order;flat=original.flat(space,mask);assert flat is not None
            acc.symmetric_difference_update(indicator(flat))
        assert acc=={frozenset()}
    return len(units),len(masks)


def calibration():
    original=Original(4,{(0,1),(1,2),(2,3),(0,3)});chart=[30];mask=15
    for point in (0,1):
        space=original.room(chart,point);flat=original.flat(space,mask)
        assert flat==([] if not point else None)
        if not point:validate_branch(original,space,point,'rank0 0\n15\n\n',4)
        else:
            try:validate_branch(original,space,point,'rank0 1\n15\n\n',4)
            except AssertionError:pass
            else:raise AssertionError('swapped parity accepted')
    # A vertical at site 1 is present before deletion; modifying the wrong diagonal must not work.
    for sign in (0,1):
        crossing={frozenset((0,4+sign)),frozenset((1,4+(1^sign)))};total=[]
        for removed in (None,0,1):
            edges=crossing|{frozenset((2*site,2*site+1)) for site in range(3) if site!=removed}
            sets=[set(subset) for subset in combinations(range(6),4) if not any(edge<=set(subset) for edge in edges)]
            total.append(sum({2,3}<=subset for subset in sets));assert removed is not None or not sets
            if removed==1:
                assert len(sets)==2 and all(subset.symmetric_difference({0,1}) not in sets for subset in sets)
        assert total==[0,0,2]
    print('original-coordinate controls: C4 parity flipped fails, both isolated-site deletions distinguished from wrong diagonal/endpoint')


def main():
    calibration();size=18;word=Path('../r13/max.q').read_text().splitlines()[21];assert word==Path('../r14/old21.q').read_text().strip()
    slots=[(left,right) for right in range(size) for left in range(right+1)];assert word[0]=='S' and len(word)==1+len(slots)
    for pair,val in zip(slots,word[1:],strict=True):
        left,right=pair;distance=min(right-left,18+left-right);assert int(val)==(distance in (0,5,6,8,9))
    pairs={pair for pair,val in zip(slots,word[1:]) if val=='1' and pair[0]!=pair[1]};original=Original(size,pairs)
    chart=list(map(int,Path('local.chart').read_text().split()));assert len(chart)==7
    eligible=[site for site in range(1,18) if (0,site) not in pairs];masks=[sum(1<<site for site in subset) for subset in combinations(eligible,8)];assert len(masks)==45
    passing=[]
    for point in range(128):
        space=original.room(chart,point);rows=[original.flat(space,mask) for mask in masks]
        assert all(row is None or not row for row in rows)
        if all(row is None for row in rows):passing.append(point)
    assert passing==list(map(int,Path('local.pass').read_text().split())) and len(passing)==11
    print('all 128 nonempty chart roles in ungauged original sign coordinates: 117 allow a named full-hole ten unconditionally, 11 remain; 45/45 flat indicators constant within each role')
    states=Counter();total=0
    for index,point in enumerate(passing):
        receipt=Path(f'branch4.{index}.proof').read_text();counts=validate_branch(original,original.room(chart,point),point,receipt,10);states[receipt.split()[0]]+=1;total+=sum(counts);print('replayed point',point,'steps/xor supports',counts)
    assert states=={'rank0':9,'xor':2};print('ID21 missing vertical impossible on old card alone:',dict(states),'total listed support occurrences',total)
    good=set(passing);restored=sorted(set(range(128))-good)
    for point in restored:
        receipt=Path(f'restored4.{point}.proof').read_text();counts=validate_branch(original,original.room(chart,point),point,receipt,10);states[receipt.split()[0]]+=1;total+=sum(counts)
    assert len(restored)==117 and states=={'rank0':126,'xor':2}
    print('VERTICAL RESTORED: all 128 local roles refuted using ONLY 10 DISTINCT SINGLETON sites; no vertical or pole rows used;',dict(states),'total listed support occurrences',total)


if __name__=='__main__':main()
