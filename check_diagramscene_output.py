#!/usr/bin/env python
"""Check DiagramScene output"""
import subprocess

cmd = 'D:\\flowchart_test\\diagramscene.exe --help'
result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)

print(f"Return code: {result.returncode}")
print(f"Stdout:\n{result.stdout}")
print(f"Stderr:\n{result.stderr}")
