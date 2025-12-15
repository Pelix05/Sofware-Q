import sys
from agent.lc_pipeline import ask_llm
import json
try:
    res = ask_llm()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
