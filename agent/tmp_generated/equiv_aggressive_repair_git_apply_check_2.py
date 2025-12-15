import sys
from agent.archive_python_tools_20251124_142656.aggressive_repair import git_apply_check
import json
try:
    res = git_apply_check(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
