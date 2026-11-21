#!/usr/bin/env python3
"""Checks that the r310_ralph flow runs itself, so that no agent can change a verdict.

    python3 -I gate.py ROOT scan                 new graph6 files in ralph/found/: is any a (3,10,40)-graph?
    python3 -I gate.py ROOT check FILE [N K]     check one graph6 file (default N=40, K=10)
    python3 -I gate.py ROOT cores CAP KILL MEMGB  workspace processes; kill the newest beyond KILL x CAP,
                                                  and the newest ones while their RSS sum is over MEMGB
    python3 -I gate.py ROOT disk                 size of ROOT/scratch in GB
    python3 -I gate.py ROOT commit ROUND [LABEL] git commit of the round; new files over 5 MB are not committed

Each command prints one JSON object on its last stdout line. State is kept in ROOT/ralph/.gate/.

A (3,10,40)-graph is a graph on 40 vertices with no triangle and no independent set of 10 vertices.
If one exists, R(3,10) = 41. Two independent algorithms must both agree before the flow says so.
"""

import json
import os
import signal
import subprocess
import sys
from pathlib import Path

BIG = 5 << 20
TICKS = os.sysconf('SC_CLK_TCK')
PAGE = os.sysconf('SC_PAGE_SIZE')
LANES = 'ABCDEFGH'
NOT_WORK = {'claude', 'node', 'codex', 'hmz', 'bash', 'sh', 'zsh', 'dash', 'ps', 'timeout',
            'nohup', 'setsid', 'sleep', 'tee', 'tail', 'head', 'cat', 'less', 'git', 'watch',
            'ssh', 'tmux', 'screen', 'flock', 'xargs', 'wait', 'env', 'time', 'uv', 'uvx',
            'rg', 'grep', 'sed', 'awk', 'find', 'du', 'ls', 'curl', 'wget'}


def gate_dir(root):
    d = root / 'ralph' / '.gate'
    d.mkdir(parents=True, exist_ok=True)
    return d


def load(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def save(path, value):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=1, sort_keys=True))
    tmp.replace(path)


# ---------------------------------------------------------------- graph6 and the two checks

def parse_graph6(line):
    """Decode one graph6 line (n < 63) into a list of neighbour sets. Raises ValueError."""
    s = line.strip()
    if s.startswith('>>graph6<<'):
        s = s[10:]
    if not s or any(not 63 <= ord(c) <= 126 for c in s):
        raise ValueError('not graph6')
    n = ord(s[0]) - 63
    if n >= 63:
        raise ValueError('n >= 63 is not supported')
    bits = []
    for c in s[1:]:
        v = ord(c) - 63
        bits.extend((v >> (5 - i)) & 1 for i in range(6))
    need = n * (n - 1) // 2
    if len(bits) < need or len(s) - 1 != (need + 5) // 6:
        raise ValueError(f'wrong length for n={n}')
    nbr = [set() for _ in range(n)]
    k = 0
    for j in range(1, n):          # graph6 order: (0,1), (0,2), (1,2), (0,3), ...
        for i in range(j):
            if bits[k]:
                nbr[i].add(j)
                nbr[j].add(i)
            k += 1
    return nbr


def triangle_free_a(nbr):
    """Method A: bitsets; an edge uv lies in a triangle iff N(u) and N(v) meet."""
    masks = [sum(1 << w for w in s) for s in nbr]
    return all(not (masks[u] & masks[v]) for u in range(len(nbr)) for v in nbr[u] if u < v)


def triangle_free_b(nbr):
    """Method B: plain triple loop over vertex triples."""
    n = len(nbr)
    for a in range(n):
        for b in range(a + 1, n):
            if b not in nbr[a]:
                continue
            for c in range(b + 1, n):
                if c in nbr[a] and c in nbr[b]:
                    return False
    return True


def has_independent_a(nbr, k):
    """Method A: does G have an independent set of size k? Bitset DFS with a clique-cover bound
    (in a triangle-free graph a clique is a vertex or an edge, so a greedy matching gives the bound)."""
    n = len(nbr)
    adj = [sum(1 << w for w in s) for s in nbr]

    def bound(cand):
        size, rem = 0, cand
        while rem:
            u = rem & -rem
            ui = u.bit_length() - 1
            rem ^= u
            w = adj[ui] & rem
            if w:
                rem ^= w & -w
            size += 1
        return size

    def rec(cand, need):
        if need == 0:
            return True
        while cand:
            if bin(cand).count('1') < need or bound(cand) < need:
                return False
            v = cand.bit_length() - 1
            cand &= ~(1 << v)
            if rec(cand & ~adj[v], need - 1):
                return True
        return False

    return rec((1 << n) - 1, k)


