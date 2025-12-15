import sys
from agent.FlaskApp import handle_file_upload
import json
try:
    res = handle_file_upload(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
