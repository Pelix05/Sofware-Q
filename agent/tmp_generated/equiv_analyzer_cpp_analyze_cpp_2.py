import sys
from agent.analyzer_cpp import analyze_cpp
import json
try:
    res = analyze_cpp(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
