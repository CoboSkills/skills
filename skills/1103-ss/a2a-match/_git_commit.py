#!/usr/bin/env python3
import subprocess, os

os.chdir(r'C:\Users\Administrator\.qclaw\workspace\a2a-match')

with open('_commit_msg.txt', 'r', encoding='utf-8') as f:
    msg = f.read().strip()

# Git add
subprocess.run(['git', 'add', 'SKILL.md'], check=True)

# Git commit
result = subprocess.run(['git', 'commit', '-m', msg], capture_output=True, text=True)
print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)

# Git push
result2 = subprocess.run(['git', 'push'], capture_output=True, text=True)
print('Push STDOUT:', result2.stdout)
print('Push STDERR:', result2.stderr)
