"""Bind the no-induced-P8 C8 source, residual library, and terminal outputs."""

from collections import Counter
from hashlib import sha256
from pathlib import Path

from cycle8_join import deletions,read_profiles,profile_key,reverse


def census(work):
    base=(work/'long-filter.tsv').read_text().splitlines()
    source=(work/'long.tsv').read_text().splitlines()
    cyclic=[]
    for profile,record in zip(source,base,strict=True):
        _,status,_,length=map(int,record.split())
        if status==0 and length<=8 and '262:1' in profile.split():
            cyclic.append(profile)
    assert cyclic==(work/'eight/cyclic.tsv').read_text().splitlines() and len(cyclic)==24962
    surviving=[]
    for index,(profile,record) in enumerate(zip(cyclic,(work/'eight/arc.out').read_text().splitlines(),strict=True)):
        ordinal,status,_,_=map(int,record.split())
        assert ordinal==index
        if not status:
            surviving.append(profile)
    assert surviving==(work/'eight/views.tsv').read_text().splitlines() and len(surviving)==17898
    complete=(work/'eight/oct.tsv').read_text().splitlines()
    assert len(complete)==len(set(complete))==3391
    pending=complete.copy()
    bound={}
    for stage,prefix,budget in [('stage1','a',500),('stage2','b',25000)]:
        observed=[];next_sources=[]
        for path in sorted((work/'eight'/stage).glob(prefix+'??.in')):
            inputs=path.read_text().splitlines()
            for ordinal,(profile,record) in enumerate(zip(inputs,path.with_suffix('.out').read_text().splitlines(),strict=True)):
                fields=record.split();index,status,nodes=map(int,fields[:3])
                assert ordinal==index and status in (-1,0)
                observed.append(profile)
                if status==-1:
                    assert nodes==budget
                    next_sources.append(profile)
                else:
                    assert nodes<=budget and sum(map(int,fields[4:]))==nodes
                    assert profile not in bound
                    bound[profile]=path.relative_to(work).with_suffix('.out').as_posix(),ordinal
        assert observed==pending
        pending=next_sources
        assert pending==(work/'eight'/stage/'residue.tsv').read_text().splitlines()
    assert not pending and len(bound)==3391
    alternate={}
    for probe in sorted((work/'eight/stage2').glob('b??.in')):
        profile,=probe.read_text().splitlines()
        result=work/'eight/no-library'/probe.with_suffix('.out').name
        fields=result.read_text().split()
        assert fields[:2]==['0','0'] and 0<int(fields[2])<=30000 and sum(map(int,fields[4:]))==int(fields[2])
        alternate[profile]=result.relative_to(work).as_posix()
    assert set(alternate)==set((work/'eight/stage1/residue.tsv').read_text().splitlines())
    views={min(view,reverse(view)) for profile in read_profiles(work/'eight/stage1/residue.tsv') for view in deletions(profile_key(profile))}
    assert sorted(views)==[profile_key(profile) for profile in read_profiles(work/'eight/stage1/views.tsv')] and len(views)==86
    with (work/'eight/terminal.tsv').open('w') as stream:
        print('dihedral_index\tprofile_sha256\tterminal_chunk\tordinal\talternate_without_library',file=stream)
        for index,profile in enumerate(complete):
            print(index,sha256((profile+'\n').encode()).hexdigest(),*bound[profile],alternate.get(profile,'-'),sep='\t',file=stream)
    print('PASS 24962 -> 17898 cyclic deletion views; 3391 complete ten-star reps -> 22 -> 0; 86-view late library used on completed C8 components only')
    print('PASS alternate 22/22 also exhausted without using any residual P7 library')


if __name__=='__main__':
    census(Path('.'))
