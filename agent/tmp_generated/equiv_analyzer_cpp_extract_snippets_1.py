import sys
from agent.analyzer_cpp import extract_snippets
import json
try:
    res = extract_snippets(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
