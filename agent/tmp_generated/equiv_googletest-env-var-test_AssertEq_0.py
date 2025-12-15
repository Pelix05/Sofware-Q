import sys
from agent.cpp_tests.build._deps.googletest-src.googletest.test.googletest-env-var-test import AssertEq
import json
try:
    res = AssertEq()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
