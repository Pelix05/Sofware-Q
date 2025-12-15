import sys
from agent.dynamic_tester import run_full_regression_tests
import json
try:
    res = run_full_regression_tests(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
