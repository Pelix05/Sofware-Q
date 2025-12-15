import sys
from agent.archive_python_tools_20251124_142656.reconstruct_patches import extract_code_blocks_from_raw
import json
try:
    res = extract_code_blocks_from_raw(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
