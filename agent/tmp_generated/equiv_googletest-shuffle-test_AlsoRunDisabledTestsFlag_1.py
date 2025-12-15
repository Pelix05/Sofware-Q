import sys
from agent.cpp_tests.build._deps.googletest-src.googletest.test.googletest-shuffle-test import AlsoRunDisabledTestsFlag
import json
try:
    res = AlsoRunDisabledTestsFlag(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
