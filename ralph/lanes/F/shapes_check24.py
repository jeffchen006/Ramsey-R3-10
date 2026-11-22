from itertools import combinations,permutations
from pathlib import Path
import json,subprocess
from source24 import DIR,ROOT,parse_graph6,cycle,subgraph,independent_sets
from orbit_extend import to_graph6

def canon(graphs):
    rows=subprocess.run(['timeout','20',ROOT/'opt/bin/labelg','-q'],input=''.join(to_graph6(adj)+'\n' for adj in graphs),text=True,capture_output=True,check=True).stdout.splitlines();assert len(rows)==len(graphs);return set(rows)
def has4or5(adj):
    four=next(independent_sets(adj,(1<<len(adj))-1,4),None) is not None
    five=any(all(row.bit_count()==2 for row in subgraph(adj,group)) for group in combinations(range(len(adj)),5));return four or five
def main():
    patterns={int(key):value for key,value in json.loads((DIR/'patterns.json').read_text()).items()};forms=[]
    for code in range(512):
        if not any(all(code>>(3*idx+mate)&1 for idx,mate in enumerate(ordering)) for ordering in permutations(range(3))):continue
        graph=[0]*6
        for left in range(3):
            for right in range(3):
                if code>>(3*left+right)&1:graph[left]|=1<<(right+3);graph[right+3]|=1<<left
        assert not has4or5(graph);forms.append(graph)
    assert canon(forms)==canon([value for key,value in patterns.items() if key!=700]);seven=[parse_graph6(row) for row in subprocess.run(['timeout','20',ROOT/'opt/bin/geng','-q','-t','7'],capture_output=True,text=True,check=True).stdout.splitlines()];others=[graph for graph in seven if not has4or5(graph)];assert len(others)==1 and canon(others)==canon([cycle(7)]);print('seven:',len(seven),'unlabeled triangle-free, unique exception C7. Six:',len(forms),'labeled 3-by-3 with perfect matching, exactly',len(patterns)-1,'distinct residual shapes, independent match.')
if __name__=='__main__':main()
