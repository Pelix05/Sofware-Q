import sys
from agent.lc_pipeline import apply_additional_rule_based_fixes_cpp
import json
try:
    res = apply_additional_rule_based_fixes_cpp(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
