import sys
from agent.archive_python_tools_20251124_142656.analyzer_py import parse_args
import json
try:
    res = parse_args()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
