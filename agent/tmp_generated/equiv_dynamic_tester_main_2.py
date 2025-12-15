import sys
from agent.dynamic_tester import main
import json
try:
    res = main(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
