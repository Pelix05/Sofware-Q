import sys
from agent.dynamic_tester import run_cpp_unit_tests
import json
try:
    res = run_cpp_unit_tests()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
