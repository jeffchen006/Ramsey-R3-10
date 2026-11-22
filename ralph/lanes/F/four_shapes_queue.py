from pathlib import Path
import subprocess,sys
import four_shapes as shapes
import six_five_queue as queue
from six_branch import graph,decode
from six_five import encode

def index(tag):
    result=[]
    for line in Path(tag+'.rows').read_text().splitlines():
        key,*fields=line.split();status='model' if 'model' in fields else 'maskcap' if fields==['maskcap'] else 'cap' if any(field.startswith('cap:') for field in fields) else 'no4';assert status!='no4' or len(fields)==3 and all(field.startswith('empty:') for field in fields);result.append(f'{key} {status}')
    Path(tag+'.results').write_text(''.join(line+'\n' for line in result))
def scan(keys,tag):
    shapes.execute([encode(key,graph(decode(key)),10,True) for key in keys],tag);index(tag)
if __name__=='__main__':
    queue.sample=scan
    if sys.argv[1]=='price':index('fixed');index('price')
    elif sys.argv[1]=='audit':queue.audit()
    else:queue.worker(int(sys.argv[1]))
