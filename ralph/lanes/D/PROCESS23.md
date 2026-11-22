# Historical launch ledger (superseded by current STATE)
## Round 23 active refill at 20:51, local node time
21:37 e18 monitor 2313339, timeout 2313315, hex/five_minute.jsonl, 0 solver slots, 6h wall/2GiB; writes hex/final23 only on empty remainder.
21:35 new 28-slot successor on 43 square-free t18 shapes, after each t17 replay completes; no overlap. `afterverify23.sh n` → `wingproof23.py squarefree18 n`, same caps, expected by 22:20 conditional on storage, 03:35 wall deadline. PIDs/timeouts/logs in square18r23:
    0	2233670	2233662	hex/e0.log
    1	2234038	2234008	hex/e1.log
    2	2234175	2234169	hex/e2.log
    3	2234238	2234216	hex/e3.log
    4	2234314	2234305	hex/e4.log
    5	2234389	2234382	hex/e5.log
    6	2234479	2234455	hex/e6.log
    7	2234522	2234517	hex/e7.log
    8	2234594	2234581	hex/e8.log
    9	2234665	2234650	hex/e9.log
    10	2234720	2234708	hex/e10.log
    11	2234799	2234791	hex/e11.log
    12	2234881	2234869	hex/e12.log
    13	2234954	2234940	hex/e13.log
    14	2235030	2235020	hex/e14.log
    15	2235104	2235094	hex/e15.log
    16	2235167	2235151	hex/e16.log
    17	2235301	2235280	hex/e17.log
    18	2235427	2235411	hex/e18.log
    19	2235560	2235547	hex/e19.log
    20	2236298	2236216	hex/e20.log
    21	2237146	2237011	hex/e21.log
    22	2237847	2237812	hex/e22.log
    23	2238576	2238556	hex/e23.log
    24	2239250	2239139	hex/e24.log
    25	2239640	2239630	hex/e25.log
    26	2239970	2239913	hex/e26.log
    27	2240116	2240094	hex/e27.log
21:30 freeze-on-completion PID 2000477 timeout 2000465, N/freeze.log, 0 solver cores; 1h wall/2400CPU, 2GiB, freezes final23 only after all keys cover.
21:30 wing observer 1975764 timeout 1975750 now reflects hub-certified aliases. Original observer exited.
21:27 replay successors after each wing producer exits (1-for-1; no active core before handoff), 20700 CPU/2GiB/6h, expected 21:45–22:30. `afterwing23.sh n` → `wingreplay23.py n`, CWD c6r23. PIDs/timeouts/logs:
    0	1870214	1870210	wing/verify/r0.log
    1	1870238	1870232	wing/verify/r1.log
    2	1870284	1870277	wing/verify/r2.log
    3	1870371	1870367	wing/verify/r3.log
    4	1870407	1870401	wing/verify/r4.log
    5	1870458	1870448	wing/verify/r5.log
    6	1870506	1870495	wing/verify/r6.log
    7	1870549	1870538	wing/verify/r7.log
    8	1870623	1870616	wing/verify/r8.log
    9	1870668	1870664	wing/verify/r9.log
    10	1870699	1870695	wing/verify/r10.log
    11	1870747	1870743	wing/verify/r11.log
    12	1870765	1870761	wing/verify/r12.log
    13	1870806	1870791	wing/verify/r13.log
    14	1870866	1870860	wing/verify/r14.log
    15	1870889	1870884	wing/verify/r15.log
    16	1870911	1870907	wing/verify/r16.log
    17	1870952	1870938	wing/verify/r17.log
    18	1871032	1871027	wing/verify/r18.log
    19	1871130	1871105	wing/verify/r19.log
    20	1871203	1871168	wing/verify/r20.log
    21	1871256	1871250	wing/verify/r21.log
    22	1871303	1871297	wing/verify/r22.log
    23	1871380	1871367	wing/verify/r23.log
    24	1871674	1871655	wing/verify/r24.log
    25	1871761	1871749	wing/verify/r25.log
    26	1871872	1871862	wing/verify/r26.log
    27	1872205	1872185	wing/verify/r27.log
21:24 correct leases (the two blank PIDs lower down were missing-script exits, no job). Verified:
    4	1691207	1691190	lease4.log
    27	1691388	1691366	lease27.log
21:23 m14 tail above priorities: temporarily STOP wing workers 4/27 only after draining their children. Their slots run lease23.sh n and per-shard anti-join; automatically CONT after repair. Expected ~21:32, timeout 90min, 1 core each in place of the stopped workers:
    4		1675846	lease4.log
    27		1676048	lease27.log
