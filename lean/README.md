# lean: Lean 4 formalization of the R(3,10) reduction lemmas

Owner: agent `lean`. Lean 4 v4.35.0, Mathlib tag `v4.35.0` (commit 56a0058).
Status (2026-10-24):
- Tasks 2a-2e and all hand-proved lemmas of `notes/cases.md` (Sec. 1): proved.
- **Cover Lemma** (`notes/cases.md` Sec. 4a, `cert/cases40.txt`): proved (`R310.cover_lemma`,
  clause form `R310.Enc.cover_assign`), from F1 and F2 only. See "Cover Lemma" below.
- **Computer part of `notes/cases.md`** (Sec. 2-3: degree-distribution lists, LP certificates, t9
  tables): checked by the Lean kernel for the pinned outputs `data/cases_pin1` of `cases`, all four
  tags (gr, gr_mtf, self, self_mtf; lib `R310Cases`). See "Case tables" below.
- **Cube files + lex-leader lemma + verified SB checker** for agent `cert` (see below).

## Build

```bash
source ./lean/env.sh     # sets ELAN_HOME=tools/elan, PATH
cd ./lean
lake exe cache get                                 # Mathlib binary cache (do not build Mathlib)
taskset -c 148-149 nice -n 5 lake build            # builds R310.* (about 1 min)
taskset -c 148-149 nice -n 5 lake env lean scripts/Axioms.lean   # axioms of all 263 theorems
```

Case tables (heavy kernel `decide`; build one tag at a time, memory capped):

```bash
tools/venv/bin/python lean/scripts/export_lean.py lean/data/cases_pin1 gr_mtf 161 1 lean   # from repo root
lean/scripts/build_tag.sh GrMtf 2      # also Gr, Self, SelfMtf; log in runs/lean/
```

A successful build means that every theorem below is checked by the Lean kernel.
No `sorry`, no `axiom`, no `native_decide`. `#print axioms` gives only `propext`,
`Classical.choice`, `Quot.sound` (standard Mathlib axioms) for every theorem.

## Notation (Mathlib)

- Graph: `G : SimpleGraph V`, `V` a `Fintype`; for n = 40, `V = Fin 40`.
- Triangle-free: `G.CliqueFree 3`. Independence number: `G.indepNum` (Mathlib).
  A (3,10,40)-graph is `G : SimpleGraph (Fin 40)` with `G.CliqueFree 3` and `G.indepNum ≤ 9`.
- `deg v` = `G.degree v`, `N(v)` = `G.neighborFinset v`, `e(G)` = `#G.edgeFinset`,
  `Z(v)` = `∑ u ∈ G.neighborFinset v, G.degree u`.
- `outside G v` = `V \ N[v]` (Finset); `delNbhd G v` = `G.induce (outside G v)` = `H_v = G - N[v]`.
- `nbrIn G v y` = `|N(v) ∩ N(y)|` (= `c_v(y)`); `outside2 G u v` = `V \ (N[u] ∪ N[v])`.
- `IsMTF G` = `Maximal (·.CliqueFree 3) G` (maximal triangle-free).
- Class LP: `cls G i` = `C_i`, `ncls G i` = `n_i`, `Mcl G i j` = `M_ij = ∑_{v ∈ C_i} |N(v) ∩ C_j|`.

## Hypotheses (outside computer facts; never proved here)

Every theorem that needs one takes it as an explicit argument.

