import sys
from agent.dynamic_tester import ensure_injected_googletest
import json
try:
    res = ensure_injected_googletest()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
