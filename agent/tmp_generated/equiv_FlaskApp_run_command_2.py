import sys
from agent.FlaskApp import run_command
import json
try:
    res = run_command(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
