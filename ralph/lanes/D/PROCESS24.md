# Lane D — round 24 live state, 2026-11-22

Scoped to regular R(3), K=2, either marked deficient path, t=18. Previous evidence and historical jobs: HANDOFF23.md. W=scratch/D/wing24. All previous PID wrappers have exited. No candidate.

**Verified carry-in (hand + enum + local cert):** 43 t=18 two-flap shapes, 2,752 roots, 17,709.94 production child CPU-s, 2,079,799,535 proof bytes. Both independent replay streams exited normally; exact key/shard join including all 2,752, 2,658.72 replay checker CPU-s (no new case credit), W/replay23.tsv, W/replay23.log, scratch/D/square18r23/hex/final23. The 17 hex shapes ruled out by the universal zero/one-flap lemma are disjoint.

**Live:** 30 one-core work24.py worker manifest i 30 coordinators, CWD W, W/worker<i>.log, 22:31:33 CET until ~22:44–22:55, hard deadline 04:31:33 CET. nice +5, 2GiB VM, 20,500s child CPU outer / 6h wall and separate per-stage limits. Four direct pilot attempts through dual checks incl one cap. Independently checked 360 distinct patch decks over all remaining 57, no zero-deck shapes. W/PRICE.txt, roster1.log, audit.log, cal2.log. 32 shapes x5, 25 x8. Raw/trim/CNF/packed guards 32/55/19/25MB, one 110MB reservation per active slot, 5.55GB total.

Slot | worker PID | timeout PID | log
---:|---:|---:|---
0 | 3939449 | 3939365 | worker0.log
1 | 3939441 | 3939366 | worker1.log
2 | 3939481 | 3939367 | worker2.log
3 | 3939420 | 3939369 | worker3.log
4 | 3939407 | 3939370 | worker4.log
5 | 3939423 | 3939371 | worker5.log
6 | 3939412 | 3939372 | worker6.log
7 | 3939419 | 3939373 | worker7.log
8 | 3939421 | 3939374 | worker8.log
9 | 3939434 | 3939375 | worker9.log
10 | 3939410 | 3939376 | worker10.log
11 | 3939414 | 3939377 | worker11.log
12 | 3939430 | 3939378 | worker12.log
13 | 3939417 | 3939379 | worker13.log
14 | 3939426 | 3939380 | worker14.log
15 | 3939408 | 3939382 | worker15.log
16 | 3939402 | 3939383 | worker16.log
17 | 3939415 | 3939384 | worker17.log
18 | 3939493 | 3939385 | worker18.log
19 | 3939450 | 3939386 | worker19.log
20 | 3939504 | 3939387 | worker20.log
21 | 3939406 | 3939388 | worker21.log
22 | 3939471 | 3939389 | worker22.log
23 | 3939422 | 3939390 | worker23.log
24 | 3939495 | 3939391 | worker24.log
25 | 3939418 | 3939392 | worker25.log
26 | 3939440 | 3939393 | worker26.log
27 | 3939435 | 3939394 | worker27.log
28 | 3939409 | 3939395 | worker28.log
29 | 3939478 | 3939396 | worker29.log

22:35: slot24.sh i (all 30 reserved successors, one core only AFTER the corresponding prior PID exits; W/tail<i>.log, nice +5 / VM 2GiB / CPU 20,500 / 6h wall, expected ~23:00 CET; 04:35 deadline). Fifth-site full census 2,074 possible leaves pre-dedup, 135 five-site census controls; only unresolved roots eligible. Real PID/timeout/log below. Observer watch24 PID 3985471 timeout 3985407, 0 solver slots, W/five_minute.jsonl.
    0	4085944	4085876	tail0.log
    1	4085935	4085877	tail1.log
    2	4085928	4085878	tail2.log
    3	4085948	4085879	tail3.log
    4	4085940	4085880	tail4.log
    5	4085964	4085882	tail5.log
    6	4085963	4085883	tail6.log
    7	4085943	4085885	tail7.log
    8	4085949	4085886	tail8.log
    9	4085954	4085888	tail9.log
    10	4085966	4085889	tail10.log
    11	4085932	4085890	tail11.log
    12	4085946	4085891	tail12.log
    13	4085936	4085892	tail13.log
    14	4085941	4085893	tail14.log
    15	4085961	4085894	tail15.log
    16	4085938	4085895	tail16.log
    17	4085990	4085896	tail17.log
    18	4085956	4085897	tail18.log
    19	4085947	4085898	tail19.log
    20	4085955	4085899	tail20.log
    21	4085939	4085900	tail21.log
    22	4085929	4085901	tail22.log
    23	4085974	4085902	tail23.log
    24	4085987	4085903	tail24.log
    25	4085976	4085904	tail25.log
    26	4085959	4085905	tail26.log
    27	4085970	4085906	tail27.log
    28	4085969	4085908	tail28.log
    29	4085950	4085909	tail29.log

