# Compare multisets of numbers in paper/draft.md and paper/latex/*.tex (critic, LaTeX sign-off).
# usage: python3 numdiff.py draft.md tex_dir
import re, sys, glob, collections
def norm(t):
    t = re.sub(r'\\(,|;|!|\s)', '', t)               # LaTeX thin spaces
    t = re.sub(r'\{,\}', ',', t)
    t = t.replace('\\times10^{', 'e').replace('\\times 10^{', 'e')
    t = re.sub(r'\\cdot\s*10\^\{?(-?\d+)\}?', r'e\1', t)
    t = re.sub(r'(?<![\d.])10\^\{?(-?\d+)\}?', r'1e\1', t)
    return t
num = re.compile(r'\d[\d,]*(?:\.\d+)?(?:e[+-]?\d+)?')
def nums(t):
    out = []
    for m in num.findall(norm(t)):
        m = m.rstrip(',').replace(',', '')
        if m: out.append(m)
    return collections.Counter(out)
md = nums(open(sys.argv[1]).read())
tx = nums(''.join(open(f).read() for f in sorted(glob.glob(sys.argv[2] + '/**/*.tex', recursive=True))))
lost = md - tx; new = tx - md
print('numbers in md not in tex:', sorted(lost.items())[:200])
print('numbers in tex not in md:', sorted(new.items())[:200])
