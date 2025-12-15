import sys
from agent.reasoning_module import generate_fix_suggestion
import json
try:
    res = generate_fix_suggestion(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
