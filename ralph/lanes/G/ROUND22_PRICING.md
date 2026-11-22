# Round 22: `h=6` full-board pilot and launch terms

A's independent exact class comparison and all board/key maps passed before the two target pilots. Both used the same physical two-shore encoding (`full`), with no hole context or alignment fixed. See `scratch/G/round22/control.log` and `work/p{0,17}`.

| Board | Deficits | Gen + deterministic rebind CPU-s | Solve CPU-s | Two checkers CPU-s | Raw bytes | Compressed bytes |
|---|---|---:|---:|---:|---:|---:|
| 0 | both repeated | 9.25 | 0.02 | 0.21 | 1,799 | 578 |
| 17 | both separated | 13.30 | 36.36 | 13.69 | 123,241,484 | 37,076,194 |

Both rebinds matched byte for byte and both LRAT verifiers accepted. These are contrasting measurements, not tail bounds. The combined pilots, including compression/integrity check, took about 74 CPU-s. Using the SS pilot as a simple reservation reference for all 47 remaining boards gives ~0.85 core-h, ~1.74 GB compressed and about 5.8 GB raw cumulatively, **not** a guarantee. Baseline per-attempt limits: 900 solve CPU-s, 1,800 solve wall-s, 320 MiB raw proof, 5 GiB address space; generator and two verifiers have smaller independent CPU/wall limits. At 20 single-core workers, live raw finishes or rescues occupy at most 6.72 GB globally for this queue. A 5 GiB compressed archive gate, serialized compression, 100 GB filesystem free-space floor, and stop-on-archive/provenance failure leave margin below G's 14 GB reservation. With 47 attempts the worst allowed solver CPU is 11.75 core-h; no new worker is started for the two pilot boards. Split only capped boards; retain real failure types and don't credit a composite without a complete split cover.
