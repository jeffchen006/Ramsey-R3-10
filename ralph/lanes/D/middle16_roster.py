"""Physical middle-star orbit census, independently of scout's skeleton enumeration."""
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, permutations
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[3]
SCOUT = ROOT/'scratch/ideas/r015_R'
PAIRS = tuple(combinations(range(7), 2))
POLES = tuple((1 << left) | (1 << right) for left, right in PAIRS)

def all_regular():
    @lru_cache(None)
    def fill(need, bounds):
        if not bounds: return [()] if need == 0 else []
        return [(weight, *rest) for weight in range(min(need, 2, bounds[0])+1)
                for rest in fill(need-weight, bounds[1:])]
    def visit(degrees, previous):
        if not degrees:
            yield bytes(previous); return
        for row in fill(degrees[0], degrees[1:]):
            yield from visit(tuple(deg-weight for deg,weight in zip(degrees[1:], row)),previous+row)
    return set(visit((4,)*7, ()))

def independent_obstruction(contacts):
    def extend(sites, used, count):
        if count > used.bit_count(): return True
        return any(extend([other for other in sites[index+1:] if other & mask], used | mask, count+1)
                   for index, mask in enumerate(sites))
    return extend(contacts, 0, 0)

def shore_words():
    def walk(picks, degrees, first):
        if len(picks) == 6:
            yield tuple(picks); return
        for site in range(first, 21):
            left, right = PAIRS[site]
            if degrees[left] < 2 and degrees[right] < 2:
                degrees[left]+=1; degrees[right]+=1
                yield from walk(picks+[site], degrees, site)
                degrees[left]-=1; degrees[right]-=1
    return list(walk([], [0]*7, 0))

def layers(picks):
    counts=Counter(picks)
    return tuple(sum(1 << site for site in counts if counts[site]>=threshold) for threshold in (1,2))

def load_rows(name):
    return [tuple(map(int,line.split())) for line in (SCOUT/name).read_text().splitlines()]

def emit(dest, name, rows):
    (dest/name).write_text(''.join(json.dumps(row,separators=(',',':'))+'\n' for row in rows))

def census(dest):
    unseen=all_regular(); assert len(unseen)==52065
    actions=[tuple(PAIRS.index(tuple(sorted((perm[left],perm[right])))) for left,right in PAIRS)
             for perm in permutations(range(7))]
    shores=shore_words(); assert len(shores)==6202
    catalogue=[]; selected=[]; prior=[]; old=load_rows('positions.tsv')+load_rows('hold.tsv'); tails=set(load_rows('tails.tsv'))
    for host, contacts in enumerate(load_rows('pure.txt')):
        word=bytes(contacts.count(mask) for mask in POLES)
        images={bytes(word[index] for index in action) for action in actions}
        assert images <= unseen; unseen-=images
        if independent_obstruction(contacts): continue
        group=[action for action in actions if all(word[src]==word[dst] for src,dst in enumerate(action))]
        sides=[picks for picks in shores if all(word[site]+num<=2 for site,num in Counter(picks).items())]
        names=list(map(layers,sides)); reverse={picks:index for index,picks in enumerate(sides)}
        action_rows=[[reverse[tuple(sorted(action[site] for site in picks))] for picks in sides] for action in group]
        allbits=(1<<len(sides))-1; permitted=[]
        for site in range(21):
            permitted.append([sum(1<<idx for idx,picks in enumerate(sides) if 1<=word[site]+weight+picks.count(site)<=2)
                              for weight in range(3)])
        ids={}; records=[]; ordered=0
        for left,picks in enumerate(sides):
            matches=allbits
            for site in range(21): matches &= permitted[site][picks.count(site)]
            ordered+=matches.bit_count()
            while matches:
                bit=matches & -matches; right=bit.bit_length()-1; matches-=bit
                if (left,right) in ids: continue
                orbit={(image[left],image[right]) for image in action_rows};orbit|={(right,left) for left,right in orbit}
                assert (left,right)==min(orbit)
                ordinal=len(records); ids.update(dict.fromkeys(orbit,ordinal)); records.append(dict(host=host,id=ordinal,weight=len(orbit),Y=contacts,word=names[left]+names[right]))
        assert sum(rec['weight'] for rec in records)==len(ids)==ordered
        avoid=set(); name_id={word:index for index,word in enumerate(names)}
        for data in old:
            if data[0]!=host: continue
            left,right=name_id[data[2:4]],name_id[data[4:6]]; ordinal=ids[left,right]; assert ordinal not in avoid; avoid.add(ordinal)
            prior.append(dict(records[ordinal],word=data[2:],kind='tail' if data in tails else 'old',old=data[1]))
        assert len(avoid)==12
        fresh=[rec for rec in records if rec['id'] not in avoid]; count=(len(records)+99)//100
        for group_no in range(count):
            block=fresh[group_no*len(fresh)//count:(group_no+1)*len(fresh)//count]
            chosen=min(block,key=lambda rec:sha256(f"D16:{host}:{rec['id']}:frozen".encode()).digest())
            selected.append(dict(chosen,kind='new'))
        print(host,len(sides),len(group),len(records),ordered,'diagonal',sum(len({key[0],key[1]})==1 for key in ids),'sample',count,flush=True);catalogue.extend(records)
    assert not unseen and len(catalogue)==15282 and sum(rec['weight'] for rec in catalogue)==320878
    assert len(prior)==72 and len(selected)==155
    emit(dest,'roster.jsonl',catalogue);emit(dest,'prior.jsonl',prior); emit(dest,'pilot.jsonl',selected+[rec for rec in prior if rec['kind']=='tail'])

if __name__=='__main__':census(Path(sys.argv[1]))
