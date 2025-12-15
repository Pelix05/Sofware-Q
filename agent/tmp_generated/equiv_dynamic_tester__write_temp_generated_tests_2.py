import sys
from agent.dynamic_tester import _write_temp_generated_tests
import json
try:
    res = _write_temp_generated_tests(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
