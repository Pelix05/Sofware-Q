import sys
from agent.lc_pipeline import aggressive_sanitize
import json
try:
    res = aggressive_sanitize(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
