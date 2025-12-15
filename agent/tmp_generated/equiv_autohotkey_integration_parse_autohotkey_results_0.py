import sys
from agent.autohotkey_integration import parse_autohotkey_results
import json
try:
    res = parse_autohotkey_results()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
