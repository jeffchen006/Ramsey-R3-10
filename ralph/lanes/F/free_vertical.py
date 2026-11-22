"""Strict screening for cyclic crossings with site-dependent verticals."""

import argparse
from collections import Counter
from itertools import combinations, product
from math import comb
from pathlib import Path

from card_replay import costs
from cyclic_proof import Formula, proof
from cyclic_check import check
from orbit_extend import parse_graph6, to_graph6
from relift_audit import decode, encode


def rows(name):
    return Path(name).read_text().splitlines()


def put(name, records):
    Path(name).write_text(''.join(f'{record}\n' for record in records))


class FreeVertical(Formula):
    def add_orbit(self, full, single):
        for shift, unit in product(range(self.size), (1, -1)):
            def move(sequence):
                return tuple(sorted((shift + unit * value) % self.size for value in sequence))
            moved = move(full)
            if all(not self.base[vertex][vertex] for vertex in moved):
                self.add(moved, move(single))


def row(base, holes):
    result = [line[:] for line in base]
    for site in range(len(base)):
        result[site][site] = int(site not in holes)
    return encode(result)


def control():
    observed = {}; physically_seen = 0
    for size in (2, 3, 4):
        count = 2 * size
        orbits = sorted({tuple(sorted({(left,right),tuple(sorted((left^1,right^1)))}))
                         for left,right in combinations(range(count),2)})
        for flags in range(1 << len(orbits)):
            adjacency = [set() for _ in range(count)]
            for index, orbit in enumerate(orbits):
                if flags >> index & 1:
                    for left,right in orbit:
                        adjacency[left].add(right); adjacency[right].add(left)
            if any(adjacency[left] & adjacency[right] for left in range(count) for right in adjacency[left]):
                continue
            base = [[len(adjacency[2*left] & {2*right,2*right+1}) for right in range(size)] for left in range(size)]
            if any(base[left][right] != base[(left+1)%size][(right+1)%size] for left,right in combinations(range(size),2)):
                continue
            physically_seen += 1
            alpha = max(len(subset) for number in range(1,count+1) for subset in combinations(range(count),number)
                        if not any(right in adjacency[left] for left,right in combinations(subset,2)))
            key = encode(base)
            previous = observed.get(key)
            if previous is None or alpha < previous[0]:
                observed[key] = (alpha, to_graph6([sum(1<<other for other in nbr) for nbr in adjacency]))
    mixed = [0,0]; decisions = 0; examples = {}
    for text,(alpha, physical) in sorted(observed.items()):
        base = decode(text); size = len(base)
        if not any(2 in line for line in base):
            assert observed[row(base,set())][0] <= alpha
        elif any(base[site][site] for site in range(size)):
            raise AssertionError('cyclic doubles force all verticals off')
        for target in (alpha, alpha+1):
            formula = FreeVertical(text,target)
            status, _, graph = formula.search(80)
            assert status == ('yes' if target>alpha else 'no')
            decisions += 1
            if 0 < sum(base[site][site] for site in range(size)) < size:
                mixed[int(status=='yes')] += 1
                if size==4 and target==4:
                    examples.setdefault(status,(text,graph if graph else parse_graph6(physical)))
    assert set(examples)=={'yes','no'} and all(mixed)
    for tag,(text,graph) in examples.items():
        put(f'control.{tag}.q',[text]);put(f'control.{tag}.g6',[to_graph6(graph)])
        if tag=='no':
            formula=FreeVertical(text,4);assert formula.search(80)[0]=='no'
            stem=Path('control-adverse');formula.serialize(stem);assert proof(stem)=='dual';check(text,4,stem)
    print('physical TF graphs after circular crossing filter',physically_seen,'quotients',len(observed),'strict decisions',decisions,'mixed no/yes',mixed)


def source():
    old=rows('../r8/ctl.q'); logs=rows('../r8/ctl.log')
    simple={text for text in old if (base:=decode(text)) and max(map(max,base))==1 and sum(base[0])==9}
    representatives=[]; binds=[]
    for text in sorted(simple):
        base=decode(text); distribution=Counter(sum(line) for line in base);assert distribution=={9:19} and all(base[site][site] for site in range(19))
        images={tuple(base[0][(step*unit)%19] for step in range(1,10)) for unit in range(1,19)}
        binds.extend((image,text) for image in sorted(images))
        representatives.append(text)
    assert sorted(word for word,text in binds)==sorted(word for word in product(range(2),repeat=9) if sum(word)==4)
    exceptional,=[text for text in representatives if 'status=yes' in logs[old.index(text)]]
    parent=decode(exceptional);assert parent[0]==[1]+[0]*5+[1]*8+[0]*5
    put('parent.q',[text for text in representatives if text!=exceptional]);put('exception.q',[exceptional]);put('distance.bind',[f'{"".join(map(str,word))} {old.index(text)} {text}' for word,text in binds])
    units=[unit for unit in range(1,19) if all(parent[0][site]==parent[0][site*unit%19] for site in range(19))]
    for holes in (1,2,3,4):
        rolemap={}
        for subset in combinations(range(19),holes):
            if holes==4 and any(min(right-left,19-right+left)<4 for left,right in combinations(subset,2)):
                continue
            key=min(tuple(sorted((unit*site+shift)%19 for site in subset)) for unit in units for shift in range(19))
            rolemap[subset]=key
        reps=sorted(set(rolemap.values()));put(f'role{holes}.q',[row(parent,key) for key in reps]);put(f'role{holes}.map',[' '.join(map(str,(*key,reps.index(value)))) for key,value in rolemap.items()]); print('holes',holes,'labelled',len(rolemap),'roles',len(reps))
    print('distance words/simple parents/adverse',len(binds),len(simple),len(simple)-1,'exception signing log2 labelled/gauged',costs(parent),'affine units',units)
    for vertical in (0,1):
        for degree in range(4,10):
            contacts=degree-vertical
            print('symmetric new vertical/degree/min holes/max labelled contact configurations per fixed lifted parent with exactly that many holes',vertical,degree,contacts,comb(contacts,contacts)*2**contacts)
    for vertical in (0,1):
        for first,second in combinations(range(4,11),2):
            first,second=first,second-1
            contacts=first+second-2*vertical; holes=(contacts+1)//2
            print('arbitrary new edge/degrees/min holes/configurations on specified minimum hole set',vertical,first,second,holes,comb(2*holes,first-vertical)*comb(2*holes-first+vertical,second-vertical))


def run(args):
    folder=Path(args.out);folder.mkdir(exist_ok=True)
    inputs=rows(args.source)
    for index in range(args.first, len(inputs) if args.end is None else args.end):
        text=inputs[index];formula=FreeVertical(text,10);status,turns,model=formula.search(100)
        stem=folder/f'{index:03}';receipt='-'
        if status=='no':
            formula.serialize(stem); receipt=proof(stem);assert receipt=='dual';check(text,10,stem)
        elif status=='yes':
            put(str(stem)+'.g6',[to_graph6(model)])
        print(index,status,turns,len(formula.supports),receipt,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('what',choices=('control','source','run'));parser.add_argument('source',nargs='?');parser.add_argument('out',nargs='?');parser.add_argument('--first',type=int,default=0);parser.add_argument('--end',type=int);args=parser.parse_args()
    assert __debug__
    if args.what=='control':control()
    elif args.what=='source':source()
    else:run(args)
