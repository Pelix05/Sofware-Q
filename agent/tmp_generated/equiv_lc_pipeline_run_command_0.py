import sys
from agent.lc_pipeline import run_command
import json
try:
    res = run_command()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
