import sys
from agent.FlaskApp import compare_files
import json
try:
    res = compare_files(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
