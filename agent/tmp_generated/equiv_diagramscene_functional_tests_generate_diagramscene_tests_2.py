import sys
from agent.diagramscene_functional_tests import generate_diagramscene_tests
import json
try:
    res = generate_diagramscene_tests(-1)
    print("EQUIV_OK", res)
    sys.exit(0)
except Exception as e:
    print("EQUIV_EXC", e)
    sys.exit(1)
