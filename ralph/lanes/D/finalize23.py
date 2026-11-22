from pathlib import Path
import time
from index23 import NEW,snapshot


def complete(report):
    return sum(value for key,value in report['key_counts'].items() if key.endswith(':root_cert') or key.endswith(':prefix_cert'))==8233


if __name__=='__main__':
    while not complete(snapshot()):time.sleep(22)
    destination=NEW/'final23';result=snapshot(destination,True);assert complete(result) and len((destination/'open.tsv').read_text().splitlines())==1
