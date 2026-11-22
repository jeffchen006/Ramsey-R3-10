"""Compile simultaneous conditional eight-star P6 marginals to ordinary CNF."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path

from pysat.solvers import Cadical195

from joint_deck import conjunction, marks
from kernel_cnf import Cnf, neg
from path_growth import bits, fixed_graph, read_profiles
from path_overlap import Library
from path_reroot import placements
from punct_path import pairs, template


def setup(profile, degree, full):
    graph = fixed_graph(profile)
    order = len(graph)
    fixed = {(src,dst): bool(graph[src] >> dst & 1) for src,dst in pairs(range(order)) if src < 8 or graph[src] & graph[dst]}
    form = Cnf(order, fixed)
    for src in range(order):
        form.cardinality([form.edge(src,dst) for dst in range(order) if src != dst], degree,degree)
    if full:
        for points in combinations(range(8,order),3):
            form.add(*(neg(form.edge(*edge)) for edge in pairs(points)))
        for src,dst in pairs(range(order)):
            common = [form.conjunction(form.edge(src,other),form.edge(dst,other)) for other in range(order) if other not in (src,dst)]
            flags = form.thresholds(common,4)
            form.add(neg(flags[3]))
            form.add(form.edge(src,dst),flags[0])
    return graph, form


def enforce(form, core, library):
    graph = template(False)
    required = [form.edge(core[src],core[dst]) if dst in graph[src] else neg(form.edge(core[src],core[dst])) for src,dst in pairs(range(8))]
    if any(lit is False for lit in required):
        return 0
    exterior = sorted(set(range(form.n)) - set(core))
    stars = [[form.edge(vertex,anchor) for anchor in core] for vertex in exterior]
    low = [sum(1<<index for index,lit in enumerate(row) if lit is True) for row in stars]
    high = [sum(1<<index for index,lit in enumerate(row) if lit is not False) for row in stars]
    keep = 255
    for lower,upper in zip(low,high):
        keep &= ~(upper ^ lower)
    code = tuple(sorted(Counter(column & keep for column in low).items()))
    guards = []
    cache = {}
    for profile in library.candidates(keep,code):
        domains = [[mask for mask,_ in profile if not (lower & ~mask or mask & ~upper)] for lower,upper in zip(low,high)]
        if not all(domains):
            continue
        switch = form.new()
        guards.append(switch)
        mask_slots = {mask: [] for mask,_ in profile}
        for vertex,(row,options) in enumerate(zip(stars,domains)):
            choices = []
            for mask in options:
                if (vertex,mask) not in cache:
                    cache[vertex,mask] = conjunction(form,[lit if mask >> index & 1 else neg(lit) for index,lit in enumerate(row)])
                value = cache[vertex,mask]
                choices.append(value)
                mask_slots[mask].append(value)
            form.add(-switch,*choices)
        for mask,size in profile:
            terms = mask_slots[mask]
            constants = sum(lit is True for lit in terms)
            leaves = [lit for lit in terms if not isinstance(lit,bool)]
            wanted = size-constants
            if wanted < 0 or wanted > len(leaves):
                form.add(-switch)
            elif wanted in (0,len(leaves)):
                for lit in leaves:
                    form.add(-switch,lit if wanted else -lit)
            else:
                flags = form.thresholds(leaves,wanted+1)
                form.add(-switch,flags[wanted-1])
                form.add(-switch,neg(flags[wanted]))
    form.add(*(neg(lit) for lit in required),*guards)
    return len(guards)


def windows(graph, form, depth):
    selected = set(placements(graph))
    if depth:
        for src,dst in pairs(range(8,len(graph))):
            if isinstance(form.edge(src,dst),bool):
                continue
            graph[src] |= 1 << dst
            graph[dst] |= 1 << src
            selected.update(placements(graph))
            graph[src] ^= 1 << dst
            graph[dst] ^= 1 << src
    return sorted(selected)


def build(profile, library, degree, full, depth, extra=()):
    graph,form = setup(profile,degree,full)
    cores = sorted(set(windows(graph,form,depth)) | set(extra))
    counts = Counter(enforce(form,core,library) for core in cores)
    return form,cores,counts


def calibration():
    records = list(marks())
    library = Library([profile for profile,_,_,_ in records])
    counts = Counter()
    seen = {}
    for profile,_,planted,width in records:
        if width != 4:
            continue
        token = tuple(sorted(profile.items()))
        if token not in seen:
            seen[token] = build(profile,library,6,True,1)[:2]
        form,cores = seen[token]
        with Cadical195(bootstrap_with=form.clauses) as solver:
            pins = [form.edge(src,dst,simplify=False)*(1 if planted[src] >> dst & 1 else -1) for src,dst in pairs(range(22))]
            assert solver.solve(assumptions=pins)
        counts['marks'] += 1
        counts['tested'] += len(cores)
        counts['active'] += len(set(cores) & set(placements(planted)))
    assert counts['marks'] == 48 and counts['active'] > counts['marks']
    profile = records[0][0]
    bad,_,_ = build(profile,Library([]),6,True,0)
    with Cadical195(bootstrap_with=bad.clauses) as solver:
        assert not solver.solve()
    print('PASS planted joint windows', dict(counts), 'empty-library control rejected', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--index',type=int)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--depth',type=int,default=1)
    parser.add_argument('--extra',type=Path)
    parser.add_argument('--degree-only',action='store_true')
    args = parser.parse_args()
    if args.index is None:
        calibration()
    else:
        profiles = list(read_profiles(args.source))
        allowed = (2298,2424,2431)
        assert args.index in allowed
        library = Library([profiles[index] for index in allowed])
        extra = [tuple(map(int,line.split())) for line in args.extra.read_text().splitlines()] if args.extra else []
        form,cores,counts = build(profiles[args.index],library,9,not args.degree_only,args.depth,extra)
        form.write(args.out)
        print('cores',len(cores),'compatible selector counts',counts,'vars',form.nvars,'clauses',len(form.clauses))
