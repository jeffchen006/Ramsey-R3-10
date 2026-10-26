#!/bin/bash
# Differential test: lean sbcheck vs cert/check_sb.py on single-clause files.
dir=$1; agree=0; dis=0; nvalid=0
for f in $dir/*.sb; do
  h=$(head -1 $f); pos=$(echo $h | sed 's/.*positions=\([a-z]*\).*/\1/'); bet=$(echo $h | sed 's/.*better=\([a-z]*\).*/\1/'); var=$(echo $h | sed 's/.*vars=\([a-z]*\).*/\1/')
  nn=$(echo $h | grep -o 'n=[0-9]*' | cut -d= -f2); nn=${nn:-40}
  py=$(python3 cert/check_sb.py --n $nn --order $var --better $bet --positions $pos $f | grep -c "RESULT: OK")
  le=$(lean/.lake/build/bin/sbcheck $f | grep -c "s VERIFIED")
  if [ "$py" = "$le" ]; then agree=$((agree+1)); else dis=$((dis+1)); echo "DISAGREE $f py=$py lean=$le"; fi
  nvalid=$((nvalid+le))
done
echo "agree=$agree disagree=$dis lean_valid=$nvalid"
