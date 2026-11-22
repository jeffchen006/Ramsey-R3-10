import json,sys
from wing_population import DEST,separate


if __name__=='__main__':
    typ,part,mod=map(int,sys.argv[1:4]);done=0
    with (DEST/'wing8.g6').open() as graphs,(DEST/'half-joined.tsv').open() as joins:
        for line,receipt in zip(graphs,joins,strict=True):
            row=receipt.split()
            if row[1]!='live' or not (int(row[4])>>typ&1):continue
            done+=1
            if (done-1)%mod==part:print(json.dumps(separate(int(row[0]),line.strip(),'basic'),separators=(',',':')),flush=True)
