import sys
from agent.lc_pipeline import classify_intent
import json
try:
    res = classify_intent(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
