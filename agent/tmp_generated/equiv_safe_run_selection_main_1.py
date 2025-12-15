import sys
from agent.safe_run_selection import main
import json
try:
    res = main(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
