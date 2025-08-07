#!/usr/bin/env python3
"""Wrapper to run OS-002.1 with sudo python3"""
import subprocess
import sys
import os

# Get the actual script to run
script = os.path.join(os.path.dirname(__file__), "run_indexer.py")
cmd = ["sudo", "python3", script] + sys.argv[1:]

# Run with sudo
result = subprocess.run(cmd)
sys.exit(result.returncode)
