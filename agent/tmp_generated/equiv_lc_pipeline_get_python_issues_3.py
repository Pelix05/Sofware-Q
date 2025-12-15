import sys
from agent.lc_pipeline import get_python_issues
import json
try:
    res = get_python_issues(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