21:20 observer 1503305 timeout 1503302, 2h, 0 solver cores. Previous observer deliberately asserted on four duplicates; retained hash-identical overlap now indexed separately, zero additional keys or leaves.
21:18 single sequential queue 1412762 (timeout 1412747, 20700s/2GiB), m14r23/hard3hub.log: O_9850 all 11 sorted heads then all feasible residual hub count cells in c6r23, 1 core until ~21:25, hard deadline 03:18. Toy/125 + front/interior/tail prices in hubprice.log.
Wing status observer 1393376 timeout 1393311, started 21:18, 6h, wing/five_minute.jsonl, 0 solver cores.
21:15 guard-dir EXDEV repair: PID 1262346, timeout 1262281, static23.py 15 27 4, earlyrepair.log, 1 core, expect 21:28–21:41, same limits; subsequent successors repair own shard before wing.
21:13 wing successor standby: 28 `post23.sh n` in `scratch/D/c6r23`, each waits for matching static23 worker to exit before exec wingproof23.py shard n. Same 2GiB/20700s/6h wraps; expected finish 21:45–22:30 depending on tails/guard. No simultaneous slot duplication. PIDs/timeouts/logs:
    0	1156949	1156928	wing/p0.log
    1	1157186	1157144	wing/p1.log
    2	1157390	1157364	wing/p2.log
    3	1157530	1157514	wing/p3.log
    4	1157679	1157662	wing/p4.log
    5	1157915	1157883	wing/p5.log
    6	1158059	1158032	wing/p6.log
    7	1158156	1158142	wing/p7.log
    8	1158291	1158279	wing/p8.log
    9	1158401	1158379	wing/p9.log
    10	1158539	1158512	wing/p10.log
    11	1158647	1158635	wing/p11.log
    12	1158773	1158756	wing/p12.log
    13	1158990	1158955	wing/p13.log
    14	1159191	1159104	wing/p14.log
    15	1159400	1159365	wing/p15.log
    16	1159594	1159561	wing/p16.log
    17	1159801	1159773	wing/p17.log
    18	1160034	1160011	wing/p18.log
    19	1160283	1160253	wing/p19.log
    20	1160535	1160514	wing/p20.log
    21	1160712	1160675	wing/p21.log
    22	1161056	1161009	wing/p22.log
    23	1161209	1161191	wing/p23.log
    24	1161324	1161286	wing/p24.log
    25	1161547	1161501	wing/p25.log
    26	1161704	1161665	wing/p26.log
    27	1161827	1161801	wing/p27.log
21:10 replaced old observer with lift-aware 1044350, timeout 1044345, five_minute.jsonl, 2h, 0 solver cores.
21:06 hard worker 878401 timeout 878380, hardqueue23.py O_18931, hard2.log, 1 core 2GiB 20700 CPU/6h; expected 21:08. Previous hard worker finished.
21:05: SQLite queue drained (1,743 ready rows transferred intact); all old coordinators incl. worker 28 resumed/exited. Static23 now runs 28 disjoint workers in m14r23, same CPU/VM/timeout, expected 21:25 to 21:45, deadline 03:05. PIDs, timeout PIDs, logs:
    0	844778	844616	s0.log
    1	845917	845713	s1.log
    2	846148	846138	s2.log
    3	846203	846188	s3.log
    4	846302	846283	s4.log
    5	846347	846338	s5.log
    6	846393	846385	s6.log
    7	846430	846417	s7.log
    8	846473	846464	s8.log
    9	846501	846491	s9.log
    10	846533	846525	s10.log
    11	846581	846569	s11.log
    12	846636	846630	s12.log
    13	846675	846661	s13.log
    14	846708	846703	s14.log
    15	846748	846734	s15.log
    16	846808	846799	s16.log
    17	846851	846844	s17.log
    18	846899	846891	s18.log
    19	846957	846945	s19.log
    20	847032	846999	s20.log
    21	847612	847463	s21.log
    22	848088	848002	s22.log
    23	848591	848578	s23.log
    24	849269	849149	s24.log
    25	849425	849417	s25.log
    26	849456	849448	s26.log
    27	849498	849489	s27.log
21:02: worker 28 (437310) is STOPPED after its child drained; its one slot is leased to bounded `scratch/D/c6r23` controls and pricing. Resume once this lease ends.
Hard worker 520461 (timeout 520427, 6h/20700 CPU/2GiB), hardqueue23.py O_10800 O_5540, hardqueue.log, 1 core, 20:57, expected ~21:04.
Worker 28 437310 (timeout 437302) started 20:55, w28.log, same command/limits/deadline +6h; both last r22 workers finished. 29 regular + 1 hard/control.
Observer: 331482 (timeout 331441, 2h; five_minute.jsonl); aggregate completed child CPU every five minutes; no solver slot.
28 new one-core dispatch23 workers, CWD `scratch/D/m14r23`, `timeout 21600`, CPU 20700, VM 2GiB. Expected 21:15–21:35; deadline 02:51 Nov 23. Columns worker, PID, timeout PID, log:
    0	302322	302318	w0.log
    1	302390	302383	w1.log
    2	302407	302403	w2.log
    3	302416	302412	w3.log
    4	302433	302425	w4.log
    5	302471	302460	w5.log
    6	302542	302535	w6.log
    7	302593	302586	w7.log
    8	302637	302625	w8.log
    9	302671	302667	w9.log
    10	302684	302679	w10.log
    11	302697	302693	w11.log
    12	302711	302707	w12.log
    13	302727	302723	w13.log
    14	302742	302740	w14.log
    15	302765	302759	w15.log
    16	302776	302772	w16.log
    17	302794	302785	w17.log
    18	302984	302829	w18.log
    19	303224	303189	w19.log
    20	303429	303360	w20.log
    21	303620	303613	w21.log
    22	303699	303673	w22.log
    23	303817	303794	w23.log
    24	303909	303901	w24.log
    25	304241	304129	w25.log
    26	304440	304430	w26.log
    27	304517	304503	w27.log
Prior 2,686 handoff count REJECTED; the revised status is the manifest anti-join, not a sum across snapshots.

