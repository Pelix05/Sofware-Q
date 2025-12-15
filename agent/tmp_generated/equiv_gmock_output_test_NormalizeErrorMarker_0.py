import sys
from agent.cpp_tests.build._deps.googletest-src.googlemock.test.gmock_output_test import NormalizeErrorMarker
import json
try:
    res = NormalizeErrorMarker()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
