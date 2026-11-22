from collections import Counter
from itertools import combinations
from pathlib import Path
from eight_chart import get,ED,free,forest
from six_sieve import events
from six_audit import rank

def main():
    units=[get(1<<index) for index in range(30)];columns=[sum(1<<index for index,adj in enumerate(units) if adj[2*left]>>(2*right)&1) for left,right in ED];assert rank(columns)==30 and not any(columns[index] for index in forest)
    matrix=dict(zip(ED,columns));assert set(matrix)=={key for key in combinations(range(16),2) if 6<=key[1]-key[0]<=12}
    forms=events(ED,16,10,columns);ordered=sorted(forms.items(),key=lambda item:(len(item[0]),item[1]));Path('columns.tsv').write_text(''.join(f'{left} {right} {expr}\n' for (left,right),expr in matrix.items()));Path('bank.tsv').write_text(''.join(' '.join(map(str,(mask,len(rows),*rows)))+'\n' for rows,mask in ordered))
    for rows,mask in ordered[:768]:
        sites={vertex for vertex in range(16) if mask>>vertex&1};assert len(sites)==10;labels={};cycles=[]
        for vertex in sorted(sites):
            if vertex in labels:continue
            labels[vertex]=0;stack=[vertex]
            while stack:
                left=stack.pop()
                for right in sites:
                    pair=tuple(sorted((left,right)))
                    if pair not in matrix:continue
                    if right in labels:cycles.append(labels[left]^labels[right]^matrix[pair]);continue
                    labels[right]=labels[left]^matrix[pair];stack.append(right)
        assert rank(list(rows)+cycles)==rank(cycles)==len(rows)==rank(rows)<=8
    print('49 physical matching columns, rank 30; 768 active support tests all independently rebound by endpoint transport. All distinct support row-space ranks:',sorted(Counter(map(len,forms)).items()))
if __name__=='__main__':main()
