import sys
from agent.archive_python_tools_20251124_142656.reconstruct_patches import git_apply_check
import json
try:
    res = git_apply_check(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
