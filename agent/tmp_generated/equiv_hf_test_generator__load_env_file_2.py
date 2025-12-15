import sys
from agent.hf_test_generator import _load_env_file
import json
try:
    res = _load_env_file(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
