import sys
from agent.lc_pipeline import apply_patch
import json
try:
    res = apply_patch(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
