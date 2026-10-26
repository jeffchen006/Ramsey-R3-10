#!/bin/bash
# t9_88.sh: all R(3,9;30,<=88) by GR increments, then glue d=9 of R(3,9;30,88) to n=40.
# Closes the "t9 <= 88" case: no (3,10;40)-graph has a 9-vertex v with e(G_v) = 88 (if 0 outputs).
# Stages (each checkpointed: a stage with OUT.ok is skipped; chunks with ok.NNNN are skipped on restart):
#  0  checks: increments (tcheck.py), input counts vs [GR] T12/T13, glue5 = glue on samples
#  1  R(3,7;15,<=16), R(3,7;16,<=22), R(3,7;17,<=28): min-degree gluing from complete R(3,6;m) (val/)
#  2  R(3,8;23,<=52), t = 3:1,4:4,5:4,6:2   -> check vs [GR] T13 (102/8241/356041/10326716)
#  3  R(3,8;22,<=44), t = 3:2,4:4,5:3,6:2   -> check vs [GR] T13 (21/1521/72353)
#  4  R(3,9;30,<=88), t = 5:3,6:4,7:3 (topt), glue5 -> check e<=87 vs [GR] T14 (1800/147335)
#  5  glue2 d=9 (degrees 4..9) on R(3,9;30,88) -> runs/gluing/n40/N_e88.g6
# Cost (measured 2026-10-25 on samples): st 1 seconds; st 2 ~2 CPU-h; st 3 < 1 CPU-h; st 4 d=5 ~15 CPU-h, d=7 <= 160 CPU-h,
#   d=6 ~1 s x 1.07e7 = ~100 CPU-days; st 5 ~6e6 x 0.04-0.13 s. ETA on 32 CPUs: ~3.5-4.5 days.
# CPUs 100-131 (gluing, TEAM_RULES), nice 5, ulimit -v 3.5 GB per worker process (32 x 3.5 = 112 GB), merges 16 GB.
# usage (from gluing/): ./src/t9_88.sh      Log: stdout (jobctl). Work dir: cls/t88/, logs runs/gluing/t88/.
set -u
cd ./gluing
CPUS=$(seq 100 131); NCPU=32
MEMKB=3500000; MERGEKB=16000000
SG=../tools/bin/shortg; PY=python3
W=cls/t88; L=../runs/gluing/t88; TMPD=$W/tmp
mkdir -p $W $L $TMPD ../runs/gluing/n40
die() { echo "ABORT: $* ($(date))"; exit 1; }
log() { echo "[$(date '+%F %T')] $*"; }

# Chunk outputs of shortg are canonically labelled, so merges are a plain sort -u (canon strings).
cmerge() { # OUT FILES... : union of canonical graph6 files
  local OUT=$1; shift
  ( ulimit -v $MERGEKB; cat "$@" | LC_ALL=C taskset -c 100-103 nice -n 5 sort -u -S 8G --parallel=4 -T $TMPD > $OUT )
}
# pool NAME NCH OUT CMD... : run CMD on every chunk of $W/NAME.in (graph6) on all CPUs (dynamic queue),
# dedupe each chunk with shortg, merge+dedupe into OUT. CMD must print a final "glue..." line on stderr.
pool() {
  local NAME=$1 NCH=$2 OUT=$3; shift 3
  local D=$W/$NAME.d
  [ -f $OUT.ok ] && { log "$NAME: done before, skip"; return 0; }
  mkdir -p $D
  if [ ! -f $D/split.ok ]; then
    split -n r/$NCH -d -a 4 $W/$NAME.in $D/in. || die "split $NAME"; touch $D/split.ok
  fi
  echo 0 > $D/cnt
  log "$NAME: start, $(wc -l < $W/$NAME.in) inputs, $NCH chunks, cmd: $*"
  for cpu in $CPUS; do
    ( while :; do
        c=$(flock $D/lock bash -c "n=\$(cat $D/cnt); echo \$((n+1)) > $D/cnt; echo \$n")
        [ $c -ge $NCH ] && break
        cs=$(printf %04d $c)
        [ -f $D/ok.$cs ] && continue
        ( ulimit -v $MEMKB; set -o pipefail
          taskset -c $cpu nice -n 5 "$@" < $D/in.$cs 2> $D/err.$cs | taskset -c $cpu nice -n 5 $SG -q -T$TMPD > $D/out.$cs 2>/dev/null
        ) && grep -q '^glue' $D/err.$cs && touch $D/ok.$cs
      done ) &
  done
  wait
  local nok=$(ls $D | grep -c '^ok\.')
  [ $nok -eq $NCH ] || die "$NAME: only $nok of $NCH chunks ok (see $D/err.*)"
  cmerge $OUT $D/out.* || die "merge $NAME"
  cat $D/err.* > $L/$NAME.err
  $PY - $L/$NAME.err <<'PY'
import sys, re
tot = {}
for l in open(sys.argv[1]):
    for k, v in re.findall(r'(\w+)=([\d.]+)s?(?=[ \n])', l):
        if k in ('in', 'nodes', 'leaves', 'out', 'cpu', 'tuples'): tot[k] = tot.get(k, 0) + float(v)
print('  sum over chunks:', ' '.join(f'{k}={v:.6g}' for k, v in tot.items()))
PY
  log "$NAME: done, $(wc -l < $OUT) distinct graphs -> $OUT"
  rm -f $D/in.* $D/out.*; touch $OUT.ok
}
# stage_merge OUT SPEC FILES... : merge + dedupe class files, exact count check vs SPEC
stage_merge() {
  local OUT=$1 SPEC=$2; shift 2
  [ -f $OUT.ok ] && { log "$OUT: done before, skip"; return 0; }
  cmerge $OUT "$@" || die "merge $OUT"
  $PY src/ecount.py $OUT "$SPEC" || die "count check $OUT"
  touch $OUT.ok
}