| Lean name | statement | meaning | source |
|---|---|---|---|
| `Ramsey3Le 9 36` | `∀ H : SimpleGraph (Fin 36), H.CliqueFree 3 → 9 ≤ H.indepNum` | R(3,9) <= 36 | Grinstead–Roberts 1982; [GR] Table 4 |
| `Ramsey3Le 8 28` | same with 28, 8 | R(3,8) <= 28 | McKay–Zhang 1992 (cited in [GR]) |
| `E39Table` | `EdgeLowerBound 9 m e` for (m,e) = (30,86), (31,95), (32,104), (33,118), (34,129), (35,140) | e(3,9,m) >= e | [GR] Tables 3, 4 |
| `EdgeLowerBound 10 40 161` | every (3,10,40)-graph has >= 161 edges | e(3,10,40) >= 161 | [GR] Table 5 |
| `FactF1` | `∀ m, 23 ≤ m → m ≤ 27 → EdgeLowerBound 8 m (6m - 91)` | F1: e(3,8,m) >= 6m - 91 | notes/cases.md Theorem A''; certificate: agent `cert` (F1 runs) |
| `FactF2` | `Ramsey3Le 8 28` | F2: R(3,8) <= 28 | McKay–Zhang 1992; [DuLBG] DRAT; agent `cert` (F2 run) |
| `Glue U G` | `∀ (d,u) ∈ U, ∀ v of degree d, u + 1 ≤ e(H_v)` | gluing result of scenario U | agent `gluing` (not yet available) |
| `Regular35` | `∀ H : SimpleGraph (Fin 35), H.CliqueFree 3 → H.indepNum < 9 → ∀ v, H.degree v = 8` | every (3,9,35)-graph is 8-regular | [GR] Thm 3 (unique graph C35(1,7,11,16)) |

`EdgeLowerBound k m e₀` := `∀ H : SimpleGraph (Fin m), H.CliqueFree 3 → H.indepNum < k → e₀ ≤ #H.edgeFinset`.
`Ramsey3Le k m` := `∀ H : SimpleGraph (Fin m), H.CliqueFree 3 → k ≤ H.indepNum`.
Both are transferred to any vertex type of the right size (`Ramsey3Le.le_indepNum`,
`EdgeLowerBound.le_card_edgeFinset`).
[GR] = Goedgebeur–Radziszowski, EJC 20(1) #P30 (2013). See `notes/edge_tables.md`.

## Theorems by task

Hypotheses column: R9 = `Ramsey3Le 9 36`, R8 = `Ramsey3Le 8 28`, T = `E39Table`,
E161 = `EdgeLowerBound 10 40 161`, U35 = `Regular35`, MTF = `IsMTF G`. All (3,10,40) theorems
also assume `G.CliqueFree 3` and `G.indepNum ≤ 9`.

### Task 2 (general `V` unless stated)

| task | Lean name (file) | statement | hyps |
|---|---|---|---|
| a | `isIndepSet_neighborFinset` (Basic) | triangle-free → `N(v)` independent | |
| a | `degree_le_indepNum` (Basic) | triangle-free → `deg v ≤ α(G)` | |
| a | `degree_le_of_indepNum_le` (Basic) | triangle-free, `α ≤ k-1` → `deg v ≤ k-1` | |
| b | `indepNum_delNbhd_add_one_le` (Basic) | `α(G - N[v]) + 1 ≤ α(G)` | |
| b | `indepNum_delNbhd_le` (Basic) | `α ≤ k-1` → `α(G - N[v]) ≤ k-2` | |
| c | `card_edgeFinset_delNbhd_add_sum_degree` (Basic) | triangle-free → `e(G - N[v]) + Z(v) = e(G)` | |
| c | `card_edgeFinset_delNbhd_eq` (Basic) | triangle-free → `e(G - N[v]) = e(G) - Z(v)` | |
| d | `sum_sum_neighborFinset_degree` (Basic) | `∑_v Z(v) = ∑_u (deg u)^2` | |
| d | `sum_card_edgeFinset_delNbhd_add` (Basic) | triangle-free → `∑_v e(G - N[v]) + ∑_u (deg u)^2 = n e(G)` | |
| d | `sum_card_edgeFinset_delNbhd` (Basic) | same with subtraction | |
| e | `card_le_degree_add` (MinDegree) | triangle-free, `α ≤ k-1`, `Ramsey3Le (k-1) m` → `n ≤ deg v + m` | R(3,k-1) |
| e | `four_le_degree` (MinDegree) | (3,10,40) → `4 ≤ deg v` | R9 |
| a | `degree_le_nine` (MinDegree) | (3,10,40) → `deg v ≤ 9` | |

### Task 3: lemmas of `notes/cases.md`

