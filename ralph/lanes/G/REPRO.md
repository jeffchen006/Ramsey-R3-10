# Round 1: degree-profile LP replication and verification

From the workspace root:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
PY=opt/venv/bin/python  # system python3 with SciPy 1.15.3 also worked
mkdir -p scratch/G/bootstrap
ulimit -v 16777216
nice -n 5 timeout 240s "$PY" -B ralph/lanes/G/degseq.py --mtf --out scratch/G/bootstrap
nice -n 5 timeout 50s "$PY" -B ralph/lanes/G/verify_certs.py scratch/G/bootstrap/certs_gr_mtf.json
cmp scratch/G/bootstrap/degseq_gr_mtf.json lean/data/cases_pin1/degseq_gr_mtf.json
cmp scratch/G/bootstrap/certs_gr_mtf.json lean/data/cases_pin1/certs_gr_mtf.json
nice -n 5 timeout 90s "$PY" -B ralph/lanes/G/check_rows.py scratch/G/exoo39.matrix
nice -n 5 timeout 90s "$PY" -B ralph/lanes/G/scan.py --verify --output ralph/lanes/G/close87.jsonl
nice -n 5 timeout 150s "$PY" -B ralph/lanes/G/scan.py --verify --output ralph/lanes/G/t9_round1_certs.jsonl
```

`exoo39.matrix` is Exoo's original complement adjacency matrix from the address
given in `notes/known39.md`; `check_rows.py` complements it and independently
checks triangle-freeness, independence number and the graph coordinates. C35
is constructed as a circulant; the 191 order-22 controls come from the repo.

For a full experiment, run from `scratch/G` with the same resource limits;
the examples assume `ROOT=<root>` and `PY` absolute:

```sh
nice -n 5 timeout 360s "$PY" -B "$ROOT/ralph/lanes/G/scan.py" --baseline bootstrap/degseq_gr_mtf.json --families profiles wedge private internal pair all --output full87.jsonl
nice -n 5 timeout 540s "$PY" -B "$ROOT/ralph/lanes/G/scan.py" --baseline bootstrap/degseq_gr_mtf.json --families lifted packing --output full_pack87.jsonl
nice -n 5 timeout 900s "$PY" -B "$ROOT/ralph/lanes/G/scan.py" --baseline bootstrap/degseq_gr_mtf.json --families combined --tighten --output tighten.jsonl
```

In `--verify` mode no third-party imports are needed (`python3 -S -B` works).
For each stored row multiplier
`y >= 0`, `scan.py` uses exact fractions to check
`min_{0<=x<=ub} y^T A x > y^T b`; the box minimum is the sum over negative
column coefficients times their upper bounds. Row and box semantics are
in `rows/`. A threshold certificate for `T` uses the previously reported
degree-8 gluing edge floor 97 and refutes the hypothesis that all degree-9
vertices have `e(H_v) >= T+1`. Thus it proves a conditional **upper bound**
`t9 <= T`, not that the corresponding gluing catalogue is empty. For `T<=87`
the already-reported degree-9 gluing yield also rules out the distribution
(conditional on that enum result). LP feasibility is not graph existence.
