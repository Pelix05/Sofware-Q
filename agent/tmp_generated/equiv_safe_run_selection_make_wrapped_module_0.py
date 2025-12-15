import sys
from agent.safe_run_selection import make_wrapped_module
import json
try:
    res = make_wrapped_module()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