| cases.md | Lean name (file) | statement | hyps |
|---|---|---|---|
| L1 | `four_le_degree`, `degree_le_nine`, `degree_mem_Icc` | `4 ≤ deg v ≤ 9` | R9 |
| L2 | `card_edgeFinset_delNbhd_add_sum_degree` (Basic) | `e(H_v) + Z(v) = e` | |
| L3 | `e39_le_card_edgeFinset_delNbhd` (EdgeBound) | `e(3,9,39 - deg v) ≤ e(H_v)` | R9, T |
| L3 | `le_card_edgeFinset_delNbhd` (EdgeBound) | general: `EdgeLowerBound (k-1) (n - deg v - 1) e₀ → e₀ ≤ e(H_v)` | |
| L4 | `sum_card_edgeFinset_delNbhd_add_sq` (TheoremA) | `∑_v e(H_v) + ∑ d^2 = 20 ∑ d` | |
| L4 | `sum_e39_add_sq_le` (EdgeBound) | `∑_v (e(3,9,39-d_v) + d_v^2) ≤ 40 e` | R9, T |
| L5 | `le_card_edgeFinset` (EdgeBound), `card_edgeFinset_le_180` (TheoremA) | `159 ≤ e ≤ 180` | R9, T |
| L5 | `exists_degree_nine` (Regular) | some vertex has degree 9 | E161 |
| L6 | `pair_lemma` (Pair) | `u ≠ v`, `u ≁ v` → `|N(u) ∩ N(v)| + 11 ≤ deg u + deg v` | R8 |
| L6 | `pair_lemma_general` (Pair) | general n, k, m | R(3,k-2) |
| L6 | `adj_of_degree_add_le` (Pair) | `u ≠ v`, `deg u + deg v ≤ 10` → `u ~ v` | R8 |
| L6 | `card_degree_le_five` (Pair) | `n4 + n5 ≤ 2` | R8 |
| L6 | `card_degree_le_six_of_deg4` (Pair) | `deg u = 4` → `#{deg ≤ 6} ≤ 5` | R8 |
| L6 | `no_degree_six_of_two_deg4` (Pair) | two 4-vertices → no 6-vertex | R8 |
| L7 | `deg4_delNbhd_regular` (Structure) | `deg u = 4` → `H_u` 8-regular | U35 |
| L7 | `deg4_degree_outside` (Structure) | `y ∉ N[u]` → `deg y = 8 + c_u(y)`, `c_u(y) ≤ 1` | U35 |
| L7 | `deg4_card_edgeFinset` (Structure) | `e(H_u) = 140`, `e = 140 + Z(u)` | U35 |
| L7 | `deg4_count_outside` (Structure) | outside `N[u]`: `#{deg 9} + 4 = Z(u)`, `#{deg 8} + #{deg 9} = 35` | U35 |
| L7 | `deg4_degree_counts` (Structure) | `n_D = [D=4] + #{x ∈ N(u), deg D} + #{y ∉ N[u], deg D}`; last is 0 unless D ∈ {8,9} | U35 |
| L7 | `deg4_nbr_degree_sum` (Structure) | `x ≠ x' ∈ N(u)` → `deg x + deg x' ≥ 12` | U35, R8 |
| L8a | `row_a` (ClassLP) | `∑_j M_ij = i n_i` | degrees in [4,9] |
| L8b | `row_b` (ClassLP) | `e(H_v) ≥ L` on `C_i` → `∑_j j M_ij + n_i L ≤ n_i e` | |
| L8c | `row_c` (ClassLP) | `2 ∑_{i,j} x_i x_j M_ij ≤ (∑_i x_i n_i)^2`, all `x : ℕ → ℕ` | |
| L8c | `weighted_mantel` (Mantel) | triangle-free, `x : V → ℕ` → `2 ∑_u x_u ∑_{v ∈ N(u)} x_v ≤ (∑ x)^2` | |
| L8d | `row_d`, `row_d_diag` (ClassLP) | `M_ij ≤ n_i min(i, n_j)`; `2 M_ii ≤ n_i^2` | |
| L8e | `row_e` (ClassLP) | `i + j ≤ 10` → `M_ij = n_i (n_j - [i = j])` | R8 |
| L8f | `row_f` (ClassLP) | `n_i (i^2 + 78) ≤ ∑_j j M_ij + 11 i n_i` | MTF |
| - | `Mcl_comm` (ClassLP) | `M_ij = M_ji` | |
| Thm A | `theoremA` (TheoremA) | `∃ v`, (deg 9 ∧ `e(H_v) ≤ 99`) ∨ (deg 8 ∧ `e(H_v) ≤ 96`) | R9, `E39TableA` (m = 32..35) |
| Thm A | `theoremA_of_not_regular` (TheoremA) | not 9-regular → same with 98 | R9, `E39TableA` |
| Thm B | `theoremB` (Mantel) | not 9-regular → `∃ v`, `deg v ≤ 8 ∧ e(H_v) + 9 deg v ≤ 180` | |
| Thm C | `theoremC_aux` (TheoremC) | degrees in {8,9}, `N = n8 < 40`, `e(H_u) ≥ L₈` on 8-vertices → `∃` 9-vertex `v`: `e(H_v) + N/2 = 99 + ε(v)`, `ε(v) ≤ 9`, `(40-N) ε(v) ≤ 8N - N (N/2 - (108 - L₈))` | |
| Thm C | `theoremC` (TheoremC) | same with `L₈ = 95` (c = 13) | R9, T |
| L9 | `regular_card_common` (Structure) | 9-regular, `u ≠ v`, `u ≁ v` → `1 ≤ |N(u) ∩ N(v)| ≤ 7` | R8 |
| L9 | `regular_nbrIn` (Structure) | 9-regular, `y ∉ N[v]` → `1 ≤ c_v(y) ≤ 7`, `deg_{H_v} y + c_v(y) = 9`, `2 ≤ deg_{H_v} y ≤ 8` | R8 |
| L9 | `regular_sum_nbrIn` (Structure) | 9-regular → `∑_{y ∉ N[v]} c_v(y) = 72` | |
| L9 | `regular_card_private` (Structure) | 9-regular → at most 9 `y ∉ N[v]` with `c_v(y) = 1` | |
| L9 | `nbr_erase_subset_outside` (Structure) | `S_x = N(x) - v ⊆ V \ N[v]`, independent, `|S_x| = deg x - 1` | |
| L9 | `regular_nine_delNbhd` (Regular) | 9-regular → `e = 180`, `|H_v| = 30`, `e(H_v) = 99`, `α(H_v) ≤ 8` | |
| M0 | `exists_isMTF_le` (MTF) | triangle-free `G` ≤ some MTF `H` with `α(H) ≤ α(G)` | |
| M0+M1 | `exists_mtf_min_degree_six` (MTF) | (3,10,40) exists → MTF (3,10,40) with min degree ≥ 6 exists | |
| M1 | `IsMTF.six_le_degree` (MTF) | MTF (3,10,40) → `6 ≤ deg v` | (no R9 needed) |
| M2 | `IsMTF.sum_degree_neighbor_ge` (MTF) | MTF (3,10,40) → `d^2 + 78 ≤ Z(v) + 11 d` | |
| M1/M2 | `IsMTF.degree_add_two_mul_card_outside_le` (MTF) | general: `d + 2 |V \ N[v]| ≤ Z(v) + d (k - d)` | |
| M3 | `isMTF_of_regular_nine`, `isMTF_of_indepNum_le_degree` (MTF) | 9-regular (3,10,40) is MTF | |
| - | `IsMTF.exists_common` (MTF) | MTF, `u ≠ v`, `u ≁ v` → common neighbour | |
| - | `card_nbrIn_eq_one_le` (Local) | `#{y ∉ N[v] : c_v(y) = 1} ≤ d (k - d)` | |
| - | `exists_card_edgeFinset_delNbhd_le` (Averaging) | `∃ v`, `n (e(H_v) + d_v^2) + 2c e ≤ n e + n c d_v` | |

