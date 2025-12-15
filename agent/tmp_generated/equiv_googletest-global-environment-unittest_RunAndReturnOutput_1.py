import sys
from agent.cpp_tests.build._deps.googletest-src.googletest.test.googletest-global-environment-unittest import RunAndReturnOutput
import json
try:
    res = RunAndReturnOutput(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
