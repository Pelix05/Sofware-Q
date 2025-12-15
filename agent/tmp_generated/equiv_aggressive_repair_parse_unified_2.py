import sys
from agent.archive_python_tools_20251124_142656.aggressive_repair import parse_unified
import json
try:
    res = parse_unified(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
