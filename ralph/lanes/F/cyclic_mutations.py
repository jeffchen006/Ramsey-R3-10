"""Negative controls for the independent source, trace and proof checker."""

from pathlib import Path

from cyclic_check import check, source_check


def rejects(name, action):
    try:
        action()
    except AssertionError:
        print('REJECT', name)
    else:
        raise RuntimeError('mutation was accepted: ' + name)


def main():
    inputs = Path('target.q').read_text().splitlines()
    rejects('missing unit orbit', lambda: source_check(inputs[:-1]))
    rejects('duplicate replacing final orbit', lambda: source_check(inputs[:-1] + inputs[:1]))
    small = Path('small.q').read_text().splitlines()[7]
    stem, original = Path('mutated'), Path('smallproof2/007')
    for extension in ('.trace', '.cnf', '.lrat'):
        stem.with_suffix(extension).write_bytes(original.with_suffix(extension).read_bytes())
    trace = original.with_suffix('.trace').read_text()
    for name, old, new in [('insufficient cycle rank', 'cut 0 15 8 10 12', 'cut 0 15 8 10'),
                           ('noncycle variable', 'cut 0 15 8 10 12', 'cut 0 15 8 10 1'),
                           ('cyclic gauge pins', 'forest 3\n', 'forest 3\nforest 4\n')]:
        assert old in trace
        stem.with_suffix('.trace').write_text(trace.replace(old, new))
        rejects(name, lambda: check(small, 4, stem))
    stem.with_suffix('.trace').write_text(trace)
    cnf = original.with_suffix('.cnf').read_text()
    assert cnf.endswith('8 10 12 0\n')
    stem.with_suffix('.cnf').write_text(cnf.replace('8 10 12 0\n', '-8 10 12 0\n'))
    rejects('flipped CNF cut literal', lambda: check(small, 4, stem))
    stem.with_suffix('.cnf').write_text(cnf)
    stem.with_suffix('.lrat').write_bytes(Path('smallproof2/000.lrat').read_bytes())
    rejects('crossed LRAT', lambda: check(small, 4, stem))


if __name__ == '__main__':
    main()
