import sys
from agent.dynamic_tester import run_environment_dependency_tests
import json
try:
    res = run_environment_dependency_tests(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
