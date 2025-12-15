import sys
from tools.plantuml_render_server import plantuml_encode
import json
try:
    res = plantuml_encode(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