22:43: follow24.py i, 30 per-slot successors to slot24.sh, only after those exit; CWD W, nice +5, 2GiB, 20,500s CPU/6h wall, 04:43 hard deadline. Tail plan = 319 remaining complementary leaves for 24 capped leader keys; all five price pilots passed physical duals. High24 fully priced; high23 gated separately. W/followpids.tsv (slot, real PID, timeout PID, log):
    0	235696	235655	follow0.log
    1	235742	235656	follow1.log
    2	235710	235657	follow2.log
    3	235721	235658	follow3.log
    4	235738	235659	follow4.log
    5	235732	235660	follow5.log
    6	235706	235661	follow6.log
    7	235695	235662	follow7.log
    8	235697	235663	follow8.log
    9	235702	235664	follow9.log
    10	235704	235666	follow10.log
    11	235709	235667	follow11.log
    12	235701	235669	follow12.log
    13	235745	235670	follow13.log
    14	235707	235671	follow14.log
    15	235756	235672	follow15.log
    16	235711	235673	follow16.log
    17	235700	235674	follow17.log
    18	235733	235675	follow18.log
    19	235703	235676	follow19.log
    20	235730	235677	follow20.log
    21	235713	235678	follow21.log
    22	235726	235679	follow22.log
    23	235722	235680	follow23.log
    24	235755	235681	follow24.log
    25	235705	235682	follow25.log
    26	235743	235683	follow26.log
    27	235765	235684	follow27.log
    28	235699	235685	follow28.log
    29	235744	235687	follow29.log

22:59: sweep24.py i, CWD W, nice+5, 2GiB/20,500s/6h, 04:59 hard deadline, follows the same follow24 slot only after it exits. 567 used t18 proofs replay then density21 and priority repair batches, no duplicate credit. Smaller 60MB reservations for 6-site compact square proofs; 110MB otherwise. PID/timeout/log:
    0	1006020	1005976	sweep0.log
    1	1006014	1005977	sweep1.log
    2	1006023	1005978	sweep2.log
    3	1006061	1005979	sweep3.log
    4	1006012	1005980	sweep4.log
    5	1006025	1005981	sweep5.log
    6	1006029	1005982	sweep6.log
    7	1006034	1005983	sweep7.log
    8	1006032	1005984	sweep8.log
    9	1006053	1005985	sweep9.log
    10	1006044	1005986	sweep10.log
    11	1006047	1005987	sweep11.log
    12	1006063	1005988	sweep12.log
    13	1006031	1005990	sweep13.log
    14	1006059	1005991	sweep14.log
    15	1006036	1005993	sweep15.log
    16	1006050	1005994	sweep16.log
    17	1006068	1005995	sweep17.log
    18	1006067	1005996	sweep18.log
    19	1006049	1005997	sweep19.log
    20	1006022	1005998	sweep20.log
    21	1006037	1005999	sweep21.log
    22	1006033	1006000	sweep22.log
    23	1006038	1006001	sweep23.log
    24	1006041	1006002	sweep24.log
    25	1006024	1006003	sweep25.log
    26	1006035	1006006	sweep26.log
    27	1006064	1006007	sweep27.log
    28	1006065	1006008	sweep28.log
    29	1006026	1006009	sweep29.log
Final active sweep: all four earlier waves have drained including both inherited stream PIDs. Coordinator 235696 was deliberately stopped only after its scoped child was done to reserve a single pilot slot; resumed after all pilots and now exited. No stopped job remains. Observer PID 1080054 timeout 1080038 (nice +5/2GiB/CPU1500/6h, 23:00–05:00 CET) records booked-session CPU deltas, actual live and reserved bytes and per-density anti-joins in W/campaign.jsonl.
23:08 transition: replay lease removal raced with a new work slot reading its size. This occurred BEFORE reserving a production key, not during proof checking. Replaced only confirmed exited sweep coordinators using `W/replacement.tsv`; all started at 23:08, same one-core slot, same 2GiB/20500s/6h deadline, new log `replacementN.log`. New workers skip already persisted replay keys. `W/activepids.tsv` supersedes the prior launch list; new process numbers copied to STATE. All old unique proof archives retained.
0	1516262	1516256	replacement0.log
1	1516367	1516359	replacement1.log
3	1516491	1516482	replacement3.log
4	1516591	1516583	replacement4.log
5	1516679	1516667	replacement5.log
9	1516806	1516797	replacement9.log
11	1516932	1516910	replacement11.log
12	1517037	1517023	replacement12.log
13	1517426	1517384	replacement13.log
16	1517905	1517883	replacement16.log
17	1518541	1518515	replacement17.log
18	1518863	1518854	replacement18.log
19	1518983	1518969	replacement19.log
20	1519248	1519217	replacement20.log
21	1519338	1519326	replacement21.log
22	1519441	1519428	replacement22.log
23	1519537	1519530	replacement23.log
24	1519689	1519669	replacement24.log
25	1519804	1519786	replacement25.log
26	1519944	1519929	replacement26.log
29	1520046	1520042	replacement29.log
