import sys
from agent.hf_test_generator import _call_hf_api
import json
try:
    res = _call_hf_api(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
