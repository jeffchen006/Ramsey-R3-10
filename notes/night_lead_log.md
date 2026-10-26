## 2026-10-25 13:15 call 1/6
- Event: IDLE duo (adv5 EXIT rc=0, 36m). Earlier adv6 CRASH rc=127 at 11:36 (0s, likely bad command).
- No notes/status/duo.md and no duo next step in PROGRESS.md -> started nothing. Queue: only WAITING jobs (sms, symsat), not blocked.
- Mailed duo and lead. Waits for day: duo next plan; teamstat shows cases MEM>CAP (403G rss, cap 16G).
- 2026-10-25 13:18 call 2/6. Events: CRASH sms/f6probe0-3 rc=-15 (SIGTERM 13:16, 1h32m, not timeout 4h).
  sms status file already records the kill; 3 probes finished, no drop seen. Cause unknown -> not a clear transient cause, no re-run.
  Mailed sms and lead. sms/Rc7b_cert still runs on 38 CPUs.
  Waits for day: sms decides about f6 probes; who sent SIGTERM.
- 2026-10-25 13:34 call 3/6. Event: IDLE duo after codex_r3 EXIT rc=0 (17m57s).
  Still no notes/status/duo.md and no duo next step in PROGRESS.md -> started nothing. Queue: 2 WAITING (sms, symsat), none blocked.
  Mailed duo and lead.
  Waits for day: duo needs a status file and a plan.
- 2026-10-25 13:37 call 4/6. Event: IDLE duo after adv39 EXIT rc=0 (33s).
  Same state as call 3: no notes/status/duo.md, no duo next step in PROGRESS.md -> started nothing. Queue: 2 WAITING, none blocked.
  duo starts short jobs itself (live tmux session?), so no new mail (duo has 11 unread, lead already told).
  Waits for day: duo status file + plan; watchd IDLE events for duo use night-lead calls (4/6 used) - lead may want to mute them.
- 2026-10-25 13:42 call 5/6. Event: IDLE cases after mforce_sel EXIT rc=0 (42s).
  notes/status/cases.md (updated 13:40, agent live) has no written next job; mforce_sel was its only "Running" item -> started nothing. Queue: 2 WAITING (sms, symsat), none blocked.
  Mailed lead only (cases is live; no new mail to it).
  Waits for day: cases next step (mforce_sel result); IDLE events from live agents used 5/6 calls - only 1 call left for 12 h; lead should mute IDLE for live tmux agents.
