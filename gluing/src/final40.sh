#!/bin/bash
# final40.sh: wait for generation (A6,A7,B6 par.sh), merge classes, count vs GR T14, glue to n=40.
# S8: glue2 -k 9 -d 8 on R(3,9;31,96); t9<=87: glue2 -k 9 -d 9 on R(3,9;30,87). Degrees 4..9, no edge/MTF bound.
cd ./gluing
SG=../tools/bin/shortg; CG=../tools/bin/countg; R=../runs/gluing/n40
while [ ! -f cls/A6.g6 ] || [ ! -f cls/A7.g6 ] || [ ! -f cls/B6.g6 ] || ls -d cls/A6.g6.parts.* cls/A7.g6.parts.* cls/B6.g6.parts.* >/dev/null 2>&1; do sleep 300; done
sleep 60
echo "gen done $(date)"; grep -h . ../runs/gluing/gen/{A6,A7,B6}.err
cat cls/A6.g6 cls/A7.g6 | $SG -q > cls/r39_31_le96.g6
cat cls/B5.g6 cls/B6.g6 cls/B7.g6 | $SG -q > cls/r39_30_le87.g6
echo "R(3,9;31,<=96) per e (GR T14: 95:560 96:35154):"; $CG --e cls/r39_31_le96.g6
echo "R(3,9;30,<=87) per e (GR T14: 86:1800 87:147335):"; $CG --e cls/r39_30_le87.g6
# HoG cross-check of minimum levels
H=../data/graphs/hog
for p in "31 95 r39_31_le96" "30 86 r39_30_le87"; do set -- $p
  python3 - cls/$3.g6 $2 > $R/.f40_$1 <<'PY'
import sys
f,e=sys.argv[1],int(sys.argv[2])
def ne(s):
    n=ord(s[0])-63; b=0
    for c in s[1:]: b+=bin(ord(c)-63).count('1')
    return b
for l in open(f):
    l=l.strip()
    if l and ne(l)==e: print(l)
PY
  a=$($SG -q < $R/.f40_$1 | sort | md5sum); b=$($SG -q < $H/Ramseygraphs_3_9_$1_e$2.g6 | sort | md5sum)
  [ "$a" = "$b" ] && echo "HoG check n=$1 e=$2: SAME" || echo "HoG check n=$1 e=$2: DIFFER"
done
python3 - <<'PY'
def ne(s):
    b=0
    for c in s[1:]: b+=bin(ord(c)-63).count('1')
    return b
for src,e,dst in [("cls/r39_31_le96.g6",96,"cls/S8_in96.g6"),("cls/r39_30_le87.g6",87,"cls/N_in87.g6")]:
    with open(dst,"w") as o:
        for l in open(src):
            if l.strip() and ne(l.strip())==e: o.write(l)
PY
glue_par() { # IN D OUT
  local IN=$1 D=$2 OUT=$3 i=0 tmp=$(mktemp -d $OUT.parts.XXXX)
  for c in $(seq 156 167); do
    awk -v n=12 -v i=$i 'NR % n == i' $IN > $tmp/in.$i
    taskset -c $c nice -n 5 bin/glue2 -k 9 -d $D -m 4 -M 9 < $tmp/in.$i > $tmp/out.$i 2> $tmp/err.$i &
    i=$((i+1))
  done
  wait; cat $tmp/out.* > $OUT.g6; cat $tmp/err.* > $OUT.err; rm -rf $tmp
  echo "$OUT: in=$(wc -l < $IN) out=$(wc -l < $OUT.g6)"; cat $OUT.err
}
echo "glue start $(date)"
glue_par cls/S8_in96.g6 8 $R/S8_e96
glue_par cls/N_in87.g6 9 $R/N_e87
for f in $R/S8_e96.g6 $R/N_e87.g6; do
  if [ -s $f ]; then mkdir -p ../runs/gluing; cp $f ../runs/gluing/FOUND_$(basename $f); fi
done
echo "final40 done $(date)"
