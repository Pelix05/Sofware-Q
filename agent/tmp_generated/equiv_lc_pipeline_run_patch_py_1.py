import sys
from agent.lc_pipeline import run_patch_py
import json
try:
    res = run_patch_py(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
