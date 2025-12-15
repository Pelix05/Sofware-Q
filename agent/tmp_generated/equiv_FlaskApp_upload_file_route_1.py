import sys
from agent.FlaskApp import upload_file_route
import json
try:
    res = upload_file_route(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
