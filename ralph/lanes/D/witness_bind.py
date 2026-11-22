"""Bind a bounded stage to its source, preserving every cutoff and its original order."""

from hashlib import sha256
from pathlib import Path
import sys


def bind(source, folder, name='p'):
    original=source.read_bytes().splitlines();all_inputs=[];open_rows=[];receipts=[];cpu=0;nodes=0
    for shard in sorted(folder.glob(name+'[0-9][0-9]')):
        inputs=shard.read_bytes().splitlines();outputs=shard.with_suffix('.out').read_bytes().splitlines()
        for idx,(row,result) in enumerate(zip(inputs,outputs,strict=True)):
            number,status,visited,elapsed=result.split();assert int(number)==idx and status in (b'0',b'-1')
            all_inputs.append(row);cpu+=float(elapsed);nodes+=int(visited)
            if status==b'-1':open_rows.append(row)
            receipts.append(b'\t'.join((str(len(all_inputs)-1).encode(),shard.name.encode(),sha256(row).hexdigest().encode(),number,status,visited,elapsed)))
    assert all_inputs==original
    (folder/'live.tsv').write_bytes(b''.join(text+b'\n' for text in open_rows));(folder/'receipt.tsv').write_bytes(b'\n'.join(receipts)+b'\n')
    print(folder,'rows',len(original),'terminal',len(original)-len(open_rows),'open',len(open_rows),'nodes',nodes,'CPU-s',round(cpu,4))


if __name__=='__main__':bind(Path(sys.argv[1]),Path(sys.argv[2]))
