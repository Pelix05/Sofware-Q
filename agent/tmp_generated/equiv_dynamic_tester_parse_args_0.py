import sys
from agent.dynamic_tester import parse_args
import json
try:
    res = parse_args()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
