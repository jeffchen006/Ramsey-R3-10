"""Physical controls, marked symmetries, and the original support-incidence inventory."""
from collections import Counter
from itertools import combinations, product
from math import comb
from pathlib import Path
import json
import subprocess
import sys

import networkx as nx

from orbit_extend import ROOT, independent_sets, to_graph6
from marked_windows import Windows


def check_window(graph, profiles, windows, occupied, full):
    singles = occupied^full; total=0
    for mode in (('both','pole','holes') if full else ('pole',)):
        chosen=0 if mode=='both' else singles
        while True:
            base=3 if mode=='both' else int(mode=='pole')
            if mode=='holes':base|=sum(3<<(2*idx+2) for idx in range(3) if full>>idx&1)
            for idx,val in enumerate(profiles):
                if chosen>>idx&1:base |= (3^val)<<(2*idx+2)
            assert not any(base>>idx&1 and base&mask for idx,mask in enumerate(graph))
            chosen_mates=base&~3
            selected=0
            for idx,val in enumerate(profiles):
                pair=3<<(2*idx+2)
                if val==3 or chosen>>idx&1:continue
                if val in (1,2):
                    if mode!='both':selected|=(3^val)<<(2*idx+2)
                    continue
                hits=sum((graph[idx*2+2+end]&chosen_mates).bit_count() for end in (0,1))
                if hits<=1:
                    selected|=sum(1<<(idx*2+2+end) for end in (0,1) if graph[idx*2+2+end]&base==0)
            assert all(not base&mask for idx,mask in enumerate(graph) if selected>>idx&1)
            threshold,order,edges,limit=windows.bounds(occupied,full,chosen,mode)
            assert 4-base.bit_count()==threshold and order==selected.bit_count()
            literal=sum((mask&selected).bit_count() for idx,mask in enumerate(graph) if selected>>idx&1)//2
            assert literal<=edges
            if edges<limit:assert next(independent_sets(graph,255,4),None) is not None
            total+=1
            if not chosen:break
            chosen=(chosen-1)&singles
    return total


def controls():
    survivors = {(int(occupied), int(full)) for occupied, full, _weight in
                 (line.split() for line in Path('small.rows').read_text().splitlines())}
    order = [0, 4, 1, 5, 2, 6, 3, 7]
    ladder = [sum(1 << idx for idx, dest in enumerate(order) if (dest - src) % 8 in (1, 4, 7)) for src in order]
    totals = Counter(); windows=Windows(3,4); checked=0
    for profiles in product(range(4), repeat=3):
        occupied = sum(1 << idx for idx, value in enumerate(profiles) if value)
        full = sum(1 << idx for idx, value in enumerate(profiles) if value == 3)
        row = min((occupied, full), tuple(int(f'{mask:03b}'[::-1], 2) for mask in (occupied, full)))
        for verticals in range(16):
            graph = [0] * 8
            def edge(left, right):
                graph[left] |= 1 << right
                graph[right] |= 1 << left
            for left, right in combinations(range(8), 2):
                if left // 2 == right // 2:
                    if verticals >> (left // 2) & 1: edge(left, right)
                elif left >= 2:
                    if ladder[left] >> right & 1: edge(left, right)
                elif profiles[right // 2 - 1] & (1 << ((left ^ right) & 1)):
                    edge(left, right)
            triangle = any(graph[left] & graph[right] for left, right in combinations(range(8), 2) if graph[left] >> right & 1)
            witness = next(independent_sets(graph, 255, 4), None)
            valid = not triangle and witness is None
            if not triangle and occupied.bit_count()+full.bit_count()<=3:
                checked+=check_window(graph,profiles,windows,occupied,full)
            if valid:assert windows.cut(occupied,full) is None
            if valid: assert row in survivors
            totals[valid, row in survivors] += 1
            positive = graph == ladder
            broken = profiles == (0, 0, 0) and verticals == 15
            if positive or broken:
                name = 'positive' if positive else 'broken'
                assert valid == positive and not triangle and (row in survivors) == positive
                assert (windows.cut(occupied,full) is None)==positive
                path = Path(name + '.g6'); path.write_text(to_graph6(graph) + '\n')
                record = json.loads(subprocess.check_output([sys.executable, '-I', ROOT / '.hmz/flows/r310_ralph/gate.py', ROOT, 'check', path, '8', '4']))
                assert record['graphs'][0]['ok'] == positive
                Path(name + '.gate').write_text(json.dumps(record, sort_keys=True) + '\n')
                print(name, 'physical witness', witness, 'degree', [mask.bit_count() for mask in graph])
    assert sum(totals.values()) == 1024 and totals[True, True] > 0
    print('all 1024 physical variants, (literal valid, row survives)', dict(sorted(totals.items())))
    print('literal grounded windows checked',checked)


def geometry():
    core = nx.Graph(); core.add_nodes_from(range(1, 18)); core.add_edges_from((left, right) for left, right in combinations(core, 2) if 6 <= right - left <= 12)
    perms = {tuple(move[site] for site in core) for move in nx.algorithms.isomorphism.GraphMatcher(core, core).isomorphisms_iter()}
    assert perms == {tuple(range(1,18)), tuple(range(17,0,-1))}; print('marked site group', sorted(perms))
    near = Counter()
    for site in range(18):
        other = [idx for idx in range(18) if 0 < min((idx-site)%18,(site-idx)%18) < 6]
        intact = sum(0 not in (*sites, site) for sites in combinations(other, 8))
        near[site] = intact
    print('intact named-hole supports of 45 per center', sorted(near.items()), 'total', sum(near.values()))
    intact = {(shift, gap) for shift in range(18) for gap in range(1,4) if all((shift+idx)%18 for idx in range(8))}
    pairs = {tuple(sorted(((shift+2)%18, (shift+2+gap)%18))) for shift, gap in intact}
    print('short double-hole interval witnesses', len(intact), 'distinct pairs', len(pairs), sorted(pairs))
    occurrences = Counter(); unique = set()
    for suffix in ('', '_eight'):
        for line in Path(__file__).with_name('round16_id8_masks'+suffix+'.txt').read_text().splitlines():
            foot,*masks = map(int,line.split())
            for mask in masks:
                kind = 'one-pole' if mask & (1<<18) else 'old'
                occurrences[kind, not mask&1] += 1
                if not mask&1: unique.add(mask)
    print('frozen support occurrences at their stored labels, (kind, avoids mark)', sorted(occurrences.items()), 'distinct avoiding', len(unique))
    labelled = fixed = 0
    for doubles in range(5):
        for singles in range(10-2*doubles):
            labelled += comb(17,doubles)*comb(17-doubles,singles)
            if doubles%2+singles%2<=1:
                fixed += comb(8,doubles//2)*comb(8-doubles//2,singles//2)
    print('degree <=9 roster direct Burnside: labelled',labelled,'fixed',fixed,'reps',(labelled+fixed)//2)


if __name__ == '__main__':
    {'control':controls, 'geometry':geometry}[sys.argv[1]]()
