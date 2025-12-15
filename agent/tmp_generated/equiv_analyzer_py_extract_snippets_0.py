import sys
from agent.archive_python_tools_20251124_142656.analyzer_py import extract_snippets
import json
try:
    res = extract_snippets()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
