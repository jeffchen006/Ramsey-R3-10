"""One missing Y edge: conditional one-shore witnesses. No target input."""
from itertools import combinations
from pathlib import Path
from time import process_time


def compile_forced(order, rows, types):
    result = []
    for left,right in combinations(range(len(rows)),2):
        first,second = rows[left],rows[right]
        if first & second:
            continue
        bridges = [site for site in types if site & first and site & second]
        assert all(site & ~(first | second) == 0 for site in bridges)
        candidates = [site for site in rows if site & first and site & second]
        limits = {}
        def extend(family,tail):
            covered = first | second
            for site in family:
                covered |= site
            mask = sum(1<<site for site in bridges if all(site & other for other in family))
            cap = covered.bit_count()-1-len(family)
            if cap < 2*mask.bit_count() and cap < limits.get(mask,order+2):
                limits[mask] = cap
            for index,site in enumerate(tail):
                extend(family+[site],[after for after in tail[index+1:] if after & site])
        extend([],candidates)
        if limits:
            result.append((left,right,tuple(limits.items())))
    return result


def flagged(tests,profile):
    seen,twice = profile
    return [(left,right) for left,right,bounds in tests if any(
        (seen & subset).bit_count()+(twice & subset).bit_count() > cap for subset,cap in bounds)]


def pack(sites):
    assert max((sites.count(item) for item in sites if item.bit_count()==2),default=0)<=2
    return tuple(sum(1<<item for item in set(sites) if sites.count(item)>=level and item.bit_count()==2) for level in (1,2))


def controls():
    import networkx as nx
    rows = [3,12]
    types = [3,5,6,9,10,12]
    checks = compile_forced(4,rows,types)
    assert flagged(checks,pack([5,6,9,10])) == [(0,1)] and not flagged(checks,pack([5,6,9]))
    assert flagged(checks,pack([5,5,10,10])) == [(0,1)]
    print('strict four bridge sites force 01--23, three do not; repeated physical bridges included')
    path = Path(__file__).resolve().parents[3]/'gluing/val/r3_7_22.g6'
    plants = edges = positives = 0
    for line in path.read_bytes().splitlines():
        graph = nx.from_graph6_bytes(line)
        stars = list(map(lambda vertex:set(graph[vertex]),graph))
        if any(len(star)!=6 for star in stars) or max(len(left & right) for left,right in combinations(stars,2))>3:
            continue
        for left,right in combinations(graph,2):
            middle = stars[left] & stars[right]
            if right in stars[left] or len(middle)!=1:
                continue
            poles = sorted(stars[next(iter(middle))]-{left,right})
            untouched = sorted(set(graph)-stars[left]-stars[right]-set(poles)-{left,right})
            def site(vertex):
                return sum(1<<num for num,pole in enumerate(poles) if pole in stars[vertex])
            host_rows = [site(vertex) for vertex in untouched]
            tests = compile_forced(4,host_rows,types)
            for tip in [left,right]:
                shore = [site(vertex) for vertex in stars[tip]-middle]
                assert max(mask.bit_count() for mask in shore)<=2
                required = flagged(tests,pack(shore))
                assert all(untouched[second] in stars[untouched[first]] for first,second in required)
                edges += len(required)
                positives += bool(required)
                plants += 1
    assert plants==250
    print('planted C22 all forced pairs are edges: shores / nonempty / forced occurrences',plants,positives,edges)


def price():
    from wing20_audit import Audit
    start = process_time()
    tables = Audit([1]+[2]*6,5,6)
    setup = process_time()-start
    rows = [7,9,10,12,17,18,20,33,34,36,65,66,68,24]
    start = process_time()
    tests = compile_forced(7,rows,tables.types)
    compiled = process_time()-start
    sample = tables.shorts[:400]+tables.longs[:400]
    start = process_time()
    incidences = sum(len(flagged(tests,profile)) for profile in sample)
    spent = process_time()-start
    print('synthetic, no roster read: edges with tests / tests / profiles / occurrences',len(tests),
          sum(len(bounds) for _,_,bounds in tests),len(sample),incidences)
    print('setup + 150 compilations + 52969 marginal calls CPU-s',round(setup+150*compiled+spent*52969/len(sample),2))


if __name__=='__main__':
    controls()
    price()
