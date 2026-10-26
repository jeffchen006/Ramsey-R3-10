#!/usr/bin/env python3
"""Wrapper: runs the C++ converter sms/lratlog2lrat (byte-identical output to the
reference Python implementation sms/lratlog2lrat_ref.py, which documents the formats)."""
import os
import sys
exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lratlog2lrat")
os.execv(exe, [exe] + sys.argv[1:])
