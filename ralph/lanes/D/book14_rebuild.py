from pathlib import Path
import hashlib,json,sys
from book_strata import DEST,standard
from book_edge_sat import encode
from triad_proof import build


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__=='__main__':
    out=Path(sys.argv[1]) if len(sys.argv)>1 else DEST/'regenerated';out.mkdir(exist_ok=True)
    for number,kind in ((26377,'full'),(26380,'edge'),(26996,'full'),(26998,'edge'),(27275,'edge')):
        record=next(row for path in DEST.glob('pop-12-13.*.jsonl') for row in map(json.loads,path.read_text().splitlines()) if row['id']==number);form,_=encode(standard(record['rows']),40,9,{(1,2)},True,kind=='full');name=f'wing-{number}-{kind}.cnf';target=out/name;form.write(target);assert digest(target)==digest(DEST/name);print(name,digest(target),flush=True)
    for parts in ((7,),(5,2),(4,3),(3,2,2)):
        form=build(7,7,parts);name='triad-7-7-'+''.join(map(str,parts))+'.cnf';target=out/name;form.write(target);assert digest(target)==digest(DEST/name);print(name,digest(target),flush=True)
