import sys
from agent.diagramscene_real_tests import generate_diagramscene_real_tests
import json
try:
    res = generate_diagramscene_real_tests(0)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
