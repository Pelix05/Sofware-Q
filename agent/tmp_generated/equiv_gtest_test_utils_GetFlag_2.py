import sys
from agent.cpp_tests.build._deps.googletest-src.googletest.test.gtest_test_utils import GetFlag
import json
try:
    res = GetFlag(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
