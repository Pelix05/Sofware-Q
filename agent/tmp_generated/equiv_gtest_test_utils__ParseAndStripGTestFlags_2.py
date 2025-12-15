import sys
from agent.cpp_tests.build._deps.googletest-src.googletest.test.gtest_test_utils import _ParseAndStripGTestFlags
import json
try:
    res = _ParseAndStripGTestFlags(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