## Cover Lemma (cases.md Sec. 4a, agreed between `cases` and `cert`)

File `R310/Cover.lean`; clause form in `R310/Encoding.lean`. Hypotheses: only F1, F2.

| Lean name | statement |
|---|---|
| `thmA2_32`, `thmA2_33` | Theorem A'': F1, F2 → `EdgeLowerBound 9 32 95`, `EdgeLowerBound 9 33 103` |
| `theoremA_mtf` | MTF (3,10,40)-graph, not 9-regular, F1, F2 → `∃ v`, (deg 9 ∧ `e(H_v) ≤ 98`) ∨ (deg 8 ∧ `e(H_v) ≤ 96`) |
| `exists_relabel` | `∃ σ`, `σ v = 0` and `N(0) = {1..deg v}` in `relabel G σ` |
| `cover_lemma` | F1, F2, (3,10,40)-graph `G` → `∃ G'` on `Fin 40`: triangle-free, `α ≤ 9`, `CodegOK G'`, and `CubeR G' ∨ CubeS8 G' ∨ CubeN G'` |
| `Enc.fdef_iff` | an assignment `x` satisfies TRI + IS(10) iff `graphOf x` is a (3,10,40)-graph (link a1) |
| `Enc.mtfClauses_iff` | MTF clauses on `x` iff `MTFc (graphOf x)` |
| `Enc.degree_graphOf`, `Enc.h0edges_graphOf` | `deg v` and `e(H_0)` as counts over the variables |
| `Enc.cover_assign` | Cover Lemma over assignments: `∃ x`, `Fdef x` ∧ codegree bound ∧ one cube |

