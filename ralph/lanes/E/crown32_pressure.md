# A fixed-core capacity sieve for 32 fixed vertices

Scope: the crown with four disjoint independent attachments, `t=2,3,4`
of size six and the rest size five. Use the same prerequisites as the
crown reduction in `involution.md` (in particular its checked minimum
degree five). `W` is the unattached fixed core of order `12−t`.

## Necessary capacity test (`hand`)

Any `w∈W` has at most `c(w)=min(9, floor((28−d_W(w))/3))−d_W(w)`
neighbors in attachments. Indeed each of the four `F\A_i` has
independence number at most seven, so its degrees are at most seven;
the sum of the four residual degrees of `w` is `3d_F(w)+d_W(w)`.

Each `W∪A_i` has independence number at most six: the three crown
vertices on one side in the other pairs can add to it. For a size-six
attachment, every `w` needs at least one neighbor. If two vertices of
`W` each have exactly one neighbor in it, the neighbors differ: adjacent
vertices with a shared neighbor make a triangle, while nonadjacent
vertices could otherwise add the same five unused attachment vertices.
Hence at least `|W|−6` vertices of `W` each require a second edge in
each size-six group. For a size-five group the zero-neighbor vertices
must form a clique; a nonadjacent zero pair could add the group. There
are at most two zeros, and if two they are adjacent.

Enumerate each possible unordered multiset of `4−t` zero sets (empty,
singleton, or an edge of `W`; repeated zero sets allowed). For each
`w`, reserve `t` units of its capacity for the size-six groups' first
edges and one unit for each size-five group where `w` is not a zero.
All spare capacities must be nonnegative. A vertex can supply at most
`min(t,spare(w))` second-edge demands, since only one demand per full
group is counted. Thus the sum must be at least `t(|W|−6)` for at least
one choice of zero sets. This test is necessary, not sufficient.

For `t=4`, if `δ(W)≥3`, the test forces `W` cubic: a degree-five vertex
cannot supply even four first edges; at degree four its spare is zero,
at degree three it is one, and eight spares are required. Each `w` in
this cubic branch has exactly one double row among the four groups,
and each group has exactly two double rows. `geng` produces two cubic
triangle-free cores of order eight (`scratch/E/r4_pilot/w8.cubic.g6`).
This gives a small pinned next branch, not an exclusion of it.

## Census and pilots (`enum`, not whole-case exclusions)

| `t` | `|W|` | Triangle-free cores | `α(W)≤5` | Capacity removals | Survive |
|---:|---:|---:|---:|---:|---:|
| 2 | 10 | 12,172 | 6,657 | 461 | 6,196 |
| 3 | 9 | 1,897 | 1,407 | 271 | 1,136 |
| 4 | 8 | 410 | 356 | 43 | 313 |

The pressure filter calibration independently enumerates the
triangle-free attachment masks of small cores and checks all 387
distinct feasible degree vectors (counted per template); none is
rejected. An explicit one-edge-cap path control is impossible, and
the two-vertex matching control is feasible. The target scan takes
4.6 CPU s; the replay from raw triangle-free inputs is byte-identical.

`involution_sat.py` fixes the moving crown and attachment memberships;
only unknown fixed edges are variables. Ramsey degree bounds in all
residues of moved independent sets and triangle clauses are static.
Independent-set cuts are against fixed residues; any missing mixed
independent set is found via its moved subset. The smaller exhaustive
tests match 22/0/22/1 completions of the Petersen-shaped and `C5`
inputs. The three unpinned target profiles have 207–229k base rows,
436–446 fixed-edge variables, and all reach the 24 CPU-s cap. Nine
probes pin first, middle, last of each pre-pressure census: 136–168k
base rows, 401–408 fixed-edge variables. Three give unchecked UNSAT
(2.50, 6.32, 1.52 CPU s); six reach the 24 CPU-s kill. Neither sample
is an estimate for a complete proof sweep; no continuation launched.

Replay the census from `scratch/E`:

```sh
set -euo pipefail
lane=../../ralph/lanes/E
tools=../../opt/bin
limited() { local budget=$1; shift; nice -n 5 timeout "$((budget + 15))" bash "$lane/limited.sh" "$budget" "$@"; }
limited 10 python3 -B "$lane/crown32_pressure.py" --control
for count in 2 3 4; do
    order=$((12-count))
    limited 10 "$tools/geng" -qt "$order" > "r4_pilot/w$order.all.g6"
    limited 20 python3 -B "$lane/crown32_pressure.py" --full "$count" \
        --cores "r4_pilot/w$order.all.g6" --output "r4_pilot/w$order.pressure.g6"
done
```

Evidence: `scratch/E/r4_pilot/{crown32_pressure.cal.log,recheck/w*.log,32.*.log}`.
