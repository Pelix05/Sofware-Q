import sys
from agent.pipeline import run_pipeline
import json
try:
    res = run_pipeline(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
