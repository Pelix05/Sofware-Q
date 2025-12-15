import sys
from agent.lc_pipeline import parse_dynamic_issues
import json
try:
    res = parse_dynamic_issues()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
