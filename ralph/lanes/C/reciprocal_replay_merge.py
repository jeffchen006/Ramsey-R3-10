from functools import lru_cache


def sites(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length()-1
        mask ^= bit


def factory(left_hosts, right_hosts, common=9, roots=3):
    left_order,right_order = len(left_hosts[0]),len(right_hosts[0])
    left_width,right_width = left_order-common,right_order-common
    neutral = left_width+right_width
    root_start = neutral+common
    order = root_start+2*roots

    def prepare(host,names):
        graph = [0]*order
        bits = tuple(1 << position for position in names)
        for entry,row in enumerate(host):
            graph[names[entry]] = sum(bits[old] for old in sites(row))
        return graph,bits

    def attach(base,bits,roots,mark):
        result = base.copy()
        for root,group in enumerate(mark,roots):
            root_bit = 1 << root
            for entry in sites(group):
                positioned = bits[entry]
                result[root] |= positioned
                result[positioned.bit_length()-1] |= root_bit
        return tuple(result)

    @lru_cache(maxsize=8192)
    def one_shell(lid,core):
        names = list(sites(((1 << left_order)-1)^core))+list(sites(core))
        translated = [0]*left_order
        for original,position in zip(names,(*range(left_width),*range(neutral,root_start)),strict=True):
            translated[original] = position
        return prepare(left_hosts[lid],translated)

    @lru_cache(maxsize=16384)
    def one_mark(lid,core,mark):
        base,bits = one_shell(lid,core)
        return attach(base,bits,root_start,mark)

    @lru_cache(maxsize=8192)
    def two_shell(rid,core,mapping):
        names = list(sites(((1 << right_order)-1)^core))+list(mapping)
        translated = [0]*right_order
        for original,position in zip(names,range(left_width,root_start),strict=True):
            translated[original] = position
        return prepare(right_hosts[rid],translated)

    @lru_cache(maxsize=16384)
    def two_mark(rid,core,mapping,mark):
        base,bits = two_shell(rid,core,mapping)
        return attach(base,bits,root_start+roots,mark)

    joined_roots = [0]*root_start + [((1 << roots)-1) << (root_start+roots)]*roots + [((1 << roots)-1) << root_start]*roots

    def combine(lid,lcore,lmarks,rid,rcore,mapping,rmarks):
        return [first | second | root for first,second,root in zip(one_mark(lid,lcore,lmarks),
                                                                  two_mark(rid,rcore,mapping,rmarks),joined_roots)]

    return combine
