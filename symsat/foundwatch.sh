#!/bin/bash
# copy any symsat n=40 SAT graph into graphs/found/ so watchd checks it and mails everyone
F=./runs/symsat/found40_candidates.g6
while true; do
  if [ -s $F ]; then cp $F ./graphs/found/symsat_candidates.g6; exit 0; fi
  sleep 60
done
