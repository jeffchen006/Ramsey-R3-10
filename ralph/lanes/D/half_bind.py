from collections import Counter
from itertools import combinations_with_replacement
from time import process_time
from book_strata import DEST
from half_lookup import table
import json


if __name__=='__main__':
    started=process_time();records=list(map(json.loads,(DEST/'half.jsonl').read_text().splitlines()));db=table(records);observed=set();multiplicity=Counter()
    for rows in combinations_with_replacement(range(16),8):
        if rows[-1]==15:continue
        columns=[sum(1<<site for site,mask in enumerate(rows) if mask>>col&1) for col in range(4)]
        if any(not(1<=word.bit_count()<=3) for word in columns) or any((word&nextword).bit_count()>2 for idx,word in enumerate(columns) for nextword in columns[:idx]):continue
        key=sum(word<<(4*site) for site,word in enumerate(rows));assert key in db;observed.add(key);multiplicity[db[key][0]]+=1
    assert observed==set(db) and len(multiplicity)==530;print('PASS entire 8x4 catalogue by literal sorted row multisets and column images:',len(observed),'row words;',len(multiplicity),'oriented classes, CPU',process_time()-started)
