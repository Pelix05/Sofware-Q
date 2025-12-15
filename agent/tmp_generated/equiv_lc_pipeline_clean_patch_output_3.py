import sys
from agent.lc_pipeline import clean_patch_output
import json
try:
    res = clean_patch_output(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
