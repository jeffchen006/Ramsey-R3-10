# Lane H — round 4 handoff, November 21, 2026

Two-core share, peak one for foreground checks. No flow-verified order-40
graph. Read the next critic directives before opening a new proof path.

## Jobs

| PID | Command | Log | Cores | Start / finish |
|---|---|---|---:|---|
| — | No live/detached H jobs. | — | 0 | — |
| foreground, ended | Targeted `lake build --old R310.RootDemand`; `lean -j1 -s8192` four axiom reports; integrated `lake build --old R310`. See `LEAN_REPRO.md`. | `scratch/H/root-demand-{build-v2,axioms,integrated}.log` | 1 | 19:55–19:59 CET |

Earlier round had no live jobs. The targeted build's first iteration had
ordinary Lean elaboration errors, then passed. All successful builds
used the existing cache with no Mathlib source build. Limits: timeout,
CPU cap, niceness, single CPU affinity, 16 GiB virtual memory.

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| Lean, H-006 | MTF attachment domination and demand cover; d+1 demands with an edge across every pair refute extension by an injection into the root neighborhood. | `lean/R310/RootDemand.lean`, `AxiomsRound4.lean`, `LEAN_REPRO.md`, `scratch/H/root-demand-axioms-audit.log` | 0.034 incl. H-007 and failed first build |
| Lean, H-007 | Given a residual floor L, MTF on 40 vertices with alpha≤9 and a degree-six root implies total e≥L+48. Does not formalize the premise L=120, the census or the LRATs. | `lean/R310/RootDemand.lean`, `FLOOR6_REVIEW.md`, `scratch/H/root-demand-axioms-audit.log` | included above |
| enum, H-008 | Independent pinned-table reconstruction matches all 55 new e167 keys and RHS entries; stage deltas and U88 match. Exactly 47 open e168 n6>0 keys would fall with a floor of 121. Uses recorded certified bounds, no new exclusions. | `check_floor6_delta.py`, `scratch/H/floor6-delta.log` | <0.001 |
| enum, controls | 5 tight C5 roots, C6/C7 correct failures without MTF, 220 rooted six-regular order-22 controls with 2,259 uncovered pair demands and 28,866 incompatibilities. | `check_root_demand_control.py`, `scratch/H/root-demand-control.log` | <0.001 |
| hand audit | MTF domination/cover clauses, isomorphism transport, private-cell count and e167 proof premise audited; 5+69 exact cover cites primary GR Tables 4/14 and A/critic independent bindings. No extra proof replay or changes to accepted exclusions. | `FLOOR6_REVIEW.md`, `ralph/lanes/A/FLOOR_AUDIT.md`, `scratch/critic/r3-G120.log` | — |
| pub/open | GR counts rechecked; 33/120 count interval 1,223–1,240 from lower bounds plus Angeltveit exact aggregate. No located later exact R(3,10) result, GR–Angeltveit order-39 bulk file, or exact dense order-30 count. | `LIT.md` | — |

Ledger mirrors round 003 verdicts: G-009/010/011/012 complete within their
stated MTF/conditional scopes. 376 near-regular plus Case R, 13 possible
further U88 cuts only. E-012 is all-graphs for (2,28,a=4), not a=6. C-013
excludes P4 spans only; C-015 leaves e(X)≤63 at diagonal five only. C-009
P5 is redundant, not promoted to `cert`. Prior H-003/004/005 were confirmed
without upgrading their scope. A-005/006/007 are independent audits, not
new exclusions; new round-4 work in other lanes may finish after this snapshot.

## Team status and next steps

Best established route is G's fixed-root exclusion, now independently
audited by A (all 74 degree-six and 68 degree-seven exception LRATs) and H
(premises and exact case sets). Floor 121 could remove 47 more, but e120
still needs an exact cover or a direct obstruction for omitted classes.
B's zero-output up86 slice is not a full e88 cover. C's P4 and P3 results
restrict R(6), not all of R; E's (2,28,a=4) is a complete symmetry branch.
F's current checked best I10=44 is not a witness; no flow-verified example.

1. Copy final round-4 claims and critic verdicts without double-counting G's
   frozen cut ledger. Do not replay full P4/P5, duplicate G's census, or
   regenerate root LRATs. A owns the portable binding packages.
2. Keep the demand theorem separate from finite coverage. If G finds an
   exact next-level route, audit its reach to edge-critical classes.
3. If C produces a short new lemma affecting P2 or diagonal-three/four P3,
   request a precise statement for Lean before taking another target.
