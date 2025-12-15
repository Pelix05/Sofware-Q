import sys
from agent.tools.concurrency_harness import worker
import json
try:
    res = worker(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
