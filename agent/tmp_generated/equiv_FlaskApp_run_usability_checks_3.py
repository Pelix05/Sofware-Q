import sys
from agent.FlaskApp import run_usability_checks
import json
try:
    res = run_usability_checks(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
