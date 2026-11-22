import hashlib
import math
import os
from pathlib import Path
import re
import resource
import subprocess
import sys


ROOT = Path('../..')
TOOLS = ROOT / 'opt/bin'
BUILD = Path('build')
WORK = Path('work')
KNOWN = WORK / 'e108_r11/critical.g6'
SOURCE = WORK / 'e108_r11_complement'
PROVENANCE = WORK / 'e108_r12_provenance'
SCOUT = Path('../ideas/r009_N')
STITCH = WORK / 'e108_r12/control/stitch'


def cpu():
    return sum(usage.ru_utime + usage.ru_stime for usage in (
        resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)))


def digest(contents):
    return hashlib.sha256(contents).hexdigest()


def lines(contents):
    return set(contents.splitlines(keepends=True))


def normalized(contents):
    return b''.join(sorted(lines(contents)))


class Budget:
    def __init__(self, cap):
        self.start = cpu()
        self.cap = cap

    def spent(self):
        return cpu() - self.start

    def run(self, args, contents=None):
        allowance = math.floor(self.cap - self.spent() - .2)
        if allowance < 1:
            raise RuntimeError(f'spent {self.spent():.3f} CPU-s; no budget for {args}')

        def limit():
            resource.setrlimit(resource.RLIMIT_CPU, (allowance, allowance))

        result = subprocess.run(args, input=contents, capture_output=True, timeout=75,
                                preexec_fn=limit, check=False)
        if result.returncode:
            raise RuntimeError((args, result.returncode, result.stderr))
        if self.spent() >= self.cap:
            raise RuntimeError(f'CPU cap reached: {self.spent():.3f}')
        return result.stdout, result.stderr


def canon(budget, contents):
    stdout, _ = budget.run([TOOLS / 'labelg', '-q'], contents)
    return normalized(stdout)


def validate(budget, out, prefix, contents, order, edges, critical, distinct=True):
    count = len(lines(contents))
    if not count:
        assert not contents
        return
    assert contents == normalized(contents)
    stdout, _ = budget.run([BUILD / 'audit_duals', str(order), str(edges), '9', str(count)], contents)
    print(stdout.decode().strip(), flush=True)
    if critical:
        stdout, _ = budget.run([BUILD / 'irreducible', '9'], contents)
        assert stdout == contents
    if distinct:
        _, stderr = budget.run([TOOLS / 'shortg', '-tu', f'-T{out}'], contents)
        assert re.search(rb'^>Z ' + str(count).encode() + rb' graphs produced$', stderr, re.M), stderr
        (out / f'{prefix}.traces').write_bytes(stderr)


def lift(budget, out, parents, part):
    count = len(parents.splitlines())
    leaves = []
    for degree in (7, 8):
        raw, stderr = budget.run([STITCH, '8', '108', str(degree)], parents)
        stats = (rb'inputs %d d %d roots \d+ anchors \d+ viable \d+ nodes \d+ '
                 rb'legalminimal \d+ critical %d\n') % (count, degree, len(raw.splitlines()))
        assert re.fullmatch(stats, stderr), stderr
        (out / f'{part}.{degree}.raw').write_bytes(raw)
        (out / f'{part}.{degree}.log').write_bytes(stderr)
        leaves.append(raw)
    keys = canon(budget, b''.join(leaves))
    (out / f'{part}.keys').write_bytes(keys)
    return keys, *(len(raw.splitlines()) for raw in leaves)