# ---------------- stage 0: checks ----------------
log "stage 0"
for a in "8 23 52 3:1,4:4,5:4,6:2" "8 22 44 3:2,4:4,5:3,6:2" "9 30 88 5:3,6:4,7:3"; do
  r=$(taskset -c 100 nice -n 5 $PY src/tcheck.py $a | tail -1); echo "  tcheck $a: $r"
  echo "$r" | grep -q '^OK' || die "increments $a"
done
$PY src/ecount.py cls/r37_19_le37.g6 37:11 || die input
$PY src/ecount.py cls/r37_18_le33.g6 30:1,31:15,32:382,33:8652 || die input
$PY src/ecount.py cls/r38_24_le58.g6 56:51,57:3419,58:129347 || die input
for m in 9 10 11 12 13 14 15; do [ -s ../gluing/val/r3_6_$m.g6 ] || die "val/r3_6_$m.g6 missing"; done
if [ ! -f $W/val5.ok ]; then   # glue5 = glue on samples of the three stage-4 steps
  i=0
  for p in "cls/r38_24_le58.g6 5 4000" "cls/r38_23_le51.g6 6 12000" "cls/r38_22_le42.g6 7 1"; do set -- $p
    awk -v s=$3 'NR % s == 1' $1 | head -40 > $W/val5_$2.in
    for b in glue glue5; do
      ( ulimit -v $MEMKB; taskset -c $((100+i)) nice -n 5 bin/$b -k 8 -d $2 -m 2 -M 8 -e 88 < $W/val5_$2.in 2>$L/val5_${b}_$2.err \
        | $SG -q 2>/dev/null | sort > $W/val5_${b}_$2.out ) &
      i=$((i+1))
    done
  done
  wait
  for d in 5 6 7; do
    cmp -s $W/val5_glue_$d.out $W/val5_glue5_$d.out || die "glue5 != glue on sample d=$d"
    echo "  glue5 = glue on sample d=$d ($(wc -l < $W/val5_glue_$d.in) inputs, $(wc -l < $W/val5_glue_$d.out) outputs)"
  done
  touch $W/val5.ok
fi

# ---------------- stage 1: small R(3,7) classes (min-degree vertex v, all of R(3,6;n-d-1)) ----------------
log "stage 1"
for p in "15 16" "16 22" "17 28"; do set -- $p; n=$1; E=$2; OUT=$W/r37_${n}_le$E.g6
  [ -f $OUT.ok ] && continue
  i=0
  for d in 1 2 3 4 5 6; do m=$((n-d-1))
    ( ulimit -v $MEMKB; taskset -c $((100+i)) nice -n 5 bin/glue -k 6 -d $d -e $E < val/r3_6_$m.g6 > $W/s1_${n}_$d.raw 2> $L/s1_${n}_$d.err ) &
    i=$((i+1))
  done
  wait
  ( ulimit -v $MERGEKB; cat $W/s1_${n}_*.raw | $SG -q -T$TMPD > $OUT ) || die "merge $OUT"
  rm -f $W/s1_${n}_*.raw
  echo "  $OUT: $(wc -l < $OUT) graphs"
  touch $OUT.ok
