"""Physical calibration of the single-pole shadow used by the final CNF."""
from collections import Counter
from itertools import combinations,product
from orbit_extend import vertices,independent_sets


def extend(graph,contacts,shadow):
    extra=len(graph);result=graph.copy()+[contacts]
    for site in vertices(contacts):result[site]|=1<<extra
    if shadow:
        opposite=sum(1<<(site^1) for site in vertices(contacts));result.append(opposite|(1<<extra));result[extra]|=1<<(extra+1)
        for site in vertices(opposite):result[site]|=1<<(extra+1)
    return result


def check():
    order=[1,5,2,6,3,7,0,4];ladder=[sum(1<<index for index,dest in enumerate(order) if (dest-site)%8 in (1,4,7)) for site in order];base=[mask&63 for mask in ladder[:6]]
    correct=ladder[6]&63;assert extend(base,correct,True)==ladder;totals=Counter()
    for word in product((0,1,2),repeat=3):
        mask=sum(1<<(2*index+value-1) for index,value in enumerate(word) if value);signatures=[]
        for shadow in (False,True):
            graph=extend(base,mask,shadow);triangle=any(graph[left]&graph[right] for left,right in combinations(range(len(graph)),2) if graph[left]>>right&1);bad=next(independent_sets(graph,(1<<len(graph))-1,4),None) is not None
            signatures.append((triangle,bad))
        assert signatures[0]==signatures[1];totals[signatures[0]]+=1
        if mask==correct:assert signatures[0]==(False,False)
        if not mask:assert signatures[0]==(False,True)
    print('all 27 three-site columns on the C8(1,4) deletion: original/shadow triangle and I4 statuses agree',sorted(totals.items()))


if __name__=='__main__':check()
