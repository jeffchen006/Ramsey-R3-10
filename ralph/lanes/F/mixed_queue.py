"""Bind the score-24 shortfall and held-out pilot indices to their exact quotient strings."""

from pathlib import Path


def queue(write=False):
    lines=lambda name:Path(name).read_text().splitlines()
    target=lines('target.q');old=lines('../r8/target.q');forced=lines('target.forced');assert len(target)==len(forced)
    chosen=[]
    for index,line in enumerate(forced):
        row,lower,_=map(int,line.split());assert row==index
        if lower<25:chosen.append((f'new {index}',target[index]))
    previous=sorted({int(line.split()[2]) for line in lines('target.maps') if line.split()[1]=='old'});chosen.extend((f'old {index}',old[index]) for index in previous)
    for tag,source in [('short',chosen),('oddpilot',chosen[5::17])]:
        for ext,content in [('ids',[pair[0] for pair in source]),('q',[pair[1] for pair in source])]:
            if write: Path(f'{tag}.{ext}').write_text('\n'.join(content)+'\n')
            else:assert lines(f'{tag}.{ext}')==content
    print('shortfall new',len(chosen)-len(previous),'previous',len(previous),'pilot',len(chosen[5::17]))


if __name__=='__main__':import sys;queue('--write' in sys.argv)
