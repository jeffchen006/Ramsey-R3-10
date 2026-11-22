from pathlib import Path
import sys
import time
from hex18 import OUT as HEX
from wingreplay23 import OUT,replay


def worker(index):
    parents={int(line.split()[0]):int(line.split()[1]) for line in (HEX/'pids.tsv').read_text().splitlines()};rows=[line.split() for line in (HEX/'manifest.tsv').read_text().splitlines()]
    for owner,key in rows[index::2]:
        while not (OUT/key/'result.json').is_file():
            try:args=Path(f'/proc/{parents[int(owner)]}/cmdline').read_bytes()
            except OSError:args=b''
            if b'wingproof23.py' not in args and b'afterverify23.sh' not in args:break
            time.sleep(2)
        replay(key,300+index)


if __name__=='__main__':worker(int(sys.argv[1]))
