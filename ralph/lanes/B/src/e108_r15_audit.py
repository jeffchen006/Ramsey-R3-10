"""Stream-check the ordered e108 disposition transcript without using the producer."""

from collections import Counter
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import sys


def read_cliques(handle):
    for line in handle:
        first, *masks = line.split()
        assert len(masks) == 8
        yield int(first)


def read_proofs(handle):
    for line in handle:
        fields = line.split()
        assert len(fields) in {6, 12, 13}
        yield int(fields[0])


def read_adopted(handle):
    for line in handle:
        rank, tag, local = line.split()
        assert int(local) > 0 and tag in {'C6', 'C14', 'P6', 'P14'}
        yield int(rank), tag


def expected(shard, source_rank):
    if not shard['done']:
        return shard['open']
    shard['local'] += 1
    local = shard['local']
    clique, proof = shard['next_clique'], shard['next_proof']
    assert clique is None or local <= clique
    assert proof is None or source_rank <= proof
    if clique == local:
        assert proof != source_rank
        shard['next_clique'] = next(shard['cliques'], None)
        return 'C15'
    assert proof == source_rank
    shard['next_proof'] = next(shard['proofs'], None)
    return 'P15'


def audit(base, require_full):
    assert __debug__
    with ExitStack() as stack:
        shards = []
        for ordinal in range(257):
            directory = base / f's{ordinal:03}'
            if not (directory / 'done.json').exists():
                shards.append({'done': False, 'open': 'incomplete' if directory.exists() else 'unstarted'})
                continue
            cliques = read_cliques(stack.enter_context((directory / 'cliques.tsv').open()))
            proofs = read_proofs(stack.enter_context((directory / 'proofs.tsv').open()))
            shards.append({'done': True, 'local': 0, 'cliques': cliques, 'proofs': proofs,
                           'next_clique': next(cliques, None), 'next_proof': next(proofs, None),
                           'keys': json.loads((directory / 'done.json').read_text())['keys']})
        adopted = read_adopted(stack.enter_context((base / 'adopted.tsv').open()))
        next_old = next(adopted, None)
        gaps = iter(stack.enter_context((base / 'unchecked-ranks.txt').open()))
        next_gap = next(gaps, None)
        ordinal, tally = 0, Counter()
        accumulator = hashlib.sha256()
        with (base / 'rank-dispositions.tsv').open('rb') as transcript:
            for rank, line in enumerate(transcript, 1):
                accumulator.update(line)
                source, tag = line.decode().split()
                assert int(source) == rank
                if next_old is not None and rank == next_old[0]:
                    assert tag == next_old[1], (rank, tag, next_old)
                    next_old = next(adopted, None)
                else:
                    assert next_old is None or rank < next_old[0]
                    want = expected(shards[ordinal % 257], rank)
                    assert tag == want, (rank, tag, want)
                    ordinal += 1
                if tag in {'incomplete', 'unstarted'}:
                    assert next_gap is not None and int(next_gap) == rank
                    next_gap = next(gaps, None)
                tally[tag] += 1
        assert rank == 2_102_271 and ordinal == 2_065_471 and next_old is None and next_gap is None
        for shard in shards:
            if shard['done']:
                assert shard['local'] == shard['keys']
                assert shard['next_clique'] is None and shard['next_proof'] is None
        summary = json.loads((base / 'summary.json').read_text())
        assert summary['counts'] == tally and summary['ordered_sha256'] == accumulator.hexdigest()
        if require_full:
            assert not tally['incomplete'] and not tally['unstarted']
        print(f'PASS ordinal/coverage audit; {rank} ranks; {dict(sorted(tally.items()))}; {accumulator.hexdigest()}')


if __name__ == '__main__':
    assert len(sys.argv) in {2, 3} and (len(sys.argv) == 2 or sys.argv[2] == '--full')
    audit(Path(sys.argv[1]), len(sys.argv) == 3)
