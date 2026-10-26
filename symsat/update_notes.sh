#!/bin/bash
# regenerate the n=40 case table in notes/symsat.md (between TABLE_N40 markers)
cd .
awk '{print $1, $2, $3}' runs/symsat/certs.log > runs/symsat/certs_status.txt
cat runs/symsat/n40_satcore.jsonl runs/symsat/n40_p2low.jsonl 2>/dev/null > runs/symsat/n40_all.jsonl
python3 symsat/table.py runs/symsat/n40_all.jsonl runs/symsat/certs_status.txt > runs/symsat/n40_table.md
python3 - <<'PY'
s = open('notes/symsat.md').read()
t = open('runs/symsat/n40_table.md').read()
a = s.find('<!-- TABLE_N40 -->'); b = s.find('<!-- /TABLE_N40 -->')
block = '<!-- TABLE_N40 -->\n' + t + '<!-- /TABLE_N40 -->'
if a >= 0:
    s = s[:a] + block + s[b + len('<!-- /TABLE_N40 -->'):]
else:
    s = s.replace('TABLE_N40', block, 1)
open('notes/symsat.md', 'w').write(s)
PY
