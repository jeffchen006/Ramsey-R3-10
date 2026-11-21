"""ecount.py FILE SPEC : exact per-edge-level counts of FILE must equal SPEC ("e:count,e:count,...").
Levels not in SPEC must be empty. Prints the counts; exit 0 if equal, 1 if not."""
import sys
from collections import Counter
f, spec = sys.argv[1], sys.argv[2]
want = {int(a): int(b) for a, b in (p.split(':') for p in spec.split(','))}
got = Counter()
for l in open(f):
    s = l.strip()
    if s:
        got[sum(bin(ord(c) - 63).count('1') for c in s[1:])] += 1
ok = dict(got) == want
print(f'{f}: got {dict(sorted(got.items()))} want {dict(sorted(want.items()))} -> {"OK" if ok else "MISMATCH"}')
sys.exit(0 if ok else 1)
