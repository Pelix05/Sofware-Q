import sys
from agent.FlaskApp import run_dynamic_cpp
import json
try:
    res = run_dynamic_cpp(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
