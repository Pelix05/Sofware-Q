import sys
from agent.dynamic_tester import apply_patches_from_dir
import json
try:
    res = apply_patches_from_dir(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
