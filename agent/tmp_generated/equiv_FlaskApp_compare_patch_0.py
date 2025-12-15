import sys
from agent.FlaskApp import compare_patch
import json
try:
    res = compare_patch()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
