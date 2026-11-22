"""No target shore join: price a future bitset/Burnside census by marginals."""
from collections import Counter
from itertools import combinations, permutations, product
from pathlib import Path
from random import Random
from time import process_time
import json
import sys


def shore_words(sites, degrees, width):
    def extend(low, picks, remaining):
        if len(picks)==width:
            yield bytes(picks.count(index) for index in range(len(sites)))
            return
        for index in range(low,len(sites)):
            left,right = sites[index]
            if remaining[left] and remaining[right]:
                remaining[left]-=1; remaining[right]-=1
                yield from extend(index,picks+[index],remaining)
                remaining[left]+=1; remaining[right]+=1
    return list(extend(0,[],list(degrees)))


def upper(cooccurrences, short, long):
    totals = {(0,0):1}
    for count in cooccurrences:
        next_totals = Counter()
        for (used_left,used_right),number in totals.items():
            for more_left,more_right in product(range(3-count),repeat=2):
                if (1<=count+more_left+more_right<=2 and used_left+more_left<=short and used_right+more_right<=long):
                    next_totals[used_left+more_left,used_right+more_right]+=number
        totals = next_totals
    return totals.get((short,long),0)


def compare_toy(triple, ordinary):
    sites = list(combinations(range(4),2))
    counts = [ordinary.count(site)+int(set(site)<=triple) for site in sites]
    lefts = shore_words(sites,(1,2,2,2),1); rights = shore_words(sites,(2,2,2,2),2)
    legal = {(left,right) for left,right in product(lefts,rights) if all(1<=weight+small+large<=2 for weight,small,large in zip(counts,left,right))}
    group = []
    for perm in permutations(range(4)):
        if perm[0]!=0 or {perm[site] for site in triple}!=triple:
            continue
        action = tuple(sites.index(tuple(sorted((perm[left],perm[right])))) for left,right in sites)
        if all(counts[index]==counts[image] for index,image in enumerate(action)):
            group.append(action)
    def acted(word,action):
        return bytes(word[source] for source in action)
    explicit = {min((acted(left,action),acted(right,action)) for action in group) for left,right in legal}
    table = [[sum(1<<index for index,word in enumerate(rights) if 1<=count+word[site]+small<=2)
              for small in range(3)] for site,count in enumerate(counts)]
    fix = []
    for action in group:
        rightfix = sum(1<<index for index,right in enumerate(rights) if acted(right,action)==right)
        subtotal = 0
        for left in lefts:
            if acted(left,action)!=left:
                continue
            matches = rightfix
            for columns,digit in zip(table,left):
                matches &= columns[digit]
            subtotal+=matches.bit_count()
        fix.append(subtotal)
    assert len(legal)==fix[0] and sum(fix)==len(group)*len(explicit) and 0<len(explicit)<len(legal)
    unrestricted = shore_words(sites,(4,4,4,4),2)
    assert upper(counts,1,2)==sum(all(1<=count+left[index]+right[index]<=2 for index,count in enumerate(counts))
                                  for left in lefts for right in unrestricted)
    print('toy oriented triple',sorted(triple),'fixed counts',fix,'raw',len(legal),'orbits',len(explicit),'upper',upper(counts,1,2))
    return fix


def estimate(records):
    assert compare_toy({0,1,2},[(0,3),(0,3),(1,2)])==[10,0]
    assert max(compare_toy({1,2,3},[(0,1),(0,2),(0,3)])[1:])>0
    sites = list(combinations(range(7),2)); lefts = shore_words(sites,[1]+[2]*6,5); rights = shore_words(sites,[2]*7,6)
    assert len(rights)==6202
    data = [row for row in map(json.loads,records.read_text().splitlines()) if row['status']=='pass']
    groups = Counter(row['aut'] for row in data)
    hist = Counter(); crude = 0
    for row in data:
        triple = {index for index in range(7) if row['triple'] >> index & 1}
        counts = [int(weight)+int(set(site)<=triple) for site,weight in zip(sites,row['word'])]
        assert sum(counts)==16
        hist[tuple(counts.count(num) for num in (0,1,2))]+=1
    for (missing,single,double),hosts in sorted(hist.items()):
        price = upper([0]*missing+[1]*single+[2]*double,5,6)
        crude += price*hosts
        print('cooccurrence histogram',missing,single,double,'hosts',hosts,'degree-relaxed pair count/host',price)
    total_actions = sum(row['aut'] for row in data)
    visits = total_actions*len(lefts)
    print('hosts',len(data),'group orders',sorted(groups.items()),'actions',total_actions)
    print('single shores (short,long)',len(lefts),len(rights),'naive ordered pairs across fixed hosts',len(data)*len(lefts)*len(rights))
    print('paired coefficient upper on all ordered outputs ignoring degrees',crude,'16-byte row payload upper',16*crude)
    print('future Burnside upper visits',visits,'word intersections',21*visits,'left/right action tests',total_actions*(len(lefts)+len(rights)))
    random = Random(1815)
    table = [[random.getrandbits(len(rights)) | (1 << (len(rights)-1)) for _ in range(3)] for _ in sites]
    checksum = 0; start = process_time()
    for _ in range(8):
        for word in lefts:
            matches = (1<<len(rights))-1
            for columns,digit in zip(table,word):
                matches &= columns[digit]
            checksum+=matches.bit_count()
    step = (process_time()-start)/(8*len(lefts))
    assert checksum>0
    action = list(reversed(range(len(sites))))
    start = process_time()
    for _ in range(8):
        for word in lefts+rights:
            checksum+=bytes(word[source] for source in action)==word
    test = (process_time()-start)/(8*(len(lefts)+len(rights)))
    units = visits*step + total_actions*(len(lefts)+len(rights))*test
    print('synthetic comparable-width price seconds per 21-AND+popcount / fixed test; projected inner CPU-s:',step,test,units)


if __name__=='__main__':
    estimate(Path(sys.argv[1]))