done
$PY src/ecount.py $W/r37_16_le22.g6 20:2,21:15,22:201 || die "R(3,7;16,<=22) vs GR T12"
$PY src/ecount.py $W/r37_17_le28.g6 25:2,26:30,27:642,28:13334 || die "R(3,7;17,<=28) vs GR T12"
$PY - $W/r37_15_le16.g6 <<'PY'
import sys, collections
c = collections.Counter(sum(bin(ord(ch)-63).count('1') for ch in l.strip()[1:]) for l in open(sys.argv[1]) if l.strip())
print('  R(3,7;15,<=16) per e (no published table):', dict(sorted(c.items())))
PY

# ---------------- stage 2: R(3,8;23,<=52) ----------------
log "stage 2"
$PY src/efilt.py 0 21 < $W/r37_16_le22.g6 > $W/s2d6.in
cp cls/r37_19_le37.g6 $W/s2d3.in; cp cls/r37_18_le33.g6 $W/s2d4.in; cp $W/r37_17_le28.g6 $W/s2d5.in
for d in 3 4 5 6; do pool s2d$d 64 $W/s2d$d.g6 bin/glue -k 7 -d $d -e 52 -m 1 -M 7; done
stage_merge $W/r38_23_le52.g6 49:102,50:8241,51:356041,52:10326716 $W/s2d3.g6 $W/s2d4.g6 $W/s2d5.g6 $W/s2d6.g6

# ---------------- stage 3: R(3,8;22,<=44) ----------------
log "stage 3"
$PY src/efilt.py 0 31 < cls/r37_18_le33.g6 > $W/s3d3.in
cp $W/r37_17_le28.g6 $W/s3d4.in; cp $W/r37_16_le22.g6 $W/s3d5.in; cp $W/r37_15_le16.g6 $W/s3d6.in
for d in 3 4 5 6; do pool s3d$d 64 $W/s3d$d.g6 bin/glue -k 7 -d $d -e 44 -m 1 -M 7; done
stage_merge $W/r38_22_le44.g6 42:21,43:1521,44:72353 $W/s3d3.g6 $W/s3d4.g6 $W/s3d5.g6 $W/s3d6.g6

# ---------------- stage 4: R(3,9;30,<=88) ----------------
log "stage 4"
cp cls/r38_24_le58.g6 $W/s4d5.in; cp $W/r38_22_le44.g6 $W/s4d7.in
[ -f $W/s4d6.in ] || cp $W/r38_23_le52.g6 $W/s4d6.in
pool s4d5 64 $W/s4d5.g6 bin/glue5 -k 8 -d 5 -e 88 -m 2 -M 8
pool s4d7 128 $W/s4d7.g6 bin/glue5 -k 8 -d 7 -e 88 -m 2 -M 8
pool s4d6 640 $W/s4d6.g6 bin/glue5 -k 8 -d 6 -e 88 -m 2 -M 8
if [ ! -f $W/r39_30_le88.g6.ok ]; then
  cmerge $W/r39_30_le88.g6 $W/s4d5.g6 $W/s4d6.g6 $W/s4d7.g6 || die "merge s4"
  touch $W/r39_30_le88.g6.ok
fi
$PY src/efilt.py 0 87 < $W/r39_30_le88.g6 > $W/r39_30_le87_check.g6
$PY src/ecount.py $W/r39_30_le87_check.g6 86:1800,87:147335 || die "R(3,9;30,<=87) vs GR T14"
$PY src/efilt.py 88 88 < $W/r39_30_le88.g6 > $W/N_in88.g6
log "R(3,9;30,88) = $(wc -l < $W/N_in88.g6) graphs (no published count; MCMC estimate 5.9e6)"
if [ -s cls/r39_30_le87.g6 ]; then
  a=$(sort $W/r39_30_le87_check.g6 | md5sum); b=$($SG -q < cls/r39_30_le87.g6 2>/dev/null | sort | md5sum)
  [ "$a" = "$b" ] && log "e<=87 part = final40 class cls/r39_30_le87.g6: SAME" || log "e<=87 part vs final40 class: DIFFER (check!)"
fi

# ---------------- stage 5: glue d=9 to n=40 ----------------
log "stage 5"
cp $W/N_in88.g6 $W/s5.in
pool s5 640 ../runs/gluing/n40/N_e88.g6 bin/glue2 -k 9 -d 9 -m 4 -M 9
F=../runs/gluing/n40/N_e88.g6
if [ -s $F ]; then
  cp $F ../runs/gluing/FOUND_N_e88.g6
  log "OUTPUTS FOUND: $(wc -l < $F) graphs; check_graph:"; $PY ../tools/check_graph.py --k 10 --n 40 $F; echo "check_graph rc=$?"
else
  log "RESULT: 0 outputs. No (3,10;40)-graph has a degree-9 vertex v with e(G_v) = 88 (degrees 4..9, no MTF/edge assumption)."
fi
log "t9_88 done"
