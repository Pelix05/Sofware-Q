import sys
from tools.plantuml_render_server import render
import json
try:
    res = render(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
