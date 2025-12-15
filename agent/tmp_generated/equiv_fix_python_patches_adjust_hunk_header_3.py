import sys
from agent.archive_python_tools_20251124_142656.fix_python_patches import adjust_hunk_header
import json
try:
    res = adjust_hunk_header(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
