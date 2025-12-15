import sys
from agent.cpp_tests.build._deps.googletest-src.googlemock.test.gmock_test_utils import Main
import json
try:
    res = Main()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