Cube files for the certified chain (`R310/Files.lean`, `R310/FilesProof.lean`), in cert's
variable numbering (edge `x(i,j)` = `j(j-1)/2 + i + 1`, MTF aux `c(i,j,l)` = `781 + p(i,j)*38 + r`):

| Lean name | statement |
|---|---|
| `Files.cubeR`, `cubeS8`, `cubeN` | constraint lists: TRI + MTF definitions + N(0) units + degree sums + e(H_0) sums |
| `Files.tri_is_iff` | `a` satisfies `triFile` and all IS clauses iff the graph of `a` is a (3,10,40)-graph |
| `Files.cover_files` | F1, F2, (3,10,40)-graph → `∃ a`, `ISall a` ∧ (all of `cubeR` ∨ all of `cubeS8` ∨ all of `cubeN` hold) |

| `Files.cover_files_sb` | lex-leader lemma (`R310/LexLeader.lean`): as `cover_files`, plus every SB clause of the cube, for SB lists whose witnesses fix 0 and {1..d} (`InGamma d`) and satisfy `SBValid better val` (violating `x` ⇒ `act π x` strictly better; `better ∈ {<, >}`, any `val`) |

`lake env lean scripts/EmitCubes.lean` writes `out/cube_{R,S8,N}.opb` (99701 / 99700 / 99700
constraints, `out/SHA256SUMS`) from these lists; agent `cert` compares them with its formulas.

Cubes (fields = rows of `cert/cases40.txt`, optional rows included):
- `CubeR`: all degrees 9; `N(0) = {1..9}`; `MTFc`; `e(H_0) = 99`.
- `CubeS8`: `MTFc`; `deg 0 = 8`; `N(0) = {1..8}`; `e(H_0) ≤ 96`; all degrees in 6..9.
- `CubeN`: `MTFc`; `deg 0 = 9`; `N(0) = {1..9}`; `e(H_0) ≤ 98`; all degrees in 6..9.
- `CodegOK` (all cubes): non-adjacent `u ≠ v` have `|N(u) ∩ N(v)| + 11 ≤ deg u + deg v`.
`MTFc G` := `∀ u ≠ v, u ~ v ∨ ∃ w, u ~ w ∧ v ~ w`.

## Verified per-clause SB checker (`sbcheck`)

- `R310/SBCore.lean`: Mathlib-free definition `checkSB` (so the executable needs no Mathlib).
- `R310/SBCheck.lean`: `R310.SB.checkSB_sound`: `checkSB minOrder pos d lits p pinv = true` →
  `∃ π`, `π = p`, `InGamma d π` and `SBValid (if minOrder then (·<·) else (·>·)) (valL pos) ⟨lits, π⟩`,
  i.e. exactly the hypotheses of `Files.cover_files_sb` (with `val = valL pos`).
