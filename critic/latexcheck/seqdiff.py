# per-section diff of number sequences, draft.md vs latex/secN.tex (critic)
import re, sys, difflib
sys.path.insert(0, 'critic/latexcheck')
num = re.compile(r'\d[\d,]*(?:\.\d+)?(?:e[+-]?\d+)?')
def norm(t, tex):
    if tex:
        t = re.sub(r'(?<!\\)%.*', '', t)
        t = re.sub(r'\\begin\{tabular\}\{[^\n]*?\}\s*$', '', t, flags=re.M)
        t = re.sub(r'p\{[\d.]+cm\}', '', t)
        t = re.sub(r'\\(ref|label|cite|eqref)\{[^}]*\}', '', t)
        t = re.sub(r'\\(,|;|!)', ' ', t); t = t.replace('{,}', ',')
        t = re.sub(r'\\cdot\s*10\^\{?(-?\d+)\}?', r'e\1', t)
        t = re.sub(r'(?<![\d.])10\^\{?(-?\d+)\}?', r'1e\1', t)
    return t
def seq(t):
    return [m.rstrip(',').replace(',', '') for m in num.findall(t)]
md = open('paper/draft.md').read()
for s in range(1, 10):
    m = re.search(r'SEC %d BEGIN.*?SEC %d END' % (s, s), md, re.S).group(0)
    a = seq(norm(m, False)); b = seq(norm(open('paper/latex/sec%d.tex' % s).read(), True))
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op != 'equal':
            print(s, op, a[i1:i2][:12], '->', b[j1:j2][:12], '| md ctx:', ' '.join(a[max(0,i1-4):i1]))
