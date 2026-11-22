"""Independent labelled orbit, physical witness and coefficient audit of the census."""
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
from math import factorial, prod
from pathlib import Path
import json
import sys


def raw_count(order, sites, triple, degrees):
    @lru_cache(None)
    def coefficient(index, remaining):
        if not any(remaining):
            return 1
        if index == len(sites):
            return 0
        left,right = sites[index]
        if any(remaining[:left]):
            return 0
        total = 0
        for exponent in range(1 + min(remaining[left],remaining[right],2-int(set((left,right)) <= triple))):
            updated = list(remaining)
            updated[left] -= exponent
            updated[right] -= exponent
            total += coefficient(index+1,tuple(updated))
        return total
    return coefficient(0,tuple(degrees[pole] - (pole in triple) for pole in range(order)))


def first_witness(physical):
    def search(members, union, still):
        if len(members) > len(union):
            return members,sorted(union)
        for offset,site in enumerate(still):
            other = [index for index in still[offset+1:] if physical[index] & physical[site]]
            witness = search(members+[site],union|physical[site],other)
            if witness:
                return witness
    return search([],set(),list(range(len(physical))))


def motifs(sites, multiplicities, triple):
    ordinary = [set(pair) for pair,count in zip(sites,multiplicities) if count]
    doubles = [set(pair) for pair,count in zip(sites,multiplicities) if count == 2]
    if any(first & second for first,second in combinations(doubles,2)):
        return 'ordinary', 'meeting_doubles'
    for double in doubles:
        if any(all({extra,pole} in ordinary for pole in double) for extra in set.union(*map(set,sites))-double):
            return 'ordinary','double_in_triangle'
    reasons = []
    if all(set(side) in ordinary for side in combinations(triple,2)):
        reasons.append('T_triangle')
    for center in set.union(*map(set,sites)):
        if all({center,neighbor} in ordinary for neighbor in triple-{center}) and any(
            center in double and (center in triple or triple & double) for double in doubles
        ):
            reasons.append('star_in' if center in triple else 'star_out')
    return ('triple', '+'.join(sorted(set(reasons)))) if reasons else ('pass','pass')


def small():
    sites = list(combinations(range(4),2))
    for triple in ({0,1,2},{1,2,3}):
        physical_count = 0
        for word in product(range(3),repeat=6):
            if any(weight + int(set(pair) <= triple) > 2 for weight,pair in zip(word,sites)):
                continue
            rows = [set(pair) for pair,weight in zip(sites,word) for _ in range(weight)]
            truth = 'ordinary' if first_witness(rows) else 'triple' if first_witness(rows+[triple]) else 'pass'
            assert motifs(sites,word,triple)[0]==truth
            physical_count += [sum(vertex in row for row in rows+[triple]) for vertex in range(4)] == [3,2,2,2]
        assert raw_count(4,sites,triple,(3,2,2,2)) == physical_count
    print('independent four-pole motif, physical clique and coefficient checks passed')


def audit(records, destination):
    small()
    sites = list(combinations(range(7),2))
    lines = [json.loads(line) for line in records.read_text().splitlines()]
    assert set(record['triple'] for record in lines)=={7,14}
    with destination.open('x') as output:
        output.write('triple\tword\tstatus\tmotif\tphysical_indices\tcovered_poles\n')
        for triple in ({0,1,2},{1,2,3}):
            mask = sum(1 << vertex for vertex in triple)
            transformations = [dict(enumerate(perm)) for perm in permutations(range(7))
                               if perm[0] == 0 and {perm[vertex] for vertex in triple} == triple]
            seen = set()
            motif_totals = Counter()
            totals = Counter()
            for record in (entry for entry in lines if entry['triple']==mask):
                word = tuple(map(int,record['word']))
                assert len(word)==21 and all(0<=count<=2-(set(pair)<=triple) for pair,count in zip(sites,word))
                physical = [set(pair) for pair,count in zip(sites,word) for _ in range(count)]
                assert len(physical)==13 and [sum(pole in row for row in physical+[triple]) for pole in range(7)]==[5]+[4]*6
                found = first_witness(physical)
                if found:
                    status = 'ordinary'
                else:
                    found = first_witness(physical+[triple]); status = 'triple' if found else 'pass'
                code, reason = motifs(sites,word,triple)
                assert status == record['status'] == code
                indices, union = found or ([],[])
                if found:
                    selected = [(physical+[triple])[index] for index in indices]
                    assert all(first & second for first,second in combinations(selected,2)) and len(selected)>len(union)
                    assert set.union(*selected)==set(union) and (status=='ordinary' or 13 in indices)
                output.write('\t'.join([str(mask),record['word'],status,reason,','.join(map(str,indices)),','.join(map(str,union))])+'\n')
                labelled = tuple(sorted(tuple(sorted(row)) for row in physical))
                images = {tuple(sorted(tuple(sorted(mapping[pole] for pole in row)) for row in labelled)) for mapping in transformations}
                assert images.isdisjoint(seen) and labelled in images
                seen.update(images)
                weight = len(images) * (105 if 0 in triple else 140)
                assert len(images)==record['fixed'] and len(transformations)==len(images)*record['aut'] and weight==record['oriented']
                motif_totals[reason]+=1
                totals[status,'reps']+=1; totals[status,'fixed']+=len(images)
                totals[status,'oriented']+=weight
                totals[status,'rows']+=weight * (factorial(14)//prod(factorial(count) for count in word))
            raw = raw_count(7,sites,triple,(5,4,4,4,4,4,4))
            assert len(seen)==raw
            print('T',sorted(triple),'coefficient',raw,'marked group order',len(transformations),'motif reps',sorted(motif_totals.items()))
            print('replayed weights (rows = poles + 14 labelled Y sites)',sorted(totals.items()))


if __name__=='__main__':
    audit(Path(sys.argv[1]),Path(sys.argv[2]))
