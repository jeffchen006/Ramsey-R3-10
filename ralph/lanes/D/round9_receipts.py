"""Bind every P7 root to its first terminal test, and every L6 audit to its proof."""

import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def bind(work):
    sources=(work/'long.tsv').read_text().splitlines()
    assert len(sources)==len(set(sources))==243175
    assert sorted(sources)==sorted((work/'direct.tsv').read_text().splitlines())
    statuses={}
    indices=list(range(len(sources)))
    def filter_table(source,columns,criterion):
        nonlocal indices
        rows=[line.split() for line in source.read_text().splitlines()]
        assert len(rows)==len(indices)
        live=[]
        for row_number,(index,row) in enumerate(zip(indices,rows)):
            assert len(row)==columns and int(row[0])==row_number
            label=criterion(tuple(map(int,row[1:])))
            if label:
                statuses[index]=(label,source.relative_to(work).as_posix(),row_number)
            else:
                live.append(index)
        indices=live
    filter_table(work/'long-filter.tsv',4,lambda row:f'base:{row[0]}' if row[0] else ('over7' if row[2]>7 else ''))
    assert [sources[index] for index in indices]==(work/'short.tsv').read_text().splitlines()
    filter_table(work/'short-arc.tsv',4,lambda row:f'arc:{row[0]}' if row[0] else '')
    assert [sources[index] for index in indices]==(work/'short-live.tsv').read_text().splitlines()
    for stage,folder,prefix,budget,next_file in (
        ('level1','seven','s',500,'seven/overlap.tsv'),
        ('level2','seven/level2','t',5000,'seven/level2/residue.tsv'),
        ('level3','seven/level3','u',30000,'seven/level3/residue.tsv'),
        ('level4','seven/level4','v',250000,None),
    ):
        remaining=[]
        already=0
        for file in sorted((work/folder).glob(prefix+'??.in')):
            inputs=file.read_text().splitlines()
            output=file.with_suffix('.out').read_text().splitlines()
            assert len(inputs)==len(output)
            for pos,(source,line) in enumerate(zip(inputs,output)):
                index=indices[already+pos]
                assert source==sources[index]
                fields=line.split()
                ordinal,status,nodes=map(int,fields[:3])
                assert ordinal==pos and status in (-1,0) and nodes<=budget
                if status==-1:
                    assert nodes==budget
                    remaining.append(index)
                else:
                    assert sum(map(int,fields[4:]))==nodes
                    statuses[index]=(stage,file.with_suffix('.out').relative_to(work).as_posix(),pos)
            already+=len(inputs)
        assert already==len(indices)
        indices=remaining
        if next_file:
            assert [sources[index] for index in indices]==(work/next_file).read_text().splitlines()
        print(stage,'still open',len(indices))
    assert not indices and set(statuses)==set(range(len(sources)))
    with (work/'seven/terminal.tsv').open('w') as stream:
        print('index\tprofile_line_sha256\tfirst_terminal_reason\treceipt\tzero_based_row',file=stream)
        for index,source in enumerate(sources):
            print(index,sha256((source+'\n').encode()).hexdigest(),*statuses[index],sep='\t',file=stream)
    print('PASS bound all 243175 to a terminal result:',Counter(value[0] for value in statuses.values()))
    files=sorted(work.glob('aud-*/*.cnf'))
    assert len(files)==105
    with (work/'graft-receipts.tsv').open('w') as stream:
        print('bundle\tcnf_sha256\tlrat_sha256',file=stream)
        for file in files:
            assert 's VERIFIED UNSAT' in file.with_suffix('.cake_lpr.log').read_text().splitlines()
            assert 'c VERIFIED' in file.with_suffix('.lrat-check.log').read_text().splitlines()
            print(file.relative_to(work),digest(file),digest(file.with_suffix('.lrat')),sep='\t',file=stream)
    print('PASS bound all 105 dual LRAT bundle receipts')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('work',type=Path)
    bind(parser.parse_args().work)
