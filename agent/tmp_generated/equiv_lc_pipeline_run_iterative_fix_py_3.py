import sys
from agent.lc_pipeline import run_iterative_fix_py
import json
try:
    res = run_iterative_fix_py(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
