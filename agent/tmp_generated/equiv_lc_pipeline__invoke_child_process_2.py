import sys
from agent.lc_pipeline import _invoke_child_process
import json
try:
    res = _invoke_child_process(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
