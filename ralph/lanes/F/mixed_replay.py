"""Rebind emitted SAT cases and old quotient maps to freshly dual-checked proofs."""

from hashlib import sha256
from pathlib import Path
from csv import DictReader
from cyclic_check import check


def digest(data):return sha256(data).hexdigest()


def replay():
    rows=Path('target.q').read_text().splitlines();zeros={index for index,line in enumerate(Path('target.forced').read_text().splitlines()) if int(line.split()[1])==0}
    ids=list(map(int,Path('target.ids').read_text().split()));status=[line.split() for line in Path('target.sat').read_text().splitlines()]
    assert len(ids)==len(zeros) and set(ids)==zeros and [int(line[0]) for line in status]==ids and all(line[1]=='no' for line in status)
    assert {int(path.stem) for path in Path('targetproof').glob('*.lrat')}==zeros
    with Path('fresh.receipt').open('w') as out:
        for index in ids:
            stem=Path('targetproof')/f'{index:06}';cuts=check(rows[index],10,stem)
            print(index,cuts,digest(rows[index].encode()),*[digest(stem.with_suffix(ext).read_bytes()) for ext in ['.cnf','.trace','.lrat']],file=out)
    inherited=sorted({int(fields[2]) for fields in map(str.split,Path('target.maps').read_text().splitlines()) if fields[1]=='old'})
    original=Path('../r8/target.q').read_text().splitlines();receipt=list(DictReader(Path('../r8/target.receipt.tsv').read_text().splitlines(),delimiter='\t'))
    with Path('old.receipt').open('w') as out:
        for index in inherited:
            assert 0<=index<len(original);line=receipt[index];text=original[index];assert int(line['row'])==index and digest(text.encode())==line['source_sha256']
            stem=Path('../r8')/line['path'];assert check(text,10,stem)==int(line['supports'])
            for ext in ['cnf','trace','lrat']:assert digest(stem.with_suffix('.'+ext).read_bytes())==line[ext+'_sha256']
            print(index,line['source_sha256'],line['cnf_sha256'],line['trace_sha256'],line['lrat_sha256'],file=out)
    print('fresh independently checked (semantic, two LRAT kernels)',len(ids),'inherited same replay',len(inherited))


if __name__=='__main__':assert __debug__;replay()
