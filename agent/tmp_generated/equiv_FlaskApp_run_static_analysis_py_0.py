import sys
from agent.FlaskApp import run_static_analysis_py
import json
try:
    res = run_static_analysis_py()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
