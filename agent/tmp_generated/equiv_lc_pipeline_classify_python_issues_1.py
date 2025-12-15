import sys
from agent.lc_pipeline import classify_python_issues
import json
try:
    res = classify_python_issues(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
