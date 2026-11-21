#!/usr/bin/env python3
"""Run a command under a Landlock write fence: it (and every process it starts, detached or not)
may write only beneath the given directories. Reading and the network are not restricted.

    fence.py DIR [DIR ...] -- CMD [ARG ...]

Unlike a mount sandbox, Landlock does not end the processes when the command ends, so detached
solver jobs keep running after a turn, still inside the fence. Exits 97 if Landlock is missing.
"""

import ctypes
import os
import sys

SYS_CREATE, SYS_ADD, SYS_RESTRICT = 444, 445, 446  # x86_64
PR_SET_NO_NEW_PRIVS = 38
RULE_PATH_BENEATH = 1
WRITE_FILE, REMOVE_DIR, REMOVE_FILE = 1 << 1, 1 << 4, 1 << 5
MAKE = sum(1 << i for i in range(6, 13))            # char, dir, reg, sock, fifo, block, sym
WRITES = WRITE_FILE | REMOVE_DIR | REMOVE_FILE | MAKE


class RulesetAttr(ctypes.Structure):
    _fields_ = [('handled_access_fs', ctypes.c_uint64)]


class PathBeneath(ctypes.Structure):
    _pack_ = 1
    _fields_ = [('allowed_access', ctypes.c_uint64), ('parent_fd', ctypes.c_int32)]


def main():
    if '--' not in sys.argv:
        raise SystemExit(__doc__)
    i = sys.argv.index('--')
    dirs, cmd = sys.argv[1:i], sys.argv[i + 1:]
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long
    attr = RulesetAttr(WRITES)
    fd = libc.syscall(SYS_CREATE, ctypes.byref(attr), ctypes.c_size_t(ctypes.sizeof(attr)), 0)
    if fd < 0:
        print(f'fence.py: landlock unavailable (errno {ctypes.get_errno()})', file=sys.stderr)
        sys.exit(97)
    for d in dirs:
        try:
            pfd = os.open(d, os.O_PATH | os.O_CLOEXEC)
        except OSError:
            continue  # a directory that does not exist needs no rule
        rule = PathBeneath(WRITES, pfd)
        if libc.syscall(SYS_ADD, fd, RULE_PATH_BENEATH, ctypes.byref(rule), 0) != 0:
            print(f'fence.py: cannot add {d} (errno {ctypes.get_errno()})', file=sys.stderr)
            sys.exit(97)
        os.close(pfd)
    if libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0 or libc.syscall(SYS_RESTRICT, fd, 0) != 0:
        print(f'fence.py: cannot restrict (errno {ctypes.get_errno()})', file=sys.stderr)
        sys.exit(97)
    os.close(fd)
    os.execvp(cmd[0], cmd)


if __name__ == '__main__':
    main()