def max_independent_b(nbr, k):
    """Method B: Bron-Kerbosch with pivot over the complement graph, on Python sets.
    Returns the largest independent set size found, stopping early once it reaches k."""
    n = len(nbr)
    non = [set(range(n)) - nbr[v] - {v} for v in range(n)]
    best = 0

    def bk(r, p, x):
        nonlocal best
        if best >= k:
            return
        if not p and not x:
            best = max(best, r)
            return
        if r + len(p) <= best:
            return
        u = max(p | x, key=lambda w: len(non[w] & p))
        for v in list(p - non[u]):
            bk(r + 1, p & non[v], x & non[v])
            p = p - {v}
            x = x | {v}

    bk(0, set(range(n)), set())
    return best


def check_file(path, n_want=40, k=10):
    """Every graph in the file; a graph counts only if both methods say: n, triangle-free, alpha < k."""
    out = []
    try:
        lines = [ln for ln in Path(path).read_text().splitlines() if ln.strip()]
    except OSError as error:
        return [{'line': 0, 'ok': False, 'why': f'unreadable: {error}'}]
    for i, line in enumerate(lines[:1000], 1):
        try:
            nbr = parse_graph6(line)
        except ValueError as error:
            out.append({'line': i, 'ok': False, 'why': str(error)})
            continue
        n = len(nbr)
        if n != n_want:
            out.append({'line': i, 'ok': False, 'n': n, 'why': f'n = {n}, not {n_want}'})
            continue
        ta, tb = triangle_free_a(nbr), triangle_free_b(nbr)
        if not (ta and tb):
            out.append({'line': i, 'ok': False, 'n': n, 'why': f'has a triangle (A {ta}, B {tb})'})
            continue
        ia = has_independent_a(nbr, k)
        ib = max_independent_b(nbr, k)
        ok = (not ia) and ib < k
        why = 'ok' if ok else f'independent set of size {k} (A {ia}, B max {ib})'
        if ia != (ib >= k):
            why = f'METHODS DISAGREE (A {ia}, B {ib}); not counted'
            ok = False
        out.append({'line': i, 'ok': ok, 'n': n, 'edges': sum(map(len, nbr)) // 2,
                    'degrees': sorted({len(s) for s in nbr}), 'why': why})
    if len(lines) > 1000:
        out.append({'line': 1001, 'ok': False, 'why': f'only the first 1000 of {len(lines)} lines checked'})
    return out


def scan(root):
    """Every graph6 file under ralph/found/ that is new or changed since the last scan."""
    seen_path = gate_dir(root) / 'seen.json'
    seen = load(seen_path, {})
    found = []
    base = root / 'ralph' / 'found'
    for path in sorted(base.rglob('*.g6')) if base.is_dir() else []:
        if path.is_symlink() or not path.is_file():
            continue
        st = path.stat()
        key = str(path.relative_to(root))
        stamp = f'{st.st_mtime_ns}:{st.st_size}'
        if seen.get(key) == stamp:
            continue
        seen[key] = stamp
        try:
            # Its own process and a time limit: a file can never stall the flow.
            res = subprocess.run([sys.executable, '-I', __file__, str(root), 'check', str(path)],
                                 capture_output=True, text=True, timeout=1800)
            graphs = json.loads(res.stdout.strip().splitlines()[-1])['graphs']
        except (OSError, ValueError, IndexError, KeyError, subprocess.TimeoutExpired) as error:
            graphs = [{'line': 0, 'ok': False, 'why': f'check failed: {type(error).__name__}'}]
        found.append({'path': key, 'valid_graphs': [g['line'] for g in graphs if g['ok']],
                      'graphs': graphs[:20]})
    save(seen_path, seen)
    return {'checked': found}


# ---------------------------------------------------------------- processes, disk, commit

def inside(path, root):
    try:
        return Path(path).resolve().is_relative_to(root)
    except OSError:
        return False


def lane_of(root, cwd, argv):
    for text in [cwd, *argv[:4]]:
        for sub in ('scratch', 'ralph/lanes'):
            prefix = f'{root}/{sub}/'
            if text.startswith(prefix):
                lane = text[len(prefix):].split('/', 1)[0]
                if lane in LANES:
                    return lane
    return '?'


