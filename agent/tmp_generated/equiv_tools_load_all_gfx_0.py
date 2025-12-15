import sys
from agent.archive_python_tools_20251124_142656.python_repo.puzzle-challenge.tools import load_all_gfx
import json
try:
    res = load_all_gfx()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
