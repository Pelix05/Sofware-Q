import sys
from agent.FlaskApp import create_submission_package
import json
try:
    res = create_submission_package(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
