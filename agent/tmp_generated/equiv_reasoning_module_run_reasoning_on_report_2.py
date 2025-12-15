import sys
from agent.reasoning_module import run_reasoning_on_report
import json
try:
    res = run_reasoning_on_report(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
