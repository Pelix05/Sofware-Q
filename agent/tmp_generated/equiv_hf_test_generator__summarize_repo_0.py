import sys
from agent.hf_test_generator import _summarize_repo
import json
try:
    res = _summarize_repo()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
