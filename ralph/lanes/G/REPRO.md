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

# Round 3: two complete low-level residue floors

From the workspace root (use a fresh reviewer-owned work directory):

```sh
G=ralph/lanes/G
W="$PWD/scratch/G/round3"
nice -n 5 timeout 160s bash "$G/replay_floor120.sh" "$W/review_floor120" "$W/full_core119"
nice -n 5 timeout 200s bash "$G/replay_floor7.sh" "$W/review_floor7" "$W"
for name in root_floor7_certs root_floor7_106_certs root_floor7_107_certs; do
  nice -n 5 timeout 90s python3 -S -B "$G/scan_root_floor.py" --verify --output "$G/$name.jsonl"
done
python3 -S -B "$G/summarize_round3.py" | diff - "$G/round3_cases.csv"
```

Floor 120 script independently verifies the 5+69 cover, binds checked CNFs
and existing proofs by SHA-256, checks both LRATs, and verifies e167 cut
bookkeeping and the 36 higher-e LP certificates. If the proof stream in
scratch is lost, regenerate with `replay_root_core.sh WORK CATALOGUE`, or
recover the old 68 through lane A and the six extra compressed proofs in
`root_certs/e119_new/`. `replay_floor7.sh` checks canonical edge-addition
equalities, all 19521 short clique witnesses, exact complement partition,
CNFs and 68 LRATs. It does not rerun the clique search or any SAT solver.
The 39 e104 inputs originate from the House of Graphs minimal Ramsey graph
file `Ramseygraphs_3_9_32_e104.g6`; the canonical list is stored locally.
The exact individual level counts are GR Table 14; the e120 upper bound
instead uses Angeltveit's combined <=121 census, not an exact e120 count.

Root-7 LP runs use `--floor7 105`, `106`, `107` in order, each with
`--edges $(seq 162 179)`. The latter levels incorporate the certified
results for previous levels from the named JSONL files. The verification
mode uses pure Python rational arithmetic. LP cuts using t9 require the
two prior gluing floors; neither residual bound itself needs them.

Rebuilding the two-/three-vertex replacement tool and its control:

```sh
c++ -O3 -Wall -Wextra -Werror -std=c++17 -Igluing/src "$G/joint_replace.cc" -o "$W/joint_replace"
c++ -O3 -Wall -Wextra -Werror -Wno-unused-function -std=c++17 -Igluing/src "$G/expand_residue_edges.cc" -o "$W/expand_residue_edges"
(
  cd "$W"; ulimit -v 16777216; ulimit -t 90
  nice -n 5 timeout 90s ./joint_replace 3 10 12 2 < control8.g6 > replay2.tsv
  nice -n 5 timeout 90s python3 -S -B ../../../ralph/lanes/G/check_joint_replace.py control8.g6 replay2.tsv 3 10 12 2 --brute
  nice -n 5 timeout 90s ./joint_replace 3 10 12 2 triple < control8.g6 > replay3.tsv
  nice -n 5 timeout 90s python3 -S -B ../../../ralph/lanes/G/check_joint_replace.py control8.g6 replay3.tsv 3 10 12 2 --brute --triple
)
```

The source of truth for the 74 usable roots is exact checked count plus
independent witnesses, not traversal connectivity. For reconstructing the
search sequence, see the measured stages in `LOG.md`.

# Round 4: e168 cuts and strict-level residue census

```sh
G=ralph/lanes/G
W="$PWD/scratch/G/round4"
nice -n 5 timeout 30s python3 -S -B "$G/scan_private_equality.py" --control scratch/G/exoo39.matrix
for stem in private_equality_cuts private_equality_t9; do
  nice -n 5 timeout 45s python3 -S -B "$G/scan_private_equality.py" --verify "$G/$stem.jsonl"
done
nice -n 5 timeout 30s python3 -S -B "$G/private_packing.py"
nice -n 5 timeout 30s python3 -S -B "$G/check_private_packing_cuts.py"
python3 -S -B "$G/freeze_round3.py" | diff - "$G/round3_frozen.csv"
python3 -S -B "$G/summarize_round4.py" | diff - "$G/round4_cases.csv"
nice -n 5 timeout 145s bash "$G/replay_e120_partial.sh" "$W/e120_review" "$W"
```

The strict e120/e121 census uses GR Tables 4 and 14, and Angeltveit,
*R(3,10) ≤ 41*, EJC 32(4) #P4.30 (2025), arXiv:2401.00392v2,
§§3.3 and 6: 14,395 combined order-33 classes through e121. The paper
does not give an exact e120 level count. `check_floor121_catalogue.py`
requires strict levels, an independent alpha and triangle check, and
sparse canonical distinctness. It refuses incomplete coverage unless
`--allow-gap` is explicitly supplied. `replay_e120_partial.sh` verifies
all 1,223 supplied e120 exclusions but intentionally does not claim
the combined count matches. Check the current gap in `STATE.md`.

Build the novel edge repair and the scoped square replacement with
`c++ -O3 -march=native -Wall -Wextra -Werror -std=c++17 -Igluing/src`
and the respective `.cc` source. Tests are `check_witness_edit.py`
(60 exact labelled n8 cells) and `check_cycle_replace.py` (seven
exact tagged n8 squares). The search loops use `run_witness_edit.sh`
with explicit source edge levels and disjoint scratch shards; each
stage's parameters/estimates are in `scratch/G/round4/*.plan`.
Every count was recomputed from strict `pickg -e` partitions. The
round-3 e120 snapshot had one e119 mixed into its 1,178 rows, and its
e121 frontier had 23 e120s; neither issue affects the accepted floor
120 proof (which used the separate exact 5+69 catalogue) or LP cuts.

Frozen e121 scope: of 13,092 rows, 10,268 clique traces and 2,813
unpinned root-core LRATs pass. `e121.core.sat.tsv` indexes the 11
complementary roots whose core was SAT; root-clause satisfaction is
not a gluing extension. All 11 refute at **total e=169** using
`root_glue.py --edges 169 --relaxed`, both LRAT checkers. The residual
121 and Z>=48 already forbid e<169. Do not promote this e121 package
to an unpinned claim. Replay by (i) validating the three clique/exception
partitions indexed by `e121.frozen.sha256`, (ii) regenerating core CNFs
in the ten original shards and two deltas and checking existing LRATs
only for `cert` rows, and (iii) regenerating the 11 pinned CNFs from
`e121.core.sat.g6` with `root_glue.py --edges 169 --relaxed` and
byte-matching `e121_e169/*.cnf` before dual replay. Prior root_glue
controls use the same code path and actual rooted MTF witnesses;
`scratch/G/root/calib_relaxed.log`. The six unsupplied residue types
remain open; there is no new global degree-six floor.
