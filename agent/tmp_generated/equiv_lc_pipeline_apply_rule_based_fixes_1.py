import sys
from agent.lc_pipeline import apply_rule_based_fixes
import json
try:
    res = apply_rule_based_fixes(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
