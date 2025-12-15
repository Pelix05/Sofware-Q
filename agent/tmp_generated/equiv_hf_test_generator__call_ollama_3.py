import sys
from agent.hf_test_generator import _call_ollama
import json
try:
    res = _call_ollama(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
