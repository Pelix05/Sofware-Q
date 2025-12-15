import sys
from agent.archive_python_tools_20251124_142656.aggressive_repair import process_one
import json
try:
    res = process_one(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
