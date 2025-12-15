import sys
from agent.cpp_tests.build._deps.googletest-src.googletest.test.googletest-filter-unittest import InvokeWithModifiedEnv
import json
try:
    res = InvokeWithModifiedEnv(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
