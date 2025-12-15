import sys
from agent.dynamic_tester import run_concurrency_tests
import json
try:
    res = run_concurrency_tests(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
