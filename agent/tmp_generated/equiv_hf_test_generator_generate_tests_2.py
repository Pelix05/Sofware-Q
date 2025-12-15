import sys
from agent.hf_test_generator import generate_tests
import json
try:
    res = generate_tests(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
