import sys
from agent.dynamic_tester import run_boundary_exception_tests
import json
try:
    res = run_boundary_exception_tests(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
