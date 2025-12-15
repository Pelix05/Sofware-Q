import sys
from tools.plantuml_render_server import append3bytes
import json
try:
    res = append3bytes(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
