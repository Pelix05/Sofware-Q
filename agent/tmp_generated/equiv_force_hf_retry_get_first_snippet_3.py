import sys
from agent.archive_python_tools_20251124_142656.force_hf_retry import get_first_snippet
import json
try:
    res = get_first_snippet(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
