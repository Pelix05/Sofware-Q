import sys
from agent.autohotkey_integration import generate_autohotkey_tests
import json
try:
    res = generate_autohotkey_tests(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
