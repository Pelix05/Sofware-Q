import sys
from agent.cpp_tests.build._deps.googletest-src.googletest.test.googletest-color-test import UsesColor
import json
try:
    res = UsesColor()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