- `SBMain.lean` → `lake build sbcheck`; run `.lake/build/bin/sbcheck FILE`. Format as
  `cert/check_sb.py`: header `c order positions=<rowmajor|colex> better=<min|max> vars=<colex|rowmajor> d=<d>`,
  lines `<lits> 0 | pi(0) ... pi(39)`. Row-major ids are renamed to colex ids first. Prints
  `s VERIFIED <k> clauses` only if every clause passes (decide on stdout, as for cake_lpr).
- Streams the input line by line (about 11 MB memory for any size); `sbcheck -` reads stdin.
  Parallel: `scripts/sbcheck_par.sh FILE <cpulist>` (one worker per CPU, each streams the file and
  checks every n-th clause; needs one header at the top). Speed on cert's S8 sample witnesses:
  0.66 ms per clause per CPU (10^8 clauses: about 18 CPU hours).
- Trusted: the parser in `SBMain.lean` and the Lean compiler; the check itself is proved.
- cert's samples: `cert/samples/sb_S8_good.wit` VERIFIED 200; `sb_S8_bad.wit` FAIL lines 2, 3
  (same two clauses as check_sb.py).
- Differences from check_sb.py: also checks the witness is in Γ_d; accepts tautological clauses
  (vacuously valid); rejects literal ids outside 1..780 (no MTF aux literals).
- Tests: `scripts/gen_sb_tests.py` + `scripts/diff_sb.sh`: 300 random n = 40 clauses, 288 equal
  verdicts, 12 differ = all tautologies; negative tests in `tests/sbneg/` (π(0) ≠ 0, aux id, flipped
  literals, non-permutation, wrong d, garbage) all FAIL.

## General n: lex-leader lemma and checker (for the F1 certificates, n = 23..27)

Files `R310/GenCore.lean` (Mathlib-free `checkG`), `R310/GenCheck.lean`, `R310/GenLex.lean`.

| Lean name | statement |
|---|---|
| `Gen.PhiG s E D d G` | triangle-free, `α < s`, `≤ E` edges, all degrees `≤ D`, and if `d > 0`: `N(0) = {1..d}` |
| `Gen.GammaG d π` | `d = 0` (all permutations), or `π` fixes vertex 0 and maps `{1..d}` onto itself |
| `Gen.checkG_sound` | `checkG n minOrder pos d lits p pinv = true` → `∃ π = p`, `GammaG d π` ∧ `SBValidG (<|>) (valLG pos) ⟨lits, π⟩` |
| `Gen.lexleader_gen` | a graph with `PhiG` → `∃ x`, `PhiG (graphOfG x)` ∧ every valid SB clause (witness in `Γ_d`) holds on `valId x` |
| `Gen.edgeLowerBound_of_unsat` | `D ≥ k-1`, valid SB clauses, `¬∃ x, PhiG k E D 0 (graphOfG x) ∧ SB` → `EdgeLowerBound k m (E+1)` (F1 form) |
| `Gen.tri_iffG`, `Gen.isc_iffG` | TRI clauses ↔ triangle-free; IS(s) clauses ↔ `α < s`, for any `n` |

Block partitions: header `blocks=1:7,2,1,2,27` (sizes, `,` or `:` separated, sum = n) runs
`checkGB` (`Gen.checkGB_sound`: witness maps every block onto itself, clause valid; `d` is then
ignored). `Gen.lexleader_inv`: for ANY formula `P` invariant under the witnesses, a model of `P`
gives a model of `P` + all valid SB clauses. Invariance of a concrete case formula (units,
codegree, block edge counts) is a hypothesis of `lexleader_inv`. For the R(7) case it is proved:
Lemma R7 and Lemma Mc (`R310/R7.lean`, `R310/Mc.lean`; hypotheses F2 = R(3,8) <= 28 and
`EdgeLowerBound 8 27 85` = e(3,8,27) >= 85 [D-E8]):
`R7.r7_count` (9-regular, non-adjacent u, v with 7 common neighbours: A–B complete, e(X) = 85),
`R7.r7_cover` (then some graph satisfies `PRc7`), `R7.no_codeg7` (if PRc7 + valid block SB is
UNSAT, every 9-regular (3,10,40)-graph has codegree <= 6 on non-adjacent pairs),
`Mc.lemma_Mc` (3 <= c* <= 7 and the relabelled normal form N(0) = {1..9}, 0 ≁ 10,
N(10) ∩ {1..9} = {1..c*}, all non-adjacent codegrees <= c*).
`Rc7.prc7_inv` (`R310/Rc7.lean`; `PRc7` = Φ + cube R + the 6 edge units + N(10) ∩ {1..9} = {1..7}
+ codegree ≤ 7 + e({13..39}) = 85, i.e. cube_R.opb + Rc7b/case.opb) and `Rc7.lexleader_rc7`.

