from collections import Counter
from pathlib import Path
import sys
from time import perf_counter
from hole_branches import bank, establish, cut, small
from hole_verify import Original,validate_branch
from id8_local import target


def check_roles(rank,points):
    base=target();chart=list(map(int,Path('roles.chart').read_text().split())); assert len(chart)==6
    keys,rows=bank(base,10,rank); print('bank',rank,Counter(len(forms) for _,forms in rows),flush=True)
    original=Original(18,set(keys))
    for point in points:
        begin=perf_counter()
        steps,proof,status=cut(rows,establish(keys,chart,point))
        print(point,status,len(steps),len(proof),f'{perf_counter()-begin:.5f}',flush=True)
        receipt=f'{status} {point}\n'+ ' '.join(map(str,steps))+'\n'+' '.join(map(str,proof))+'\n'
        if status!='open':validate_branch(original,original.room(chart,point),point,receipt,10)
        Path(f'role.{rank}.{point}.proof').write_text(receipt)


if __name__=='__main__':
    if sys.argv[1]=='control':small()
    else:check_roles(int(sys.argv[1]),[int(text) for text in sys.argv[2:]])