def cores(root, cap, kill_factor, mem_gb):
    """Solver processes whose cwd, program or first arguments are in this workspace."""
    me, flow_pid = os.getuid(), os.getppid()
    work = []
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if entry.stat().st_uid != me:
                continue
            argv = [a.decode(errors='replace') for a in (entry / 'cmdline').read_bytes().split(b'\0') if a]
            comm = (entry / 'comm').read_text().strip()
            cwd = os.readlink(entry / 'cwd')
            exe = os.readlink(entry / 'exe')
            state = (entry / 'stat').read_text().rsplit(')', 1)[1].split()
        except (OSError, IndexError):
            continue
        pid = int(entry.name)
        if not argv or pid in (os.getpid(), flow_pid) or comm in NOT_WORK:
            continue
        if any(Path(a).name == 'hmz' for a in argv[:2]):
            continue
        if not (inside(cwd, root) or inside(exe, root) or any(a.startswith(str(root)) for a in argv[:4])):
            continue
        cpu = (int(state[11]) + int(state[12])) / TICKS
        rss = int(state[21]) * PAGE
        if state[0] not in 'RD' and cpu < 60 and rss < (1 << 30):
            continue
        work.append({'pid': pid, 'start': int(state[19]), 'cpu': round(cpu), 'rss_gb': round(rss / 2**30, 1),
                     'stat': state[0], 'lane': lane_of(root, cwd, argv), 'args': ' '.join(argv)[:160]})
    work.sort(key=lambda p: p['start'])
    busy = [p for p in work if p['stat'] in 'RDS']  # stopped (T) processes use no core
    killed = []

    def kill(proc, why):
        try:
            os.kill(proc['pid'], signal.SIGTERM)
            killed.append({**proc, 'why': why})
        except OSError:
            pass

    if kill_factor > 0 and len(busy) > kill_factor * cap:
        for proc in busy[int(kill_factor * cap):]:
            if proc['cpu'] >= 10:
                kill(proc, 'over core cap')
    total = sum(p['rss_gb'] for p in work)
    if mem_gb > 0 and total > mem_gb:
        for proc in reversed(work):
            if total <= mem_gb:
                break
            if proc['rss_gb'] >= 1 and all(k['pid'] != proc['pid'] for k in killed):
                kill(proc, 'over RAM cap')
                total -= proc['rss_gb']
    per_lane = {}
    for p in busy:
        per_lane[p['lane']] = per_lane.get(p['lane'], 0) + 1
    return {'count': len(busy), 'cap': cap, 'per_lane': dict(sorted(per_lane.items())),
            'rss_gb': round(sum(p['rss_gb'] for p in work), 1), 'mem_cap_gb': mem_gb,
            'stopped': len(work) - len(busy), 'killed': killed}


def disk(root):
    target = root / 'scratch'
    try:
        out = subprocess.run(['du', '-sb', str(target)], capture_output=True, text=True, timeout=300)
        size = int(out.stdout.split()[0])
    except (OSError, ValueError, IndexError, subprocess.TimeoutExpired) as error:
        return {'error': f'du failed: {type(error).__name__}'}
    try:
        st = os.statvfs(root)
        free = st.f_bavail * st.f_frsize
    except OSError:
        free = 0
    return {'scratch_gb': round(size / 1e9, 1), 'fs_free_gb': round(free / 1e9)}


def commit(root, round_no, label='r310_ralph'):
    def git(*args):
        return subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
    untracked = git('ls-files', '--others', '--exclude-standard', '-z').stdout.split('\0')
    big = [p for p in untracked if p and (root / p).is_file() and (root / p).stat().st_size > BIG]
    if big:
        with open(root / '.git' / 'info' / 'exclude', 'a') as fh:
            fh.write(''.join(f'/{p}\n' for p in big))
    git('add', '-A')
    out = git('-c', f'user.name={label}', '-c', 'user.email=r310_ralph@localhost',
              'commit', '-q', '--no-verify', '-m', f'{label}: round {round_no}')
    head = git('rev-parse', '--short', 'HEAD').stdout.strip()
    return {'committed': out.returncode == 0, 'head': head, 'excluded_big': big[:50]}


def main():
    root = Path(sys.argv[1]).resolve()
    command = sys.argv[2]
    if command == 'scan':
        result = scan(root)
    elif command == 'check':
        n, k = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (40, 10)
        result = {'graphs': check_file(sys.argv[3], n, k)}
    elif command == 'cores':
        result = cores(root, int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))
    elif command == 'disk':
        result = disk(root)
    elif command == 'commit':
        result = commit(root, int(sys.argv[3]), *sys.argv[4:5])
    else:
        raise SystemExit(f'unknown command {command}')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
