import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path
from high24 import HIGH,OUT
from book_controls import graph_masks,sites,bitset

def witnesses(edge):
    roster=json.loads((HIGH/f'spec{edge}.json').read_text());byid={row['number']:row for row in roster};records=(HIGH/f'rowcuts{edge}.tsv').read_text().splitlines();graphlines=(HIGH/f'raw{edge}.g6').read_text().splitlines();tests=[];cuts={}
    for line in records:
        key,site=line.split();site=int(site);prefix,number,idx=key.split('_');assert prefix==f'h{edge}';number=int(number);idx=int(idx);row=byid[number];assert row['g6']==graphlines[number-1];wing=graph_masks(graphlines[number-1]);marked=row['points'];words=row['decks'][idx];assert site not in marked
        stars=[set(sites(word)) for word in wing]+[set(range(8))|{18},set(range(8,16))|{18},{16,17}];
        for pos in range(16):stars[pos].add(16+int(pos>=8))
        for offset,mark in enumerate(marked):stars[mark].update(19+index for index,mask in enumerate(words) if mask&(1<<offset))
        debit=sum(max(0,2-len(stars[left]&stars[right])) for left,right in combinations(marked,2) if right not in stars[left]);assert debit in (0,1);needed=9-len(stars[site]);entry=[21,len(marked),needed,debit,*[bitset(point-19 for point in stars[mark] if point>=19) for mark in marked],*[-1 if site in stars[mark] else len(stars[site]&stars[mark]) for mark in marked]];tests.append(' '.join(map(str,[key,*entry])));cuts[key]=site
    answer=subprocess.run([OUT/'rowcut'],input='\n'.join(tests)+'\n',text=True,capture_output=True,check=True);results={key:int(flag) for key,flag,mask in map(str.split,answer.stdout.splitlines())};assert results.keys()==cuts.keys() and not any(results.values());print(edge,len(results),'independent star-book rebinds, exhaustively negative',flush=True)

if __name__=='__main__':
    for edge in map(int,sys.argv[1:]):witnesses(edge)
