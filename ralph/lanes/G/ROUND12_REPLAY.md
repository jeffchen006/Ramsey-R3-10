# Round 12: join the two mixed equality windows

The scope is the exact mixed e168 pin `(2,7,4,27)` with the adjacent
degree-six roots, a path/leaf A strip and matching/incident or
path/middle B strip. The share is 14 cores. There is no profile
closure, no proposal of an order-40 graph, and no new class LP row.
G-037 is terminal and unchanged. See `rows/equality_reroot_join.md`
for the graph proof and all symbolic premises. In commands below,
the working directory is `scratch/G/round12` and the shell inherited
`ulimit -v 16777216`; `src=../../../ralph/lanes/G` and
`py=../../../opt/venv/bin/python`.

## A-small: actual bound map, then prices

Use A's original-ID coverage of the complete order-27 catalogue,
not a gluer pad: `scratch/A/strip12/map27.tsv` binds 899 links to
48 d8 IDs, including the full/τ1 link's single ID. A's extra MTF
support cut narrows this to 22 IDs; we use the conservative 48-ID
baseline for pilot exclusions. Independently complete in their
**named minima only**, A's maps of order26/δ3 and order25/δ2 give
77 d8 full/τ0 IDs, zero d9 order26 IDs, and 16 d9 full/τ0 IDs.
Parsing the raw/canonical sets and actual relabellings is A's work;
see `ralph/lanes/A/ROUND12_REPLAY.md`. They price reroot choices but
are not exclusions of higher minima. No A-013 proof transfer.

`full.v2.map` binds each original ID and variant to the first passing
optimistic wing table or a zero. A before/after per-variant counts:

| Side / fixed degree / reroot | Before | After |
|---|---:|---:|
| A d8 order27 leaf | 18,797 | 16,021 |
| A d8 order27 full/τ1 | 37,594 | 27,922 |
| A d8 order26 full/τ0 | 37,594 | 37,594 |
| A d9 order26 leaf | 1,798 | 1,798 |
| A d9 order26 full/τ1 | 3,596 | 3,596 |
| A d9 order25 full/τ0 | 3,596 | 3,596 |

There is zero loss of *original* A-small IDs on the optimistic table
test alone: 18,797 d8 and 1,798 d9 survive. Pricing the two windows
inside the same order-31/30 graph with exact edge parity gives
27/32 dual proofs in an A8/full/τ0 wing pilot; five relaxed SAT.
To compare the **same original roots**, use both leaf choices (64
variants on the 32 IDs), the singleton maximal column and full
independence witness repair. This gives 55 eager dual proofs and
eight repaired dual proofs. The only remaining relaxation-positive
variant is on an ID with one certified sibling. All 31 two-variant
IDs lie outside even the wider 48-ID order27 map. Thus 31 of the
32 selected original d8 A-small IDs are excluded (conditional on
the order27 cover); the one remaining ID is open. These 31 IDs
are disjoint from the **three** direct A-small order24 receipts
from round 11. The other four direct receipts are B-small already
covered by G-038 and are not counted as A-small. No A production.

The d9 full/τ0 projection finds 10/12 genuinely alpha≤8 order-30
windows in its relaxation, while order26 leaf and full/τ1 each
find 1/12. Adding the maximal column and A's stronger minima
leaves those counts unchanged, and misses the final A8 ID too.
These projected graphs are not order-40 candidates. Evidence:
`mini.parity.log`, `mini.proof.log`, `a8.sibling.log`, `a8.repair.log`,
`a8.repair.proof.log`, `a8.no27.two.variant.keys`, `a8.direct.keys`,
`column.pilot.log`, `extra.floors.log` in the working directory.

## B-small: price separately

Reversibility and G-038 let us choose the original B pivot to have
codegree 3 and original window minimum 4. When τ=0, its exchanged
mate has codegree 2, so use the order25 arm (δ≥3 in middle by G-037,
δ≥2 in matching). When τ=1 both have codegree 3 and both minima
are 4. The middle arm's two B holes meet the B cross anchor; the
matching arm can have either choice of the codegree-three pivot.
This is a cover of possible graphs up to the documented reversal,
not a one-to-one reroot of every earlier rooted role.

