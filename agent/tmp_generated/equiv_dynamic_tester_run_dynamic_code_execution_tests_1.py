import sys
from agent.dynamic_tester import run_dynamic_code_execution_tests
import json
try:
    res = run_dynamic_code_execution_tests(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
