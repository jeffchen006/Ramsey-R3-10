"""Rebuild the conventional certificate in an empty scratch directory from frozen masks only."""
from pathlib import Path
import sys

from cyclic_check import check
from cyclic_proof import proof
from id8_frozen import direct,frozen,rebind,labels
from id8_merge import merge,checks
from id8_saturation import target
from id8_saturation_check import geometry,cyclelaw,audit
from relift_audit import encode
from orbit_extend import ROOT


def rebuild(mode):
    assert (ROOT/'scratch/F') in Path.cwd().parents and not Path('bank').exists() and mode in ('pilot','strong')
    lines=sorted(tuple(map(int,line.split())) for line in frozen().read_text().splitlines());assert len(lines)==1406
    if mode=='strong':lines=sorted(lines+[tuple(map(int,line.split())) for line in frozen(True).read_text().splitlines()]);assert len(lines)==2623
    labels([row[0] for row in lines],8 if mode=='strong' else 7)
    if mode=='pilot':lines=lines[::109]
    target();cyclelaw();audit(*geometry());Path('bank').mkdir();arms=[Path('no_blind_pole')]
    for foot,*masks in lines:
        formula=direct(foot,masks);stem=Path('bank')/f'f{foot}';formula.serialize(stem);assert proof(stem)=='dual' and check(encode(formula.base),10,stem)==len(masks);arms.append(stem)
    stem=Path('id8_'+mode);merge(arms,stem);checks(stem);rebind(mode)


if __name__=='__main__':rebuild(sys.argv[1])
