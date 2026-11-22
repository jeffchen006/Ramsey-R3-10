# Round 20 — one-shore test only

Apply the exact factorization in `proofs/panel20_factored_card.md` to
the already frozen 116 right frames at `(75,5)` with a triple. Take
both flag settings independently of the round-19 pair margins. Report
the original group sizes, number of legal rows, numbers passing each
flag, one physical witness per live key and all failed right keys.
Use the old 578-row file only for a frozen literal comparison; do not
generate any pairs or rerun any margins or signed joins. If every
right frame passes both settings, stop. Otherwise report exact failing
keys and price, but do not perform, a physical margin intersection.

Before the full scan: the C35 control recovered 840 planted rows (105
marked root pairs) with literal restorations in success and masked
failure settings. Four smaller labelled perturbations handled original
size five and the marked-pair bound. Twelve evenly spaced right keys
(`index % 10 == 0` in the fixed roster) took **0.83 CPU-s** and 36,792
KiB peak RSS including file scan, raw template binding and both checks.
They had 554 legal rows, all 554 passing tau=4, 380 passing tau=3, and
12/12 keys live for both flags. Even charging the entire sample linearly
forecasts ~8.0 CPU-s for 116; budget 45 CPU-s per full replay, one
worker, 512 MiB VM, under the shared 0.08 core-h cap including controls
and clean replay. No detached work.
