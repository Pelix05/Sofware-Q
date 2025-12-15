import sys
from agent.cpp_tests.build._deps.googletest-src.googletest.test.gtest_help_test import is_bsd_based_os
import json
try:
    res = is_bsd_based_os(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