`sbcheck`: a header with `n=<n>` (and optional `s=<s>`, recorded only) selects `checkG n`; without
`n=` the n = 40 checker is used (unchanged). Row-major ids for general n are
`i*n - i(i+1)/2 + (j-i)`. Tests (`scripts/gen_sb_tests.py OUT COUNT SEED N`): n = 23, 25, 27, 40:
all verdicts equal to check_sb.py except tautologies (22 of 800); general n = 40 equals the
n = 40 checker on all 300 old tests; negative tests in `tests/sbnegn/` (π moves 0 with d = 5,
flipped literals, identity witness, short permutation, id > N, wrong n) all FAIL.

## Case tables (computer part of cases.md, Sec. 2-3)

Pinned input: `data/cases_pin1` (copy of `cases/degseq.py` and `cases/out/*`, `SHA256SUMS`).
Four tags: `gr` (all G, e >= 161), `gr_mtf` (MTF, e >= 161), `self` (all G, e >= 159 proved),
`self_mtf` (MTF, e >= 159).

How it works:
- `LP/Cert.lean`: rows of the class LP (L8), exact certificate checker `Cert.check` (integers),
  soundness `Cert.sound`.
- `LP/Graph.lean`: every admissible row holds for the class counts `M_ij` of a (3,10,40)-graph;
  `Cert.no_graph`: a checked certificate excludes every graph that fits its instance.
- `LP/Simple.lean`: the simple checks of `degseq.py` (parity, edge bounds, M1, GR sum, L6,
  L7, min Z) as `passSimple`, and `passSimple_distOf`: every (3,10,40)-graph passes them.
- `LP/Cases.lean`: generic `caseTable` (exhaustive enumeration `enumOK` + LP kills) and
  `t9_bound`, `t9_main` (t9 tables with inline certificates).
- `LP/Cases<Tag>.lean`, `LP/Data/<Tag>*.lean`: generated by `scripts/export_lean.py`; all
  checks by `decide +kernel` (no `native_decide`).
- Cross-check: `scripts/lean_simple.py` (Python mirror of `passSimple`) gives exactly the same
  distribution sets as `degseq.py` for all 4 tags; all 19,890 certificates convert.

Main theorems (namespace `R310.LP.Data`):

| Lean name | statement | hyps |
|---|---|---|
| `caseTable_<tag>` | `distOf G ∈ surv_<tag>` (the list of `cases`) | R9, R8, T, (E161 for gr*), (U35 for non-MTF), (MTF for *_mtf) |
| `t9_<tag>_<s>_main` | `Glue U_s G` → `∃ v`, deg 9 ∧ `e(H_v) ≤ t9of t9_<tag>_<s> (distOf G)` | same + `Glue U_s G` |

Scenarios `U_s` (degseq.py `SCENARIOS`): none = [], U8 = [(8,96)],
known = [(4,140),(5,130),(6,119),(7,108),(8,96)], ang = [(4,140),(5,130),(6,121),(7,112),(8,96)].
For `self` and `self_mtf`, scenario `none` has 2 survivors without a t9 certificate; only the
other three scenarios get a `_main` theorem.

## Notes

- Theorem C is stated without `min(9, floor(...))`: it gives `ε(v) ≤ 9` and
  `(40 - N) ε(v) ≤ 8N - N max(0, N/2 - c)`, which is equivalent.
- Theorem B and L8(c) use weighted Mantel for integer weights only (proof: Mantel for the
  blow-up, from Mathlib's Turán theorem). This is all that cases.md uses.
- M1 does not need R(3,9) <= 36.
- The case tables are checked for the pinned files only. If `cases` regenerates its outputs,
  re-pin and re-run `export_lean.py` + `build_tag.sh`.
