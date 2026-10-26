#!/bin/bash
cd ./symsat
for f in 24 16 14 12; do
  taskset -c 88-95,168-175 nice -n 5 ../tools/venv/bin/python ext27.py ../data/graphs/mckay/r38_27.g6.gz $f
done
