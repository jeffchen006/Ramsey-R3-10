#!/bin/bash
# Stop duo/shared11 if its RSS passes 14 GB; exit when it is no longer running.
cd .
while true; do
  l=$(tools/bin/jobctl status duo | grep ' shared11 ')
  echo "$l" | grep -q RUNNING || exit 0
  g=$(echo "$l" | sed -n 's/.*rss= *\([0-9.]*\)G.*/\1/p')
  if [ -n "$g" ] && awk "BEGIN{exit !($g>14)}"; then tools/bin/jobctl stop duo shared11; echo "stopped at ${g}G"; exit 0; fi
  sleep 60
done
