"""When both books retain seven petals, expose the partner of each blocked site."""
from collections import Counter
from itertools import combinations,product
from pathlib import Path
import json
import sys
from book_controls import book,bitset,sites
from book_seedpack import upper
from book_counter import isets


def cases(frame):
    fixed,*rows=frame;may=upper(frame);paths=[];wings=[]
    for ends in ((0,1),(2,3)):
        path,groups=book(rows,ends);paths.append(bitset(path));wings.append([bitset(side) for side in groups])
    pools=[left|right for left,right in wings];marked=paths[0]|paths[1];eligible=[pool&~marked for pool in pools];blocked=[next(sites(pool&marked)) for pool in pools];assert all((pool&marked).bit_count()==1 for pool in pools)
    options=[]
    for site,groups in zip(blocked,wings):
        opposite,=[group for group in groups if not group>>site&1];options.append(list(sites(opposite&may[site])))
    for first,second in product(*options):
        mates=[first,second];supports=[pool&~(1<<mate) for pool,mate in zip(eligible,mates)];private=[pool&~supports[1-idx] for idx,pool in enumerate(eligible)];lo=rows[:];hi=may[:]
        for lhs,rhs in zip(blocked,mates):lo[lhs]|=1<<rhs;lo[rhs]|=1<<lhs
        for word in private:
            for site in sites(word):hi[site]&=~(word^(1<<site))
        conflict=any(low&~high for low,high in zip(lo,hi));direct=next(isets(hi,len(rows),rows[0].bit_count()+1),0)
        yield dict(mates=mates,blocked=blocked,private=private,lo=lo,ban=[((1<<len(rows))-1)&~(high|1<<point) for point,high in enumerate(hi)],unit=conflict,I=direct)


def main(folder):
    result=[];controls=[];stats=Counter()
    for key,frame,truth in map(json.loads,(folder/'hard-four.in').read_text().splitlines()):
        if key not in (110,119,179):continue
        for record in cases(frame):
            record['id']=key;result.append(record);stats[key,'total']+=1;stats[key,'blocked']+=bool(record['unit'] or record['I'])
    (folder/'mate-cases.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n'for r in result));print(dict(stats))
    for r in result:
        if not r['unit'] and not r['I']:controls.append(' '.join(map(str,[15,*r['lo'],*r['ban']]))+'\n')
    (folder/'mate-live.in').write_text(''.join(controls))


if __name__=='__main__':main(Path(sys.argv[1]))
