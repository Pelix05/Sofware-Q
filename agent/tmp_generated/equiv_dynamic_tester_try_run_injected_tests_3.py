import sys
from agent.dynamic_tester import try_run_injected_tests
import json
try:
    res = try_run_injected_tests(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
