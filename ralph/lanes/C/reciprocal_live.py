import argparse
from collections import Counter
from pathlib import Path

from reciprocal_audit import SOURCE22, code_window, decode, host_masks, vertices
from reciprocal_census_proofs import HEADER
from reciprocal_proof_r11 import formula as standard, proof
from reciprocal_row_support import formula as support


def run(dense):
    left = [host_masks(decode(row)) for row in SOURCE22.read_text().splitlines()]
    right = {}
    output = Path('live-proofs-dense' if dense else 'live-proofs')
    output.mkdir(exist_ok=True)
    counts = Counter()
    with (output/'receipts.tsv').open('w') as receipts, (output/'unclosed.tsv').open('w') as unclosed:
        print(HEADER,file=receipts)
        for index,row in enumerate(Path('live.tsv').read_text().splitlines()):
            filename,raw = row.split(':',1)
            folder = Path(filename).parent
            start,end = map(int,folder.name.split('-'))
            if folder not in right:
                right[folder] = [host_masks(decode(row)) for row in (folder/'hosts.g6').read_text().splitlines()]
                assert len(right[folder]) == end-start
            *fields,reason,witness = raw.split()
            key = tuple(map(int,fields))
            assert (reason,witness) == ('live','0') and start <= key[5] < end
            tag = f'live-{index:03d}'
            try:
                terminal = proof(tag,key,9,left[key[0]],right[folder][key[5]-start],3,False,output,False,
                                 build=standard if dense else support)
            except AssertionError as error:
                if error.args and isinstance(error.args[0],tuple) and error.args[0][0] == 'completion candidate for independent checking':
                    proposed = error.args[0][1]
                    assert len(proposed) == 40 and all(mask.bit_count() == 9 for mask in proposed)
                    assert all(not (proposed[src] & proposed[dst]) for src,mask in enumerate(proposed) for dst in vertices(mask))
                    record = code_window([set(vertices(mask)) for mask in proposed],list(range(40)))
                    (output/f'{tag}.g6').write_text(record+'\n')
                    counts['candidate-to-check'] += 1
                else:
                    counts['assert-failed'] += 1
                print(tag,row,repr(error),sep='\t',file=unclosed,flush=True)
                continue
            print(*terminal,sep='\t',file=receipts,flush=True)
            counts[terminal[1]] += 1
    print(dict(counts))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dense',action='store_true')
    run(parser.parse_args().dense)
