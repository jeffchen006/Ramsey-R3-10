# Critic job state

Round 5: the foreground A audit's outer `timeout 240s` returned 124,
but a nested timeout process group survived. Registering the critic's
own one-slot job before stopping it:

- Timeout PID `653141`, Python PID `653146`, cwd `scratch/critic/r5-A-out`.
- Command: `timeout 850s <root>/opt/venv/bin/python -B <root>/ralph/lanes/A/audit_high_residue_proofs.py audit <root>/scratch/G/round4 <root>/scratch/critic/r5-A-out/index-full.tsv --sample 0`.
- Log `scratch/critic/r5-A-out/proof-full.log`, index in the same directory; inner timeout would end about 22:12 CET on November 21, 2026.

Stopped via the registered timeout PID after checking its command line;
both PIDs are gone. The 6,114-line index prefix matches A's retained
index byte-for-byte. No live critic jobs.
