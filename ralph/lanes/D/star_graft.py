"""Exact, stabilizer-safe extension of a complete star through a marked P6."""

import argparse
import json
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
import time

from joint_deck import marks
from path_growth import bits, fixed_graph, path_lengths, read_profiles
from path_overlap import Library
from path_reroot import placements
from punct_path import pairs


def occupied(vertices):
    return sum(1 << vertex for vertex in vertices)


def alloc(cells, count):
    if not cells:
        if count == 0:
            yield 0
        return
    cell, *rest = cells
    for take in range(max(0, count-sum(map(len,rest))), min(len(cell),count)+1):
        value = occupied(cell[:take])
        for suffix in alloc(rest,count-take):
            yield value | suffix


def graft(graph, frozen, core, pivot, library):
    index = core.index(pivot)
    keep = 255 ^ (1 << index)
    classes = defaultdict(lambda: defaultdict(list))
    counts = Counter()
    exact = Counter()
    for vertex in range(len(graph)):
        if vertex in core:
            continue
        mask = sum(1 << slot for slot,anchor in enumerate(core) if slot != index and graph[vertex] >> anchor & 1)
        counts[mask] += 1
        if vertex in frozen:
            exact[mask] += graph[pivot] >> vertex & 1
        elif not graph[vertex] & graph[pivot]:
            classes[mask][graph[vertex]].append(vertex)
    candidates = library.candidates(keep, tuple(sorted(counts.items())))
    answers = set()
    for target in candidates:
        desired = Counter({mask & keep: number for mask,number in target if mask >> index & 1})
        partial = [list(alloc(list(classes[mask].values()), desired[mask]-exact[mask])) for mask in counts]
        for pieces in product(*partial):
            answers.add(sum(pieces))
    return answers


def forbidden_independent(upper, target):
    def clique(candidates, size):
        if size <= 0:
            return True
        while candidates.bit_count() >= size:
            pivot = candidates & -candidates
            candidates ^= pivot
            if clique(candidates & ~upper[pivot.bit_length()-1], size-1):
                return True
        return False
    return clique((1<<len(upper))-1,target)


def validate(graph, frozen, degree, cap, qmax, detailed=True):
    if max(row.bit_count() for row in graph) > degree:
        return 'overdegree'
    if any(graph[src] & graph[dst] for src in frozen for dst in bits(graph[src])):
        return 'triangle'
    if max((left & right).bit_count() for left,right in pairs(graph)) > 3:
        return 'cap'
    if path_lengths(graph) > cap:
        return 'path'
    if max(sum((graph[other] & graph[center]).bit_count()-1 for other in bits(graph[root]) if other != center) for root in frozen for center in bits(graph[root])) > qmax:
        return 'qmax'
    hood = occupied(frozen)
    upper = list(graph)
    for src,dst in pairs(list(bits(((1<<len(graph))-1) ^ hood))):
        if not graph[src] & graph[dst] and graph[src].bit_count() < degree and graph[dst].bit_count() < degree:
            upper[src] |= 1<<dst
            upper[dst] |= 1<<src
    if min(row.bit_count() for row in upper) < degree:
        return 'degree'
    if any(not upper[src] >> dst & 1 and not upper[src] & upper[dst] for src,dst in pairs(range(len(graph)))):
        return 'undominated'
    if detailed and forbidden_independent(upper,degree+1):
        return 'independent'
    return ''


def next_step(graph, frozen, library):
    choices = {}
    for core in placements(graph):
        unknown = set(core) - frozen
        if not unknown:
            masks = Counter(sum(1 << index for index,anchor in enumerate(core) if graph[vertex] >> anchor & 1) for vertex in range(len(graph)) if vertex not in core)
            if not library.candidates(255,tuple(sorted(masks.items()))):
                return -1,[]
        if len(unknown) != 1:
            continue
        pivot, = unknown
        options = graft(graph,frozen,core,pivot,library)
        if pivot in choices:
            choices[pivot].intersection_update(options)
        else:
            choices[pivot] = options
        if not choices[pivot]:
            return pivot,[]
    if not choices:
        return -1,None
    length,pivot = min((len(options),pivot) for pivot,options in choices.items())
    return pivot,sorted(choices[pivot])