| B shape / reroot | Before | Static survivors |
|---|---:|---:|
| Matching order25 | 24,640 | 24,494 |
| Matching order26 | 12,320 | 11,359 |
| Middle order25 | 6,160 | 6,108 |
| Middle order26 | 6,160 | 5,268 |

All 128 dispersed B proof-pilot variants obtained dual LRATs at
6,500 conflicts. Matching 64/64 is **only a pilot**, not an
exclusion; no matching production. B-middle is a separate 12,320
row roster conservatively scheduled in two batches, including
944 static rejections so none need trust that prefilter for being
excluded. The independent five-anchor oracle matches all 49,280
B role IDs and freezes the 12,320 middle entries (`b.middle.audit.log`).
The before-launch prices are in `b.middle.price` and
`b.middle.static.price` in the working directory.

**Terminal producer result (hand + enum + cert, pending critic):**
all **12,320** B-middle roles are certified, 6,160 under each value
of τ. The main batch ended with 11,369 dual proofs and seven
relaxation-SAT order-25 rows; the static-rejection batch gave 944
dual proofs. The seven tail rows all gave dual proofs after adding
the singleton maximal column and 537 explicit I9 cuts on the
order-32 graph (`b.middle.repair25.cuts/`). Each cut names nine
distinct vertices of `P`; it never includes the extra column.
The independent hole oracle schedule and terminal manifest match
exactly; all trace sizes/digests bind, total 719,725,531 compressed
bytes. Fresh producer replay validates 28 dispersed baseline traces
and all seven repairs; these are not claimed as a separate lane's
check. Measured production, binding and fresh replay: 8,330.20
CPU-s (2.314 CPU-h). PIDs 3268364 and 3475785 are retired.

The terminal claim is **no B-side equality for a degree-eight
noncross B pivot of the middle shape** under the named mixed e168
strip hypotheses. This uses the prior reductions G-038/A-013 and
the named minimum scopes G-033/G-037; it does not exclude arbitrary
minimum-four windows, the matching shape, crossed pivots, A-side
equality, or the full distribution. The accepted 21,236 older
G-037 proofs were neither generated nor re-bound here.

Manifest `scratch/G/round12/b.middle.final.tsv`:
`8967461e699b4ebbf4aa1e0fb89314e9bda2c2481940e6247d2aebf1c3a8073f`.
The log sources are `b.middle.main.cert.log`, the three
`b.middle.static.<rank>.log`, and `b.middle.repair25.proof.log`.
The binder is `bind_reroot.py`, matching the five-anchor schedule
`b.middle.all.selection`. The original seven open keys exactly
equal `b.middle.repair25.selection`.

## Calibration and commands

Small physical shells with an exact literal permutation oracle:
14 matched test cases, from Exoo39/C35/C13 and adverse edge-bound
mutations, plus rooted positive/negative SAT join controls from
Exoo39/C35 (`controls4.log`, `mini.control3.log`). The maximal-column
positive/negative control checks all 676 columns and their one-contact
deletions on the three graphs after maximalizing Exoo39; it separates
the MTF premise (`column.control2.log`). A 256-core sample for the
static map cost 0.64 CPU-s before the all-role map at ~12 CPU-s.

```sh
nice -n 5 timeout 60s "$py" -B "$src/test_reroot_shell.py" ./reroot_shell ../round11/neighborhood.known.g6
nice -n 5 timeout 25s "$py" -B "$src/reroot_shell_jobs.py" ../round10/short-anchor.full.keys > full.v2.in
nice -n 5 timeout 35s ./reroot_shell < full.v2.in > full.v2.map
nice -n 5 timeout 30s "$py" -B "$src/audit_reroot_roles.py" ../round10/short-anchor.full.keys full.v2.map b.middle.all.selection
```
