import sys
from agent.hf_test_generator import _build_prompt
import json
try:
    res = _build_prompt(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
