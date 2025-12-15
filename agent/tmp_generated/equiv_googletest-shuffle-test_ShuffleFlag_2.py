import sys
from agent.cpp_tests.build._deps.googletest-src.googletest.test.googletest-shuffle-test import ShuffleFlag
import json
try:
    res = ShuffleFlag(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
