/- Write lean/out/cube_{R,S8,N}.opb from the Lean definitions `R310.Files.cubeR/S8/N`.
Run: cd lean && lake env lean scripts/EmitCubes.lean -/
import R310.Files

open R310.Files

#eval show IO Unit from do
  IO.FS.createDirAll "out"
  for (name, cs) in [("cube_R.opb", cubeR), ("cube_S8.opb", cubeS8), ("cube_N.opb", cubeN)] do
    let hdr := s!"* generated from Lean R310.Files ({name}); constraints: {cs.length}\n"
    IO.FS.writeFile ("out/" ++ name) (hdr ++ renderFile cs)
    IO.println s!"{name}: {cs.length} constraints"
