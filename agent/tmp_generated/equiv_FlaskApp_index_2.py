import sys
from agent.FlaskApp import index
import json
try:
    res = index(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
