/-
`sbcheck FILE`: per-clause check of SB clauses with the verified checker `R310.SB.checkSB`
(soundness: `R310.SB.checkSB_sound`). Input format (as cert/check_sb.py):
  header  "c order positions=<rowmajor|colex> better=<min|max> vars=<colex|rowmajor> d=<d> [n=<n> s=<s>]"
          without n=: the n = 40 checker `checkSB` (soundness `R310.SB.checkSB_sound`, Γ_d with d ≥ 1);
          with n=: the general checker `checkG n` (soundness `R310.Gen.checkG_sound`; d = 0 means
          all permutations); s= is recorded only (the check does not depend on s)
  lines   "<DIMACS literals> 0 | pi(0) pi(1) ... pi(39)"
Literals with vars=rowmajor are renamed to colex ids before the check (the checked clause is the
renamed one). Prints "s VERIFIED <k> clauses" only if every clause passes. Streams the input line by line
(constant memory); FILE = `-` reads stdin.
Trusted: this parser and the Lean compiler; the checking function itself is proved sound.
-/
import R310.SBCore
import R310.GenCore

open R310.SB R310.Files R310.Gen

structure Hdr where
  rowPos : Bool := true
  minOrder : Bool := false
  rowVars : Bool := false
  d : Nat := 9
  /-- `some n`: general checker `checkG n` (header field `n=`); `none`: the n = 40 checker. -/
  n : Option Nat := none
  s : Option Nat := none
  /-- block sizes (header `blocks=1:7,2,...`): witnesses must map each block onto itself. -/
  blocks : Option (List Nat) := none

def parseHdr (s : String) : Option Hdr := do
  let ws := (s.splitOn " ").filter (· ≠ "")
  guard (ws.take 2 == ["c", "order"])
  let mut h : Hdr := {}
  let mut seen : Nat := 0
  for w in ws.drop 2 do
    match w.splitOn "=" with
    | ["positions", v] =>
      h := { h with rowPos := v == "rowmajor" }; seen := seen + 1
      guard (v == "rowmajor" || v == "colex")
    | ["better", v] =>
      h := { h with minOrder := v == "min" }; seen := seen + 1
      guard (v == "min" || v == "max")
    | ["vars", v] =>
      h := { h with rowVars := v == "rowmajor" }; seen := seen + 1
      guard (v == "rowmajor" || v == "colex")
    | ["d", v] => h := { h with d := ← v.toNat? }; seen := seen + 1
    | ["n", v] => h := { h with n := some (← v.toNat?) }
    | ["s", v] => h := { h with s := some (← v.toNat?) }
    | ["blocks", v] =>
      let parts := (v.splitOn ",").flatMap (·.splitOn ":")
      h := { h with blocks := some (← parts.mapM String.toNat?) }
    | _ => none
  guard (seen == 4)
  return h

def rowArr : Array (Fin 40 × Fin 40) := rowPairs.toArray

/-- Literal from a DIMACS integer. -/
def mkLit (rowVars : Bool) (z : Int) : Option Lit := do
  let n := z.natAbs
  guard (n ≥ 1)
  let id ← if rowVars then do
      guard (n ≤ 780)
      let p := rowArr[n - 1]!
      pure (xid p.1 p.2)
    else pure n
  return ⟨id, z > 0⟩

/-- Parse one clause line; `none` on a format error. -/
def parseLine (h : Hdr) (s : String) : Option (List Lit × Array (Fin 40)) := do
  let parts := s.splitOn "|"
  guard (parts.length == 2)
  let ls := ((parts[0]!).splitOn " ").filter (· ≠ "")
  let ps := ((parts[1]!).splitOn " ").filter (fun t => t ≠ "" && t ≠ "\n" && t ≠ "\r")
  let zs ← ls.mapM String.toInt?
  guard (zs.getLast? == some 0)
  let lits ← (zs.dropLast).mapM (mkLit h.rowVars)
  let pis ← ps.mapM (fun t => t.trimAscii.toString.toNat?)
  guard (pis.length == 40)
  let arr ← pis.mapM (fun v => if hv : v < 40 then some (⟨v, hv⟩ : Fin 40) else none)
  return (lits, arr.toArray)

/-- Literal from a DIMACS integer, general `n`. -/
def mkLitG (n : Nat) (rowArr : Array (Fin n × Fin n)) (rowVars : Bool) (z : Int) : Option Lit := do
  let k := z.natAbs
  guard (k ≥ 1)
  let id ← if rowVars then do
      guard (k ≤ rowArr.size)
      let p ← rowArr[k - 1]?
      pure (xid p.1 p.2)
    else pure k
  return ⟨id, z > 0⟩

