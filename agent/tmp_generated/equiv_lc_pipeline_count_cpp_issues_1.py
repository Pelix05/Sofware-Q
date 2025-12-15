import sys
from agent.lc_pipeline import count_cpp_issues
import json
try:
    res = count_cpp_issues(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
