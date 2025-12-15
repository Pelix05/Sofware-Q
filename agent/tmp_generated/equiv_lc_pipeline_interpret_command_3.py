import sys
from agent.lc_pipeline import interpret_command
import json
try:
    res = interpret_command(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
