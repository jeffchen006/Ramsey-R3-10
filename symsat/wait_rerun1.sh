#!/bin/bash
until [ $(wc -l < ./runs/symsat/rerun1.jsonl) -ge 73 ]; do sleep 120; done
