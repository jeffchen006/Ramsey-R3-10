"""efilt.py EMIN EMAX < in.g6 > out.g6 : keep graph6 lines with EMIN <= edges <= EMAX."""
import sys
lo, hi = int(sys.argv[1]), int(sys.argv[2])
for l in sys.stdin:
    s = l.strip()
    if not s:
        continue
    b = sum(bin(ord(c) - 63).count('1') for c in s[1:])
    if lo <= b <= hi:
        sys.stdout.write(s + '\n')
