import sys
from agent.archive_python_tools_20251124_142656.reconstruct_patches import find_candidate_newtext
import json
try:
    res = find_candidate_newtext(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
