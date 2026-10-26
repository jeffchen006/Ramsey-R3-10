#!/bin/bash
cd .
./runs/pilot/codex/bin/codex exec resume --skip-git-repo-check <id> -c model_reasoning_effort=xhigh -c sandbox_mode="read-only" -o duo/codex_r6.md - < duo/codex_r6.txt
