"""Exercise bound chunks end to end, then change graph order as a negative control."""

from pathlib import Path

from audit_chunks import audit
from seed import preprocess, worker


source = Path('val/r3_6_17.g6')
directory = Path('work/round4_chunk_bind')
directory.mkdir(exist_ok=True)
flags = ['build/gluecheap', '-k', '6', '-d', '4', '-m', '4', '-M', '6', '-E', '63', '-e', '63']
for job in preprocess(directory, [(4, source, flags)], 3):
    worker(job)
with source.open('rb') as stream:
    audit(directory, 4, 7, 3, stream)
lines = source.read_bytes().splitlines(keepends=True)
assert len(lines) == 7 and lines[2] != lines[3]
lines[2], lines[3] = lines[3], lines[2]
corruption = directory / 'wrong_order.g6'
corruption.write_bytes(b''.join(lines))
with corruption.open('rb') as stream:
    try:
        audit(directory, 4, 7, 3, stream)
    except ValueError as error:
        if 'ordered input hash differs' not in str(error):
            raise
        print(f'expected rejection of permuted inputs: {error}')
    else:
        raise ValueError('accepted permuted inputs')
