import sys
from agent.cpp_tests.build._deps.googletest-src.googletest.test.googletest-list-tests-unittest import Run
import json
try:
    res = Run()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
