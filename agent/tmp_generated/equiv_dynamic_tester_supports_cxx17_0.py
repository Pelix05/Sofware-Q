import sys
from agent.dynamic_tester import supports_cxx17
import json
try:
    res = supports_cxx17()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
