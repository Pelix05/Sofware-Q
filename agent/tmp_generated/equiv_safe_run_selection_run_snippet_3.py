import sys
from agent.safe_run_selection import run_snippet
import json
try:
    res = run_snippet(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
