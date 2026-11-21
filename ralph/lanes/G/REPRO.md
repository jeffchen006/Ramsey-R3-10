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

# Round 2: degree-six root residual floor

`root_certs/hog33_118.g6` came from House of Graphs, Minimal Ramsey Graphs,
`https://houseofgraphs.org/data/ramsey/minramsey/Ramseygraphs_3_9_33_e118_some.g6`.
Despite `_some` in the filename, the five distinct valid classes match the
complete count from Goedgebeur–Radziszowski Table 14. Trusting that published
count and Table 4's edge floor is explicit. `root_certs/inputs.sha256` pins
the input, the incomplete extended catalogue, and the exact distribution
cut list. The principal replay regenerates CNF and checks existing LRAT;
it does not run a solver. All commands below start at the workspace root;
replace `scratch/G` with a reviewer-owned scratch directory if checking.

```sh
G=ralph/lanes/G
(cd "$G/root_certs" && sha256sum -c inputs.sha256)
opt/bin/labelg -q "$G/root_certs/hog33_118.g6" | sort -u | wc -l  # 5
python3 -S -B tools/check_graph.py --n 33 --k 9 "$G/root_certs/hog33_118.g6"
bash "$G/replay_root_core.sh" scratch/G/root/review166
python3 -S -B "$G/check_root_distribution.py" | diff - "$G/root_certs/closed166.csv"
python3 -S -B "$G/check_root_cover.py" --edges 166 --controls scratch/G/exoo39.matrix "$G/root_certs/hog33_118.g6"
python3 -S -B "$G/root_core.py" --controls scratch/G/exoo39.matrix "$G/root_certs/hog33_118.g6" scratch/G/root/review166
```

The primary proof does not assume `e(G)=166` or the previous gluing floors.
The threshold-dependent `root_glue.py` is the initial stronger encoding
used for measurement; its traces are not the shipped `root_certs/*.lrat.gz`.
The 68-input exploratory list consists of the five 118-edge graphs and
63 of the 69 published 119-edge classes. Testing it does **not** raise the
unconditional-on-prior-gluing floor to 120. To regenerate and check the
exploratory traces, pass that catalogue as the second argument to
`replay_root_core.sh`. The second mode prints `not_certified` on a non-UNSAT
solver result; only the explicit `cert` output lines denote checked proofs.

For the higher-edge threshold scan, reproduce with system Python + SciPy and
replay without third-party dependencies:

```sh
G=ralph/lanes/G
(
  ulimit -v 16777216; ulimit -t 240
  export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
  nice -n 5 timeout 450s /usr/bin/python3 -B "$G/scan_root_floor.py" --output scratch/G/root/review_floor.jsonl
  nice -n 5 timeout 90s python3 -S -B "$G/scan_root_floor.py" --verify --output "$G/root_floor_certs.jsonl"
)
```

These LP certificates use the new trusted-with-LRAT floor `e(H6)>=119`
and the original `e(H8)>=97` gluing floor. The one new `t9<=87` closure
also needs the original `e(H9)>=88` gluing floor; the five new `t9<=88`
bounds are not closures unless the stronger MTF gluing exclusion arrives.
