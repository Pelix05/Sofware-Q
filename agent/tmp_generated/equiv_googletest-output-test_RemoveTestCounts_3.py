import sys
from agent.cpp_tests.build._deps.googletest-src.googletest.test.googletest-output-test import RemoveTestCounts
import json
try:
    res = RemoveTestCounts(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
