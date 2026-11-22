from itertools import permutations
import json
from book_strata import DEST
from book_controls import bitset


def table(records):
    lookup={}
    for record in records:
        for order in permutations(range(4)):
            permuted=sorted(bitset(idx for idx,point in enumerate(order) if word>>point&1) for word in record['rows']);word=sum(mask<<(4*idx) for idx,mask in enumerate(permuted));assert lookup.setdefault(word,(record['id'],record['status']))==(record['id'],record['status'])
    return lookup


if __name__=='__main__':
    rows=list(map(json.loads,(DEST/'half.jsonl').read_text().splitlines()));assert len(rows)==530;lookup=table(rows)
    for key,(idx,status) in sorted(lookup.items()):print(key,idx,int(status=='fractional'))
