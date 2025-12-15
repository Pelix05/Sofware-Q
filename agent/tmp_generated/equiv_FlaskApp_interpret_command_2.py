import sys
from agent.FlaskApp import interpret_command
import json
try:
    res = interpret_command(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
