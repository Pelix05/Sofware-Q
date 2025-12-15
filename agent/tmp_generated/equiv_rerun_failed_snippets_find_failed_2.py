import sys
from agent.archive_python_tools_20251124_142656.rerun_failed_snippets import find_failed
import json
try:
    res = find_failed(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
