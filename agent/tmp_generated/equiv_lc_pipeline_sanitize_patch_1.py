import sys
from agent.lc_pipeline import sanitize_patch
import json
try:
    res = sanitize_patch(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