def archived_binding(out):
    budget = Budget(6)
    archive = (SCOUT / 'audit.deck.g6').read_bytes()
    assert archive == (SCOUT / 'new31.deck').read_bytes()
    assert len(archive.splitlines()) == 843
    assert digest(archive) == 'da50bd80a490eb0dbdf89aff54352e156df180604a6ebcaddfc8b565ebc0c82a'
    picked, _ = budget.run([TOOLS / 'pickg', '-qe98'], archive)
    bound = canon(budget, picked)
    assert len(bound.splitlines()) == 200
    assert bound == (PROVENANCE / 'deck.overlap').read_bytes()
    validate(budget, out, 'archived', bound, 31, 98, True)
    archive_log = (SCOUT / 'audit.final.replay').read_bytes()
    summary = [f'archive\t{digest(archive)}\n', f'log\t{digest(archive_log)}\n']
    for degree, processed in ((7, 843), (8, 806)):
        raw = (SCOUT / f'audit.lateral.{degree}.raw').read_bytes()
        count = len(raw.splitlines())
        assert re.search(rb'^inputs %d d %d .* critical %d$' % (processed, degree, count), archive_log, re.M)
        keys = canon(budget, raw)
        assert keys == (SCOUT / f'frontier.{degree}.set').read_bytes()
        summary.append(f'd{degree}\t{count}\t{digest(raw)}\t{digest(keys)}\n')
    (out / 'archived.sources.tsv').write_text(''.join(summary))
    (out / 'archived.e98.g6').write_bytes(bound)
    print(f'Archived N deck: 200/745 exact e98 keys bound to the earlier two-arm run; '
          f'no fresh lifting on these keys ({budget.spent():.3f} CPU-s).', flush=True)
    return lines(bound)


def calibration(out):
    budget = Budget(12)
    parents = (SCOUT / 'cal15deck.g6').read_bytes()
    stdout = b''
    for degree in range(1, 7):
        raw, _ = budget.run([STITCH, '6', '22', str(degree)], parents)
        stdout += raw
    keys = canon(budget, stdout)
    assert keys == canon(budget, (SCOUT / 'cal16.ref').read_bytes())
    assert len(keys.splitlines()) == 42
    (out / 'control.keys').write_bytes(keys)
    print(f'Calibration: all 42 known critical order-16/e22 classes ({budget.spent():.3f} CPU-s).', flush=True)


def complement(out):
    calibration(out)
    bound = archived_binding(out)
    budget = Budget(40)
    roster = (PROVENANCE / 'not_deck_bound.g6').read_bytes()
    fresh = lines(roster)
    assert len(fresh) == 545 and not fresh & bound
    assert fresh | bound == lines((SOURCE / 'deck.conservative_only').read_bytes())
    for path in (SOURCE / 'deck.known_r10r11', SOURCE / 'total.98.fresh'):
        assert not (fresh | bound) & lines(path.read_bytes())
    validate(budget, out, 'roster', roster, 31, 98, True)
    known = lines(KNOWN.read_bytes())
    assert len(known) == 1875
    produced, tested = set(), set()
    roster_rows = roster.splitlines(keepends=True)
    header = 'shard\tparents\tparent_sha256\td7_raw\td8_raw\tkeys\tkey_sha256\tcpu_s\n'
    with (out / 'done.tsv').open('w') as receipts:
        receipts.write(header)
        for start in range(0, len(roster_rows), 96):
            before = budget.spent()
            shard = f'part{start // 96:02d}'
            parents = b''.join(roster_rows[start:start + 96])
            (out / f'{shard}.parents').write_bytes(parents)
            keys, count7, count8 = lift(budget, out, parents, shard)
            tested.update(lines(parents))
            produced.update(lines(keys))
            fields = (shard, len(lines(parents)), digest(parents), count7, count8,
                      len(lines(keys)), digest(keys), f'{budget.spent() - before:.3f}')
            receipt = '\t'.join(map(str, fields))
            receipts.write(receipt + '\n')
            receipts.flush()
            print(receipt, flush=True)
            novel_count = len(produced - known)
            assert novel_count <= 5
            if novel_count == 5:
                break
    novel = produced - known
    assert tested == fresh or len(novel) == 5
    result = b''.join(sorted(produced))
    validate(budget, out, 'produced', result, 32, 108, True)
    validate(budget, out, 'novelty', b''.join(sorted(known | produced)), 32, 108, False)
    for name, keys in (('tested', tested), ('remaining', fresh - tested), ('novel', novel), ('produced', produced)):
        (out / f'{name}.g6').write_bytes(b''.join(sorted(keys)))
    print(f'PASS complement: tested={len(tested)} distinct={len(produced)} novel={len(novel)} '
          f'lift+audit={budget.spent():.3f} CPU-s', flush=True)


if __name__ == '__main__':
    os.environ.update(LC_ALL='C', PYTHONDONTWRITEBYTECODE='1')
    resource.setrlimit(resource.RLIMIT_AS, (16 << 30, 16 << 30))
    destination = Path(sys.argv[1])
    destination.mkdir()
    os.environ['TMPDIR'] = str(destination.resolve())
    complement(destination)
