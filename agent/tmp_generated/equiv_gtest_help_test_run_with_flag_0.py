import sys
from agent.cpp_tests.build._deps.googletest-src.googletest.test.gtest_help_test import run_with_flag
import json
try:
    res = run_with_flag()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
