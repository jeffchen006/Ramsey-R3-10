from collections import Counter
from pathlib import Path
import tempfile

from round18_middle import (ROOT, audit, census, check, load, make_plan, paths, physical,
                            read_jsonl, sha, unpack)


ARCHIVE = ROOT / 'scratch/G/round18'


def review():
    audit()
    make_plan()
    for name in ('orbits.json', 'sample.json'):
        assert Path(name).read_bytes() == (ARCHIVE / name).read_bytes()
    roster = load('orbits.json')
    plan = load('sample.json')
    groups, _, stabilizers, orbits, _, _ = census()
    sample = set(map(int, plan['selected']))
    target = {int(rank): ['inherited', source, action]
              for rank, (source, action, _) in roster['prior'].items()}
    checked = set()
    weights = Counter()
    block_images = 0
    production = sorted((ARCHIVE / 'production').glob('*'))
    assert len(production) == 13
    for directory in [ARCHIVE / 'sample', *production]:
        is_sample = directory.name == 'sample'
        archive_paths = set(directory.glob('*.z'))
        for record, replay in zip(read_jsonl(directory / 'make.jsonl'),
                                  read_jsonl(directory / 'replay.jsonl'), strict=True):
            rep = record['rank']
            assert rep not in checked and rep in orbits and (rep in sample) == is_sample
            assert replay['rank'] == rep and replay['digest'] == record['digest']
            archive_path = paths(directory, rep)
            archive_paths.remove(archive_path)
            with tempfile.TemporaryDirectory(dir=Path.cwd()) as work:
                work_path = Path(work)
                unpack(archive_path, work_path, record)
                witness = check(work_path, groups[rep])
                orbit = orbits[rep]
                assert orbit == roster['new'][str(rep)]
                weights[len(orbit)] += 1
                for member, action in orbit.items():
                    rank = int(member)
                    assert rank not in target and action in stabilizers
                    physical(groups[rep], groups[rank], action, witness)
                    target[rank] = [rep, str(archive_path.relative_to(ARCHIVE)), action]
                    block_images += len(witness['blocks'])
            checked.add(rep)
        assert not archive_paths
        print('reviewed', directory.name, 'cumulative new orbits', len(checked), flush=True)
    assert checked == set(map(int, roster['new'])) and set(target) == set(range(len(groups)))
    reconciliation = load(ARCHIVE / 'reconciliation.json')
    assert reconciliation['checked'] == {str(rank): owner for rank, owner in target.items()}
    assert not any(reconciliation[key] for key in ('open_ids', 'open_reps', 'staged_only'))
    print('clean replay PASS', len(groups), dict(weights), 'explicit block images', block_images,
          'ledger SHA256', sha((ARCHIVE / 'reconciliation.json').read_bytes()), flush=True)


if __name__ == '__main__':
    review()
