"""Independent checker for star-graft tries. No producer or root-discovery imports."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import sys

from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195


REPS = (2298,2424,2431)
TEMPLATE = ((0,4),(0,5),(0,6),(0,7),(1,4),(1,7),(2,4),(2,5),(2,7),(3,4),(3,5),(3,6))
FLIP = (4,6,5,7,0,2,1,3)


def parse(path):
    rows = path.read_text().splitlines()
    profiles = []
    for index in REPS:
        counts = {int(key):int(count) for key,count in (field.split(':') for field in rows[index].split())}
        profiles.append(counts)
    return profiles


def orientations(profiles):
    output = []
    for profile in profiles:
        for perm in (tuple(range(8)),FLIP):
            output.append(Counter({sum(1<<position for position,old in enumerate(perm) if mask & (1<<old)):size for mask,size in profile.items()}))
    return output


def initial(profile):
    masks = [mask for mask,count in sorted(profile.items()) for _ in range(count)]
    graph = [set() for _ in range(8+len(masks))]
    for src,dst in TEMPLATE:
        graph[src].add(dst)
        graph[dst].add(src)
    for vertex,mask in enumerate(masks,8):
        for anchor in range(8):
            if mask & (1<<anchor):
                graph[vertex].add(anchor)
                graph[anchor].add(vertex)
    return graph


def kernel_walks(graph,size):
    for src,row in enumerate(graph):
        for dst in sorted(row):
            if dst <= src:
                continue
            kernel = (graph[src]|graph[dst]) - {src,dst}
            def grow(path):
                if len(path) == size:
                    yield tuple(path)
                else:
                    for vertex in sorted((graph[path[-1]] & kernel)-set(path)):
                        yield from grow(path+[vertex])
            starts = graph[src]-{dst} if size%2 == 0 else kernel
            for first in sorted(starts):
                for path in grow([first]):
                    yield src,dst,path


def both_sides(graph):
    for src,dst,path in kernel_walks(graph,6):
        if path[-1] not in graph[path[0]]:
            core = (dst,path[0],path[2],path[4],src,path[3],path[5],path[1])
            assert all((core[second] in graph[core[first]]) == ((first,second) in TEMPLATE) for first,second in combinations(range(8),2))
            yield core


def possible(graph, marked, degree=9):
    result = [set(row) for row in graph]
    for src,dst in combinations(sorted(set(range(len(graph)))-marked),2):
        if not graph[src].intersection(graph[dst]) and max(len(graph[src]),len(graph[dst])) < degree:
            result[src].add(dst)
            result[dst].add(src)
    return result


def concrete(reason,graph,marked,degree=9):
    if reason == 'cap':
        for src,dst in combinations(range(len(graph)),2):
            common = sorted(graph[src] & graph[dst])
            if len(common) > 3:
                return [src,dst,common[:4]]
    if reason == 'path':
        for src,dst,path in kernel_walks(graph,7):
            return [src,dst,path]
    if reason in ('undominated','independent'):
        upper = possible(graph,marked,degree)
        if reason == 'undominated':
            for src,dst in combinations(range(len(graph)),2):
                if dst not in upper[src] and not upper[src].intersection(upper[dst]):
                    return [src,dst]
        else:
            def extend(vertices,need):
                if need == 0:
                    return []
                while len(vertices) >= need:
                    point = vertices[-1]
                    vertices = vertices[:-1]
                    tail = extend([vertex for vertex in vertices if vertex not in upper[point]],need-1)
                    if tail is not None:
                        return [point]+tail
                return None
            return extend(list(range(len(graph))),degree+1)
    return None


class RowCnf:
    def __init__(self,order):
        self.clauses = []
        self.nvars = order

    def card(self, literals, lower, upper, guard=None):
        prefix = [] if guard is None else [-guard]
        for signed,limit in ((literals,upper),([-lit for lit in literals],len(literals)-lower)):
            if limit < 0:
                self.clauses.append(prefix)
            elif limit < len(signed):
                gate = CardEnc.atmost(signed,bound=limit,top_id=self.nvars,encoding=EncType.seqcounter)
                self.nvars = max(self.nvars,gate.nv)
                self.clauses.extend([prefix+clause for clause in gate.clauses])


def star_formula(graph,marked,pivot,library,cores,degree=9):
    vertices = set(range(len(graph)))
    result = RowCnf(len(graph))
    for other in sorted(marked|{pivot}):
        result.clauses.append([(other+1) * (1 if other in graph[pivot] else -1)])
    for other in sorted(vertices-marked-{pivot}):
        if graph[pivot] & graph[other] or len(graph[other]) >= degree:
            result.clauses.append([-other-1])
    result.card(list(range(1,len(graph)+1)),degree,degree)
    for point in sorted(marked):
        result.card([vertex+1 for vertex in sorted(graph[point])],1 if point not in graph[pivot] else 0,3)
    cells = defaultdict(list)
    for other in sorted(vertices-marked-{pivot}):
        cells[tuple(sorted(graph[other]))].append(other)
    for cell in cells.values():
        for first,second in zip(cell,cell[1:]):
            result.clauses.append([first+1,-second-1])
    for core in cores:
        if set(core)-marked != {pivot}:
            continue
        pos = core.index(pivot)
        old = defaultdict(list)
        for vertex in sorted(vertices-set(core)):
            mask = sum(1<<index for index,anchor in enumerate(core) if index!=pos and vertex in graph[anchor])
            old[mask].append(vertex+1)
        selectors = []
        for profile in library:
            if any(len(group) != profile[mask]+profile[mask|(1<<pos)] for mask,group in old.items()):
                continue
            result.nvars += 1
            select = result.nvars
            selectors.append(select)
            for mask,group in sorted(old.items()):
                count = profile[mask|(1<<pos)]
                result.card(group,count,count,select)
        result.clauses.append(selectors)
    return result


def profile_witness(graph,marked,library,cores):
    for core in cores:
        if set(core) <= marked:
            counts = Counter(sum(1<<index for index,anchor in enumerate(core) if vertex in graph[anchor]) for vertex in range(len(graph)) if vertex not in core)
            if counts not in library:
                return list(core),None
    preferred = {next(iter(set(core)-marked)) for core in cores if len(set(core)-marked)==1}
    for pivot in sorted(preferred) + sorted(set(range(len(graph)))-marked-preferred):
        formula = star_formula(graph,marked,pivot,library,cores)
        with Cadical195(bootstrap_with=formula.clauses) as solver:
            if not solver.solve():
                return pivot,formula
    raise AssertionError('unexplained profile leaf')


class Bundle:
    def __init__(self,out):
        self.out = out
        self.cnfs = []
        self.batch = 0
        self.total = 0

    def put(self,formula):
        if self.out:
            self.cnfs.append(formula)
            if len(self.cnfs) == 24:
                self.flush()
        self.total += 1

    def flush(self):
        if not self.cnfs:
            return
        switches = list(range(1,1+len(self.cnfs)))
        clauses = [switches]
        offset = len(switches)
        for switch,formula in zip(switches,self.cnfs):
            clauses.extend([[-switch]+[(offset+abs(lit))*(1 if lit>0 else -1) for lit in row] for row in formula.clauses])
            offset += formula.nvars
        with (self.out/f'{self.batch:04}.cnf').open('w') as stream:
            print('p cnf',offset,len(clauses),file=stream)
            for row in clauses:
                print(*row,0,file=stream)
        self.batch += 1
        self.cnfs = []


def check(profile,library,rows,out=None):
    graph = initial(profile)
    tree = {}
    for reason,route in rows:
        node = tree
        for pivot,added in route:
            node = node.setdefault((pivot,added),{})
        assert 'end' not in node
        node['end'] = reason
    stats = Counter()
    bundle = Bundle(out)
    receipts = (out/'witnesses.jsonl').open('w') if out else None
    def verify(node,marked,address):
        assert all(len(graph[point]) == 9 for point in marked)
        obligation = None
        if 'end' in node:
            assert len(node) == 1
            reason = node['end']
            stats[reason] += 1
            if reason == 'profile':
                witness,obligation = profile_witness(graph,marked,library,list(both_sides(graph)))
            else:
                witness = concrete(reason,graph,marked)
                assert witness is not None,(address,reason)
        else:
            pivots = {pivot for pivot,_ in node}
            assert len(pivots) == 1
            pivot = pivots.pop()
            assert pivot not in marked
            obligation = star_formula(graph,marked,pivot,library,list(both_sides(graph)))
            children = sorted(node)
            for _,added in children:
                cover = set(graph[pivot]) | {point for point in range(len(graph)) if added & (1<<point)}
                obligation.clauses.append([-(point+1) if point in cover else point+1 for point in range(len(graph))])
            witness = [pivot,len(children)]
            reason = 'branch'
            stats['branch'] += 1
        if obligation is not None:
            with Cadical195(bootstrap_with=obligation.clauses) as solver:
                if solver.solve():
                    raise AssertionError(('missing representative',address,witness,solver.get_model()[:len(graph)]))
            bundle.put(obligation)
        if receipts:
            print(json.dumps([address,reason,witness,bundle.total-1 if obligation is not None else None]),file=receipts)
        if reason == 'branch':
            for pivot,added in children:
                points = [point for point in range(len(graph)) if added & (1<<point)]
                assert not (set(points)&(marked|{pivot})) and not graph[pivot].intersection(points)
                graph[pivot].update(points)
                for point in points:
                    graph[point].add(pivot)
                verify(node[pivot,added],marked|{pivot},address+[(pivot,added)])
                graph[pivot].difference_update(points)
                for point in points:
                    graph[point].remove(pivot)
    verify(tree,set(range(8)),[])
    bundle.flush()
    if receipts:
        receipts.close()
    return stats,bundle.total,bundle.batch


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profiles',type=Path)
    parser.add_argument('index',type=int,choices=REPS)
    parser.add_argument('trie',type=Path)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--mutate',action='store_true')
    args = parser.parse_args()
    profiles = parse(args.profiles)
    library = orientations(profiles)
    rows = [json.loads(line) for line in args.trie.read_text().splitlines()]
    if args.mutate:
        min_depth = min(len(route) for _,route in rows)
        rows.pop(next(index for index,(_,route) in enumerate(rows) if len(route) == min_depth))
    if args.out:
        args.out.mkdir(parents=True,exist_ok=True)
    print('PASS complete labelled SAT branch audit and raw terminal witnesses',check(profiles[REPS.index(args.index)],library,rows,args.out))
