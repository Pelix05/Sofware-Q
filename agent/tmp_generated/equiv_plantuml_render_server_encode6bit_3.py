import sys
from tools.plantuml_render_server import encode6bit
import json
try:
    res = encode6bit(10000000000)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
