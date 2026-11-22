# Round 21 — price only the eight frozen h=7 pilots

The order, hole lists, and exact expected key sets are inherited from
`ROUND19_PREREG.md` and `scratch/G/round19/h7-prereg.json`. Start with
51/1,213 two-sided keys already checked; the most these pilots can add
is 184. The separate exact alignment denominator is lane A's work.
No other left list, aligned `h=8` re-solve, or `h≤6` work is authorized.

Preflight reproduced the exact smaller one-defect 129/11 canonical
class sets, 269 physical plants including 128 changed right lists, all
physical singleton/double incidences, and the concrete preregistered
two-sided key sets. Stabilizer enumeration finds no allowed transpose
on boards 2 and 3. All eight generated CNFs bind before any target
solve; each rejects shortening an MTF row, dropping an optional-site
guard and padding a false three-site blocker. First preflight stopped
before target because the small-control binder assumed nonempty,
distinct existence rows; the small fixture can have empty rows and
multiple physical requirements yielding the same clause. The repaired
binder matches the multiset and still requires nonempty target rows.

Cost before target: the previous same-width broad `h=7` proofs on
boards 0 and 5 took 1.27 and 4.38 CPU-s end to end, with CNF+LRAT
sizes 1,034,057 and 13,491,970 bytes (`scratch/ideas/r018_N/e2e.log`).
The new inputs have 20,832–25,111 clauses versus 20,807/22,361 for
those two pilots; this is not a proof-complexity bound. Budget about
35–70 CPU-s and 8–110 MiB for eight comparable cases including setup
and clean replay, or stop on caps. Measured setup so far: 10.09 CPU-s
including failed preflight; staged CNFs and metadata ~4.9 MB.

One sequential foreground worker, nice +5, virtual memory 512 MiB,
solver ≤30 CPU-s / 45 wall-s, 48 MiB/proof, 448 MiB total staging and
0.20 core-h all-in. Cap the entire target at 405 wall-s and the clean
review at 120 wall-s, in addition to each per-process cap. Halt on
model, cap, invalid binding, checker failure or staging limit.
Regenerate and bind the bytes again and require both LRAT verifiers
before recording a checked key. No production request is implied by
passing the pilot. No time extrapolation to other overlaps.
