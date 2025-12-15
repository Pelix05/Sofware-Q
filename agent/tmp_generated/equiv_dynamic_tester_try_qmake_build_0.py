import sys
from agent.dynamic_tester import try_qmake_build
import json
try:
    res = try_qmake_build()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