/-- Parse one clause line for general `n`. -/
def parseLineG (n : Nat) (rowArr : Array (Fin n × Fin n)) (h : Hdr) (s : String) :
    Option (List Lit × Array (Fin n)) := do
  let parts := s.splitOn "|"
  guard (parts.length == 2)
  let ls := ((parts[0]!).splitOn " ").filter (· ≠ "")
  let ps := ((parts[1]!).splitOn " ").filter (fun t => t ≠ "" && t ≠ "\n" && t ≠ "\r")
  let zs ← ls.mapM String.toInt?
  guard (zs.getLast? == some 0)
  let lits ← (zs.dropLast).mapM (mkLitG n rowArr h.rowVars)
  let pis ← ps.mapM (fun t => t.trimAscii.toString.toNat?)
  guard (pis.length == n)
  let arr ← pis.mapM (fun v => if hv : v < n then some (⟨v, hv⟩ : Fin n) else none)
  return (lits, arr.toArray)

/-- Inverse of a map, general `n` (garbage if not a permutation; `checkG` tests it). -/
def invArrG (n : Nat) (a : Array (Fin n)) : Option (Array (Fin n)) := do
  guard (a.size == n)
  let mut b : Array (Fin n) := a
  for i in List.finRange n do
    b := b.set! (a[i.val]?.getD i).val i
  return b

/-- Check one clause line with the general checker. -/
def checkLineG (h : Hdr) (n : Nat) (t : String) : Option Bool := do
  let rowArr := (rowPairsG n).toArray
  let (lits, p) ← parseLineG n rowArr h t
  let pinv ← invArrG n p
  let pos := if h.rowPos then rowPairsG n else colexPairsG n
  if let some bs := h.blocks then
    return checkGB n h.minOrder pos bs lits (fun v => p[v.val]?.getD v) (fun v => pinv[v.val]?.getD v)
  return checkG n h.minOrder pos h.d lits (fun v => p[v.val]?.getD v) (fun v => pinv[v.val]?.getD v)

/-- Inverse of a map given as an array (garbage if not a permutation; `checkSB` tests it). -/
def invArr (a : Array (Fin 40)) : Array (Fin 40) := Id.run do
  let mut b : Array (Fin 40) := Array.replicate 40 0
  for i in List.finRange 40 do
    b := b.set! (a[i.val]!).val i
  return b

/-- Process one line; returns the updated state or an error exit code. -/
structure St where
  hdr : Option Hdr := none
  ok : Nat := 0
  bad : Nat := 0
  lineNo : Nat := 0

def step (st : St) (line : String) : IO (Except UInt32 St) := do
  let st := { st with lineNo := st.lineNo + 1 }
  let t := line.trimAscii.toString
  if t.isEmpty then return .ok st
  if t.startsWith "c" then
    if (t.splitOn " ").take 2 == ["c", "order"] then
      match parseHdr t with
      | some h => return .ok { st with hdr := some h }
      | none => IO.println s!"FAIL line {st.lineNo}: bad header"; return .error 1
    return .ok st
  let some h := st.hdr | IO.println s!"FAIL line {st.lineNo}: clause before header"; return .error 1
  let res : Option Bool := match h.n with
    | some n => checkLineG h n t
    | none =>
      match parseLine h t with
      | none => none
      | some (lits, p) =>
        let pinv := invArr p
        let pos := if h.rowPos then rowPairs else colexPairs
        some (checkSB h.minOrder pos h.d lits (fun v => p[v.val]!) (fun v => pinv[v.val]!))
  match res with
  | none =>
    IO.println s!"FAIL line {st.lineNo}: parse error"
    return .ok { st with bad := st.bad + 1 }
  | some true => return .ok { st with ok := st.ok + 1 }
  | some false =>
    if st.bad < 20 then IO.println s!"FAIL line {st.lineNo}: clause not valid"
    return .ok { st with bad := st.bad + 1 }

/-- Read lines one at a time (constant memory); `-` = stdin. -/
partial def loop (hd : IO.FS.Stream) (st : St) : IO (Except UInt32 St) := do
  let line ← hd.getLine
  if line.isEmpty then return .ok st   -- end of input
  match ← step st line with
  | .error e => return .error e
  | .ok st' => loop hd st'

def main (args : List String) : IO UInt32 := do
  let some file := args.head? | IO.eprintln "usage: sbcheck FILE   (FILE = - for stdin)"; return 2
  let hd ← if file == "-" then IO.getStdin else IO.FS.Stream.ofHandle <$> IO.FS.Handle.mk file .read
  match ← loop hd {} with
  | .error e => return e
  | .ok st =>
    if st.bad == 0 && st.ok > 0 then
      IO.println s!"s VERIFIED {st.ok} clauses"
      return 0
    else
      IO.println s!"s FAILED {st.bad} of {st.ok + st.bad} clauses"
      return 1
