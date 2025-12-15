import sys
from agent.FlaskApp import status_route
import json
try:
    res = status_route(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
