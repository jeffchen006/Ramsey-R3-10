# Lane H — round 1, November 21, 2026

Core share 4; no first-round critic directives. No flow-verified (3,10,40)
graph. Read the current critic directives and BOARD before resuming.

## Jobs

| Supervisor / worker | Command | Log | Cores | Start / hard stop (host CET) |
|---|---|---|---:|---|
| 1253143 / shell 1253159 / cache 1253379 | `timeout 3000 taskset -c 148-149 bash ralph/lanes/H/lean_round1.sh dynamic` (launcher `scratch/H`, Lake in `lean`) | `scratch/H/lean_round1_dynamic.log`, `cache-dynamic.log`, then `mathlib-cache-check.log`, `lake-build.log`, `axioms.log`, `lemmas-build.log` | 2 | 17:12 / 18:02, fetch stage cap 17:37 |

Last checked ~17:24: pinned cache helper still reading Mathlib sources for
hashes; no fetch output yet. No solver jobs. Earlier PIDs 517645, 667823,
667827, 989560, 989565 are gone; none should be restarted as-is. First
Lake cache attempts hit instance/thread/runtime overhead; the prior
static cache linker attempt was stopped deliberately. The partial copy
`scratch/H/lake-work` is not a valid package cache. Read `lean_round1.sh`
and `link_from_lake.sh` before further Lean setup.

## Evidence and claims

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| pub | Audit: classical bounds remain 40–41 in sources found through November 21. Angeltveit journal §7 reports at least 43,225,483 distinct order-39 graphs; no full or bulk release located and no new exact order-30 dense level (e ≥ 88) located. | `LIT.md` | — |
| hand | R(7) boundary/package/DFS reduction review: necessities, side ordering, first-present-mask branching and domain-shortage leaves justify the proof format. | `R7_REVIEW.md`, C-003/C-004 | — |
| hand | R(6) codegree-path and C8-window reduction reviewed; sequential neighbourhood union bounds replace four-way inclusion–exclusion in the first step. | `C6_REVIEW.md`, C-006 | — |
| enum | Independently reconstructed C8 cover without C code, nauty, or precomputed windows; 191 checked seeds, 270 eligible placements, 32 residue families, 95,984 four-type words, zero complementary half-load pairs. Both toy load controls pass. | `check_cycle8.py`, `scratch/H/cycle8-independent-v2.log`, C-007 | 0.0014 final / 0.012 incl. unoptimized replay |
| cert (same checker, exact replay) | G's six conditional distribution certificates and 231 threshold certificates all replay, zero failures. Does not certify the original gluing floors or exclude e88. | `scratch/H/recheck-G-base.log`, `scratch/H/recheck-G-threshold.log`, G-001/G-002 | <0.001 |
| enum (calibration) | Native pinned Lean `sbcheck-dyn` accepts all 157 witnesses on A's order-18 SMS control; separately the interpreted check also passed. | `scratch/H/dyn-link.log`, `scratch/H/sbcheck-valid.log` | <0.01 |
| open | Standalone Lean extract emitted R/S8/N OPBs with 99,701 / 99,700 / 99,700 constraints. This provenance is provisional: no byte comparison to full-project export yet. | `scratch/H/emit-standalone.log`, `scratch/H/emit/out/`, `check_round1_exports.sh`, A-001 | <0.01 |
| open | Drafted C's residue and overlap rows, biclique exclusions, the C6 four-neighbourhood/cover steps, and G's typed wedge identities. Typechecking and axiom audit not complete; drafts are not imported by `lean/R310.lean`. | `lean/R310/Residue.lean`, `lean/R310/Wedge.lean`, `AxiomsRound1.lean` | — |

Ledger refreshed in `ralph/CLAIMS.md`, preserving the lanes' labels and
pending critic verdicts. R(7) is the strongest round result: A independently
regenerated the cover and replayed 49,569,079 nodes for all 977,008 C pairs.
Keep C-004/C-007 `enum` pending critic acceptance. E's order-five/five-fixed
case has four checked DRAT proofs; D's symmetry quotient of C's 78 exact
R(3) exclusions leaves 110 representatives. B's planned prefix cannot
close e88 and F has no order-40 witness.

## Next round

1. Collect bounded cache/build logs first. Cache uses Lean v4.35.0 and
   Mathlib v4.35.0 commit `56a005855ea17e0b0958f73ec801ae140b0a1679`;
   path-override manifest in `scratch/H/packages-local.json` bypasses the
   slow Lake git diff on pinned packages. `lean --print-prefix` has
   `bin/leantar`; the cache command must run inside `lean` with elan PATH
   and `LEAN_SRC_PATH` from the launcher. `cache query` is not useful for
   upstream per-file caches. If the 25-minute fetch stage expires during
   hashing or unpacking, give the pinned helper a longer budget; do not
   launch overlapping package writers or build Mathlib from source.
2. Verify the full project build and `lean/scripts/Axioms.lean`, then
   typecheck `+R310.Residue +R310.Wedge` and run `AxiomsRound1.lean`. Fix
   drafts before integration or any `Lean` claim. Get the C6 path
   endpoint lemma from the two generic drafted cover steps if time permits.
3. After `R310.Files` builds, run `bash ralph/lanes/H/check_round1_exports.sh`
   for the bytewise formal/provisional OPB comparison and notify A/D.
4. Ask the critic to review the two finite packing proofs, especially
   hand coverage and input census dependencies. Prefer new C6 path splits
   and D's mask-profile factorization to bulk raw SMS. Reconcile new lane
   claims with the ledger without upgrading any labels.
