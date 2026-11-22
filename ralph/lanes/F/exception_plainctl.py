from itertools import combinations
from pathlib import Path
import json
import subprocess
import sys
from one_double_pilot import graph_build,tri_free,ROOT,to_graph6

def go():
    groups=list(combinations(range(7),4))
    for matched in (0,1):
        edges=[(0,1)] if matched else []
        for left in range(3):
            for right in range(3):
                for verticals in range(4):
                    core=graph_build(2,edges,0,verticals,(left,right));assert len(core)==6
                    for other in range(16):
                        contact=48|other;graph=[row|((contact>>site&1)<<6) for site,row in enumerate(core)]+[contact]
                        if not tri_free(graph) or any(all(not(graph[a]>>b&1) for a,b in combinations(group,2)) for group in groups):continue
                        Path('plain-pole.g6').write_text(to_graph6(graph)+'\n');graph[4]|=1<<5;graph[5]|=1<<4;assert not tri_free(graph)
                        run=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check','plain-pole.g6','7','4'],capture_output=True,text=True,check=True);assert json.loads(run.stdout)['graphs'][0]['ok'];Path('plain-pole.gate').write_text(run.stdout)
                        print('marked crossing masks',left,right,'old edge',matched,'verticals',verticals,'outside',contact,'actual pole sees both; adding marked vertical makes triangle');return
    raise AssertionError('no small planted vertical counterexample')

if __name__=='__main__':go()
