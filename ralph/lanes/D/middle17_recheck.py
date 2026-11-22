"""Read-only archive verifier. Start from frozen physical rows, not the stored CNF."""
import json
from pathlib import Path
import sys
from zipfile import ZipFile
from middle17 import CHECKS, DATA, checked, compact, cpu, digest, scheduled, tag, target


def verify(path, phase, worker, offset, directory=None):
    group=scheduled(phase,worker)[offset:offset+24]; assert group
    dest=directory or path.parent
    source=dest/'reconstructed.cnf'; proof=dest/'archived.lrat'; records=[]
    with ZipFile(path,'r') as pack:
        names=[tag(rec)+'.'+ext for rec in group for ext in ['cnf','lrat','json']]
        assert pack.namelist()==names
        for rec in group:
            assert not (DATA/'STOP').exists() or directory is not None
            start=cpu(); key=tag(rec); result=json.loads(pack.read(key+'.json'))
            assert (result['key'],result['weight'],result['physical'])==(key,rec['weight'],digest(compact(rec).encode()))
            assert result['receipts']==[list(item) for item in [('cadical',20,'s UNSATISFIABLE'),*CHECKS]]
            target(rec,source); data=pack.read(key+'.cnf'); raw=pack.read(key+'.lrat')
            assert data==source.read_bytes() and digest(data)==result['cnf'] and digest(raw)==result['lrat']
            assert (len(data),len(raw))==(result['cnf_bytes'],result['proof_bytes'])
            proof.write_bytes(raw); receipts=[]
            for tool,rc,marker in reversed(CHECKS):
                receipts.append(checked(tool,rc,marker,[source,proof],10-result['cpu']-(cpu()-start)))
            source.unlink(); proof.unlink(); used=cpu()-start; assert used+result['cpu']<10
            records.append(dict(key=key,weight=rec['weight'],physical=result['physical'],cnf=result['cnf'],lrat=result['lrat'],production=result['cpu'],replay=used,zbytes=result['zbytes'],proof_bytes=len(raw),receipts=receipts))
    receipt=dest/(path.stem+'.ok'); assert not receipt.exists()
    temp=receipt.with_suffix('.tmp'); temp.write_text(''.join(compact(item)+'\n' for item in records));temp.rename(receipt)


if __name__=='__main__':verify(Path(sys.argv[1]),sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),Path(sys.argv[5]) if len(sys.argv)>5 else None)