def free_options(graph,frozen,pivot,degree):
    groups = defaultdict(list)
    for vertex in sorted(set(range(len(graph))) - frozen - {pivot}):
        if not graph[pivot] & graph[vertex] and graph[vertex].bit_count() < degree:
            groups[graph[vertex]].append(vertex)
    coords = sorted(frozen)
    cells = sorted(groups.items(),key=lambda item:(-item[0].bit_count(),item[0]))
    lower = [int(not (graph[pivot] >> anchor & 1)) for anchor in coords]
    tally = [(graph[pivot] & graph[anchor]).bit_count() for anchor in coords]
    incidence = [[index for index,anchor in enumerate(coords) if mask >> anchor & 1] for mask,_ in cells]
    remaining = [sum(len(cell) for _,cell in cells[index:]) for index in range(len(cells)+1)]
    def search(index,need,added):
        if need < 0 or need > remaining[index]:
            return
        if not need:
            if all(actual >= bound for actual,bound in zip(tally,lower)):
                yield added
            return
        _,cell = cells[index]
        relevant = incidence[index]
        max_take = min([need,len(cell)] + [3-tally[point] for point in relevant])
        for take in range(max(0,need-remaining[index+1]),max_take+1):
            for point in relevant:
                tally[point] += take
            yield from search(index+1,need-take,added|occupied(cell[:take]))
            for point in relevant:
                tally[point] -= take
    yield from search(0,degree-graph[pivot].bit_count(),0)


def free_step(graph,frozen,degree):
    from itertools import islice
    reps = {}
    for vertex in sorted(set(range(len(graph)))-frozen):
        reps.setdefault(graph[vertex],vertex)
    best = None
    for pivot in sorted(reps.values(),key=lambda vertex:(-graph[vertex].bit_count(),vertex)):
        choices = free_options(graph,frozen,pivot,degree)
        if best is None:
            opts = list(choices)
        else:
            opts = list(islice(choices,len(best[1])))
        if best is None or len(opts) < len(best[1]):
            best = pivot,opts
            if not opts:
                break
    return (-1,None) if best is None else best


def extend(graph,pivot,add):
    work = list(graph)
    work[pivot] |= add
    for vertex in bits(add):
        work[vertex] |= 1<<pivot
    return work


def calibrate(free=False):
    records = list(marks())
    library = Library([profile for profile,_,_,_ in records])
    hist = Counter()
    for profile,_,planted,width in records:
        if width != 4:
            continue
        graph = fixed_graph(profile)
        frozen = set(range(8))
        for step in range(14):
            assert all(graph[anchor] == planted[anchor] for anchor in frozen)
            assert not validate(graph,frozen,6,8,20)
            pivot,opts = next_step(graph,frozen,library)
            if opts is None and free:
                pivot,opts = free_step(graph,frozen,6)
            if opts is None:
                break
            groups = defaultdict(list)
            for other in sorted(set(range(len(graph)))-frozen-{pivot}):
                groups[graph[other]].append(other)
            perm = list(range(len(graph)))
            rep = 0
            for cell in groups.values():
                seen = [vertex for vertex in cell if planted[pivot] >> vertex & 1]
                ordered = seen+[vertex for vertex in cell if vertex not in seen]
                for old,new in zip(ordered,cell):
                    perm[old] = new
                rep |= occupied(cell[:len(seen)])
            assert rep in opts
            next_graph = [0]*len(graph)
            for vertex,row in enumerate(planted):
                next_graph[perm[vertex]] = occupied(perm[other] for other in bits(row))
            planted = next_graph
            graph = extend(graph,pivot,rep)
            frozen.add(pivot)
        hist[len(frozen)] += 1
    assert sum(hist.values()) == 48
    print('PASS transported C22 completions on all 48 marks, terminal frozen stars',sorted(hist.items()))


def run(profile,library,cutoff,out,free=False):
    counts = Counter()
    start = time.process_time()
    def dfs(graph, frozen, route):
        depth = len(frozen)
        why = validate(graph,frozen,9,6,13)
        if not why:
            pivot,options = next_step(graph,frozen,library)
            if options is None and free:
                pivot,options = free_step(graph,frozen,9)
            if options is None:
                why = 'stalled'
            elif not options:
                why = 'profile'
            elif depth >= cutoff:
                why = 'depth-cap'
            else:
                counts[depth,'branch'] += 1
                for add in options:
                    dfs(extend(graph,pivot,add),frozen|{pivot}, route+[(pivot,add)])
                return
        counts[depth,why] += 1
        print(json.dumps([why,route]),file=out,flush=True)
    dfs(fixed_graph(profile),set(range(8)),[])
    print('nodes',sum(counts.values()),'CPU',round(time.process_time()-start,3),sorted(counts.items()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--index',type=int)
    parser.add_argument('--cutoff',type=int,default=14)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--free',action='store_true')
    parser.add_argument('--two',action='store_true')
    args = parser.parse_args()
    if args.index is None:
        calibrate(args.free)
    else:
        profiles = list(read_profiles(args.source))
        allowed = (2298,2424) if args.two else (2298,2424,2431)
        assert args.index in allowed
        with args.out.open('w') as stream:
            run(profiles[args.index],Library([profiles[index] for index in allowed]),args.cutoff,stream,args.free)
