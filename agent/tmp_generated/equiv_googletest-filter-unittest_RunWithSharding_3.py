import sys
from agent.cpp_tests.build._deps.googletest-src.googletest.test.googletest-filter-unittest import RunWithSharding
import json
try:
    res = RunWithSharding(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
