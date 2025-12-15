import sys
from agent.dynamic_tester import _translate_command_for_windows
import json
try:
    res = _translate_command_for_windows()
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
