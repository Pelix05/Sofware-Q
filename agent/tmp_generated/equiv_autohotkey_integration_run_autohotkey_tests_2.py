import sys
from agent.autohotkey_integration import run_autohotkey_tests
import json
try:
    res = run_autohotkey_tests(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
